"""Arms D / D50 (lapse-risk hook) and the pre-registered ship rule (docs/ASSUMPTIONS.md, "Arm D")."""

import itertools

import pytest
import sim.arms
from rebound_engine.risk import FEATURE_NAMES, RiskModel
from sim import load_config
from sim.report import ALL_SCENARIOS, burden_verdict, risk_hook_decision, verdict
from sim.run import simulate

CFG = load_config("baseline")


class Constant:
    def predict_proba(self, rows):
        return [[0.1, 0.9] for _ in rows]


def _always_alert() -> RiskModel:
    names = FEATURE_NAMES
    return RiskModel(model=Constant(), kind="logistic", feature_names=names, threshold=0.5,
                     mean={n: 0.0 for n in names}, std={n: 1.0 for n in names}, weights={n: 0.0 for n in names})


@pytest.fixture(scope="module")
def hooked_run():
    mp = pytest.MonkeyPatch()
    mp.setattr(sim.arms, "load_arm_risk_model", lambda cfg: _always_alert())
    try:
        events, _, metrics = simulate(15, 60, [1], ["C", "D", "D50"], CFG, workers=1, quiet=True)
    finally:
        mp.undo()
    return events, metrics


def test_hook_is_safe_and_respects_quiet_hours(hooked_run):
    _events, metrics = hooked_run
    for arm in ("D", "D50"):
        assert metrics["arms"][arm]["safety_violations"]["max"] == 0  # shown actions and offered options audited
        assert metrics["arms"][arm]["quiet_messages"]["max"] == 0


def test_lighter_options_are_offered_and_sometimes_taken(hooked_run):
    events, _ = hooked_run
    acts = events[events["kind"] == "action"]
    assert not acts.loc[acts["arm"] == "C", "offered_lighter"].any()
    for arm in ("D", "D50"):
        mine = acts[acts["arm"] == arm]
        assert mine["offered_lighter"].any() and mine["took_lighter"].any()
        took, offered = mine["took_lighter"].astype(bool), mine["offered_lighter"].astype(bool)
        assert not (took & ~offered).any()


def test_risk_checkins_are_paced(hooked_run):
    events, _ = hooked_run
    sent = events[events["kind"] == "checkin_sent"]
    for (_, _), g in sent[sent["arm"].isin(["D", "D50"])].groupby(["arm", "persona_id"]):
        assert g["day"].is_unique  # never two check-in messages on one day
        at_risk = sorted(g.loc[g["detail"] == "at_risk", "day"])
        assert all(b - a >= 7 for a, b in itertools.pairwise(at_risk))


def _comp(lapse=(-0.05, -0.01), engagement=(-0.01, 0.01), msgs=0.3):
    s = {k: {"mean": sum(engagement) / 2, "ci_low": engagement[0], "ci_high": engagement[1]}
         for k in ("persistence_w12", "recovery_rate", "retention")}
    s["lapse_rate"] = {"mean": sum(lapse) / 2, "ci_low": lapse[0], "ci_high": lapse[1]}
    s["messages_per_week"] = {"mean": msgs, "ci_low": msgs - 0.1, "ci_high": msgs + 0.1}
    return {"comparisons": {"D_vs_C": s}}


def test_lapse_rate_lower_is_better():
    assert verdict({"ci_low": -0.05, "ci_high": -0.01}, lower_is_better=True) == "helps"
    assert verdict({"ci_low": 0.01, "ci_high": 0.05}, lower_is_better=True) == "worse"


def test_burden_worse_only_above_the_cap():
    assert burden_verdict({"mean": 0.4}) == "within cap"
    assert burden_verdict({"mean": 0.6}) == "worse"


def test_ship_rule():
    ok = {s: _comp() for s in ALL_SCENARIOS}
    assert risk_hook_decision(ok)[0] == "ship the hook"
    no_lapse_gain = {**ok, "baseline": _comp(lapse=(-0.02, 0.01))}
    assert risk_hook_decision(no_lapse_gain)[0] == "keep the hook out of the app"
    worse = {**ok, "shock_heavy": _comp(engagement=(-0.03, -0.01))}
    assert any("shock_heavy" in r for r in risk_hook_decision(worse)[1])
    heavy = {**ok, "low_checkin": _comp(msgs=0.7)}
    assert any("(3)" in r for r in risk_hook_decision(heavy)[1])
    partial = {s: v for s, v in ok.items() if s != "harsh_attrition"}
    assert risk_hook_decision(partial)[0] == "incomplete"
