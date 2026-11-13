"""Run the simulation.

python -m sim.run --n 300 --days 90 --seeds 1-10 --arms A B C --scenario baseline --out sim/out/run_001 --sensitivity
python -m sim.run ... --all-scenarios --out sim/out/run_004      # one sub-folder per scenario
"""

import argparse
import json
import os
import signal
import sys
import time
from multiprocessing import Pool, TimeoutError
from pathlib import Path

import pandas as pd
import yaml
from rebound_engine import config as engine_config
from rebound_engine.safety import SCREENING_QUESTIONS

from . import SIM_DIR, load_config
from .arms import run_persona
from .metrics import aggregate, persona_table, seed_metrics
from .personas import SEGMENTS, generate_personas


def parse_seeds(text: str) -> list[int]:
    seeds: list[int] = []
    for part in text.split(","):
        lo, _, hi = part.partition("-")
        seeds.extend(range(int(lo), int(hi or lo) + 1))
    return seeds


def _engine_overrides(cfg: dict) -> dict:
    overrides = cfg.get("engine_overrides") or {}
    unknown = [k for k in overrides if not hasattr(engine_config, k)]
    if unknown:
        raise ValueError(f"unknown engine config names in engine_overrides: {unknown}")
    return overrides


def run_seed(args: tuple) -> tuple[int, pd.DataFrame, pd.DataFrame, dict]:
    seed, n, days, arms, cfg = args
    overrides = _engine_overrides(cfg)
    saved = {k: getattr(engine_config, k) for k in overrides}
    personas = generate_personas(n, seed, cfg)
    rows = []
    try:  # sweep only: engine constants (e.g. STEP_UP_SUCCESSES) changed for this run, always restored
        for k, v in overrides.items():
            setattr(engine_config, k, v)
        for arm in arms:
            for payload, traits in personas:
                rows.extend(run_persona(arm, payload, traits, cfg, days, seed))
    finally:
        for k, v in saved.items():
            setattr(engine_config, k, v)
    events = pd.DataFrame(rows)
    persona_df = personas_frame(seed, personas)
    return seed, events, persona_df, seed_metrics(persona_table(events, persona_df, days), days)


