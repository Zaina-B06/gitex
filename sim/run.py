"""Run the simulation.

python -m sim.run --n 300 --days 90 --seeds 1-10 --arms A B C --scenario baseline --out sim/out/run_001 --sensitivity
"""

import argparse
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import pandas as pd
import yaml
from rebound_engine.safety import SCREENING_QUESTIONS

from . import load_config
from .arms import run_persona
from .metrics import aggregate, persona_table, seed_metrics
from .personas import SEGMENTS, generate_personas


def parse_seeds(text: str) -> list[int]:
    seeds: list[int] = []
    for part in text.split(","):
        lo, _, hi = part.partition("-")
        seeds.extend(range(int(lo), int(hi or lo) + 1))
    return seeds


def run_seed(args: tuple) -> tuple[int, pd.DataFrame, pd.DataFrame, dict]:
    seed, n, days, arms, cfg = args
    personas = generate_personas(n, seed, cfg)
    rows = []
    for arm in arms:
        for payload, traits in personas:
            rows.extend(run_persona(arm, payload, traits, cfg, days, seed))
    events = pd.DataFrame(rows)
    persona_df = pd.DataFrame(
        [
            {
                "seed": seed,
                "persona_id": t.persona_id,
                **{s: t.segment[s] for s in SEGMENTS},
                "goals": "+".join(p.basics.goals),
                "fasting": t.fasting,
                "screening_flag": any(getattr(p.screening, q) for q in SCREENING_QUESTIONS),
            }
            for p, t in personas
        ]
    )
    return seed, events, persona_df, seed_metrics(persona_table(events, persona_df, days), days)


def simulate(n: int, days: int, seeds: list[int], arms: list[str], cfg: dict, workers: int = 0, quiet: bool = False):
    """Returns (events, personas, metrics). workers=0 -> one process per seed (capped at CPU count)."""
    cfg = {**cfg, "days": days}
    jobs = [(s, n, days, arms, cfg) for s in seeds]
    results = []
    started = time.perf_counter()
    if workers == 1 or len(seeds) == 1:
        iterator = map(run_seed, jobs)
        pool = None
    else:
        pool = Pool(workers or min(len(seeds), os.cpu_count() or 1))
        iterator = pool.imap_unordered(run_seed, jobs)
    try:
        for i, res in enumerate(iterator, 1):
            results.append(res)
            if not quiet:
                bar = "#" * i + "." * (len(jobs) - i)
                print(f"\r[{bar}] {i}/{len(jobs)} seeds  {time.perf_counter() - started:5.1f}s", end="", flush=True)
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    if not quiet:
        print()
    results.sort(key=lambda r: r[0])
    events = pd.concat([r[1] for r in results], ignore_index=True)
    personas = pd.concat([r[2] for r in results], ignore_index=True)
    metrics = aggregate({r[0]: r[3] for r in results})
    return events, personas, metrics


def _write_table(df: pd.DataFrame, path: Path) -> Path:
    try:
        df.to_parquet(path.with_suffix(".parquet"), index=False)
        return path.with_suffix(".parquet")
    except ImportError:  # pyarrow missing: fall back to CSV
        df.to_csv(path.with_suffix(".csv"), index=False)
        return path.with_suffix(".csv")


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Rebound synthetic-population simulation")
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--seeds", default="1-10")
    ap.add_argument("--arms", nargs="+", default=["A", "B", "C"])
    ap.add_argument("--scenario", default="baseline")
    ap.add_argument("--all-scenarios", action="store_true", help="Drop 2")
    ap.add_argument("--sensitivity", action="store_true", help="also run A with streak_sensitivity = 0 (arm A0)")
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--out", default="sim/out/run_001")
    args = ap.parse_args(argv)
    if args.all_scenarios:
        sys.exit("--all-scenarios comes in Drop 2; only 'baseline' exists for now.")

    arms = list(dict.fromkeys(args.arms + (["A0"] if args.sensitivity else [])))
    cfg = load_config(args.scenario)
    seeds = parse_seeds(args.seeds)
    print(f"scenario={args.scenario} n={args.n} days={args.days} seeds={seeds} arms={arms}")
    events, personas, metrics = simulate(args.n, args.days, seeds, arms, cfg, args.workers)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ev_path = _write_table(events, out / "events")
    _write_table(personas, out / "personas")
    metrics["run"] = {"scenario": args.scenario, "n": args.n, "days": args.days, "arms": arms}
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1, sort_keys=True), encoding="utf-8")
    (out / "config_snapshot.yaml").write_text(
        yaml.safe_dump({"scenario": args.scenario, **cfg, "days": args.days}, sort_keys=True), encoding="utf-8"
    )
    print(f"wrote {ev_path}, metrics.json and config_snapshot.yaml to {out}")

    # Fail loudly: the engine arms must never show an unsafe action or message in quiet hours.
    for arm in ("B", "C"):
        if arm in metrics["arms"]:
            bad = metrics["arms"][arm]["safety_violations"]["max"] or 0
            quiet = metrics["arms"][arm]["quiet_messages"]["max"] or 0
            if bad or quiet:
                sys.exit(f"FAIL: arm {arm} has {bad:.0f} safety violations / {quiet:.0f} quiet-hour messages "
                         f"(see the 'violation' and 'quiet' columns in {ev_path.name})")
    print("safety audit: 0 violations and 0 quiet-hour messages in B and C")


if __name__ == "__main__":
    main()
