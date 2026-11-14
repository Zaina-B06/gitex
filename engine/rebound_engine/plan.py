"""Personal plan builder (Task 05 Part A).

build_plan(profile) describes what the engine will do for this person and why. It reads the same safety and
starting-tier functions the engine uses, so the summary can't drift from what users actually get."""

from . import config
from .models import Behaviour, Condition, PlanBehaviour, PlanSummary, SmokingStatus, UserProfile
from .safety import screening_flags
from .state import starting_movement_tier

# User-facing reason keys, most important first (safety, then conditions, then starting level, then context).
_ORDER = (
    "see_doctor_gentle",  # chest pain or fainting on the health check
    "high_blood_pressure",  # chip -> health-check Q1 rules
    "back_or_joint_pain",  # chip -> health-check Q6 rules (low-impact)
    "health_check",  # any other "yes" on the health check
    "pregnancy",  # pregnancy-safe steps only
    "mobility",  # seated movement
    "recovering",  # gentlest starting level
    "recovery_first",  # recovering or stressed, and chose recovery -> rest steps first
    "nutrition_first",  # diabetes, and chose nutrition -> meal steps early
    "senior_start",  # balance-friendly start at 65+
    "small_start",  # few active days now -> small first steps
    "fasting",  # fasts in Ramadan -> fasting-safe steps then
    "rotating",  # more goals than daily actions -> the last slot rotates
)
REASON_KEYS = frozenset(_ORDER)
SAFETY_REASONS = frozenset(_ORDER[:6])
_MOVEMENT_ONLY = frozenset({"see_doctor_gentle", "high_blood_pressure", "back_or_joint_pain", "health_check",
                            "mobility", "recovering", "senior_start", "small_start"})


def goal_order(profile: UserProfile) -> list[Behaviour]:
    """The user's goals, most important first: recovery when recovering or stressed, nutrition with diabetes, then
    the usual order. Movement-and-sleep users without these answers keep [movement, sleep] (the simulator's case)."""
    managing = set(profile.conditions.managing)
    first = []
    if managing & {Condition.recovering_from_illness_or_injury, Condition.stress}:
        first.append(Behaviour.recovery)
    if Condition.diabetes in managing:
        first.append(Behaviour.nutrition)
    goals = profile.basics.goals
    return [b for b in first if b in goals] + [b for b in Behaviour if b in goals and b not in first]


def build_plan(profile: UserProfile) -> PlanSummary:
    screening = screening_flags(profile)
    managing = set(profile.conditions.managing)
    goals = profile.basics.goals
    order = goal_order(profile)
    moves = Behaviour.movement in goals
    start_tiers: dict[Behaviour, int] = {}
    if moves:
        start_tiers[Behaviour.movement] = starting_movement_tier(profile, screening)
    if Behaviour.sleep in goals:
        start_tiers[Behaviour.sleep] = config.SLEEP_START_TIER
    for b in (Behaviour.nutrition, Behaviour.smoking, Behaviour.recovery):
        if b in goals:
            start_tiers[b] = config.NEW_BEHAVIOUR_START_TIER
    active = order[: config.MAX_ACTIVE_BEHAVIOURS]

    found = {
        "see_doctor_gentle": screening.see_doctor,
        "high_blood_pressure": Condition.high_blood_pressure in managing,
        "back_or_joint_pain": Condition.back_or_joint_pain in managing,
        "health_check": bool(screening.positive) and not screening.see_doctor,
        "pregnancy": screening.pregnancy_safe_only,
        "mobility": screening.seated_only,
        "recovering": Condition.recovering_from_illness_or_injury in managing,
        "fasting": profile.preferences.fasting_ramadan,
        "recovery_first": bool(order) and order[0] == Behaviour.recovery,
        "nutrition_first": Behaviour.nutrition in active and Condition.diabetes in managing,
        "rotating": len(order) > config.MAX_ACTIVE_BEHAVIOURS,
    }
    gentle_start = moves and start_tiers[Behaviour.movement] == config.MIN_TIER and not (
        found["see_doctor_gentle"] or found["recovering"])
    found["senior_start"] = gentle_start and profile.basics.age_years >= config.SENIOR_AGE
    found["small_start"] = gentle_start and not found["senior_start"]
    reasons = [k for k in _ORDER if found[k] and (moves or k not in _MOVEMENT_ONLY)]

    # Queued (internal, never shown): goals beyond the daily cap, then behaviours that would fit what the person
    # manages but that they didn't choose. Recovery first (rest before effort).
    queued: list[PlanBehaviour] = list(order[config.MAX_ACTIVE_BEHAVIOURS:])
    queued_reasons: list[str] = []
    for behaviour, reason, applies in (
        (PlanBehaviour.recovery, "queue_recovering", Condition.recovering_from_illness_or_injury in managing),
        (PlanBehaviour.recovery, "queue_stress", Condition.stress in managing),
        (PlanBehaviour.nutrition, "queue_diabetes", Condition.diabetes in managing),
        (PlanBehaviour.smoking, "queue_smoker", profile.history.smoking_status == SmokingStatus.current),
    ):
        if applies and behaviour not in goals:
            queued_reasons.append(reason)
            if behaviour not in queued:
                queued.append(behaviour)

    return PlanSummary(
        active=active, queued=queued, queued_reasons=queued_reasons, start_tiers=start_tiers,
        movement_tier_cap=screening.movement_tier_cap, reasons=reasons,
    )
