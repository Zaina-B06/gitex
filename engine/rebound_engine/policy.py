"""Policy: safety filter -> rules layer (tier) -> bandit (action + window) -> tier changes. AGENTS.md §6.3."""

import random
from typing import Protocol

from . import config
from .actions import filter_actions
from .calendar import in_busy
from .models import (
    Action,
    ActionSetting,
    Barrier,
    Behaviour,
    Channel,
    Condition,
    Context,
    ContextFlag,
    DayOutcome,
    EngagementState,
    PlaceSetting,
    ScheduledAction,
    TimeRange,
    TimeWindow,
    UserProfile,
    UserState,
)
from .safety import screening_flags

# Message template ids; the text itself lives in the LLM/templates layer (Task 03).
BARRIER_MESSAGE = {
    Barrier.time: "implementation_intention",
    Barrier.energy_fatigue: "rest_is_ok",
    Barrier.illness_pain: "care",
    Barrier.schedule_change: "new_time",
    Barrier.environment: "indoor_swap",
    Barrier.low_motivation: "your_reason",
    Barrier.social_family: "thanks_for_sharing",
    Barrier.forgot: "new_reminder",
    Barrier.other: "thanks_for_sharing",
    Barrier.craving: "craving_tip",
    Barrier.stress: "stress_rest",
    Barrier.others_smoking: "smoke_free_space",
    Barrier.no_healthy_food_nearby: "pantry_swap",
}

# When several barriers are given, the first one in this order is applied (safety-relevant first).
# Part B barriers slot in without changing the order of the original ones.
BARRIER_PRIORITY = (
    Barrier.illness_pain,
    Barrier.environment,
    Barrier.energy_fatigue,
    Barrier.stress,
    Barrier.schedule_change,
    Barrier.time,
    Barrier.craving,
    Barrier.others_smoking,
    Barrier.no_healthy_food_nearby,
    Barrier.forgot,
    Barrier.low_motivation,
    Barrier.social_family,
    Barrier.other,
)

# A barrier that prefers steps with this tag (until the next full completion clears last_barrier).
BARRIER_TAG = {
    Barrier.craving: "substitution",
    Barrier.others_smoking: "cue_avoidance",
    Barrier.no_healthy_food_nearby: "no_shopping",
}


def primary_barrier(barriers: list[Barrier]) -> Barrier | None:
    return min(barriers, key=BARRIER_PRIORITY.index) if barriers else None


def arm_key(action_id: str, window: TimeWindow) -> str:
    return f"{action_id}@{window.value}"


class Bandit(Protocol):
    def select(self, arms: list[ScheduledAction], user_state: UserState) -> ScheduledAction: ...


class RulesBandit:
    """Rules mode: the arms come ranked by the rules layer (default window first); take the top one."""

    def select(self, arms: list[ScheduledAction], user_state: UserState) -> ScheduledAction:
        return arms[0]


class ThompsonBandit:
    """Thompson sampling over (action, window) arms with per-user Beta(alpha, beta) in state.bandit_params."""

    def __init__(self, rng: random.Random) -> None:
        self.rng = rng  # seeded by the caller; no global randomness

    def select(self, arms: list[ScheduledAction], user_state: UserState) -> ScheduledAction:
        params = user_state.bandit_params

        def draw(arm: ScheduledAction) -> float:
            alpha, beta = params.get(arm_key(arm.action.id, arm.time_window), config.BANDIT_PRIOR)
            return self.rng.betavariate(alpha, beta)

        return max(arms, key=draw)


def update_arm(state: UserState, key: str, reward: float) -> None:
    """Fractional Beta update: alpha += r, beta += 1 - r."""
    alpha, beta = state.bandit_params.get(key, list(config.BANDIT_PRIOR))
    state.bandit_params[key] = [alpha + reward, beta + 1 - reward]


