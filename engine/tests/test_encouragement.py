"""Task 05 Part C: encouragement moments, positive and real, instead of streaks.

Only on a completion (full or partial), at most one a day, never while paused or after a red flag, and users can turn
them off. One-time moments: first_day_done, three_good_days, first_week_done, habit_strength_50 (per behaviour).
Repeating: comeback (first completion after each slip into drifting/lapsed), tried_something_new (a step not done
before)."""

import pytest

from rebound_engine.models import Barrier, ContextFlag, EngagementState, Event, EventType

MOMENTS = {"first_day_done", "three_good_days", "comeback", "habit_strength_50", "first_week_done",
           "tried_something_new"}


def run(engine, uid, days, outcome=EventType.completed, start=1):
    for day in range(start, start + days):
        for s in engine.today(uid, day).actions:
            engine.record(Event(user_id=uid, day=day, type=outcome, action_id=s.action.id))


def moments(engine, uid):
    return [(e.day, e.payload["moment"]) for e in engine.events(uid) if e.type == EventType.encouragement]


@pytest.fixture
def user(make_engine, make_payload):
    def _make(**groups):
        engine = make_engine()
        engine.onboard(make_payload(**groups), user_id="u1")
        return engine
    return _make


def test_the_first_completion_is_a_moment(user):
    engine = user()
    action = engine.today("u1", 1).actions[0].action
    state = engine.record(Event(user_id="u1", day=1, type=EventType.completed, action_id=action.id))
    assert state.encouragement.moment == "first_day_done" and state.encouragement.day == 1
    assert moments(engine, "u1") == [(1, "first_day_done")]


def test_at_most_one_a_day_and_one_time_moments_fire_once(user):
    engine = user()
    run(engine, "u1", 21)
    fired = moments(engine, "u1")
    days = [d for d, _ in fired]
    assert len(days) == len(set(days))  # never two on one day
    names = [m for _, m in fired]
    assert {"first_day_done", "three_good_days", "first_week_done", "habit_strength_50"} <= set(names)
    for once in ("first_day_done", "three_good_days", "first_week_done"):
        assert names.count(once) == 1, once
    assert set(names) <= MOMENTS


def test_habit_strength_50_once_per_behaviour(user):
    engine = user()
    run(engine, "u1", 30)
    payloads = [e.payload for e in engine.events("u1") if e.type == EventType.encouragement
                and e.payload["moment"] == "habit_strength_50"]
    behaviours = [p["behaviour"] for p in payloads]
    assert behaviours and len(behaviours) == len(set(behaviours))


def test_comeback_after_a_slip(user):
    engine = user()
    run(engine, "u1", 4)
    run(engine, "u1", 6, outcome=EventType.no_response, start=5)
    assert engine.get_state("u1").engagement_state in (EngagementState.drifting, EngagementState.lapsed)
    action = engine.today("u1", 11).actions[0].action
    state = engine.record(Event(user_id="u1", day=11, type=EventType.completed, action_id=action.id))
    assert state.encouragement.moment == "comeback"


def test_nothing_for_skips_or_while_paused_or_after_a_red_flag(user):
    engine = user()
    run(engine, "u1", 3, outcome=EventType.skipped)
    assert moments(engine, "u1") == []
    engine.record(Event(user_id="u1", day=3, type=EventType.pause, payload={"on": True}))
    run(engine, "u1", 3, start=4)
    assert moments(engine, "u1") == []
    red = user()
    red.checkin("u1", [Barrier.other], free_text="I keep fainting")
    assert ContextFlag.paused in red.get_state("u1").context_flags
    run(red, "u1", 3)
    assert moments(red, "u1") == []


def test_users_can_turn_them_off(user):
    engine = user(preferences={"encouragement": False})
    run(engine, "u1", 10)
    assert moments(engine, "u1") == []
    assert engine.get_state("u1").encouragement is None


def test_today_shows_only_todays_encouragement(user):
    engine = user()
    run(engine, "u1", 1)
    assert engine.today("u1", 1).encouragement.moment == "first_day_done"
    assert engine.today("u1", 2).encouragement is None
