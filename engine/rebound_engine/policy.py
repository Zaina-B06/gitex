"""Policy: safety filter -> rules layer (tier) -> bandit (action + window) -> tier changes. AGENTS.md §6.3."""

import random
from typing import Protocol

from . import config
from .actions import filter_actions
from .models import (
    Action,
    ActionSetting,
    Barrier,
    Behaviour,
    Channel,
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
}

# When several barriers are given, the first one in this order is applied (safety-relevant first).
BARRIER_PRIORITY = (
    Barrier.illness_pain,
    Barrier.environment,
    Barrier.energy_fatigue,
    Barrier.schedule_change,
    Barrier.time,
    Barrier.forgot,
    Barrier.low_motivation,
    Barrier.social_family,
    Barrier.other,
)


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


def _candidate_windows(behaviour: Behaviour) -> list[TimeWindow]:
    return list(TimeWindow) if behaviour == Behaviour.movement else [TimeWindow.evening]


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
    default = state.time_window if behaviour == Behaviour.movement else TimeWindow.evening
    i = windows.index(default)
    ordered = windows[i:] + windows[:i]  # default first, then the next windows in order
    quiet = profile.preferences.quiet_hours
    free = [(w, h) for w in ordered if not _in_quiet_hours(h := window_hour(profile, w), quiet)]
    return free or [(default, quiet.end.hour)]


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
    return BARRIER_MESSAGE[barrier]


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
            for a in filter_actions(profile, state, Context(flags=state.context_flags, hour=h), library)
            if a.behaviour == behaviour
        ]
        for w, h in options
    }
    pool = [a for actions in allowed_at.values() for a in actions]
    if not pool:
        return None
    target = min(state.current_tier[behaviour], tier_cap(profile, behaviour))
    at_or_below = [a.tier for a in pool if a.tier <= target]
    best = max(at_or_below) if at_or_below else min(a.tier for a in pool)
    arms = [
        ScheduledAction(action=a, time_window=w, hour=h, explanation_id=a.id)
        for (w, h), actions in allowed_at.items()
        for a in sorted((a for a in actions if a.tier == best), key=lambda a: _setting_rank(profile, a))
    ]
    return (bandit or RulesBandit()).select(arms, state)


def choose_actions(
    profile: UserProfile,
    state: UserState,
    library: list[Action] | tuple[Action, ...] | None = None,
    bandit: Bandit | None = None,
) -> list[ScheduledAction]:
    """One action per goal (movement first), each with its prompt window and hour."""
    picks = (choose_action(profile, state, b, library=library, bandit=bandit) for b in Behaviour)
    return [a for a in picks if a is not None]
