"""Policy: safety filter -> rules layer -> (bandit) -> tier changes. AGENTS.md §6.3."""

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


class Bandit(Protocol):
    def select(self, allowed_actions: list[Action], user_state: UserState) -> Action: ...


class RulesBandit:
    """Stub until Task 02 (Thompson sampling): returns the rules layer's top-ranked action."""

    def select(self, allowed_actions: list[Action], user_state: UserState) -> Action:
        return allowed_actions[0]


def tier_cap(profile: UserProfile, behaviour: Behaviour) -> int:
    if behaviour == Behaviour.movement:
        return screening_flags(profile).movement_tier_cap
    return config.MAX_TIER


def action_window(state: UserState, behaviour: Behaviour) -> TimeWindow:
    return state.time_window if behaviour == Behaviour.movement else TimeWindow.evening


def window_hour(profile: UserProfile, window: TimeWindow) -> int:
    if window == TimeWindow.morning:
        return (profile.basics.usual_wake_time.hour + config.MORNING_OFFSET_H) % 24
    if window == TimeWindow.midday:
        return config.MIDDAY_HOUR
    return (profile.basics.usual_sleep_time.hour + config.EVENING_OFFSET_H) % 24


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
        state.time_window = _next_window(state.time_window)
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
) -> Action | None:
    """Today's action for one behaviour. None = nothing safe to show (or paused / not a goal)."""
    if ContextFlag.paused in state.context_flags or behaviour not in state.current_tier:
        return None
    hour = window_hour(profile, action_window(state, behaviour)) if hour is None else hour
    allowed = filter_actions(profile, state, Context(flags=state.context_flags, hour=hour), library)
    pool = [a for a in allowed if a.behaviour == behaviour]
    if not pool:
        return None
    target = min(state.current_tier[behaviour], tier_cap(profile, behaviour))
    at_or_below = [a for a in pool if a.tier <= target]
    best = max(a.tier for a in at_or_below) if at_or_below else min(a.tier for a in pool)
    ranked = sorted((a for a in pool if a.tier == best), key=lambda a: _setting_rank(profile, a))
    return (bandit or RulesBandit()).select(ranked, state)


def choose_actions(
    profile: UserProfile,
    state: UserState,
    library: list[Action] | tuple[Action, ...] | None = None,
    bandit: Bandit | None = None,
) -> list[Action]:
    """One action per goal (movement first), each at its own prompt window."""
    picks = (
        choose_action(profile, state, b, library=library, bandit=bandit) for b in Behaviour
    )
    return [a for a in picks if a is not None]