def init_bandit_params(
    profile: UserProfile, library: list[Action] | tuple[Action, ...]
) -> dict[str, list[float]]:
    """Prior for every arm the user could get, with a warm start for BCTs matching past_helpers."""
    helper_bcts = {
        bct for h in profile.history.past_helpers for bct in config.HELPER_BCTS.get(h.value, [])
    }
    params = {}
    for a in library:
        if a.behaviour not in profile.basics.goals:
            continue
        alpha, beta = config.BANDIT_PRIOR
        if a.bct_code in helper_bcts:
            alpha += config.WARM_START_BONUS
        for w in _candidate_windows(a.behaviour):
            params[arm_key(a.id, w)] = [alpha, beta]
    return params


def tier_cap(profile: UserProfile, behaviour: Behaviour) -> int:
    if behaviour == Behaviour.movement:
        return screening_flags(profile).movement_tier_cap
    return config.MAX_TIER


def effective_flags(state: UserState) -> set[ContextFlag]:
    """Explicit flags plus what the calendar worked out (Task 05 A2); the calendar never removes a flag."""
    return state.context_flags | state.auto_flags


# Prompt windows per behaviour: movement can move between all three; meals at lunch, the first cigarette in the
# morning, rest and sleep in the evening.
_WINDOWS = {
    Behaviour.movement: list(TimeWindow),
    Behaviour.sleep: [TimeWindow.evening],
    Behaviour.nutrition: [TimeWindow.afternoon],
    Behaviour.smoking: [TimeWindow.morning],
    Behaviour.recovery: [TimeWindow.evening],
}


def _candidate_windows(behaviour: Behaviour) -> list[TimeWindow]:
    return list(_WINDOWS[behaviour])


def window_hour(profile: UserProfile, window: TimeWindow) -> int:
    if window == TimeWindow.morning:
        return (profile.basics.usual_wake_time.hour + config.MORNING_OFFSET_H) % 24
    if window == TimeWindow.afternoon:
        return config.AFTERNOON_HOUR
    return (profile.basics.usual_sleep_time.hour + config.EVENING_OFFSET_H) % 24


def _in_quiet_hours(hour: int, quiet: TimeRange | None) -> bool:
    if quiet is None:
        return False
    start, end = quiet.start.hour, quiet.end.hour
    return start <= hour < end if start <= end else hour >= start or hour < end


def prompt_options(
    profile: UserProfile, state: UserState, behaviour: Behaviour
) -> list[tuple[TimeWindow, int]]:
    """(window, hour) pairs outside quiet hours; the rules-mode default window comes first.
    If every window is quiet, the default window moves to the end of quiet hours."""
    windows = _candidate_windows(behaviour)
    default = state.time_window if behaviour == Behaviour.movement else windows[0]
    i = windows.index(default)
    ordered = windows[i:] + windows[:i]  # default first, then the next windows in order
    quiet = profile.preferences.quiet_hours
    if state.day_times is None and state.iftar_hour is None:  # no calendar context: unchanged (the simulator)
        free = [(w, h) for w in ordered if not _in_quiet_hours(h := window_hour(profile, w), quiet)]
        return free or [(default, quiet.end.hour)]
    return _calendar_options(profile, state, behaviour, ordered, quiet)


