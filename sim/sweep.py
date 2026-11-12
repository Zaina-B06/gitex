"""Sensitivity sweep + tornado chart (Task 02 §4.4).

python -m sim.sweep --out sim/out/sweep_001                      # default sweep, all parameters below
python -m sim.sweep --param traits.success_feedback --values 0 0.025 0.05 0.1 --out sim/out/sweep_delta

Each run uses arms A, A0 and C on the baseline scenario (or --scenario). Values are parsed as YAML, so
ranges are written like [0.3,1.0].
"""

import argparse
import copy
import json
import sys
from pathlib import Path

import matplotlib
import yaml

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from rebound_engine import config as engine_config

from . import load_config
from .metrics import METRICS
from .run import parse_seeds, simulate

ARMS = ["A", "A0", "C"]
# Reasons for each range: docs/ASSUMPTIONS.md, "Sensitivity sweep". The middle value is the baseline.
DEFAULT_SWEEP: dict[str, list] = {
    "traits.streak_sensitivity": [[0.0, 0.0], [0.3, 1.0], [0.8, 1.6]],
    "traits.motivation_volatility": [[0.1, 0.4], [0.2, 0.8], [0.5, 1.2]],
    "traits.checkin_rate_multiplier": [0.5, 1.0, 1.5],
    "traits.bct_responsiveness_sd": [0.0, 0.5, 1.0],
    "disruptions.shocks.rate": [0.0, 1.0, 3.0],
    "behaviour.tier_fit_penalty": [0.5, 1.5, 3.0],
    "traits.success_feedback": [0.0, 0.025, 0.05, 0.1],
    "engine_overrides.STEP_UP_SUCCESSES": [2, 3, 4, 5],
}
# (comparison, metric) pairs recorded for every run; the first two drive the tornado charts.
GAPS = (
    ("C_vs_A", "persistence_w12"),
    ("C_vs_A0", "persistence_w12"),
    ("C_vs_A", "recovery_rate"),
    ("C_vs_A0", "recovery_rate"),
    ("C_vs_A", "retention"),
    ("C_vs_A0", "retention"),
    # Activity, so engagement and how much people do can be weighed together (e.g. for the step-up threshold).
    ("C_vs_A0", "delta_minutes"),
    ("C_vs_A0", "delta_sleep_effort"),
)


def get_path(cfg: dict, path: str):
    head, _, rest = path.partition(".")
    if head == "engine_overrides":
        return cfg.get("engine_overrides", {}).get(rest, getattr(engine_config, rest))
    node = cfg
    for part in path.split("."):
        node = node[part]
    return node


def set_path(cfg: dict, path: str, value) -> dict:
    """Copy of cfg with one value replaced. Refuses paths that don't exist (typos would silently do nothing)."""
    out = copy.deepcopy(cfg)
    parts = path.split(".")
    if parts[0] == "engine_overrides":
        if len(parts) != 2 or not hasattr(engine_config, parts[1]):
            raise ValueError(f"unknown engine config name in {path!r}")
        out.setdefault("engine_overrides", {})[parts[1]] = value
        return out
    node = out
    for part in parts[:-1]:
        node = node[part]
    if parts[-1] not in node:
        raise ValueError(f"unknown config path {path!r}")
    node[parts[-1]] = value
    return out


def sweep(params: dict[str, list], n: int, days: int, seeds: list[int], base_cfg: dict, workers: int = 0,
          quiet: bool = False) -> dict:
    results = []
    total = sum(len(v) for v in params.values())
    i = 0
    for path, values in params.items():
        for value in values:
            i += 1
            if not quiet:
                print(f"[{i}/{total}] {path} = {value}", flush=True)
            _, _, m = simulate(n, days, seeds, ARMS, set_path(base_cfg, path, value), workers, quiet=True)
            results.append({
                "param": path,
                "value": value,
                "gaps": {f"{c}.{k}": m["comparisons"][c][k] for c, k in GAPS},
                "arms": {a: {k: m["arms"][a][k] for k in ("persistence_w12", "recovery_rate", "retention")}
                         for a in ARMS},
            })
    baseline = {p: get_path(base_cfg, p) for p in params}
    return {"n": n, "days": days, "seeds": seeds, "baseline": baseline, "results": results}


