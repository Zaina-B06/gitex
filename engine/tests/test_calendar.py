"""Task 05 Part A2: context the engine works out by itself (Ramadan, Eid, heat, shift timings).

Only with a calendar (the API passes one). Engine() without a calendar, as the simulator uses it, is unchanged."""

from datetime import date, time, timedelta

import pytest

from rebound_engine import config
from rebound_engine.calendar import DAWN_SUNSET, RAMADAN, day_context
from rebound_engine.engine import Engine, InMemoryStore
from rebound_engine.models import Behaviour, ContextFlag, Event, EventType
from rebound_engine.policy import window_hour

M, S = Behaviour.movement, Behaviour.sleep
NIGHT_SHIFTS = [{"days": ["sun", "mon", "tue", "wed", "thu"], "start": "22:00", "end": "06:00"}]


class FixedCalendar:
    """Engine day 1 = `start`; the real rules from rebound_engine.calendar."""

    def __init__(self, start: date, start_shift: int = 0, end_shift: int = 0) -> None:
        self.start, self.start_shift, self.end_shift = start, start_shift, end_shift

    def day(self, profile, day):
        return day_context(profile, self.start + timedelta(days=day - 1), self.start_shift, self.end_shift)


def engine_with(calendar=None):
    return Engine(store=InMemoryStore(), calendar=calendar)


def hours(today):
    return {s.action.behaviour: s.hour for s in today.actions}


# ---------- tables ----------


def test_ramadan_table_is_the_umm_al_qura_source():
    assert RAMADAN == (
        (date(2026, 2, 18), date(2026, 3, 20)),
        (date(2027, 2, 8), date(2027, 3, 9)),
        (date(2028, 1, 28), date(2028, 2, 26)),
    )
    assert all((shawwal - start).days in (29, 30) for start, shawwal in RAMADAN)


def test_dawn_sunset_table_covers_every_ramadan_month():
    for start, shawwal in RAMADAN:
        d = start
        while d < shawwal:
            assert d.month in DAWN_SUNSET, d
            d += timedelta(days=1)
    assert all(dawn < time(7) and time(17) < sunset for dawn, sunset in DAWN_SUNSET.values())


# ---------- no calendar: unchanged (the simulator's engine) ----------


def test_without_a_calendar_nothing_is_automatic(make_payload, make_profile):
    engine = engine_with()
    payload = make_payload(preferences={"fasting_ramadan": True}, basics={"shifts": NIGHT_SHIFTS})
    engine.onboard(payload, user_id="u1")
    today = engine.today("u1", 1)
    state = engine.get_state("u1")
    assert state.auto_flags == set() and state.day_times is None
    profile = make_profile(preferences={"fasting_ramadan": True})
    assert hours(today)[M] == window_hour(profile, state.time_window)  # usual window, shifts ignored


# ---------- Ramadan, Eid, heat ----------


def test_ramadan_starts_by_itself_for_fasting_users_only(make_payload):
    engine = engine_with(FixedCalendar(date(2027, 2, 6)))  # Ramadan 1448 starts on day 3 (8 Feb)
    engine.onboard(make_payload(preferences={"fasting_ramadan": True}), user_id="fast")
    engine.onboard(make_payload(), user_id="other")
    before = {uid: engine.today(uid, 2) for uid in ("fast", "other")}
    first = {uid: engine.today(uid, 3) for uid in ("fast", "other")}
    assert ContextFlag.ramadan not in engine.get_state("fast").context_flags  # explicit flags untouched
    assert ContextFlag.ramadan in engine.get_state("fast").auto_flags
    assert ContextFlag.ramadan not in engine.get_state("other").auto_flags
    assert all(s.action.fasting_safe for s in first["fast"].actions)
    iftar = DAWN_SUNSET[2][1].hour
    assert hours(first["fast"])[M] == (iftar + config.RAMADAN_MOVE_AFTER_IFTAR_H) % 24
    assert hours(first["fast"])[M] != hours(before["fast"])[M]  # the plan changed with no action from the user
    assert hours(first["other"]) == hours(before["other"])


def test_iftar_time_can_be_adjusted(make_payload):
    engine = engine_with(FixedCalendar(date(2027, 2, 8)))
    engine.onboard(make_payload(preferences={"fasting_ramadan": True, "iftar_time": "19:00"}), user_id="u1")
    assert hours(engine.today("u1", 1))[M] == (19 + config.RAMADAN_MOVE_AFTER_IFTAR_H) % 24


def test_moon_sighting_correction_shifts_the_dates(make_profile):
    p = make_profile(preferences={"fasting_ramadan": True})
    assert ContextFlag.ramadan in day_context(p, date(2027, 2, 8)).flags
    assert ContextFlag.ramadan not in day_context(p, date(2027, 2, 8), start_shift=1).flags
    assert ContextFlag.ramadan in day_context(p, date(2027, 2, 9), start_shift=1).flags
    assert ContextFlag.ramadan in day_context(p, date(2027, 3, 9), end_shift=1).flags  # one more fasting day


