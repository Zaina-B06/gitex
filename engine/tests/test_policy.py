from itertools import pairwise

from rebound_engine.actions import filter_actions
from rebound_engine.demo import LAPSE_DAYS, run
from rebound_engine.engine import Engine
from rebound_engine.models import Barrier, Behaviour, Context, ContextFlag, Event, EventType
from rebound_engine.policy import choose_action
from rebound_engine.safety import screening_flags
from rebound_engine.state import initial_state


def _profile_and_state(make_profile, **groups):
    profile = make_profile(**groups)
    return profile, initial_state(profile, screening_flags(profile))


def test_time_barrier_lowers_tier(make_profile):
    profile, state = _profile_and_state(
        make_profile, basics={"goals": ["movement"]}, baseline={"active_days_per_week": 5}
    )
    assert state.current_tier[Behaviour.movement] == 3
    action = choose_action(profile, state, barrier=Barrier.time)
    assert state.current_tier[Behaviour.movement] == 2
    assert action.tier <= 2


def test_time_barrier_never_goes_below_tier_1(make_profile):
    profile, state = _profile_and_state(make_profile, basics={"goals": ["movement"]})
    choose_action(profile, state, barrier=Barrier.time)
    assert state.current_tier[Behaviour.movement] == 1


def test_illness_pain_removes_movement(make_profile):
    profile, state = _profile_and_state(make_profile)
    action = choose_action(profile, state, barrier=Barrier.illness_pain)
    assert action.behaviour == Behaviour.sleep
    allowed = filter_actions(profile, state, Context(flags=state.context_flags, hour=9))
    assert all(a.behaviour != Behaviour.movement for a in allowed)


def test_illness_pain_with_movement_only_goal_shows_nothing(make_profile):
    profile, state = _profile_and_state(make_profile, basics={"goals": ["movement"]})
    assert choose_action(profile, state, barrier=Barrier.illness_pain) is None


def test_environment_barrier_swaps_to_indoor(make_profile):
    profile, state = _profile_and_state(
        make_profile, basics={"goals": ["movement"]}, preferences={"setting": "outdoor"}
    )
    assert choose_action(profile, state).setting == "outdoor"
    assert choose_action(profile, state, barrier=Barrier.environment).setting != "outdoor"


def _movement_engine(make_payload, **groups):
    engine = Engine()
    payload = make_payload(basics={"goals": ["movement"]}, **groups)
    return engine, engine.onboard(payload, user_id="u1").user_id


def _complete_day(engine, uid, day):
    action = engine.today(uid, day).action
    engine.record(Event(user_id=uid, day=day, type=EventType.completed, action_id=action.id))
    return action


def test_step_up_after_three_successes(make_payload):
    engine, uid = _movement_engine(make_payload)
    for day in (1, 2, 3):
        assert _complete_day(engine, uid, day).tier == 1
    assert engine.get_state(uid).current_tier[Behaviour.movement] == 2
    assert engine.today(uid, 4).action.tier == 2


def test_step_up_never_jumps_two_tiers(make_payload):
    engine, uid = _movement_engine(make_payload)
    tiers = [1]
    for day in range(1, 20):
        _complete_day(engine, uid, day)
        tiers.append(engine.get_state(uid).current_tier[Behaviour.movement])
    assert all(b - a in (0, 1) for a, b in pairwise(tiers))
    assert tiers[-1] == 4


def test_step_up_respects_screening_cap(make_payload):
    engine, uid = _movement_engine(make_payload, screening={"prescribed_medication": True})
    for day in range(1, 20):
        _complete_day(engine, uid, day)
    assert engine.get_state(uid).current_tier[Behaviour.movement] == 2


def test_red_flag_in_checkin_stops_coaching(make_payload):
    engine, uid = _movement_engine(make_payload)
    result = engine.checkin(uid, [Barrier.other], free_text="I had chest pain yesterday")
    assert result.red_flag and result.adjusted_action is None
    assert engine.today(uid, 1).action is None
    assert ContextFlag.paused in engine.get_state(uid).context_flags
    assert any(e.type == EventType.red_flag for e in engine.events(uid))


def test_multiple_barriers_apply_highest_priority(make_payload):
    engine = Engine()
    uid = engine.onboard(make_payload(), user_id="u2").user_id
    result = engine.checkin(uid, [Barrier.time, Barrier.illness_pain])
    assert result.barrier == Barrier.illness_pain
    assert result.adjusted_action.behaviour == Behaviour.sleep
    assert engine.today(uid, 1).action.behaviour == Behaviour.sleep
    assert ContextFlag.illness in engine.get_state(uid).context_flags


def test_red_flag_in_motivation_reason_at_onboarding(make_payload):
    engine = Engine()
    result = engine.onboard(make_payload(history={"motivation_reason": "I keep fainting"}), user_id="u3")
    assert result.red_flag
    assert engine.today(result.user_id, 1).action is None
    assert any(e.type == EventType.red_flag for e in engine.events(result.user_id))
    ok = engine.onboard(make_payload(history={"motivation_reason": "Play with my kids"}), user_id="u4")
    assert not ok.red_flag and engine.today(ok.user_id, 1).action is not None


def test_demo_lapse_dips_h_without_reset():
    rows = run(days=30, seed=1)
    states = [r["state"] for r in rows]
    assert "lapsed" in states
    assert states.index("lapsed") < max(i for i, s in enumerate(states) if s in ("recovering", "active"))
    for r in rows:
        if r["day"] in LAPSE_DAYS:
            assert r["h_move"] > 0 and r["h_sleep"] > 0
