"""Small JSON for the outcome dashboard (GET /dashboard/outcomes).

    python -m sim.export_dashboard --run sim/out/run_011 --risk sim/out/risk_001 --out docs/results/dashboard.json

sim/out isn't committed. If the run or the risk output isn't on this machine, the committed dashboard.json is kept
as it is, so nobody has to re-run the simulator to get a dashboard."""

import argparse
import json
import sys
from pathlib import Path

import yaml

from .metrics import METRICS
from .report import HEADLINE_COMPARISONS, verdict

MEASURES = ("recovery_rate", "persistence_w12", "retention", "delta_minutes", "delta_sleep_effort")
ARM_MEASURES = (*MEASURES, "lapse_rate", "messages_per_week")
SAFETY_ARMS = ("B", "C")


def _ci(s: dict) -> dict:
    return {"mean": s.get("mean"), "ci_low": s.get("ci_low"), "ci_high": s.get("ci_high")}


def _scenario(path: Path) -> tuple[dict, dict, dict]:
    m = json.loads((path / "metrics.json").read_text(encoding="utf-8"))
    snapshot = yaml.safe_load((path / "config_snapshot.yaml").read_text(encoding="utf-8"))
    comps = m["comparisons"]
    out = {
        "comparisons": {
            c: {k: {**_ci(comps[c][k]), "verdict": verdict(comps[c][k])} for k in MEASURES}
            for c in HEADLINE_COMPARISONS if c in comps
        },
        "arms": {a: {k: _ci(m["arms"][a][k]) for k in ARM_MEASURES} for a in m["arms"]},
        "safety": {
            a: {"violations": m["arms"][a]["safety_violations"]["max"] or 0,
                "quiet_messages": m["arms"][a]["quiet_messages"]["max"] or 0}
            for a in SAFETY_ARMS if a in m["arms"]
        },
    }
    return out, m, snapshot


def _risk(path: Path) -> dict:
    r = json.loads((path / "risk" / "metrics_risk.json").read_text(encoding="utf-8"))
    keep = ("auroc", "auroc_ci", "recall", "recall_ci", "precision", "alert_rate", "rows", "positives")
    return {
        "chosen": r["chosen"],
        "test_seeds": r["splits"]["test"],
        "test": {name: {k: v.get(k) for k in keep} for name, v in r["test"].items()},
        "model_minus_heuristic_auroc_ci": r["model_minus_heuristic_auroc_ci"],
        "in_app_hook": "off (pre-registered test run_008 failed)",
    }


def build(run: Path, risk: Path) -> dict:
    scenarios, first = {}, None
    for d in sorted(p for p in run.iterdir() if (p / "metrics.json").exists()):
        scenarios[d.name], m, snapshot = _scenario(d)
        first = first or (m, snapshot)
    if not scenarios:
        raise FileNotFoundError(f"no */metrics.json under {run} (expected an --all-scenarios run)")
    m, snapshot = first
    open_only = snapshot.get("traits", {}).get("checkin_needs_open_app", False)
    return {
        "run": run.name,
        "world": "check-ins answered only on open days" if open_only else "check-ins answered on any day",
        "seeds": m["seeds"] if isinstance(m["seeds"], list) else sorted(m["seeds"]),
        "personas": m["run"]["n"],
        "days": m["run"]["days"],
        "arms": m["run"]["arms"],
        "verdict_rule": "helps = whole 95% interval above zero; worse = whole interval below; otherwise not shown",
        "units_note": "pct values are fractions (0.017 = 1.7 percentage points); min = minutes per week",
        "measures": {k: {"label": METRICS[k][0], "unit": METRICS[k][1]} for k in ARM_MEASURES},
        "scenarios": scenarios,
        "safety_audit_passed": all(v["violations"] == 0 and v["quiet_messages"] == 0
                                   for s in scenarios.values() for v in s["safety"].values()),
        "risk_model": _risk(risk),
    }


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--risk", type=Path, default=Path("sim/out/risk_001"))
    ap.add_argument("--out", type=Path, default=Path("docs/results/dashboard.json"))
    args = ap.parse_args(argv)
    missing = [p for p in (args.run, args.risk / "risk" / "metrics_risk.json") if not p.exists()]
    if missing:
        if args.out.exists():
            print(f"{', '.join(map(str, missing))} not found; keeping the committed {args.out}")
            return
        sys.exit(f"{', '.join(map(str, missing))} not found and no {args.out} to fall back on")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(build(args.run, args.risk), indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
