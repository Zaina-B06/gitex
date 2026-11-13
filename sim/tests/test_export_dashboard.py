import argparse
import json

import pytest
from sim.export_dashboard import main
from sim.run import run_scenario

RISK = {
    "chosen": "logistic",
    "splits": {"test": [29, 30]},
    "test": {"logistic": {"auroc": 0.77, "recall": 0.93}, "completion_heuristic": {"auroc": 0.73, "recall": 0.62}},
    "model_minus_heuristic_auroc_ci": [0.03, 0.05],
}


@pytest.fixture(scope="module")
def run_dir(tmp_path_factory):
    root = tmp_path_factory.mktemp("sim")
    args = argparse.Namespace(n=12, days=28, seeds="1", workers=1, set=[])
    assert run_scenario("baseline", args, ["A", "B", "C", "A0"], root / "run_x" / "baseline")
    (root / "risk_x" / "risk").mkdir(parents=True)
    (root / "risk_x" / "risk" / "metrics_risk.json").write_text(json.dumps(RISK), encoding="utf-8")
    return root


def test_export_has_headline_safety_and_risk(run_dir):
    out = run_dir / "dashboard.json"
    main(["--run", str(run_dir / "run_x"), "--risk", str(run_dir / "risk_x"), "--out", str(out)])
    d = json.loads(out.read_text(encoding="utf-8"))
    assert d["world"] == "check-ins answered only on open days"  # the adopted default
    assert set(d["scenarios"]) == {"baseline"}
    comps = d["scenarios"]["baseline"]["comparisons"]
    assert set(comps) == {"C_vs_A", "C_vs_A0", "C_vs_B"}
    assert comps["C_vs_A"]["recovery_rate"]["verdict"] in ("helps", "worse", "not shown")
    assert set(comps["C_vs_A"]) == {"recovery_rate", "persistence_w12", "retention", "delta_minutes",
                                    "delta_sleep_effort"}
    assert d["safety_audit_passed"] is True
    assert d["risk_model"]["chosen"] == "logistic"
    assert "persona_id" not in out.read_text(encoding="utf-8")  # aggregates only


def test_missing_run_keeps_the_committed_file(run_dir):
    out = run_dir / "kept.json"
    out.write_text('{"run": "old"}', encoding="utf-8")
    main(["--run", str(run_dir / "nope"), "--risk", str(run_dir / "risk_x"), "--out", str(out)])
    assert json.loads(out.read_text(encoding="utf-8")) == {"run": "old"}
    with pytest.raises(SystemExit):
        main(["--run", str(run_dir / "nope"), "--out", str(run_dir / "absent.json")])
