"""Task 05 Part A: personal plan builder. Conditions only ever tighten safety; plans differ by person from day one."""

import itertools

from rebound_engine import config
from rebound_engine.models import Behaviour, Condition, Event, EventType, PlanBehaviour
from rebound_engine.plan import REASON_KEYS, SAFETY_REASONS, build_plan
from rebound_engine.safety import SCREENING_QUESTIONS, SEE_DOCTOR_QUESTIONS, screening_flags
from rebound_engine.state import starting_movement_tier

M, S = Behaviour.movement, Behaviour.sleep


def managing(*conditions: Condition) -> dict:
    return {"managing": [c.value for c in conditions]}


def first_week_movement(make_engine, payload, uid):
    """Movement actions shown over 7 days for a user who completes everything."""
    engine = make_engine()
    engine.onboard(payload, user_id=uid)
    shown = []
    for day in range(1, 8):
        for s in engine.today(uid, day).actions:
            if s.action.behaviour == M:
                shown.append(s.action)
            engine.record(Event(user_id=uid, day=day, type=EventType.completed, action_id=s.action.id))
    return shown


# ---------- nothing new answered: exactly today's behaviour (keeps run_011 valid) ----------


def test_no_condition_answers_keep_the_old_safety_rule(make_profile):
    for q in (None, *SCREENING_QUESTIONS):
        profile = make_profile(screening={q: True} if q else {})
        expected = (config.GENTLE_TIER_CAP if q in SEE_DOCTOR_QUESTIONS
                    else config.SCREENING_TIER_CAP if q else config.MAX_TIER)
        result = screening_flags(profile)
        assert result.movement_tier_cap == expected
        assert result.flag == bool(q)


def test_no_condition_answers_plan_is_the_goals(make_profile):
    plan = build_plan(make_profile())
    assert plan.active == [M, S]
    assert plan.queued == []
    assert set(plan.reasons) <= REASON_KEYS


# ---------- conditions tighten, never loosen ----------


def test_high_blood_pressure_chip_caps_like_the_health_check(make_profile, make_engine, make_payload):
    profile = make_profile(baseline={"active_days_per_week": 7}, conditions=managing(Condition.high_blood_pressure))
    assert not profile.screening.heart_condition_or_high_bp  # Q1 answered "no"
    result = screening_flags(profile)
    assert result.movement_tier_cap == config.SCREENING_TIER_CAP and result.flag
    engine = make_engine()
    payload = make_payload(baseline={"active_days_per_week": 7}, conditions=managing(Condition.high_blood_pressure))
    engine.onboard(payload, user_id="u1")
    today = engine.today("u1", 1)
    assert all(s.action.tier <= config.SCREENING_TIER_CAP for s in today.actions if s.action.behaviour == M)
    assert "check_with_doctor" in today.message_keys
    assert "high_blood_pressure" in build_plan(profile).reasons


def test_back_or_joint_pain_gets_low_impact_movement(make_engine, make_payload):
    payload = make_payload(baseline={"active_days_per_week": 7}, conditions=managing(Condition.back_or_joint_pain))
    shown = first_week_movement(make_engine, payload, "u1")
    assert shown
    assert all("bone_joint_muscle_problem" not in a.contraindications for a in shown)
    assert all(a.tier <= config.SCREENING_TIER_CAP for a in shown)


def test_conditions_never_unlock_a_harder_tier(make_profile):
    screenings = [{}] + [{q: True} for q in SCREENING_QUESTIONS] + [{q: True for q in SCREENING_QUESTIONS}]
    combos = [c for n in range(len(Condition) + 1) for c in itertools.combinations(Condition, n)]
    for answers in screenings:
        base = make_profile(baseline={"active_days_per_week": 7}, screening=answers)
        cap, start = screening_flags(base).movement_tier_cap, starting_movement_tier(base, screening_flags(base))
        for conditions in combos:
            p = make_profile(baseline={"active_days_per_week": 7}, screening=answers, conditions=managing(*conditions))
            r = screening_flags(p)
            assert r.movement_tier_cap <= cap, (answers, conditions)
            assert starting_movement_tier(p, r) <= start, (answers, conditions)
            assert set(screening_flags(base).positive) <= set(r.contraindicated)


def test_recovering_from_illness_starts_at_the_gentlest_level(make_profile):
    p = make_profile(baseline={"active_days_per_week": 7},
                     conditions=managing(Condition.recovering_from_illness_or_injury))
    assert starting_movement_tier(p, screening_flags(p)) == config.MIN_TIER
    plan = build_plan(p)
    assert plan.start_tiers[M] == config.MIN_TIER
    assert "recovering" in plan.reasons


# ---------- which behaviours come first ----------


def test_queued_behaviours_follow_what_people_manage(make_profile):
    assert build_plan(make_profile(conditions=managing(Condition.stress))).queued == [PlanBehaviour.recovery]
    assert build_plan(make_profile(conditions=managing(Condition.diabetes))).queued == [PlanBehaviour.nutrition]
    assert build_plan(make_profile(history={"smoking_status": "current"})).queued == [PlanBehaviour.smoking]
    everything = make_profile(history={"smoking_status": "current"},
                              conditions=managing(Condition.diabetes, Condition.recovering_from_illness_or_injury))
    plan = build_plan(everything)
    assert plan.queued == [PlanBehaviour.recovery, PlanBehaviour.nutrition, PlanBehaviour.smoking]
    assert plan.active == [M, S]  # queued ones stay internal until they have actions (Part B)
    assert len(plan.active) <= config.MAX_ACTIVE_BEHAVIOURS
    assert build_plan(make_profile(history={"smoking_status": "former"})).queued == []


def test_queued_behaviours_never_add_reasons_the_user_sees(make_profile):
    plan = build_plan(make_profile(history={"smoking_status": "current"},
                                   conditions=managing(Condition.stress, Condition.diabetes)))
    assert plan.queued and plan.queued_reasons
    assert not set(plan.queued_reasons) & set(plan.reasons)


# ---------- reasons ----------


def test_reasons_are_known_and_safety_comes_first(make_profile):
    p = make_profile(screening={"mobility_limitation": "mobility_aid"},
                     conditions=managing(Condition.back_or_joint_pain, Condition.high_blood_pressure))
    plan = build_plan(p)
    assert set(plan.reasons) <= REASON_KEYS
    assert plan.reasons[0] in SAFETY_REASONS
    assert len(plan.reasons) == len(set(plan.reasons))


def test_two_people_get_different_plans_from_day_one(make_profile, make_engine, make_payload):
    a = {"baseline": {"active_days_per_week": 7},
             "conditions": managing(Condition.back_or_joint_pain, Condition.high_blood_pressure)}
    b = {"baseline": {"active_days_per_week": 7}, "history": {"smoking_status": "current"},
             "conditions": managing(Condition.diabetes)}
    plan_a, plan_b = build_plan(make_profile(**a)), build_plan(make_profile(**b))
    assert plan_a.reasons != plan_b.reasons
    assert plan_a.start_tiers[M] < plan_b.start_tiers[M]
    week_a = {x.id for x in first_week_movement(make_engine, make_payload(**a), "a")}
    week_b = {x.id for x in first_week_movement(make_engine, make_payload(**b), "b")}
    assert week_a != week_b