def _calendar_options(
    profile: UserProfile, state: UserState, behaviour: Behaviour, ordered: list[TimeWindow], quiet: TimeRange | None
) -> list[tuple[TimeWindow, int]]:
    """Task 05 A2: prompt hours from real shift timings and iftar; never in quiet, work or post-night-shift sleep."""
    t = state.day_times
    busy = t.busy if t else []
    wake = t.wake if t else profile.basics.usual_wake_time.hour
    sleep = t.sleep if t else profile.basics.usual_sleep_time.hour

    def hour(w: TimeWindow) -> int:
        if w == TimeWindow.morning:
            return (wake + config.MORNING_OFFSET_H) % 24
        if w == TimeWindow.afternoon:
            return config.AFTERNOON_HOUR
        return (sleep + config.EVENING_OFFSET_H) % 24

    fasting = ContextFlag.ramadan in (state.context_flags | state.auto_flags)
    if behaviour == Behaviour.movement and state.iftar_hour is not None and fasting:
        candidates = [(TimeWindow.evening, (state.iftar_hour + config.RAMADAN_MOVE_AFTER_IFTAR_H) % 24)]
    elif behaviour in (Behaviour.nutrition, Behaviour.smoking) and state.iftar_hour is not None and fasting:
        candidates = [(ordered[0], state.iftar_hour)]  # meals and the first cigarette come at iftar
    elif behaviour == Behaviour.sleep and t is not None and t.sleep_prompt is not None:
        candidates = [(TimeWindow.evening, t.sleep_prompt)]  # wind-down as the night shift ends
    else:
        candidates = [(w, hour(w)) for w in ordered]

    def free(h: int) -> bool:
        return not _in_quiet_hours(h, quiet) and not in_busy(h, busy)

    options = [(w, h) for w, h in candidates if free(h)]
    if options:
        return options
    w, h = candidates[0]
    later = next(((h + k) % 24 for k in range(1, 24) if free((h + k) % 24)), h)
    return [(w, later)]


def _next_window(w: TimeWindow) -> TimeWindow:
    order = list(TimeWindow)
    return order[(order.index(w) + 1) % len(order)]


# ---------- tier changes ----------


def _set_tier(state: UserState, b: Behaviour, tier: int) -> None:
    state.current_tier[b] = tier
    state.successes_at_tier[b] = 0
    state.fails_at_tier[b] = 0


def _tier_down(state: UserState, b: Behaviour, by: int = 1) -> None:
    if b in state.current_tier:
        _set_tier(state, b, max(config.MIN_TIER, state.current_tier[b] - by))


def shrink_on_slip(state: UserState, new_state: EngagementState) -> None:
    """Entering drifting -> every tier -1; entering lapsed -> every tier back to 1."""
    for b in list(state.current_tier):
        if new_state == EngagementState.drifting:
            _tier_down(state, b, config.DRIFT_TIER_DROP)
        elif new_state == EngagementState.lapsed:
            _set_tier(state, b, config.MIN_TIER)


def update_tier_counters(
    state: UserState, behaviour: Behaviour, action_tier: int, outcome: DayOutcome, cap: int
) -> None:
    """Step-up after consecutive full completions, step-down after consecutive misses (while active)."""
    if outcome in (DayOutcome.paused, DayOutcome.illness):
        return
    if action_tier != state.current_tier[behaviour]:
        return  # a context fallback (e.g. Ramadan) to a lower tier doesn't move the tier
    b = behaviour
    if outcome == DayOutcome.completed:
        state.fails_at_tier[b] = 0
        state.successes_at_tier[b] += 1
        # No step-up while drifting or lapsed: after a lapse, only once recovering/active.
        if (
            state.successes_at_tier[b] >= config.STEP_UP_SUCCESSES
            and state.engagement_state in (EngagementState.active, EngagementState.recovering)
            and state.current_tier[b] < cap
        ):
            _set_tier(state, b, state.current_tier[b] + 1)
    elif outcome == DayOutcome.partial:
        state.fails_at_tier[b] = 0  # a response breaks the run of misses; doesn't count toward step-up
    else:
        state.successes_at_tier[b] = 0
        state.fails_at_tier[b] += 1
        if (
            state.fails_at_tier[b] >= config.STEP_DOWN_FAILURES
            and state.engagement_state == EngagementState.active
        ):
            _tier_down(state, b)


# ---------- rules layer ----------


