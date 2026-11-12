"""Habit strength and engagement state (AGENTS.md §6.1)."""

from . import config
from .models import (
    Behaviour,
    ContextFlag,
    DayLog,
    DayOutcome,
    EngagementState,
    ScheduleType,
    ScreeningResult,
    UserProfile,
    UserState,
)

_NOT_COUNTED = (DayOutcome.paused, DayOutcome.illness)
_DONE = (DayOutcome.completed, DayOutcome.partial)


def update_habit_strength(h: float, outcome: DayOutcome, lam: float = config.HABIT_LAMBDA) -> float:
    """H_t = lam * H_{t-1} + (1 - lam) * a_t. Decays, never resets; paused/illness days leave H unchanged."""
    if outcome in _NOT_COUNTED:
        return h
    a = config.OUTCOME_VALUE[outcome]
    return min(1.0, max(0.0, lam * h + (1 - lam) * a))


def _completions(days: list[DayLog]) -> int:
    return sum(d.outcome in _DONE for d in days)


def compute_engagement_state(history: list[DayLog], previous: EngagementState) -> EngagementState:
    days = [d for d in history if d.outcome not in _NOT_COUNTED]
    if len(days) < config.MIN_DAYS_FOR_STATE:
        return previous
    window = days[-config.ENGAGEMENT_WINDOW_DAYS :]
    # Rate, not count, so the first week works with fewer than 7 days.
    rate = _completions(window) / len(window)

    no_response_run = 0
    for d in reversed(days):
        if d.outcome != DayOutcome.no_response:
            break
        no_response_run += 1
    if no_response_run >= config.LAPSE_CONSECUTIVE_NO_RESPONSE:
        return EngagementState.lapsed

    if previous in (EngagementState.lapsed, EngagementState.recovering):
        if rate >= config.ACTIVE_MIN_RATE:
            return EngagementState.active
        recent = days[-config.RECOVERY_WINDOW_DAYS :]
        if _completions(recent) >= config.RECOVERY_MIN_COMPLETIONS:
            return EngagementState.recovering
        if previous == EngagementState.lapsed:
            return EngagementState.lapsed

    if rate <= config.LAPSED_MAX_RATE:
        return EngagementState.lapsed
    if rate < config.ACTIVE_MIN_RATE:
        return EngagementState.drifting
    # The ">= 50% drop vs previous 7 days" rule can't fire here: >= 4/7 now and a 50% drop
    # would need >= 8/7 before. Any such drop already lands in drifting above. See ASSUMPTIONS.md.
    return EngagementState.active


def starting_movement_tier(profile: UserProfile, screening: ScreeningResult) -> int:
    days = profile.baseline.active_days_per_week
    tier = next(t for max_days, t in config.START_TIER_BY_ACTIVE_DAYS if days <= max_days)
    if profile.basics.age_years >= config.SENIOR_AGE:
        tier = min(tier, config.SENIOR_START_TIER)
    body = profile.body
    if body and body.height_cm and body.weight_kg:
        bmi = body.weight_kg / (body.height_cm / 100) ** 2  # internal only, never shown
        for threshold, cap in config.BMI_START_CAPS:
            if bmi >= threshold:
                tier = min(tier, cap)
                break
    return min(tier, screening.movement_tier_cap)


def initial_state(profile: UserProfile, screening: ScreeningResult) -> UserState:
    goals = profile.basics.goals
    tiers: dict[Behaviour, int] = {}
    if Behaviour.movement in goals:
        tiers[Behaviour.movement] = starting_movement_tier(profile, screening)
    if Behaviour.sleep in goals:
        tiers[Behaviour.sleep] = config.SLEEP_START_TIER
    flags = {ContextFlag.shift_pattern} if profile.basics.schedule_type == ScheduleType.shift else set()
    # Users told to see a doctor start with sleep: behaviours alternate away from last_behaviour.
    last = Behaviour.movement if screening.see_doctor and Behaviour.sleep in goals else None
    return UserState(
        user_id=profile.user_id,
        habit_strength={b: 0.0 for b in tiers},
        current_tier=tiers,
        successes_at_tier={b: 0 for b in tiers},
        context_flags=flags,
        channel=profile.preferences.channel,
        last_behaviour=last,
    )