def test_eid_days_are_rest_friendly(make_payload):
    engine = engine_with(FixedCalendar(date(2027, 3, 9)))  # Eid al-Fitr 1448
    engine.onboard(make_payload(preferences={"fasting_ramadan": True}), user_id="u1")
    today = engine.today("u1", 1)
    assert ContextFlag.eid in engine.get_state("u1").auto_flags
    assert "eid_rest" in today.message_keys
    h = dict(engine.get_state("u1").habit_strength)
    for s in today.actions:
        engine.record(Event(user_id="u1", day=1, type=EventType.skipped, action_id=s.action.id))
    assert engine.get_state("u1").habit_strength == h  # a missed Eid day doesn't count


def test_heat_is_on_in_the_summer_months_and_explicit_flags_win(make_payload):
    summer = engine_with(FixedCalendar(date(2027, 7, 15)))
    summer.onboard(make_payload(), user_id="u1")
    summer.today("u1", 1)
    assert ContextFlag.heat in summer.get_state("u1").auto_flags
    winter = engine_with(FixedCalendar(date(2027, 11, 15)))
    winter.onboard(make_payload(), user_id="u2")
    winter.set_context("u2", ContextFlag.heat, True)  # demo override
    winter.today("u2", 1)
    state = winter.get_state("u2")
    assert ContextFlag.heat not in state.auto_flags and ContextFlag.heat in state.context_flags


# ---------- shift timings ----------


def test_night_shift_worker_is_never_prompted_while_asleep_or_at_work(make_payload):
    engine = engine_with(FixedCalendar(date(2027, 11, 7)))  # a Sunday
    engine.onboard(make_payload(basics={"schedule_type": "shift", "shifts": NIGHT_SHIFTS}), user_id="u1")
    for day in range(1, 15):
        today = engine.today("u1", day)
        d = date(2027, 11, 7) + timedelta(days=day - 1)
        after_night = d.strftime("%a").lower()[:3] in ("mon", "tue", "wed", "thu", "fri")
        for s in today.actions:
            busy_until = 6 + config.SHIFT_HOME_H + config.SHIFT_SLEEP_H
            if after_night:
                assert not (6 + config.SHIFT_HOME_H <= s.hour < busy_until), (d, s.action.behaviour, s.hour)
            if d.strftime("%a").lower()[:3] in ("sun", "mon", "tue", "wed", "thu"):
                assert not (s.hour >= 22), (d, s.hour)  # not during tonight's shift
            if after_night and s.action.behaviour == S:
                assert s.hour == 6  # wind-down as the shift ends, before their sleep
        for s in today.actions:
            engine.record(Event(user_id="u1", day=day, type=EventType.completed, action_id=s.action.id))


def test_day_shift_keeps_the_usual_sleep_and_avoids_work_hours(make_payload):
    shifts = [{"days": ["mon", "tue", "wed", "thu", "fri"], "start": "07:00", "end": "15:00"}]
    engine = engine_with(FixedCalendar(date(2027, 11, 8)))  # a Monday
    payload = make_payload(basics={"usual_wake_time": "05:00", "shifts": shifts})
    engine.onboard(payload, user_id="u1")
    h = hours(engine.today("u1", 1))
    assert not 7 <= h[M] < 15
    assert h[S] == (23 + config.EVENING_OFFSET_H) % 24  # usual sleep time (23:00 in the test profile)


def test_changing_shifts_moves_the_windows_the_next_day(make_payload):
    engine = engine_with(FixedCalendar(date(2027, 11, 8)))  # Monday
    engine.onboard(make_payload(basics={"schedule_type": "shift", "shifts": NIGHT_SHIFTS}), user_id="u1")
    monday = hours(engine.today("u1", 1))
    profile = engine.store.get_profile("u1")
    early = [{"days": ["sun", "mon", "tue", "wed", "thu"], "start": "06:00", "end": "14:00"}]
    engine.store.save_profile(profile.model_copy(
        update={"basics": profile.basics.model_validate({**profile.basics.model_dump(), "shifts": early})}))
    assert hours(engine.today("u1", 1)) == monday  # today stays as shown
    tuesday = hours(engine.today("u1", 2))
    assert tuesday[M] != monday[M]
    assert not 6 <= tuesday[M] < 14


def test_shifts_must_name_days():
    from pydantic import ValidationError

    from rebound_engine.models import Shift

    with pytest.raises(ValidationError):
        Shift.model_validate({"days": [], "start": "22:00", "end": "06:00"})
    with pytest.raises(ValidationError):
        Shift.model_validate({"days": ["someday"], "start": "22:00", "end": "06:00"})
