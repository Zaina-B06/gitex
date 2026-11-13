"""Charts + markdown summary for a run: python -m sim.report --run sim/out/run_001"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .metrics import COMPARE_METRICS, EQUITY_METRICS, METRICS

ARM_LABEL = {"A": "A · streak app", "A0": "A0 · streak app, no AVE", "B": "B · Rebound rules", "C": "C · Rebound full",
             "C4": "C4 · Rebound full, step-up 4"}
HEADLINE_COMPARISONS = ("C_vs_A", "C_vs_A0", "C_vs_B")
HEADLINE_METRICS = ("recovery_rate", "persistence_w12", "retention")
ARM_COLOR = {"A": "#9a9a9a", "A0": "#c9b27c", "B": "#5b8def", "C": "#2a9d6f", "C4": "#b5487a"}
# Pre-registered step-up test (docs/ASSUMPTIONS.md, "Step-up 3 → 4"). The decision uses C4 vs C only.
STEPUP_COMPARISONS = ("C4_vs_C", "C4_vs_A", "C4_vs_A0")
STEPUP_MEASURES = ("delta_minutes", "delta_sleep_effort", "persistence_w12", "recovery_rate", "retention")
STEPUP_ENGAGEMENT = ("persistence_w12", "recovery_rate", "retention")
ALL_SCENARIOS = ("baseline", "ramadan_heavy", "hot_summer", "low_checkin", "high_dropout", "shock_heavy",
                 "harsh_attrition")


def verdict(s: dict | None) -> str:
    """helps = whole 95% interval above zero; worse = whole interval below zero; otherwise not shown."""
    if not s or s.get("ci_low") is None:
        return "not shown"
    if s["ci_low"] > 0:
        return "helps"
    if s["ci_high"] < 0:
        return "worse"
    return "not shown"


def fmt(summary: dict, unit: str, signed: bool = False) -> str:
    if summary is None or summary.get("mean") is None:
        return "n/a"
    k = 100 if unit == "pct" else 1
    sign = "+" if signed else ""
    m, lo, hi = (summary[x] * k for x in ("mean", "ci_low", "ci_high"))
    suffix = {"pct": "%" if not signed else " pts", "days": " d", "min": " min", "count": ""}[unit]
    return f"{m:{sign}.1f}{suffix} [{lo:{sign}.1f}, {hi:{sign}.1f}]"


def _arms(m: dict) -> list[str]:
    return [a for a in ("A", "A0", "B", "C", "C4") if a in m["arms"]]


def chart_persistence(m: dict, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    for arm in _arms(m):
        weeks = m["persistence_by_week"][arm]
        x = np.arange(1, len(weeks) + 1)
        mean = np.array([w["mean"] for w in weeks]) * 100
        lo = np.array([w["ci_low"] for w in weeks]) * 100
        hi = np.array([w["ci_high"] for w in weeks]) * 100
        ax.plot(x, mean, label=ARM_LABEL[arm], color=ARM_COLOR[arm], lw=2)
        ax.fill_between(x, lo, hi, color=ARM_COLOR[arm], alpha=0.2, lw=0)
    ax.set(xlabel="Week", ylabel="% personas with ≥ 3 active days", ylim=(0, 100),
           title="Persistence by week (mean, 95% interval across seeds)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out / "persistence_by_week.png", dpi=150)
    plt.close(fig)


def chart_recovery(m: dict, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4))
    bins = np.arange(0, 61, 3)
    for arm in _arms(m):
        times = m["recovery_times"][arm]
        if times:
            ax.hist(times, bins=bins, histtype="step", lw=2, color=ARM_COLOR[arm], density=True,
                    label=f"{ARM_LABEL[arm]} (n={len(times)})")
    ax.set(xlabel="Days from lapse onset to active", ylabel="Share of lapse episodes",
           title="Time to recover (all seeds pooled)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out / "recovery_time.png", dpi=150)
    plt.close(fig)


def chart_equity(m: dict, out: Path, metric: str = "persistence_w12") -> None:
    arms = _arms(m)
    rows = [(seg, v) for seg, vals in m["equity"][arms[0]].items() for v in vals]
    def cell(arm: str, seg: str, v: str) -> float:
        mean = m["equity"][arm][seg].get(v, {}).get(metric, {}).get("mean")
        return np.nan if mean is None else mean * 100

    data = np.array([[cell(a, seg, v) for a in arms] for seg, v in rows])
    fig, ax = plt.subplots(figsize=(1.6 * len(arms) + 3, 0.35 * len(rows) + 1.5))
    im = ax.imshow(data, cmap="viridis", aspect="auto", vmin=0, vmax=100)
    ax.set_xticks(range(len(arms)), [ARM_LABEL[a] for a in arms], rotation=20, ha="right")
    ax.set_yticks(range(len(rows)), [f"{seg}: {v}" for seg, v in rows])
    for i in range(len(rows)):
        for j in range(len(arms)):
            if not np.isnan(data[i, j]):
                ax.text(j, i, f"{data[i, j]:.0f}", ha="center", va="center", color="white", fontsize=8)
    fig.colorbar(im, label=f"{METRICS[metric][0]} (%)")
    ax.set_title("Equity: persistence at week 12 by segment")
    fig.tight_layout()
    fig.savefig(out / "equity_heatmap.png", dpi=150)
    plt.close(fig)


def chart_sensitivity(m: dict, out: Path) -> None:
    arms = _arms(m)
    metrics = ["persistence_w12", "recovery_rate", "retention"]
    fig, ax = plt.subplots(figsize=(8, 4))
    width = 0.8 / len(arms)
    for j, arm in enumerate(arms):
        s = [m["arms"][arm][k] for k in metrics]
        mean = np.array([x["mean"] or 0 for x in s]) * 100
        err = np.array([[(x["mean"] or 0) - (x["ci_low"] or 0), (x["ci_high"] or 0) - (x["mean"] or 0)] for x in s]).T * 100
        ax.bar(np.arange(len(metrics)) + j * width, mean, width, yerr=err, capsize=3,
               color=ARM_COLOR[arm], label=ARM_LABEL[arm])
    ax.set_xticks(np.arange(len(metrics)) + width * (len(arms) - 1) / 2, [METRICS[k][0] for k in metrics])
    ax.set(ylabel="%", ylim=(0, 100), title="Sensitivity: does Rebound still win without the streak penalty (A0)?")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(out / "sensitivity.png", dpi=150)
    plt.close(fig)


def headline_cells(m: dict, name: str, metrics: tuple[str, ...] = HEADLINE_METRICS) -> list[str]:
    cells = []
    for k in metrics:
        s = m["comparisons"][name].get(k)
        cells.append(f"{fmt(s, METRICS[k][1], signed=True)} ({verdict(s)})")
    return cells


def stepup_decision(by_scenario: dict[str, dict]) -> tuple[str, list[str]]:
    """Applies the pre-registered rule to C4 vs C. Returns (decision, reasons)."""
    reasons = []
    missing = [s for s in ALL_SCENARIOS if s not in by_scenario or "C4_vs_C" not in by_scenario[s]["comparisons"]]
    if missing:
        return "incomplete", [f"C4 vs C missing for: {', '.join(missing)} (the rule needs all 7 scenarios)"]
    minutes = verdict(by_scenario["baseline"]["comparisons"]["C4_vs_C"]["delta_minutes"])
    if minutes != "helps":
        reasons.append(f"(a) fails: baseline Δ weekly active minutes is '{minutes}', not 'helps'")
    for s in ALL_SCENARIOS:
        for k in STEPUP_ENGAGEMENT:
            if verdict(by_scenario[s]["comparisons"]["C4_vs_C"][k]) == "worse":
                reasons.append(f"(b) fails: {METRICS[k][0].lower()} is 'worse' in {s}")
    if not reasons:
        return "keep 4", ["(a) baseline Δ active minutes helps; (b) no engagement measure is worse in any scenario"]
    return "revert to 3", reasons


def stepup_markdown(by_scenario: dict[str, dict]) -> str:
    lines = ["## Pre-registered step-up test: C4 (step up after 4) vs C (after 3)", "",
             ("Decision rule (docs/ASSUMPTIONS.md): keep 4 only if (a) Δ weekly active minutes for C4 vs C is "
              "\"helps\" in baseline and (b) no engagement measure (persistence wk 12, recovery, retention) for "
              "C4 vs C is \"worse\" in any scenario; otherwise revert to 3."), "",
             "| Scenario | Comparison | " + " | ".join(METRICS[k][0] for k in STEPUP_MEASURES) + " |",
             "|---|---|" + "---|" * len(STEPUP_MEASURES)]
    for scenario, m in by_scenario.items():
        for name in STEPUP_COMPARISONS:
            if name in m["comparisons"]:
                lines.append(f"| {scenario} | {name.replace('_vs_', ' vs ')} | "
                             + " | ".join(headline_cells(m, name, STEPUP_MEASURES)) + " |")
    decision, reasons = stepup_decision(by_scenario)
    lines += ["", f"**Decision: {decision}.**", ""] + [f"- {r}" for r in reasons]
    return "\n".join(lines) + "\n"


def scenarios_markdown(by_scenario: dict[str, dict]) -> str:
    """Pre-registered headline for every scenario in one table."""
    lines = ["## Pre-registered headline across scenarios", "",
             ("\"helps\" = whole 95% interval of the difference above zero; \"worse\" = whole interval below zero; "
              "otherwise \"not shown\"."), "",
             "| Scenario | Comparison | " + " | ".join(METRICS[k][0] for k in HEADLINE_METRICS) + " |",
             "|---|---|" + "---|" * len(HEADLINE_METRICS)]
    for scenario, m in by_scenario.items():
        for name in HEADLINE_COMPARISONS:
            if name in m["comparisons"]:
                lines.append(f"| {scenario} | {name.replace('_vs_', ' vs ')} | " + " | ".join(headline_cells(m, name)) + " |")
    lines += ["", "Recovery after unlabelled shocks vs labelled disruptions (C vs A, C vs A0):", ""]
    for scenario, m in by_scenario.items():
        parts = []
        for name in ("C_vs_A", "C_vs_A0"):
            comp = m["comparisons"].get(name, {})
            for k in ("recovery_labelled", "recovery_shock"):
                if k in comp:
                    parts.append(f"{name.replace('_vs_', ' vs ')} {METRICS[k][0].split(', ')[1]}: "
                                 f"{fmt(comp[k], 'pct', signed=True)}")
        lines.append(f"- {scenario}: " + "; ".join(parts))
    md = "\n".join(lines) + "\n"
    if any("C4_vs_C" in m["comparisons"] for m in by_scenario.values()):
        md += "\n" + stepup_markdown(by_scenario)
    return md


def summary_markdown(m: dict) -> str:
    arms = _arms(m)
    run = m.get("run", {})
    lines = [
        f"## Simulation results: scenario `{run.get('scenario', '?')}`",
        "",
        (
            f"{run.get('n', '?')} personas × {run.get('days', '?')} days × {len(m['seeds'])} seeds. "
            "Every number is the mean across seeds with a 95% interval for that mean."
        ),
        "",
        "| Metric | " + " | ".join(ARM_LABEL[a] for a in arms) + " |",
        "|---|" + "---|" * len(arms),
    ]
    for key, (label, unit) in METRICS.items():
        if any(key in m["arms"][a] for a in arms):  # older runs lack newer metrics
            lines.append(f"| {label} | " + " | ".join(fmt(m["arms"][a].get(key), unit) for a in arms) + " |")
    lines += ["", ("Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep "
                   "action), so the comparisons use the tier-weighted version."),
              "", "### Pre-registered headline (docs/ASSUMPTIONS.md, commit dc054ab)", "",
              ("Rebound \"helps\" on a measure only if the whole 95% interval of the difference is above zero; "
               "\"worse\" if it is entirely below zero; otherwise \"not shown\"."), "",
              "| Comparison | " + " | ".join(METRICS[k][0] for k in HEADLINE_METRICS) + " |",
              "|---|" + "---|" * len(HEADLINE_METRICS)]
    for name in HEADLINE_COMPARISONS:
        if name in m["comparisons"]:
            lines.append(f"| {name.replace('_vs_', ' vs ')} | " + " | ".join(headline_cells(m, name)) + " |")
    lines += ["", "### All arm comparisons (difference, 95% interval)", ""]
    doesnt_help = []
    for name, comp in m["comparisons"].items():
        a, b = name.split("_vs_")
        for key in COMPARE_METRICS:
            label, unit = METRICS[key]
            s = comp.get(key)
            if s is None:
                continue
            lines.append(f"- {a} vs {b}, {label.lower()}: {fmt(s, unit, signed=True)}")
            if a == "C" and b in ("A", "A0") and s["mean"] is not None:
                lower_is_better = key in ("time_to_recover", "days_to_active")
                surely_better = s["ci_high"] < 0 if lower_is_better else s["ci_low"] > 0
                surely_worse = s["ci_low"] > 0 if lower_is_better else s["ci_high"] < 0
                if not surely_better:
                    verdict = "Rebound is worse" if surely_worse else "no clear difference"
                    doesnt_help.append(f"{label} vs {b}: {fmt(s, unit, signed=True)} ({verdict})")
    lines += ["", "### Equity: best-minus-worst segment gap (lower is fairer)", "",
              "| Segment | Metric | " + " | ".join(ARM_LABEL[a] for a in arms) + " |",
              "|---|---|" + "---|" * len(arms)]
    for seg in m["equity_gap"][arms[0]]:
        for key in EQUITY_METRICS:
            label, unit = METRICS[key]
            lines.append(f"| {seg} | {label} | " + " | ".join(fmt(m["equity_gap"][a][seg][key], unit) for a in arms) + " |")
    lines += ["", "### Safety and burden", ""]
    for a in arms:
        lines.append(f"- {ARM_LABEL[a]}: {m['arms'][a]['safety_violations']['max']:.0f} safety violations (max over seeds), "
                     f"{m['arms'][a]['quiet_messages']['max']:.0f} quiet-hour messages, "
                     f"{fmt(m['arms'][a]['messages_per_week'], 'count')} messages per persona-week")
    lines += ["", "### Where Rebound doesn't help", ""]
    lines += [f"- {x}" for x in doesnt_help] or ["- Nothing in this scenario: every C-vs-A/A0 interval is in Rebound's favour."]
    return "\n".join(lines) + "\n"


def report_run(run: Path) -> tuple[dict, str]:
    m = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
    charts = run / "charts"
    charts.mkdir(exist_ok=True)
    chart_persistence(m, charts)
    chart_recovery(m, charts)
    chart_equity(m, charts)
    chart_sensitivity(m, charts)
    md = summary_markdown(m)
    (run / "summary.md").write_text(md, encoding="utf-8")
    return m, md


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Charts + summary for a simulation run (or an --all-scenarios folder)")
    ap.add_argument("--run", required=True)
    args = ap.parse_args(argv)
    run = Path(args.run)
    sys.stdout.reconfigure(encoding="utf-8")  # Windows uses cp1252 when output is redirected; Δ/× would crash
    if (run / "metrics.json").exists():
        _, md = report_run(run)
        print(md)
        print(f"charts in {run / 'charts'}, summary in {run / 'summary.md'}")
        return
    subs = sorted(d for d in run.iterdir() if (d / "metrics.json").exists())
    if not subs:
        sys.exit(f"no metrics.json in {run} or its sub-folders")
    by_scenario = {d.name: report_run(d)[0] for d in subs}
    md = scenarios_markdown(by_scenario)
    (run / "scenarios.md").write_text(md, encoding="utf-8")
    print(md)
    print(f"per-scenario charts and summary.md in each sub-folder; overview in {run / 'scenarios.md'}")


if __name__ == "__main__":
    main()
