"""Lapse-risk features (Task 02b): engine-visible inputs only, complete and finite."""

import inspect
import math

from rebound_engine.models import Event, EventType, UserProfile, UserState
from rebound_engine.risk import FEATURE_NAMES, compute_features


def test_feature_function_takes_only_engine_data():
    params = inspect.signature(compute_features).parameters
    assert list(params) == ["profile", "state", "events", "day"]
    hints = inspect.get_annotations(compute_features, eval_str=True)
    assert hints["profile"] is UserProfile and hints["state"] is UserState and hints["events"] == list[Event]


def test_features_are_complete_and_finite(make_engine, make_payload):
    engine = make_engine()
    uid = engine.onboard(make_payload(), user_id="u").user_id
    for day in range(1, 12):
        for i, s in enumerate(engine.today(uid, day).actions):
            outcome = EventType.completed if (day + i) % 3 else EventType.skipped
            engine.record(Event(user_id=uid, day=day, type=outcome, action_id=s.action.id))
        f = compute_features(engine.store.get_profile(uid), engine.get_state(uid), engine.events(uid), day)
        assert tuple(f) == FEATURE_NAMES
        assert all(isinstance(v, float) and math.isfinite(v) for v in f.values())
    assert 0 < f["comp_rate_7"] < 1
    assert f["n_shown_7"] == 14  # two goals, seven days


def test_consecutive_misses_and_slope(make_engine, make_payload):
    engine = make_engine()
    uid = engine.onboard(make_payload(basics={"goals": ["movement"]}), user_id="u").user_id
    for day in range(1, 10):
        outcome = EventType.completed if day <= 6 else EventType.no_response
        for s in engine.today(uid, day).actions:
            engine.record(Event(user_id=uid, day=day, type=outcome, action_id=s.action.id))
    engine.today(uid, 10)  # starts day 10, which records H at the start of the day
    f = compute_features(engine.store.get_profile(uid), engine.get_state(uid), engine.events(uid), 9)
    assert f["consecutive_misses"] == 3
    assert f["no_response_share_14"] == 3 / 9
    assert f["schedule_office"] == 1.0 and f["schedule_shift"] == 0.0
