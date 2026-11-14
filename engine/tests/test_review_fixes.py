"""Fixes from the review of a9f2ed8: illness-rest only when it fits, no two actions at the same hour, no dates for
diabetic users at iftar."""

from datetime import date

from conftest import _data
from test_calendar import FixedCalendar

from rebound_engine.engine import Engine, InMemoryStore
from rebound_engine.models import Barrier, Behaviour, OnboardingPayload

R, N, SM, M, S = Behaviour.recovery, Behaviour.nutrition, Behaviour.smoking, Behaviour.movement, Behaviour.sleep
SMOKER = {"smoking_status": "current"}
RAMADAN_DAY = date(2027, 2, 10)  # inside Ramadan 1448


def first_action(engine, uid, behaviour, day=1):
    return next(s for s in engine.today(uid, day).actions if s.action.behaviour == behaviour)


# ---------- 1. the rest-after-illness step ----------


def test_rest_after_illness_only_when_recovering_or_ill(make_engine, make_payload):
    engine = make_engine()
    engine.onboard(make_payload(basics={"goals": ["recovery"]}, conditions={"managing": ["stress", "diabetes"]}), "a")
    assert first_action(engine, "a", R).action.id == "rc_t1_breathing"

    engine.onboard(make_payload(basics={"goals": ["recovery"]},
                                conditions={"managing": ["recovering_from_illness_or_injury"]}), "b")
    assert first_action(engine, "b", R).action.id == "rc_t1_rest_after_illness"

    engine.onboard(make_payload(basics={"goals": ["recovery"]}), "c")
    engine.checkin("c", [Barrier.illness_pain])
    assert first_action(engine, "c", R).action.id == "rc_t1_rest_after_illness"


# ---------- 2. no two actions at the same hour ----------


def test_iftar_actions_get_different_hours():
    engine = Engine(store=InMemoryStore(), calendar=FixedCalendar(RAMADAN_DAY))
    payload = OnboardingPayload.model_validate(
        _data(basics={"goals": ["nutrition", "smoking"]}, history=SMOKER, preferences={"fasting_ramadan": True}))
    engine.onboard(payload, user_id="u1")
    hours = {s.action.behaviour: s.hour for s in engine.today("u1", 1).actions}
    assert hours[N] != hours[SM]
    assert abs(hours[N] - hours[SM]) >= 1


def test_movement_and_sleep_clashes_stay_as_before(make_engine, make_payload):
    """The simulator can produce this (movement moved to the evening); changing it would change run_011."""
    engine = make_engine()
    engine.onboard(make_payload(), "u1")
    engine.checkin("u1", [Barrier.schedule_change])  # morning -> afternoon
    engine.checkin("u1", [Barrier.schedule_change])  # afternoon -> evening, same hour as the sleep step
    hours = {s.action.behaviour: s.hour for s in engine.today("u1", 1).actions}
    assert hours[M] == hours[S]


# ---------- 3. no dates for diabetic users at iftar ----------


def _iftar_drink_step(diabetes: bool):
    engine = Engine(store=InMemoryStore(), calendar=FixedCalendar(RAMADAN_DAY))
    groups = {"basics": {"goals": ["nutrition"]}, "preferences": {"fasting_ramadan": True}}
    if diabetes:
        groups["conditions"] = {"managing": ["diabetes"]}
    engine.onboard(OnboardingPayload.model_validate(_data(**groups)), user_id="u1")
    state = engine.get_state("u1")
    state.current_tier[N] = 3
    engine.store.save_state(state)
    return first_action(engine, "u1", N).action


def test_diabetic_users_get_an_iftar_step_without_dates():
    step = _iftar_drink_step(diabetes=True)
    assert "date" not in step.title.en.lower() and step.id == "nu_t3_iftar_water_first"
    assert _iftar_drink_step(diabetes=False).id == "nu_t3_iftar_drink"
