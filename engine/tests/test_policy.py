from itertools import pairwise

import pytest

from rebound_engine import config
from rebound_engine.actions import filter_actions
from rebound_engine.demo import LAPSE_DAYS, run
from rebound_engine.models import (
    Barrier,
    Behaviour,
    Context,
    ContextFlag,
    EngagementState,
    Event,
    EventType,
    TimeWindow,
)
from rebound_engine.policy import apply_barrier, choose_action, shrink_on_slip
from rebound_engine.safety import screening_flags
from rebound_engine.state import initial_state

M = Behaviour.movement
OUTCOME = {
    "C": EventType.completed,
    "H": EventType.partial,
    "S": EventType.skipped,
    "N": EventType.no_response,
}


def _profile_and_state(make_profile, **groups):
    profile = make_profile(**groups)
    return profile, initial_state(profile, screening_flags(profile))


def _movement_engine(make_engine, make_payload, **groups):
    engine = make_engine()
    payload = make_payload(basics={"goals": ["movement"]}, **groups)
    return engine, engine.onboard(payload, user_id="u1").user_id


def _play(engine, uid, codes, start_day=1):
    """One character per day for a movement-only user; returns the tier after each day."""
    tiers = []
    for i, c in enumerate(codes):
        day = start_day + i
        for s in engine.today(uid, day).actions:
            engine.record(Event(user_id=uid, day=day, type=OUTCOME[c], action_id=s.action.id))
        tiers.append(engine.get_state(uid).current_tier[M])
    return tiers


# ---------- rules layer ----------


def test_time_barrier_lowers_tier(make_profile):
    profile, state = _profile_and_state(
        make_profile, basics={"goals": ["movement"]}, baseline={"active_days_per_week": 5}
    )
    assert state.current_tier[M] == 3
    apply_barrier(profile, state, Barrier.time)
    assert state.current_tier[M] == 2
    assert choose_action(profile, state, M).action.tier == 2


def test_time_barrier_never_goes_below_tier_1(make_profile):
    profile, state = _profile_and_state(make_profile, basics={"goals": ["movement"]})
    apply_barrier(profile, state, Barrier.time)
    assert state.current_tier[M] == 1


def test_illness_pain_removes_movement(make_profile):
    profile, state = _profile_and_state(make_profile)
    apply_barrier(profile, state, Barrier.illness_pain)
    assert choose_action(profile, state, M) is None
    assert choose_action(profile, state, Behaviour.sleep) is not None
    allowed = filter_actions(profile, state, Context(flags=state.context_flags, hour=9))
    assert all(a.behaviour != M for a in allowed)


def test_environment_barrier_swaps_to_indoor(make_profile):
    profile, state = _profile_and_state(
        make_profile, basics={"goals": ["movement"]}, preferences={"setting": "outdoor"}
    )
    assert choose_action(profile, state, M).action.setting == "outdoor"
    apply_barrier(profile, state, Barrier.environment)
    assert choose_action(profile, state, M).action.setting != "outdoor"


def test_multiple_barriers_apply_highest_priority(make_engine, make_payload):
    engine = make_engine()
    uid = engine.onboard(make_payload(), user_id="u2").user_id
    result = engine.checkin(uid, [Barrier.time, Barrier.illness_pain])
    assert result.barrier == Barrier.illness_pain
    assert result.adjusted_actions and all(a.behaviour != M for a in result.adjusted_actions)
    assert all(s.action.behaviour != M for s in engine.today(uid, 1).actions)
    assert ContextFlag.illness in engine.get_state(uid).context_flags


# ---------- one action per goal per day ----------


def test_one_action_per_goal_per_day(make_engine, make_payload):
    engine = make_engine()
    uid = engine.onboard(make_payload(), user_id="u5").user_id
    actions = engine.today(uid, 1).actions
    assert [s.action.behaviour for s in actions] == [Behaviour.movement, Behaviour.sleep]
    assert actions[0].time_window == TimeWindow.morning
    assert actions[1].time_window == TimeWindow.evening


