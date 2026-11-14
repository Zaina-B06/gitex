"""Task 05 Part E: family context (household, caregiver, family_fasting), family variants, social_family.

With household unset (every simulator persona), behaviour must be exactly what it was before Part E."""

import pytest

from rebound_engine.actions import default_library, filter_actions
from rebound_engine.models import Barrier, Behaviour, Context, ContextFlag, Household, Preferences
from rebound_engine.plan import build_plan
from rebound_engine.policy import choose_actions
from rebound_engine.recipes import suggest_recipe

FAMILY_TAGS = {"family", "family_iftar", "caregiver"}
ALL_GOALS = ["movement", "sleep", "nutrition", "smoking", "recovery"]
SMOKER = {"smoking_status": "current"}
PRE_PART_E = tuple(a for a in default_library() if not FAMILY_TAGS & set(a.tags))


def _family(a) -> bool:
    return bool(FAMILY_TAGS & set(a.tags))


def _start(make_engine, make_payload, **groups):
    engine = make_engine()
    uid = engine.onboard(make_payload(**groups)).user_id
    return engine, uid


def _ids(engine, uid, day=1) -> dict[Behaviour, str]:
    return {s.action.behaviour: s.action.id for s in engine.today(uid, day).actions}


def test_family_fields_default_to_unset():
    p = Preferences()
    assert p.household is None and p.caregiver is False and p.family_fasting is False


def test_library_has_family_caregiver_and_family_iftar_variants():
    tags = {t for a in default_library() for t in a.tags}
    assert FAMILY_TAGS <= tags
    for a in default_library():
        if "family_iftar" in a.tags:
            assert "ramadan_only" in a.tags and a.fasting_safe, a.id


# ---------- household unset: nothing changes (the simulator's case) ----------


@pytest.mark.parametrize("barrier", [None, Barrier.social_family, Barrier.others_smoking, Barrier.time])
@pytest.mark.parametrize("flags", [set(), {ContextFlag.ramadan}])
def test_unset_household_picks_exactly_what_the_pre_part_e_library_picks(make_engine, make_payload, barrier, flags):
    engine, uid = _start(make_engine, make_payload, basics={"goals": ALL_GOALS, "schedule_type": "home_caregiver"},
                         history=SMOKER, preferences={"fasting_ramadan": True})
    for f in flags:
        engine.set_context(uid, f, True)
    if barrier:
        engine.checkin(uid, [barrier])
    profile, state = engine.store.get_profile(uid), engine.store.get_state(uid)
    for rotation in range(3):  # every goal gets its turn in the rotating slot
        state.rotation = rotation
        assert choose_actions(profile, state) == choose_actions(profile, state, library=PRE_PART_E)


def test_unset_household_never_sees_family_steps_or_the_family_message(make_engine, make_payload):
    engine, uid = _start(make_engine, make_payload, basics={"goals": ALL_GOALS}, history=SMOKER)
    profile, state = engine.store.get_profile(uid), engine.store.get_state(uid)
    for flags in (set(), {ContextFlag.ramadan}):
        assert not any(_family(a) for a in filter_actions(profile, state, Context(flags=flags, hour=19)))
    assert engine.checkin(uid, [Barrier.social_family]).message_key == "thanks_for_sharing"


def test_living_alone_is_the_same_as_unset(make_engine, make_payload):
    engine, uid = _start(make_engine, make_payload, basics={"goals": ALL_GOALS}, history=SMOKER,
                         preferences={"household": "alone"})
    profile, state = engine.store.get_profile(uid), engine.store.get_state(uid)
    assert not any(_family(a) for a in filter_actions(profile, state, Context(flags=set(), hour=19)))
    assert engine.checkin(uid, [Barrier.social_family]).message_key == "thanks_for_sharing"


# ---------- with family ----------


