import pytest

from rebound_engine.actions import default_library, filter_actions
from rebound_engine.models import ActionSetting, Behaviour, Context, ContextFlag
from rebound_engine.policy import choose_action
from rebound_engine.safety import SCREENING_QUESTIONS, context_filter, detect_red_flags, screening_flags
from rebound_engine.state import initial_state

MORNING = Context(flags=set(), hour=9)


def _state_at_max_tier(profile):
    state = initial_state(profile, screening_flags(profile))
    state.current_tier[Behaviour.movement] = 4  # the cap must hold even if the tier says otherwise
    return state


# ---------- library ----------


def test_library_has_enough_valid_actions():
    lib = default_library()
    assert len(lib) >= 16
    move = [a for a in lib if a.behaviour == Behaviour.movement]
    for tier in (1, 2, 3, 4):
        settings = {a.setting for a in move if a.tier == tier and not a.seated}
        assert {ActionSetting.indoor, ActionSetting.outdoor} <= settings
    assert {a.tier for a in move if a.seated} >= {1, 2}
    assert {a.tier for a in lib if a.behaviour == Behaviour.sleep} == {1, 2, 3, 4}
    for a in lib:
        assert a.title.en and a.title.ar and a.bct_code and a.bct_name and a.rationale and a.limits


# ---------- screening ----------


def test_chest_pain_gives_sleep_or_gentle_actions_only(make_profile):
    profile = make_profile(screening={"chest_pain": True})
    result = screening_flags(profile)
    assert result.see_doctor and result.flag
    state = _state_at_max_tier(profile)
    allowed = filter_actions(profile, state, MORNING)
    assert allowed
    assert all(a.behaviour == Behaviour.sleep or a.tier == 1 for a in allowed)
    assert choose_action(profile, state, Behaviour.movement).tier == 1


@pytest.mark.parametrize("question", SCREENING_QUESTIONS)
def test_any_yes_caps_movement_at_tier_2(make_profile, question):
    profile = make_profile(screening={question: True})
    assert screening_flags(profile).movement_tier_cap <= 2
    allowed = filter_actions(profile, _state_at_max_tier(profile), MORNING)
    assert all(a.tier <= 2 for a in allowed if a.behaviour == Behaviour.movement)


def test_no_yes_means_no_cap(make_profile):
    result = screening_flags(make_profile())
    assert not result.flag and result.movement_tier_cap == 4


def test_pregnancy_gives_pregnancy_safe_subset(make_profile):
    profile = make_profile(screening={"pregnant": "yes"})
    allowed = filter_actions(profile, _state_at_max_tier(profile), MORNING)
    assert allowed and all(a.pregnancy_safe for a in allowed)


def test_mobility_limitation_gives_seated_movement(make_profile):
    profile = make_profile(screening={"mobility_limitation": "mobility_aid"})
    allowed = filter_actions(profile, _state_at_max_tier(profile), MORNING)
    move = [a for a in allowed if a.behaviour == Behaviour.movement]
    assert move and all(a.seated for a in move)


def test_pregnancy_question_rejected_for_non_female(make_payload):
    with pytest.raises(ValueError):
        make_payload(basics={"sex": "male"}, screening={"pregnant": "no"})


# ---------- context ----------


def test_heat_mode_at_13_removes_outdoor_actions():
    lib = default_library()
    assert any(a.setting == ActionSetting.outdoor for a in lib)
    hot = context_filter(lib, {ContextFlag.heat}, 13)
    assert hot and all(a.setting != ActionSetting.outdoor for a in hot)
    assert any(a.setting == ActionSetting.outdoor for a in context_filter(lib, {ContextFlag.heat}, 9))
    assert any(a.setting == ActionSetting.outdoor for a in context_filter(lib, {ContextFlag.heat}, 16))


def test_fasting_removes_non_fasting_safe_actions():
    lib = default_library()
    assert any(not a.fasting_safe for a in lib)
    fasting = context_filter(lib, {ContextFlag.ramadan}, 9)
    assert fasting and all(a.fasting_safe for a in fasting)


def test_illness_flag_removes_movement():
    left = context_filter(default_library(), {ContextFlag.illness}, 9)
    assert left and all(a.behaviour == Behaviour.sleep for a in left)


# ---------- red flags ----------


@pytest.mark.parametrize(
    "text",
    [
        "I had chest pain on my walk",
        "I fainted yesterday after the gym",
        "I can't breathe when I climb stairs",
        "sometimes I want to kill myself",
        "I've been making myself vomit after meals",
        "عندي ألم في الصدر",
        "أُغمي عليّ أمس",
        "أفكر في الانتحار",
        "ما أقدر أتنفس",
    ],
)
def test_red_flags_detected(text):
    assert detect_red_flags(text)


@pytest.mark.parametrize(
    "text",
    ["I was too busy at work", "felt tired today", "it was chest day at the gym", "كنت مشغول جدا", "نسيت"],
)
def test_ordinary_text_is_not_a_red_flag(text):
    assert not detect_red_flags(text)
