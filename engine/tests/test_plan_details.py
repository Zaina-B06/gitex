"""Backend personalisation (18 Nov): level changes are recorded with their reason (observation only, nothing here
changes which action is chosen), the starting level has a reason, display_name and anchor are optional."""

import json

import pytest
from pydantic import ValidationError

from rebound_engine import config
from rebound_engine.models import Barrier, Behaviour, Event, EventType, Preferences
from rebound_engine.safety import screening_flags
from rebound_engine.state import movement_start, starting_movement_tier

M = Behaviour.movement


def _days(engine, uid, first, last, outcome=EventType.completed):
    for day in range(first, last + 1):
        for s in engine.today(uid, day).actions:
            engine.record(Event(user_id=uid, day=day, type=outcome, action_id=s.action.id))


def _changes(engine, uid, behaviour=M):
    return [c for c in engine.get_state(uid).tier_changes if c.behaviour == behaviour]


def test_step_up_is_recorded(make_engine, make_payload):
    engine = make_engine()
    uid = engine.onboard(make_payload(basics={"goals": ["movement"]})).user_id
    _days(engine, uid, 1, config.STEP_UP_SUCCESSES)
    (change,) = _changes(engine, uid)
    assert (change.kind, change.from_tier, change.to_tier, change.barrier) == ("stepped_up", 1, 2, None)
    assert change.day == config.STEP_UP_SUCCESSES


def test_check_in_ease_is_recorded_with_its_barrier(make_engine, make_payload):
    engine = make_engine()
    uid = engine.onboard(make_payload(basics={"goals": ["movement"]}, baseline={"active_days_per_week": 3})).user_id
    _days(engine, uid, 1, 1)
    engine.checkin(uid, [Barrier.time])
    (change,) = _changes(engine, uid)
    assert (change.kind, change.from_tier, change.to_tier, change.barrier) == ("eased", 2, 1, Barrier.time)


def test_slip_and_missed_days_are_recorded(make_engine, make_payload):
    engine = make_engine()
    uid = engine.onboard(make_payload(basics={"goals": ["movement"]}, baseline={"active_days_per_week": 6})).user_id
    _days(engine, uid, 1, 10, outcome=EventType.skipped)
    kinds = {c.kind for c in _changes(engine, uid)}
    assert kinds <= {"eased", "shrunk_after_slip"} and "shrunk_after_slip" in kinds


def test_no_change_no_record(make_engine, make_payload):
    engine = make_engine()
    uid = engine.onboard(make_payload(basics={"goals": ["movement"]})).user_id  # starts at tier 1
    engine.checkin(uid, [Barrier.time])  # already at the lowest level: nothing to ease
    assert _changes(engine, uid) == []


def test_tier_change_log_is_bounded(make_engine, make_payload):
    from rebound_engine.policy import _set_tier
    engine = make_engine()
    uid = engine.onboard(make_payload(basics={"goals": ["movement"]})).user_id
    state = engine.get_state(uid)
    for i in range(2 * config.TIER_CHANGES_KEEP):
        state.day = i
        _set_tier(state, M, 1 + i % 2, kind="stepped_up")
    assert len(state.tier_changes) == config.TIER_CHANGES_KEEP
    assert state.tier_changes[-1].day == 2 * config.TIER_CHANGES_KEEP - 1  # the newest are kept


@pytest.mark.parametrize(("groups", "reason"), [
    ({"baseline": {"active_days_per_week": 3}}, "active_days"),
    ({"basics": {"age_years": 70}, "baseline": {"active_days_per_week": 6}}, "senior"),
    ({"conditions": {"managing": ["recovering_from_illness_or_injury"]}, "baseline": {"active_days_per_week": 6}},
     "recovering"),
    ({"screening": {"heart_condition_or_high_bp": True}, "baseline": {"active_days_per_week": 6}}, "health_check"),
    ({"body": {"height_cm": 160, "weight_kg": 120}, "baseline": {"active_days_per_week": 6}}, "safe_start"),
])
def test_movement_start_reason(make_profile, groups, reason):
    profile = make_profile(**groups)
    screening = screening_flags(profile)
    tier, why = movement_start(profile, screening)
    assert why == reason and tier == starting_movement_tier(profile, screening)


def test_old_saved_state_without_tier_changes_still_loads(make_engine, make_payload):
    """States saved before 18 Nov (e.g. in the deployed database) have no tier_changes key."""
    from rebound_engine.models import UserState
    engine = make_engine()
    uid = engine.onboard(make_payload()).user_id
    _days(engine, uid, 1, 3)
    old = engine.get_state(uid).model_dump(mode="json")
    old.pop("tier_changes")
    state = UserState.model_validate_json(json.dumps(old))
    assert state.tier_changes == []
    engine.store.save_state(state)
    _days(engine, uid, 4, config.STEP_UP_SUCCESSES + 1)  # and the engine carries on from it
    kinds = [c.kind for c in engine.get_state(uid).tier_changes]
    assert kinds and set(kinds) == {"stepped_up"}


def test_display_name_and_anchor_are_optional_and_trimmed():
    p = Preferences()
    assert p.display_name is None and p.anchor is None
    p = Preferences(display_name="  Zaina  ", anchor=" after maghrib ")
    assert (p.display_name, p.anchor) == ("Zaina", "after maghrib")
    for bad in ({"display_name": "   "}, {"display_name": "x" * 41}, {"anchor": "y" * 41}):
        with pytest.raises(ValidationError):
            Preferences(**bad)