def test_unanswered_actions_become_no_response_next_day(make_engine, make_payload):
    engine = make_engine()
    uid = engine.onboard(make_payload(), user_id="u6").user_id
    engine.today(uid, 1)
    engine.today(uid, 2)
    day1 = [d for d in engine.get_state(uid).history if d.day == 1]
    assert len(day1) == 2 and all(d.outcome == "no_response" for d in day1)


# ---------- step-up / step-down ----------


N = config.STEP_UP_SUCCESSES  # tests follow the engine's threshold rather than hard-coding it


def test_step_up_after_n_consecutive_completions(make_engine, make_payload):
    engine, uid = _movement_engine(make_engine, make_payload)
    assert _play(engine, uid, "C" * N) == [1] * (N - 1) + [2]
    assert engine.today(uid, N + 1).actions[0].action.tier == 2


def test_skip_resets_step_up_counter(make_engine, make_payload):
    engine, uid = _movement_engine(make_engine, make_payload)
    run = "C" * (N - 1) + "S" + "C" * (N - 1)
    assert _play(engine, uid, run) == [1] * len(run)
    assert _play(engine, uid, "C", start_day=len(run) + 1) == [2]


def test_partial_neither_adds_nor_resets(make_engine, make_payload):
    engine, uid = _movement_engine(make_engine, make_payload)
    assert _play(engine, uid, "C" * (N - 1) + "H" + "C") == [1] * N + [2]


def test_step_up_never_jumps_two_tiers(make_engine, make_payload):
    engine, uid = _movement_engine(make_engine, make_payload)
    tiers = [1, *_play(engine, uid, "C" * (3 * N + 1))]
    assert all(b - a in (0, 1) for a, b in pairwise(tiers))
    assert tiers[-1] == 4


def test_step_up_respects_screening_cap(make_engine, make_payload):
    engine, uid = _movement_engine(make_engine, make_payload, screening={"prescribed_medication": True})
    assert _play(engine, uid, "C" * (3 * N + 1))[-1] == 2


def test_two_misses_while_active_step_down(make_engine, make_payload):
    engine, uid = _movement_engine(make_engine, make_payload, baseline={"active_days_per_week": 5})
    assert _play(engine, uid, "SN") == [3, 2]


def test_partial_breaks_a_run_of_misses(make_engine, make_payload):
    engine, uid = _movement_engine(make_engine, make_payload, baseline={"active_days_per_week": 5})
    assert _play(engine, uid, "CCSHS") == [3, 3, 3, 3, 3]  # CC first so the state stays active


# ---------- shrink on slip ----------


@pytest.mark.parametrize(
    ("new_state", "expected"),
    [(EngagementState.drifting, 2), (EngagementState.lapsed, 1), (EngagementState.recovering, 3)],
)
def test_shrink_on_slip(make_profile, new_state, expected):
    _, state = _profile_and_state(make_profile, baseline={"active_days_per_week": 5})
    state.current_tier[Behaviour.sleep] = 3
    shrink_on_slip(state, new_state)
    assert state.current_tier == {M: expected, Behaviour.sleep: expected}


def test_entering_drifting_lowers_tier_and_sends_checkin(make_engine, make_payload):
    engine, uid = _movement_engine(make_engine, make_payload, baseline={"active_days_per_week": 5})
    tiers = _play(engine, uid, "CSCS")  # 2/4 done -> drifting, never 2 misses in a row
    assert engine.get_state(uid).engagement_state == EngagementState.drifting
    assert tiers == [3, 3, 3, 2]
    sent = [e for e in engine.events(uid) if e.type == EventType.checkin_sent]
    assert [e.payload["state"] for e in sent] == ["drifting"]
    assert engine.get_state(uid).checkin_due


def test_entering_lapsed_resets_to_tier_1_and_sends_checkin(make_engine, make_payload):
    engine, uid = _movement_engine(make_engine, make_payload, baseline={"active_days_per_week": 5})
    _play(engine, uid, "NNN")
    state = engine.get_state(uid)
    assert state.engagement_state == EngagementState.lapsed and state.current_tier[M] == 1
    assert any(e.payload.get("state") == "lapsed" for e in engine.events(uid) if e.type == EventType.checkin_sent)


