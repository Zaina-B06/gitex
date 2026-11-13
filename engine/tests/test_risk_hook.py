"""Lapse-risk engine hook (Task 02b Drop B): lighter option + gentle check-in, safe and paced."""

from rebound_engine import config
from rebound_engine.actions import filter_actions
from rebound_engine.models import Barrier, Context, EngagementState, Event, EventType
from rebound_engine.risk import FEATURE_NAMES, RiskModel


class Constant:
    def __init__(self, p):
        self.p = p

    def predict_proba(self, rows):
        return [[1 - self.p, self.p] for _ in rows]


def _model(p: float) -> RiskModel:
    names = FEATURE_NAMES
    return RiskModel(model=Constant(p), kind="logistic", feature_names=names, threshold=0.5,
                     mean={n: 0.0 for n in names}, std={n: 1.0 for n in names},
                     weights={n: (0.5 if n == "no_response_share_14" else 0.0) for n in names})


def _setup(make_engine, make_payload, p, **groups):
    engine = make_engine(risk_model=_model(p))
    payload = make_payload(baseline={"active_days_per_week": 5}, **groups)  # movement starts at tier 3
    return engine, engine.onboard(payload, user_id="u").user_id


def _complete_all(engine, uid, day, use_lighter=False):
    today = engine.today(uid, day)
    for s in today.actions:
        action = s.lighter if use_lighter and s.lighter else s.action
        engine.record(Event(user_id=uid, day=day, type=EventType.completed, action_id=action.id))
    return today


def test_no_model_means_no_offers(make_engine, make_payload):
    engine = make_engine()
    uid = engine.onboard(make_payload(baseline={"active_days_per_week": 5}), user_id="u").user_id
    today = engine.today(uid, 1)
    assert today.risk is None and all(s.lighter is None for s in today.actions)


def test_low_risk_means_no_offers(make_engine, make_payload):
    engine, uid = _setup(make_engine, make_payload, p=0.1)
    today = engine.today(uid, 1)
    assert today.risk == 0.1 and all(s.lighter is None for s in today.actions)
    assert not any(e.type == EventType.risk_alert for e in engine.events(uid))


def test_high_risk_offers_a_safe_lighter_option(make_engine, make_payload):
    engine, uid = _setup(make_engine, make_payload, p=0.9, screening={"pregnant": "yes"})
    today = engine.today(uid, 1)
    profile, state = engine.store.get_profile(uid), engine.get_state(uid)
    move = next(s for s in today.actions if s.action.behaviour == "movement")
    assert move.lighter is not None
    assert move.lighter.behaviour == move.action.behaviour and move.lighter.tier < move.action.tier
    assert move.lighter in filter_actions(profile, state, Context(flags=state.context_flags, hour=move.hour))
    assert move.lighter.pregnancy_safe
    assert "lighter_option" in today.message_keys
    alerts = [e for e in engine.events(uid) if e.type == EventType.risk_alert]
    assert len(alerts) == 1 and alerts[0].payload["reasons"] == today.risk_reasons


def test_hook_doesnt_change_the_plan(make_engine, make_payload):
    plain = make_engine()
    hooked, uid = _setup(make_engine, make_payload, p=0.9)
    uid2 = plain.onboard(make_payload(baseline={"active_days_per_week": 5}), user_id="u").user_id
    a, b = plain.today(uid2, 1), hooked.today(uid, 1)
    assert [s.action.id for s in a.actions] == [s.action.id for s in b.actions]
    assert plain.get_state(uid2).current_tier == hooked.get_state(uid).current_tier


def test_taking_the_lighter_option_closes_the_day(make_engine, make_payload):
    engine, uid = _setup(make_engine, make_payload, p=0.9)
    _complete_all(engine, uid, 1, use_lighter=True)
    state = engine.get_state(uid)
    assert state.pending == []
    assert any(e.type == EventType.completed and e.action_id in state.lighter_offers.values() for e in engine.events(uid))


def test_risk_checkin_at_most_once_per_7_days(make_engine, make_payload):
    engine, uid = _setup(make_engine, make_payload, p=0.9)
    for day in range(1, 16):
        if engine.get_state(uid).checkin_due:
            engine.checkin(uid, [Barrier.time])
        _complete_all(engine, uid, day)
    sent = [e.day for e in engine.events(uid) if e.type == EventType.checkin_sent and e.payload.get("state") == "at_risk"]
    assert sent == [1, 1 + config.RISK_CHECKIN_EVERY_DAYS, 1 + 2 * config.RISK_CHECKIN_EVERY_DAYS]
    per_day = [e.day for e in engine.events(uid) if e.type == EventType.checkin_sent]
    assert len(per_day) == len(set(per_day))  # never two check-in messages on one day


def test_no_hook_unless_active(make_engine, make_payload):
    engine, uid = _setup(make_engine, make_payload, p=0.9)
    state = engine.get_state(uid)
    state.engagement_state = EngagementState.drifting
    engine.store.save_state(state)
    today = engine.today(uid, 1)
    assert all(s.lighter is None for s in today.actions)
    assert not any(e.payload.get("state") == "at_risk" for e in engine.events(uid) if e.type == EventType.checkin_sent)
