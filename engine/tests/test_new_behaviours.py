"""Task 05 Part B: nutrition (with curated recipes), smoking, recovery; new barriers; at most 3 actions a day.

Also pins what must NOT change, so the simulator and the frozen lapse-risk model keep working."""

import re

import pytest
from pydantic import ValidationError

from rebound_engine import config
from rebound_engine.actions import ICONS, default_library
from rebound_engine.models import (
    Barrier,
    Behaviour,
    Condition,
    ContextFlag,
    Event,
    EventType,
    OnboardingPayload,
)
from rebound_engine.plan import build_plan
from rebound_engine.recipes import CUISINES, RECIPE_TAGS, load_recipes, suggest_recipe
from rebound_engine.risk.features import FEATURE_NAMES

N, SM, R, M, S = Behaviour.nutrition, Behaviour.smoking, Behaviour.recovery, Behaviour.movement, Behaviour.sleep
NEW = (N, SM, R)
ALL_GOALS = ["movement", "sleep", "nutrition", "smoking", "recovery"]
SMOKER = {"smoking_status": "current"}

NO_NUMBERS_FOOD = re.compile(r"\b(calories?|kcal|kilojoules?|kj|kg|grams? of sugar|weight|lose|diet pill)\b", re.IGNORECASE)
NO_MEDICINE = re.compile(r"\b(nicotine (replacement|patch|gum)|patches|varenicline|bupropion|e-?cigarettes?|vap\w*|"
                         r"medication|medicine dose|dosage)\b", re.IGNORECASE)
NO_TREATMENT = re.compile(r"\b(therapy|treat(ment|s)?|cure|diagnos\w*|disorder)\b", re.IGNORECASE)


def _text(a) -> str:
    return " ".join(filter(None, [a.title.en, a.rationale, a.limits, a.simple.en if a.simple else ""]))


def _days(engine, uid, days, outcome=EventType.completed):
    seen = []
    for day in range(1, days + 1):
        today = engine.today(uid, day)
        seen.append(today.actions)
        for s in today.actions:
            engine.record(Event(user_id=uid, day=day, type=outcome, action_id=s.action.id))
    return seen


# ---------- what must not change (simulator, frozen risk model) ----------


def test_risk_features_stay_movement_sleep_and_the_original_barriers():
    for word in ("nutrition", "smoking", "recovery", "craving", "stress", "others_smoking", "no_healthy_food"):
        assert not any(word in f for f in FEATURE_NAMES), word
    assert [f for f in FEATURE_NAMES if f.startswith("last_barrier_")] == [
        f"last_barrier_{b}" for b in ("time", "energy_fatigue", "illness_pain", "schedule_change", "environment",
                                      "low_motivation", "social_family", "forgot", "other")]


def test_movement_and_sleep_only_users_get_what_they_got_before(make_engine, make_payload):
    engine = make_engine()
    engine.onboard(make_payload(), user_id="u1")
    for actions in _days(engine, "u1", 10):
        assert [s.action.behaviour for s in actions] == [M, S]


# ---------- the library ----------


@pytest.mark.parametrize("behaviour", NEW)
def test_each_new_behaviour_has_four_tiers_with_everything_a_step_needs(behaviour):
    actions = [a for a in default_library() if a.behaviour == behaviour]
    assert {a.tier for a in actions} == {1, 2, 3, 4}
    for a in actions:
        assert a.title.en and a.title.ar and not a.title.ar_reviewed, a.id
        assert a.simple and a.simple.en and a.simple.ar, a.id
        assert a.icon in ICONS, a.id
        assert a.bct_code and a.bct_name and a.rationale and a.limits, a.id


def test_new_steps_never_give_numbers_targets_medicine_or_treatment():
    for a in default_library():
        if a.behaviour == N:
            assert not NO_NUMBERS_FOOD.search(_text(a)), a.id
            assert "not medical advice" in a.limits.lower(), a.id
        if a.behaviour == SM:
            assert not NO_MEDICINE.search(_text(a).replace("doesn't use medicines or nicotine products", "")), a.id
        if a.behaviour == R:
            assert not NO_TREATMENT.search(_text(a).replace("not treatment", "")), a.id


def test_fasting_users_get_suhoor_and_iftar_steps_in_ramadan(make_engine, make_payload):
    engine = make_engine()
    engine.onboard(make_payload(basics={"goals": ["nutrition"]}, preferences={"fasting_ramadan": True}), "u1")
    engine.set_context("u1", ContextFlag.ramadan, True)
    step = engine.today("u1", 1).actions[0].action
    assert step.fasting_safe and "ramadan_only" in step.tags
    other = make_engine()
    other.onboard(make_payload(basics={"goals": ["nutrition"]}), "u2")
    assert "ramadan_only" not in other.today("u2", 1).actions[0].action.tags


# ---------- goals and the burden cap ----------


def test_smoking_goal_is_only_for_people_who_smoke(make_payload):
    with pytest.raises(ValidationError):
        make_payload(basics={"goals": ["smoking"]})
    assert make_payload(basics={"goals": ["smoking"]}, history=SMOKER)


def test_at_most_three_actions_a_day_and_every_goal_gets_a_turn(make_engine, make_payload):
    engine = make_engine()
    engine.onboard(make_payload(basics={"goals": ALL_GOALS}, history=SMOKER), user_id="u1")
    seen = _days(engine, "u1", 6)
    assert all(len(actions) <= config.MAX_ACTIVE_BEHAVIOURS for actions in seen)
    assert {s.action.behaviour for actions in seen for s in actions} == set(Behaviour)
    plan = build_plan(engine.store.get_profile("u1"))
    assert len(plan.active) == config.MAX_ACTIVE_BEHAVIOURS and "rotating" in plan.reasons