def test_no_step_up_after_lapse_until_recovering_and_n_completions(make_engine, make_payload):
    engine, uid = _movement_engine(make_engine, make_payload)
    _play(engine, uid, "NNN")
    assert engine.get_state(uid).engagement_state == EngagementState.lapsed
    # Day 4 still lapsed, day 5 -> recovering; the N-th consecutive completion since the return steps up.
    assert _play(engine, uid, "C" * N, start_day=4) == [1] * (N - 1) + [2]
    assert engine.get_state(uid).engagement_state in (EngagementState.recovering, EngagementState.active)


def test_checkin_can_replace_todays_open_actions(make_engine, make_payload):
    engine = make_engine()
    uid = engine.onboard(make_payload(baseline={"active_days_per_week": 7}), user_id="u1").user_id
    shown = {s.action.behaviour: s.action for s in engine.today(uid, 1).actions}
    assert shown[M].tier == 3
    result = engine.checkin(uid, [Barrier.time], replace_pending=True)
    adjusted = {a.behaviour: a for a in result.adjusted_actions}
    assert adjusted[M].tier == 2
    state = engine.get_state(uid)
    assert adjusted[M].id in state.pending and shown[M].id not in state.pending
    assert [s.action.id for s in engine.today(uid, 1).actions] == [a.id for a in result.adjusted_actions]
    swaps = [e for e in engine.events(uid) if e.type == EventType.action_shown and "replaces" in e.payload]
    assert any(e.action_id == adjusted[M].id and e.payload["replaces"] == shown[M].id for e in swaps)
    engine.record(Event(user_id=uid, day=1, type=EventType.completed, action_id=adjusted[M].id))
    assert adjusted[M].id not in engine.get_state(uid).pending


def test_checkin_keeps_todays_actions_by_default(make_engine, make_payload):
    """The simulator's behaviour: adjusted actions start tomorrow."""
    engine = make_engine()
    uid = engine.onboard(make_payload(baseline={"active_days_per_week": 7}), user_id="u1").user_id
    shown = [s.action.id for s in engine.today(uid, 1).actions]
    engine.checkin(uid, [Barrier.time])
    assert engine.get_state(uid).pending == shown
    assert not any("replaces" in e.payload for e in engine.events(uid))


# ---------- red flags ----------


def test_red_flag_in_checkin_stops_coaching(make_engine, make_payload):
    engine, uid = _movement_engine(make_engine, make_payload)
    result = engine.checkin(uid, [Barrier.other], free_text="I had chest pain yesterday")
    assert result.red_flag and result.adjusted_actions == []
    assert engine.today(uid, 1).actions == []
    assert ContextFlag.paused in engine.get_state(uid).context_flags
    assert any(e.type == EventType.red_flag for e in engine.events(uid))


def test_red_flag_in_motivation_reason_at_onboarding(make_engine, make_payload):
    engine = make_engine()
    result = engine.onboard(make_payload(history={"motivation_reason": "I keep fainting"}), user_id="u3")
    assert result.red_flag
    assert engine.today(result.user_id, 1).actions == []
    assert any(e.type == EventType.red_flag for e in engine.events(result.user_id))
    ok = engine.onboard(make_payload(history={"motivation_reason": "Play with my kids"}), user_id="u4")
    assert not ok.red_flag and engine.today(ok.user_id, 1).actions


# ---------- demo ----------


def test_demo_lapse_dips_h_without_reset():
    rows = run(days=30, seed=1)
    states = [r["state"] for r in rows]
    assert "lapsed" in states
    assert states.index("lapsed") < max(i for i, s in enumerate(states) if s in ("recovering", "active"))
    for r in rows:
        assert r["movement"] != "-" and r["sleep"] != "-"
        if r["day"] in LAPSE_DAYS:
            assert r["h_move"] > 0 and r["h_sleep"] > 0