def apply_barrier(profile: UserProfile, state: UserState, barrier: Barrier) -> str:
    """Adjust the plan for a barrier. Mutates state; returns the message template id."""
    state.last_barrier = barrier
    if barrier == Barrier.time:
        for b in list(state.current_tier):
            _tier_down(state, b)
    elif barrier == Barrier.energy_fatigue:
        # Movement gets smaller; sleep actions stay as they are (and only low-energy actions show).
        target = Behaviour.movement if Behaviour.movement in state.current_tier else Behaviour.sleep
        _tier_down(state, target)
    elif barrier in (Barrier.schedule_change, Barrier.forgot):
        state.time_window = _next_window(state.time_window)  # rules mode; bandit mode: see Engine.checkin
        if barrier == Barrier.forgot:
            # voice_note is disabled in the prototype, so toggle between the two live channels.
            state.channel = Channel.whatsapp_style if state.channel == Channel.app else Channel.app
    elif barrier == Barrier.illness_pain:
        state.context_flags.add(ContextFlag.illness)
    elif barrier == Barrier.environment:
        state.prefer_indoor = True
    elif barrier == Barrier.craving:
        _tier_down(state, Behaviour.smoking)  # and a substitution step (BARRIER_TAG)
    elif barrier == Barrier.stress:
        for b in (Behaviour.movement, Behaviour.nutrition, Behaviour.smoking):
            _tier_down(state, b)  # recovery comes first today (todays_behaviours)
    return BARRIER_MESSAGE[barrier]


def _tag_rank(profile: UserProfile, state: UserState, a: Action) -> int:
    """0 for a variant that fits this person right now (Ramadan, diabetes, recovering), else 1. Movement and sleep
    actions carry no tags, so their order is unchanged."""
    managing = profile.conditions.managing
    fits = (
        ("ramadan_only" in a.tags and ContextFlag.ramadan in effective_flags(state))
        or ("diabetes" in a.tags and Condition.diabetes in managing)
        or ("after_illness" in a.tags and (Condition.recovering_from_illness_or_injury in managing
                                           or ContextFlag.illness in effective_flags(state)))
    )
    return 0 if fits else 1


def todays_behaviours(state: UserState) -> list[Behaviour]:
    """Goals in plan order; stress puts recovery first. With more than MAX_ACTIVE_BEHAVIOURS goals, the first ones
    stay and the last slot rotates daily through the rest (burden cap)."""
    order = [b for b in (state.order or list(Behaviour)) if b in state.current_tier]
    order += [b for b in Behaviour if b in state.current_tier and b not in order]
    if state.last_barrier == Barrier.stress and Behaviour.recovery in order:
        order.remove(Behaviour.recovery)
        order.insert(0, Behaviour.recovery)
    cap = config.MAX_ACTIVE_BEHAVIOURS
    if len(order) <= cap:
        return order
    fixed, rest = order[: cap - 1], order[cap - 1 :]
    return [*fixed, rest[state.rotation % len(rest)]]


def _setting_rank(profile: UserProfile, a: Action) -> int:
    preferred = (
        ActionSetting.outdoor
        if profile.preferences.setting == PlaceSetting.outdoor
        else ActionSetting.indoor
    )
    if a.setting == preferred:
        return 0
    return 1 if a.setting == ActionSetting.any else 2


def choose_action(
    profile: UserProfile,
    state: UserState,
    behaviour: Behaviour,
    hour: int | None = None,
    library: list[Action] | tuple[Action, ...] | None = None,
    bandit: Bandit | None = None,
) -> ScheduledAction | None:
    """Today's action for one behaviour. None = nothing safe to show (or paused / not a goal).

    The rules layer fixes the tier; every arm is a safe (action, window) pair at that tier.
    `hour` overrides the prompt hour (tests)."""
    if ContextFlag.paused in state.context_flags or behaviour not in state.current_tier:
        return None
    options = prompt_options(profile, state, behaviour)
    if hour is not None:
        options = [(options[0][0], hour)]
    allowed_at = {
        (w, h): [
            a
            for a in filter_actions(profile, state, Context(flags=effective_flags(state), hour=h), library)
            if a.behaviour == behaviour
        ]
        for w, h in options
    }
    pool = [a for actions in allowed_at.values() for a in actions]
    if not pool:
        return None
    target = min(state.current_tier[behaviour], tier_cap(profile, behaviour))
    # A Part B barrier (craving, others smoking, no healthy food nearby) prefers its kind of step when one fits.
    tag = BARRIER_TAG.get(state.last_barrier) if state.last_barrier else None
    if not (tag and any(tag in a.tags and a.tier <= target for a in pool)):
        tag = None
    pool = [a for a in pool if tag is None or tag in a.tags]
    at_or_below = [a.tier for a in pool if a.tier <= target]
    best = max(at_or_below) if at_or_below else min(a.tier for a in pool)
    arms = [
        ScheduledAction(action=a, time_window=w, hour=h, explanation_id=a.id)
        for (w, h), actions in allowed_at.items()
        for a in sorted(
            (a for a in actions if a.tier == best and (tag is None or tag in a.tags)),
            key=lambda a: (_tag_rank(profile, state, a), _setting_rank(profile, a)),
        )
    ]
    return (bandit or RulesBandit()).select(arms, state)


