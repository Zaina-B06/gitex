"""Lapse-risk features (Task 02b). Pure Python, engine-visible data only.

`compute_features` takes exactly what the engine itself holds for a user (profile, state, its own event log)
and nothing from a simulator. The same function is used for training and at inference, so they can't drift."""

from ..actions import default_library
from ..models import (
    Barrier,
    Behaviour,
    ContextFlag,
    EngagementState,
    Event,
    EventType,
    ScheduleType,
    UserProfile,
    UserState,
)
from ..safety import SCREENING_QUESTIONS

_OUTCOMES = {EventType.completed, EventType.partial, EventType.skipped, EventType.no_response}
_DONE = {EventType.completed, EventType.partial}
_TIER = {a.id: a.tier for a in default_library()}
_BEHAVIOUR = {a.id: a.behaviour for a in default_library()}
_DAYS_CAP = 30  # "days since" features are capped here (and set to it when the thing never happened)

FEATURE_NAMES: tuple[str, ...] = (
    "comp_rate_3", "comp_rate_7", "comp_rate_14", "comp_trend", "consecutive_misses",
    "partial_share_14", "no_response_share_14", "n_shown_7",
    "tier_movement", "tier_sleep", "tier_gap_movement", "tier_gap_sleep",
    "h_movement", "h_sleep", "h_slope_movement", "h_slope_sleep",
    "days_since_checkin", "checkin_due",
    *(f"last_barrier_{b.value}" for b in Barrier),
    "ctx_ramadan", "ctx_heat", "ctx_illness",
    *(f"schedule_{s.value}" for s in ScheduleType),
    "has_screening_flag",
    "state_active", "state_drifting", "state_recovering",
    "weekend_gap_14",
)


def _window(outcomes: list[Event], day: int, days: int) -> list[Event]:
    return [e for e in outcomes if day - days < e.day <= day]


def _rate(evs: list[Event], kinds: set[EventType]) -> float:
    return sum(e.type in kinds for e in evs) / len(evs) if evs else 0.0


def compute_features(profile: UserProfile, state: UserState, events: list[Event], day: int) -> dict[str, float]:
    """Features at the end of `day`, from the last 14 days of the engine's own log."""
    outcomes = sorted((e for e in events if e.type in _OUTCOMES and e.day <= day), key=lambda e: e.day)
    last3, last7, last14 = (_window(outcomes, day, n) for n in (3, 7, 14))
    rate3, rate7, rate14 = (_rate(w, _DONE) for w in (last3, last7, last14))

    misses = 0
    for e in reversed(outcomes):
        if e.type in _DONE:
            break
        misses += 1

    f: dict[str, float] = {
        "comp_rate_3": rate3,
        "comp_rate_7": rate7,
        "comp_rate_14": rate14,
        "comp_trend": rate3 - rate14,
        "consecutive_misses": float(min(misses, 14)),
        "partial_share_14": _rate(last14, {EventType.partial}),
        "no_response_share_14": _rate(last14, {EventType.no_response}),
        "n_shown_7": float(len(last7)),
    }

    shown = [e for e in events if e.type == EventType.action_shown and e.day <= day and e.action_id in _TIER]
    for b in Behaviour:
        current = state.current_tier.get(b, 0)
        max_seen = max((_TIER[e.action_id] for e in shown if _BEHAVIOUR[e.action_id] == b), default=current)
        hist = state.h_daily.get(b, [])
        h_now = state.habit_strength.get(b, 0.0)
        f[f"tier_{b.value}"] = float(current)
        f[f"tier_gap_{b.value}"] = float(max(0, max_seen - current))
        f[f"h_{b.value}"] = h_now
        f[f"h_slope_{b.value}"] = h_now - (hist[-7] if len(hist) >= 7 else (hist[0] if hist else h_now))

    checkins = [e for e in events if e.type == EventType.checkin and e.day <= day]
    f["days_since_checkin"] = float(min(day - checkins[-1].day, _DAYS_CAP) if checkins else _DAYS_CAP)
    f["checkin_due"] = float(state.checkin_due)
    last_primary = checkins[-1].payload.get("primary") if checkins else None
    for b in Barrier:
        f[f"last_barrier_{b.value}"] = float(last_primary == b.value)

    for flag in (ContextFlag.ramadan, ContextFlag.heat, ContextFlag.illness):
        f[f"ctx_{flag.value}"] = float(flag in state.context_flags)
    for s in ScheduleType:
        f[f"schedule_{s.value}"] = float(profile.basics.schedule_type == s)
    f["has_screening_flag"] = float(any(getattr(profile.screening, q) for q in SCREENING_QUESTIONS))
    for st in (EngagementState.active, EngagementState.drifting, EngagementState.recovering):
        f[f"state_{st.value}"] = float(state.engagement_state == st)

    # Weekend dip: day 1 is treated as a Monday, so days 6 and 7 of each week are the weekend.
    weekend = [e for e in last14 if e.day % 7 in (6, 0)]
    weekday = [e for e in last14 if e.day % 7 not in (6, 0)]
    f["weekend_gap_14"] = _rate(weekend, _DONE) - _rate(weekday, _DONE) if weekend and weekday else 0.0

    return {name: f[name] for name in FEATURE_NAMES}
