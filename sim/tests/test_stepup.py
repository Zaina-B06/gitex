"""Pre-registered step-up test (docs/ASSUMPTIONS.md, "Step-up 3 → 4"): arm C4 and the decision rule."""

import sim.arms
from rebound_engine import config as engine_config
from sim import load_config
from sim.report import ALL_SCENARIOS, stepup_decision
from sim.run import simulate

CFG = load_config("baseline")
ROW_COLUMNS = ["persona_id", "day", "kind", "behaviour", "action_id", "tier", "window", "hour", "outcome", "app_open"]


def _actions(events, arm):
    acts = events[(events["kind"] == "action") & (events["arm"] == arm)]
    return acts[ROW_COLUMNS].reset_index(drop=True)


def test_c4_with_threshold_3_is_identical_to_c(monkeypatch):
    """Same bandit seed, same personas: with the override set back to 3, C4 must reproduce C exactly,
    so in the real test the threshold is the only difference."""
    monkeypatch.setattr(sim.arms, "ARM_ENGINE_OVERRIDES", {"C4": {"STEP_UP_SUCCESSES": 3}})
    events, _, _ = simulate(8, 40, [1], ["C", "C4"], CFG, workers=1, quiet=True)
    c, c4 = _actions(events, "C"), _actions(events, "C4")
    assert len(c) > 100
    assert c.equals(c4)


def test_c4_uses_threshold_4_and_restores_it():
    before = engine_config.STEP_UP_SUCCESSES
    events, _, metrics = simulate(20, 60, [1], ["C", "C4"], CFG, workers=1, quiet=True)
    assert engine_config.STEP_UP_SUCCESSES == before == 3
    c, c4 = _actions(events, "C"), _actions(events, "C4")
    assert not c.equals(c4)  # the threshold changes what people are shown
    assert c4["tier"].mean() <= c["tier"].mean()  # slower step-up: never higher on average
    assert "C4_vs_C" in metrics["comparisons"] and "delta_minutes" in metrics["comparisons"]["C4_vs_C"]


def _summary(lo: float, hi: float) -> dict:
    return {"mean": (lo + hi) / 2, "ci_low": lo, "ci_high": hi}


def _scenarios(minutes=(1.0, 3.0), engagement=(-0.5, 0.5), worse_in=None):
    out = {}
    for s in ALL_SCENARIOS:
        comp = {k: _summary(*engagement) for k in ("persistence_w12", "recovery_rate", "retention")}
        comp["delta_minutes"] = _summary(*minutes)
        comp["delta_sleep_effort"] = _summary(-1.0, 1.0)
        if s == worse_in:
            comp["retention"] = _summary(-0.03, -0.01)
        out[s] = {"comparisons": {"C4_vs_C": comp}}
    return out


def test_decision_rule_keep():
    assert stepup_decision(_scenarios())[0] == "keep 4"


def test_decision_rule_reverts_when_minutes_not_clearly_better():
    decision, reasons = stepup_decision(_scenarios(minutes=(-0.5, 2.0)))
    assert decision == "revert to 3" and any("(a)" in r for r in reasons)


def test_decision_rule_reverts_when_any_scenario_is_worse():
    decision, reasons = stepup_decision(_scenarios(worse_in="shock_heavy"))
    assert decision == "revert to 3" and any("shock_heavy" in r for r in reasons)


def test_decision_rule_needs_all_scenarios():
    partial = _scenarios()
    del partial["harsh_attrition"]
    assert stepup_decision(partial)[0] == "incomplete"
