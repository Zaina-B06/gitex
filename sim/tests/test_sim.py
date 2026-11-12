import json

import pytest
from rebound_engine.actions import default_library
from rebound_engine.models import ContextFlag
from sim import _merge, load_config
from sim.arms import audit
from sim.personas import generate_personas
from sim.run import simulate

CFG = load_config("baseline")
LIB = {a.id: a for a in default_library()}


@pytest.fixture(scope="module")
def engine_run():
    """B and C, full 90 days, small population."""
    events, _, metrics = simulate(40, 90, [1], ["B", "C"], CFG, workers=1, quiet=True)
    return events, metrics


def test_persona_distributions_match_config():
    personas = generate_personas(300, 1, CFG)
    pc = CFG["personas"]

    def share(pred):
        return sum(pred(p, t) for p, t in personas) / len(personas)

    for value, expected in pc["schedule_type"].items():
        assert share(lambda p, t, v=value: t.segment["schedule_type"] == v) == pytest.approx(expected, abs=0.08)
    for value, expected in pc["language"].items():
        assert share(lambda p, t, v=value: t.segment["language"] == v) == pytest.approx(expected, abs=0.08)
    flagged = share(lambda p, t: any(getattr(p.screening, q) for q in
                                     ("heart_condition_or_high_bp", "chest_pain", "dizziness_or_fainting",
                                      "other_long_term_condition", "prescribed_medication",
                                      "bone_joint_muscle_problem", "supervised_exercise_only")))
    assert flagged == pytest.approx(pc["screening_flag_rate"], abs=0.06)
    assert share(lambda p, t: t.fasting) == pytest.approx(pc["fasting_rate"], abs=0.08)
    assert share(lambda p, t: len(p.basics.goals) == 2) == pytest.approx(pc["goals"]["both"], abs=0.08)
    assert all(pc["age"][0] <= p.basics.age_years <= pc["age"][1] for p, _ in personas)
    assert all(p.screening.pregnant is None for p, _ in personas if p.basics.sex != "female")


def test_same_seed_gives_identical_metrics():
    a = simulate(12, 28, [3], ["A", "B", "C"], CFG, workers=1, quiet=True)[2]
    b = simulate(12, 28, [3], ["A", "B", "C"], CFG, workers=1, quiet=True)[2]
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_safety_audit_is_zero_for_engine_arms(engine_run):
    events, metrics = engine_run
    actions = events[events["kind"] == "action"]
    assert len(actions) > 1000
    assert (actions["violation"] == "").all()
    for arm in ("B", "C"):
        assert metrics["arms"][arm]["safety_violations"]["max"] == 0


def test_no_quiet_hour_messages_for_engine_arms(engine_run):
    events, metrics = engine_run
    assert not events.loc[events["kind"] == "action", "quiet"].any()
    for arm in ("B", "C"):
        assert metrics["arms"][arm]["quiet_messages"]["max"] == 0


def test_churned_persona_gets_no_more_events():
    # Nobody ever responds -> everyone churns after 14 silent days (later if a day had nothing to answer).
    cfg = _merge(CFG, {"behaviour": {"b0": -20.0, "partial_share": 0.0, "no_response_base": 20.0}})
    events, _, metrics = simulate(6, 60, [1], ["A", "B", "C"], cfg, workers=1, quiet=True)
    churn = events[events["kind"] == "churn"]
    assert len(churn) == 6 * 3
    assert (churn["day"] >= cfg["behaviour"]["dropout_silent_days"]).all()
    last = events.groupby(["arm", "persona_id"])["day"].max()
    churn_day = churn.set_index(["arm", "persona_id"])["day"]
    assert (last <= churn_day.reindex(last.index)).all()
    for arm in ("A", "B", "C"):
        assert metrics["arms"][arm]["retention"]["mean"] == 0


def test_arm_a_never_changes_its_plan():
    events, _, _ = simulate(30, 40, [2], ["A"], CFG, workers=1, quiet=True)
    actions = events[events["kind"] == "action"]
    assert (actions.groupby(["persona_id", "behaviour"])["action_id"].nunique() == 1).all()


def test_audit_catches_unsafe_actions():
    payload = generate_personas(1, 1, CFG)[0][0].model_copy(deep=True)
    payload.screening.chest_pain = True
    assert "tier_cap" in audit(LIB["mv_t3_home_workout"], 9, payload, set())
    assert "heat" in audit(LIB["mv_t1_outdoor_walk"], 13, payload, {ContextFlag.heat})
    assert "heat" not in audit(LIB["mv_t1_outdoor_walk"], 9, payload, {ContextFlag.heat})
    assert "fasting" in audit(LIB["mv_t3_home_workout"], 20, payload, {ContextFlag.ramadan})
    assert "illness" in audit(LIB["mv_t1_home_walk"], 9, payload, {ContextFlag.illness})
    assert audit(LIB["sl_t1_fixed_wake"], 20, payload, {ContextFlag.illness}) == ""


def test_daily_open_sequence_is_the_same_in_every_arm():
    """Motivation and the app-open draw are persona-only, on their own random stream. A0, B and C never move
    motivation, so their open/no-open days match for the whole run; A matches until its first streak reset."""
    n = 25
    events, _, _ = simulate(n, 90, [4], ["A", "A0", "B", "C"], CFG, workers=1, quiet=True)
    acts = events[events["kind"] == "action"]
    opens = acts.groupby(["arm", "persona_id", "day"])["app_open"].first()
    resets = events[(events["kind"] == "streak_reset") & (events["arm"] == "A")].groupby("persona_id")["day"].min()
    assert len(resets) > 0 and not opens.all()  # the A check and the comparison aren't vacuous
    compared = 0
    for pid in range(n):
        ref = opens.loc[("A0", pid)]
        for arm in ("B", "C", "A"):
            other = opens.loc[(arm, pid)]
            common = ref.index.intersection(other.index)
            if arm == "A":
                common = common[common <= resets.get(pid, 10**9)]
            assert (ref[common] == other[common]).all(), f"arm {arm}, persona {pid}"
            compared += len(common)
    assert compared > n * 90  # most persona-days were actually compared