def test_plan_order_follows_what_people_manage(make_profile):
    p = make_profile(basics={"goals": ["movement", "nutrition", "recovery"]},
                     conditions={"managing": [Condition.recovering_from_illness_or_injury.value,
                                              Condition.diabetes.value]})
    plan = build_plan(p)
    assert plan.active[:2] == [R, N]
    assert {"recovery_first", "nutrition_first"} <= set(plan.reasons)


def test_a_slip_shrinks_smoking_like_any_other_behaviour(make_engine, make_payload):
    engine = make_engine()
    engine.onboard(make_payload(basics={"goals": ["smoking"]}, history=SMOKER), user_id="u1")
    _days(engine, "u1", config.STEP_UP_SUCCESSES)
    assert engine.get_state("u1").current_tier[SM] == 2
    for day in range(config.STEP_UP_SUCCESSES + 1, config.STEP_UP_SUCCESSES + 1 + config.STEP_DOWN_FAILURES):
        for s in engine.today("u1", day).actions:
            engine.record(Event(user_id="u1", day=day, type=EventType.skipped, action_id=s.action.id))
    assert engine.get_state("u1").current_tier[SM] == 1


# ---------- new barriers ----------


@pytest.mark.parametrize(("barrier", "goal", "tag", "message"), [
    (Barrier.craving, "smoking", "substitution", "craving_tip"),
    (Barrier.others_smoking, "smoking", "cue_avoidance", "smoke_free_space"),
    (Barrier.no_healthy_food_nearby, "nutrition", "no_shopping", "pantry_swap"),
])
def test_new_barriers_pick_a_matching_step(make_engine, make_payload, barrier, goal, tag, message):
    engine = make_engine()
    engine.onboard(make_payload(basics={"goals": [goal]}, history=SMOKER), user_id="u1")
    engine.today("u1", 1)
    result = engine.checkin("u1", [barrier], replace_pending=True)
    assert result.message_key == message
    assert tag in result.adjusted_actions[0].tags


def test_stress_puts_recovery_first_and_eases_the_rest(make_engine, make_payload):
    engine = make_engine()
    engine.onboard(make_payload(basics={"goals": ["movement", "recovery"], "age_years": 30},
                                baseline={"active_days_per_week": 5}), user_id="u1")
    engine.today("u1", 1)
    before = engine.get_state("u1").current_tier[M]
    result = engine.checkin("u1", [Barrier.stress])
    assert result.message_key == "stress_rest"
    assert result.adjusted_actions[0].behaviour == R
    assert engine.get_state("u1").current_tier[M] == before - 1


def test_diet_changes_suggest_checking_with_a_doctor(make_engine, make_payload):
    engine = make_engine()
    engine.onboard(make_payload(basics={"goals": ["nutrition"]}, conditions={"managing": ["diabetes"]}), "u1")
    assert "diet_check_with_doctor" in engine.today("u1", 1).message_keys
    engine.onboard(make_payload(basics={"goals": ["nutrition"]}, screening={"pregnant": "yes"}), "u2")
    assert "diet_check_with_doctor" in engine.today("u2", 1).message_keys
    engine.onboard(make_payload(basics={"goals": ["nutrition"]}), "u3")
    assert "diet_check_with_doctor" not in engine.today("u3", 1).message_keys


# ---------- recipes ----------


def test_recipes_are_curated_tagged_and_free_of_numbers():
    recipes = load_recipes()
    assert len(recipes) >= 18
    assert {r.cuisine for r in recipes} == set(CUISINES)
    for tag in ("diabetes_friendly", "fasting", "family", "quick", "budget"):
        assert sum(tag in r.tags for r in recipes) >= 3, tag
    for r in recipes:
        assert set(r.tags) <= RECIPE_TAGS, r.id
        assert r.title.en and r.title.ar and not r.title.ar_reviewed
        assert r.ingredients and r.steps
        text = " ".join([r.title.en, r.swap, *r.ingredients, *r.steps])
        assert not NO_NUMBERS_FOOD.search(text), r.id


def test_recipes_are_suggested_for_cooking_steps_and_fit_the_person(make_profile):
    cooking = next(a for a in default_library() if "cooking" in a.tags and "ramadan_only" not in a.tags)
    water = next(a for a in default_library() if a.behaviour == N and a.tier == 1)
    plain = make_profile(basics={"goals": ["nutrition"]})
    assert suggest_recipe(plain, water, day=1, flags=set()) is None
    assert suggest_recipe(plain, cooking, day=1, flags=set()) is not None
    diabetic = make_profile(basics={"goals": ["nutrition"]}, conditions={"managing": ["diabetes"]})
    assert all("diabetes_friendly" in suggest_recipe(diabetic, cooking, d, set()).tags for d in range(10))
    assert all("fasting" in suggest_recipe(plain, cooking, d, {ContextFlag.ramadan}).tags for d in range(10))
    picks = {suggest_recipe(plain, cooking, d, set()).id for d in range(10)}
    assert len(picks) > 1  # rotates


def test_onboarding_model_accepts_the_new_goals():
    data = OnboardingPayload.model_json_schema()
    assert set(data["$defs"]["Behaviour"]["enum"]) == set(ALL_GOALS)
