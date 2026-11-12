"""Policy: safety filter -> rules layer -> (bandit) -> step-up. AGENTS.md §6.3."""

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


def window_hour(profile: UserProfile, window: TimeWindow) -> int:
    if window == TimeWindow.morning:
        return (profile.basics.usual_wake_time.hour + config.MORNING_OFFSET_H) % 24
    if window == TimeWindow.midday:
        return config.MIDDAY_HOUR
    return (profile.basics.usual_sleep_time.hour + config.EVENING_OFFSET_H) % 24


def _next_window(w: TimeWindow) -> TimeWindow:
    order = list(TimeWindow)
    return order[(order.index(w) + 1) % len(order)]


def _tier_down(state: UserState, b: Behaviour) -> None:
    if b in state.current_tier:
        state.current_tier[b] = max(config.MIN_TIER, state.current_tier[b] - 1)
        state.successes_at_tier[b] = 0


def apply_barrier(profile: UserProfile, state: UserState, barrier: Barrier) -> str:
    """Rules layer: adjust the plan for a barrier. Mutates state; returns the message template id."""
    state.last_barrier = barrier
    focus = state.last_behaviour or profile.basics.goals[0]
    if barrier == Barrier.time:
        _tier_down(state, focus)
    elif barrier == Barrier.energy_fatigue:
        _tier_down(state, Behaviour.movement if Behaviour.movement in state.current_tier else focus)
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


def _pick_behaviour(profile: UserProfile, state: UserState, allowed: list[Action]) -> Behaviour | None:
    available = [b for b in profile.basics.goals if any(a.behaviour == b for a in allowed)]
    if not available:
        return None
    if state.last_barrier == Barrier.energy_fatigue and Behaviour.sleep in available:
        return Behaviour.sleep
    others = [b for b in available if b != state.last_behaviour]
    return others[0] if others else available[0]


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
    barrier: Barrier | None = None,
    hour: int | None = None,
    library: list[Action] | tuple[Action, ...] | None = None,
    bandit: Bandit | None = None,
) -> Action | None:
    """Pick today's action. Applies `barrier` to the plan first (mutating state). None = nothing to show."""
    if barrier is not None:
        apply_barrier(profile, state, barrier)
    if ContextFlag.paused in state.context_flags:
        return None
    hour = window_hour(profile, state.time_window) if hour is None else hour
    allowed = filter_actions(profile, state, Context(flags=state.context_flags, hour=hour), library)
    behaviour = _pick_behaviour(profile, state, allowed)
    if behaviour is None:
        return None
    pool = [a for a in allowed if a.behaviour == behaviour]
    target = min(state.current_tier[behaviour], tier_cap(profile, behaviour))
    at_or_below = [a for a in pool if a.tier <= target]
    best = max(a.tier for a in at_or_below) if at_or_below else min(a.tier for a in pool)
    ranked = sorted((a for a in pool if a.tier == best), key=lambda a: _setting_rank(profile, a))
    return (bandit or RulesBandit()).select(ranked, state)


def register_success(state: UserState, behaviour: Behaviour, action_tier: int, cap: int) -> None:
    """Step-up: 3 full completions at the current tier -> up one tier, never past the cap."""
    if action_tier != state.current_tier[behaviour]:
        return  # a context fallback (e.g. Ramadan) to a lower tier doesn't earn a step-up
    state.successes_at_tier[behaviour] += 1
    if (
        state.successes_at_tier[behaviour] >= config.STEP_UP_SUCCESSES
        and state.current_tier[behaviour] < cap
    ):
        state.current_tier[behaviour] += 1
        state.successes_at_tier[behaviour] = 0
