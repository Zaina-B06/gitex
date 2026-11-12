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


def _open_sequences(cfg, n=25, seed=4):
    events, _, _ = simulate(n, 90, [seed], ["A", "A0", "B", "C"], cfg, workers=1, quiet=True)
    acts = events[events["kind"] == "action"]
    opens = acts.groupby(["arm", "persona_id", "day"])["app_open"].first()
    outcomes = acts.sort_values("behaviour").groupby(["arm", "persona_id", "day"])["outcome"].agg(tuple)
    resets = events[(events["kind"] == "streak_reset") & (events["arm"] == "A")].groupby("persona_id")["day"].min()
    return opens, outcomes, resets


def _first_difference(a, b) -> int:
    """First day the two arms' outcomes differ (or one shows nothing); 10**9 if never."""
    days = sorted(set(a.index) | set(b.index))
    return next((d for d in days if a.get(d) != b.get(d)), 10**9)


def _check_opens_match(opens, outcomes, resets, n, until_outcomes_differ):
    compared = 0
    for pid in range(n):
        ref = opens.loc[("A0", pid)]
        for arm in ("B", "C", "A"):
            other = opens.loc[(arm, pid)]
            common = ref.index.intersection(other.index)
            limit = 10**9
            if arm == "A":
                limit = resets.get(pid, limit)  # A's streak penalty moves motivation from the next day
            if until_outcomes_differ:  # success feedback moves motivation from the next day
                limit = min(limit, _first_difference(outcomes.loc[("A0", pid)], outcomes.loc[(arm, pid)]))
            common = common[common <= limit]
            assert (ref[common] == other[common]).all(), f"arm {arm}, persona {pid}"
            compared += len(common)
    return compared


def test_daily_open_sequence_is_the_same_in_every_arm_without_feedback():
    """With success feedback off, nothing in A0, B or C moves motivation: identical open days for the whole run.
    A matches until its first streak reset."""
    n = 25
    opens, outcomes, resets = _open_sequences(_merge(CFG, {"traits": {"success_feedback": 0.0}}), n)
    assert len(resets) > 0 and not opens.all()  # not vacuous
    assert _check_opens_match(opens, outcomes, resets, n, until_outcomes_differ=False) > n * 90


def test_daily_open_sequence_is_the_same_until_outcomes_differ():
    """With success feedback on (same rule in every arm), open days match until the arms' outcomes first differ."""
    n = 25
    opens, outcomes, resets = _open_sequences(CFG, n)
    assert _check_opens_match(opens, outcomes, resets, n, until_outcomes_differ=True) >= n  # day 1 at least


def test_success_feedback_is_the_same_rule_in_every_arm():
    """The feedback only depends on the outcome: same persona, same outcome -> same motivation change in any arm."""
    import numpy as np
    from sim.personas import generate_personas
    from sim.user_model import PersonaSim

    traits = generate_personas(1, 1, CFG)[0][1]
    action = LIB["mv_t1_home_walk"]
    deltas = {}
    for result_forced in ("completed", "partial", "skipped"):
        sim = PersonaSim(traits, CFG, 90, np.random.default_rng(0), np.random.default_rng(0))
        sim.start_day(1)
        sim.app_open = True
        before = sim.motivation
        b = dict(sim.b)
        # force the outcome through the model's own thresholds
        b["b0"] = {"completed": 50.0, "partial": -50.0, "skipped": -50.0}[result_forced]
        b["partial_share"] = 1.0 if result_forced == "partial" else 0.0
        b["no_response_base"] = -50.0
        sim.b = b
        assert sim.outcome(action, "morning", 8) == result_forced
        deltas[result_forced] = sim.motivation - before
    d = CFG["traits"]["success_feedback"]
    assert deltas == pytest.approx({"completed": d, "partial": d / 2, "skipped": -d})