@pytest.mark.parametrize("household", [Household.family, Household.children, Household.older_relatives])
def test_family_variants_are_preferred_when_living_with_family(make_engine, make_payload, household):
    engine, uid = _start(make_engine, make_payload, basics={"goals": ["movement", "nutrition", "smoking"]},
                         history=SMOKER, preferences={"household": household.value})
    picked = [default_library_by_id()[i] for i in _ids(engine, uid).values()]
    assert all("family" in a.tags for a in picked), [a.id for a in picked]


def test_family_variants_still_pass_the_safety_filter(make_engine, make_payload):
    # Indoor-only users never get the outdoor family walk; mobility limits get seated steps.
    engine, uid = _start(make_engine, make_payload, preferences={"household": "children", "setting": "indoor"},
                         baseline={"active_days_per_week": 3})  # starts at tier 2, where the family step is a walk
    assert default_library_by_id()[_ids(engine, uid)[Behaviour.movement]].setting != "outdoor"
    engine, uid = _start(make_engine, make_payload, preferences={"household": "children"},
                         screening={"mobility_limitation": "mobility_aid"})
    assert default_library_by_id()[_ids(engine, uid)[Behaviour.movement]].seated


def test_social_family_offers_a_family_step_and_the_family_message(make_engine, make_payload):
    engine, uid = _start(make_engine, make_payload, basics={"goals": ["movement", "sleep"]},
                         preferences={"household": "children"})
    result = engine.checkin(uid, [Barrier.social_family])
    assert result.message_key == "family_together"
    assert any("family" in a.tags for a in result.adjusted_actions)


def test_family_fasting_uses_family_iftar_wording_in_ramadan(make_engine, make_payload):
    def nutrition_pick(**prefs):
        engine, uid = _start(make_engine, make_payload, basics={"goals": ["nutrition"]},
                             preferences={"fasting_ramadan": True, **prefs})
        engine.set_context(uid, ContextFlag.ramadan, True)
        return default_library_by_id()[_ids(engine, uid)[Behaviour.nutrition]]

    assert "family_iftar" in nutrition_pick(family_fasting=True).tags
    assert not FAMILY_TAGS & set(nutrition_pick().tags)  # unchanged without family_fasting


def test_family_iftar_steps_only_in_ramadan(make_engine, make_payload):
    engine, uid = _start(make_engine, make_payload, basics={"goals": ["nutrition"]},
                         preferences={"fasting_ramadan": True, "family_fasting": True, "household": "family"})
    assert "family_iftar" not in default_library_by_id()[_ids(engine, uid)[Behaviour.nutrition]].tags


# ---------- caregiver ----------


def test_caregiver_gets_the_short_caregiver_pause_and_a_plan_reason(make_engine, make_payload, make_profile):
    engine, uid = _start(make_engine, make_payload, basics={"goals": ["recovery"]}, preferences={"caregiver": True})
    pause = default_library_by_id()[_ids(engine, uid)[Behaviour.recovery]]
    assert "caregiver" in pause.tags and pause.tier == 1
    assert "caregiver" in build_plan(make_profile(basics={"goals": ["recovery"]},
                                                  preferences={"caregiver": True})).reasons
    assert "caregiver" not in build_plan(make_profile(basics={"goals": ["recovery"]})).reasons
    # No rest goal, no rest-step reason.
    assert "caregiver" not in build_plan(make_profile(preferences={"caregiver": True})).reasons


def test_family_households_get_family_recipes(make_profile):
    cooking = next(a for a in default_library() if "cooking" in a.tags and "ramadan_only" not in a.tags)
    family = make_profile(basics={"goals": ["nutrition"]}, preferences={"household": "children"})
    alone = make_profile(basics={"goals": ["nutrition"]})
    assert all("family" in suggest_recipe(family, cooking, d, set()).tags for d in range(10))
    assert any("family" not in suggest_recipe(alone, cooking, d, set()).tags for d in range(20))


def default_library_by_id():
    return {a.id: a for a in default_library()}