def choose_actions(
    profile: UserProfile,
    state: UserState,
    library: list[Action] | tuple[Action, ...] | None = None,
    bandit: Bandit | None = None,
) -> list[ScheduledAction]:
    """One action per behaviour shown today (plan order, at most MAX_ACTIVE_BEHAVIOURS), with window and hour."""
    picks = (choose_action(profile, state, b, library=library, bandit=bandit) for b in todays_behaviours(state))
    return _spread_hours(profile, state, [a for a in picks if a is not None])


# Movement and sleep can already share an hour in the simulator (movement moved to the evening); moving one would
# change run_011, so only clashes involving another behaviour are spread.
_SIM_BEHAVIOURS = frozenset({Behaviour.movement, Behaviour.sleep})


def _spread_hours(profile: UserProfile, state: UserState, scheduled: list[ScheduledAction]) -> list[ScheduledAction]:
    """When a later action shares an hour with an earlier one, move it 1-3 hours later to a free hour (outside quiet
    hours, work/post-shift sleep and, for outdoor steps, the heat window). If none is free it stays."""
    quiet = profile.preferences.quiet_hours
    busy = state.day_times.busy if state.day_times else []
    heat = ContextFlag.heat in effective_flags(state)

    def free(h: int, a: Action, used: dict[int, Behaviour]) -> bool:
        hot = heat and a.setting == ActionSetting.outdoor and config.HEAT_START_HOUR <= h < config.HEAT_END_HOUR
        return h not in used and not _in_quiet_hours(h, quiet) and not in_busy(h, busy) and not hot

    used: dict[int, Behaviour] = {}
    out = []
    for s in scheduled:
        other = used.get(s.hour)
        if other is not None and not {other, s.action.behaviour} <= _SIM_BEHAVIOURS:
            later = next(((s.hour + k) % 24 for k in range(1, config.SPREAD_MAX_SHIFT_H + 1)
                          if free((s.hour + k) % 24, s.action, used)), None)
            if later is not None:
                s = s.model_copy(update={"hour": later})
        used.setdefault(s.hour, s.action.behaviour)
        out.append(s)
    return out


def lighter_option(
    profile: UserProfile,
    state: UserState,
    scheduled: ScheduledAction,
    library: list[Action] | tuple[Action, ...] | None = None,
) -> Action | None:
    """A smaller action of the same behaviour, at the same hour, through the same safety filter (risk hook).
    None if the shown action is already the smallest that's allowed."""
    behaviour = scheduled.action.behaviour
    target = scheduled.action.tier - 1
    if target < config.MIN_TIER:
        return None
    allowed = filter_actions(profile, state, Context(flags=effective_flags(state), hour=scheduled.hour), library)
    pool = [a for a in allowed if a.behaviour == behaviour and a.tier <= target]
    if not pool:
        return None
    best = max(a.tier for a in pool)
    return min((a for a in pool if a.tier == best), key=lambda a: _setting_rank(profile, a))