def personas_frame(seed: int, personas: list) -> pd.DataFrame:
    """Segments and a few flags per persona (for metrics and fairness breakdowns; never given to the engine)."""
    return pd.DataFrame(
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


def _ignore_sigint() -> None:
    """Workers ignore Ctrl+C; the main process catches it and terminates the pool (otherwise every worker
    prints its own traceback on Windows)."""
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def _interrupted(pool) -> None:
    if pool is not None:
        pool.terminate()
        pool.join()
    print("\ninterrupted: all workers stopped, nothing written for this run", file=sys.stderr)
    sys.exit(130)


def map_seeds(func, jobs: list[tuple], workers: int = 0, quiet: bool = False) -> list:
    """Run func(job) for every job (one per seed), in parallel unless workers == 1. Results sorted by job[0].
    Ctrl+C terminates the pool and exits cleanly."""
    results = []
    started = time.perf_counter()
    pool = None

    def progress() -> None:
        if not quiet:
            i = len(results)
            bar = "#" * i + "." * (len(jobs) - i)
            print(f"\r[{bar}] {i}/{len(jobs)} seeds  {time.perf_counter() - started:5.1f}s", end="", flush=True)

    try:
        if workers == 1 or len(jobs) == 1:
            for job in jobs:
                results.append(func(job))
                progress()
        else:
            pool = Pool(workers or min(len(jobs), os.cpu_count() or 1), initializer=_ignore_sigint)
            iterator = pool.imap_unordered(func, jobs)
            while len(results) < len(jobs):
                try:  # short timeouts so Ctrl+C is noticed on Windows (a blocking wait ignores it)
                    results.append(iterator.next(timeout=0.5))
                except TimeoutError:
                    continue
                progress()
            pool.close()
            pool.join()
            pool = None
    except KeyboardInterrupt:
        _interrupted(pool)
    finally:
        if pool is not None:  # a worker raised: don't leave processes behind
            pool.terminate()
            pool.join()
    if not quiet:
        print()
    return sorted(results, key=lambda r: r[0])


def simulate(n: int, days: int, seeds: list[int], arms: list[str], cfg: dict, workers: int = 0, quiet: bool = False):
    """Returns (events, personas, metrics). workers=0 -> one process per seed (capped at CPU count)."""
    cfg = {**cfg, "days": days}
    results = map_seeds(run_seed, [(s, n, days, arms, cfg) for s in seeds], workers, quiet)
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


def run_scenario(scenario: str, args: argparse.Namespace, arms: list[str], out: Path) -> bool:
    """Run one scenario and write its outputs. Returns False if the safety audit failed."""
    cfg = load_config(scenario)
    seeds = parse_seeds(args.seeds)
    print(f"scenario={scenario} n={args.n} days={args.days} seeds={seeds} arms={arms}")
    events, personas, metrics = simulate(args.n, args.days, seeds, arms, cfg, args.workers)

    out.mkdir(parents=True, exist_ok=True)
    ev_path = _write_table(events, out / "events")
    _write_table(personas, out / "personas")
    metrics["run"] = {"scenario": scenario, "n": args.n, "days": args.days, "arms": arms}
    (out / "metrics.json").write_text(json.dumps(metrics, indent=1, sort_keys=True), encoding="utf-8")
    (out / "config_snapshot.yaml").write_text(
        yaml.safe_dump({"scenario": scenario, **cfg, "days": args.days}, sort_keys=True), encoding="utf-8"
    )
    print(f"wrote {ev_path}, metrics.json and config_snapshot.yaml to {out}")

    # Fail loudly: the engine arms must never show an unsafe action or message in quiet hours.
    ok = True
    engine_arms = [a for a in ("B", "C", "C4") if a in metrics["arms"]]
    for arm in engine_arms:
        if arm in metrics["arms"]:
            bad = metrics["arms"][arm]["safety_violations"]["max"] or 0
            quiet = metrics["arms"][arm]["quiet_messages"]["max"] or 0
            if bad or quiet:
                print(f"FAIL [{scenario}]: arm {arm} has {bad:.0f} safety violations / {quiet:.0f} quiet-hour "
                      f"messages (see the 'violation' and 'quiet' columns in {ev_path.name})")
                ok = False
    if ok:
        print(f"safety audit [{scenario}]: 0 violations and 0 quiet-hour messages in {', '.join(engine_arms)}")
    return ok


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Rebound synthetic-population simulation")
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--seeds", default="1-10")
    ap.add_argument("--arms", nargs="+", default=["A", "B", "C"])
    ap.add_argument("--scenario", default="baseline")
    ap.add_argument("--all-scenarios", action="store_true", help="run every scenario in scenarios.yaml")
    ap.add_argument("--sensitivity", action="store_true", help="also run A with streak_sensitivity = 0 (arm A0)")
    ap.add_argument("--workers", type=int, default=0)
    ap.add_argument("--out", default="sim/out/run_001")
    args = ap.parse_args(argv)
    try:
        _main(args)
    except KeyboardInterrupt:  # outside simulate(), e.g. while writing outputs
        _interrupted(None)


def _main(args: argparse.Namespace) -> None:
    arms = list(dict.fromkeys(args.arms + (["A0"] if args.sensitivity else [])))
    out = Path(args.out)
    if args.all_scenarios:
        names = list(yaml.safe_load((SIM_DIR / "scenarios.yaml").read_text(encoding="utf-8")))
        failed = [name for name in names if not run_scenario(name, args, arms, out / name)]
    else:
        failed = [] if run_scenario(args.scenario, args, arms, out) else [args.scenario]
    if failed:
        sys.exit(f"FAIL: safety audit failed in {failed}")


if __name__ == "__main__":
    main()