def tornado(data: dict, out: Path) -> None:
    keys = [f"{c}.{k}" for c, k in GAPS[:2]]
    params = list(dict.fromkeys(r["param"] for r in data["results"]))
    fig, axes = plt.subplots(1, len(keys), figsize=(6 * len(keys), 0.6 * len(params) + 1.8), sharey=True)
    for ax, key in zip(axes, keys, strict=True):
        comp, metric = key.split(".")
        spans = []
        for p in params:
            rows = [r for r in data["results"] if r["param"] == p and r["gaps"][key]["mean"] is not None]
            if not rows:
                continue
            vals = [r["gaps"][key]["mean"] * 100 for r in rows]
            spans.append((p, min(vals), max(vals), rows[0]["value"], rows[-1]["value"], vals[0], vals[-1]))
        spans.sort(key=lambda s: s[2] - s[1])  # widest bar on top
        for y, (p, lo, hi, v_first, v_last, g_first, g_last) in enumerate(spans):
            ax.barh(y, hi - lo, left=lo, color="#5b8def", alpha=0.8)
            ax.text(g_first, y + 0.3, f"{v_first}", fontsize=7, ha="center")
            ax.text(g_last, y - 0.45, f"{v_last}", fontsize=7, ha="center")
        ax.axvline(0, color="black", lw=1)
        ax.set_yticks(range(len(spans)), [s[0] for s in spans])
        ax.set_xlabel(f"{comp.replace('_vs_', ' vs ')}: {METRICS[metric][0]} gap (pts)")
        ax.set_title(f"How the {comp.replace('_vs_', ' vs ')} gap moves")
    fig.tight_layout()
    fig.savefig(out / "tornado.png", dpi=150)
    plt.close(fig)


def summary_markdown(data: dict) -> str:
    lines = [
        "## Sensitivity sweep",
        "",
        (
            f"{data['n']} personas × {data['days']} days × {len(data['seeds'])} seeds per setting; arms A, A0, C. "
            "Gaps are C minus the comparator, mean [95% interval]: percentage points, except active minutes "
            "(minutes per week)."
        ),
        "",
        "| Parameter | Value | " + " | ".join(f"{c.replace('_vs_', ' vs ')} {METRICS[k][0].lower()}" for c, k in GAPS)
        + " |",
        "|---|---|" + "---|" * len(GAPS),
    ]
    doesnt_help = []
    for r in data["results"]:
        cells = []
        for c, k in GAPS:
            s = r["gaps"][f"{c}.{k}"]
            if s["mean"] is None:
                cells.append("n/a")
                continue
            scale, unit = (100, "pts") if METRICS[k][1] == "pct" else (1, METRICS[k][1])
            cells.append(f"{s['mean'] * scale:+.1f} [{s['ci_low'] * scale:+.1f}, {s['ci_high'] * scale:+.1f}]")
            if s["mean"] <= 0:
                doesnt_help.append(f"{r['param']} = {r['value']}: {c.replace('_vs_', ' vs ')} "
                                   f"{METRICS[k][0].lower()} gap {s['mean'] * scale:+.1f} {unit}")
        base = "  (baseline)" if r["value"] == data["baseline"].get(r["param"]) else ""
        lines.append(f"| {r['param']} | {r['value']}{base} | " + " | ".join(cells) + " |")
    lines += ["", "### Where Rebound doesn't help (gap ≤ 0)", ""]
    lines += [f"- {x}" for x in doesnt_help] or ["- No setting in this sweep makes any recorded gap ≤ 0."]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Sensitivity sweep for the C-vs-A / C-vs-A0 gaps")
    ap.add_argument("--param", help="config path, e.g. traits.success_feedback (default: the full default sweep)")
    ap.add_argument("--values", nargs="+", help="values for --param, parsed as YAML")
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--seeds", default="1-5")
    ap.add_argument("--scenario", default="baseline")
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--out", default="sim/out/sweep_001")
    args = ap.parse_args(argv)
    if bool(args.param) != bool(args.values):
        sys.exit("--param and --values go together")
    params = {args.param: [yaml.safe_load(v) for v in args.values]} if args.param else DEFAULT_SWEEP

    try:
        data = sweep(params, args.n, args.days, parse_seeds(args.seeds), load_config(args.scenario), args.workers)
    except KeyboardInterrupt:  # between runs; Ctrl+C inside a run is handled by simulate()
        print("\ninterrupted: sweep stopped, nothing written", file=sys.stderr)
        sys.exit(130)
    data["scenario"] = args.scenario
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "sweep.json").write_text(json.dumps(data, indent=1, sort_keys=True), encoding="utf-8")
    tornado(data, out)
    md = summary_markdown(data)
    (out / "summary.md").write_text(md, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(md)
    print(f"wrote sweep.json, tornado.png and summary.md to {out}")


if __name__ == "__main__":
    main()
