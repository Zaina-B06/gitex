# Handoff: where Rebound stands

Last updated 2026-11-13. Deadline: working prototype + technical docs + assumptions/limitations due **20 Nov 2026**.
Read `AGENTS.md` (identical to `CLAUDE.md`) first: product spec, rules and conventions. The build plan is
`docs/tasks/PLAN.md`.

## Done

| Task | What exists | Key commits |
|---|---|---|
| **Task 01: engine core** | `engine/rebound_engine`: Pydantic models, 17-action library (`engine/data/actions.yaml`), safety layer (screening, context filters, red flags EN/AR), habit strength + engagement state, rules policy (shrink on slip, consecutive step-up/down), Engine facade with a `Store` protocol, 30-day demo CLI. One movement and one sleep action per goal per day. | `8408739` → `b765f35` |
| **Task 02 Drop 1: simulator** | Thompson-sampling bandit in the engine (`policy_mode="bandit"`), quiet hours, fast store. `sim/`: personas + hidden traits, behaviour model (daily app-open step, novelty decay, pre-registered success feedback δ = 0.05), arms A (streak app) / A0 (no streak penalty) / B (rules) / C (bandit), independent safety audit, metrics with 95% intervals, charts + summary. | `70a181d`, `dc054ab` (pre-registration), `b79f72a` |
| **Task 02 Drop 2: robustness** | 7 scenarios (incl. `harsh_attrition`), unlabelled shocks the engine never sees, recovery split by what preceded a lapse, sensitivity sweep + tornado chart, `--all-scenarios`, clean Ctrl+C. | `d68779f` |

All parameters, calibration and results are in `docs/ASSUMPTIONS.md`. A snapshot of the reviewed outputs is in
`docs/results/` (run_005 = all scenarios, sweep_002 = full sweep, sweep_003 = step-up threshold with activity).

## Key findings (simulation; relative, not real-world effect sizes)

- **Against a streak app that penalises misses, Rebound improves recovery (+13 to +20 pts), week-12 persistence
  (+17 to +25 pts) and retention (+13 to +18 pts) in all 7 scenarios.** Safety audit: 0 unsafe actions and 0
  quiet-hour messages everywhere.
- **That advantage depends entirely on the abstinence-violation assumption** (missing a day on a streak app lowers
  motivation). With no such effect it disappears: C vs A persistence −1.0 pts [−3.0, +1.0] (sweep_002).
- **Against a static plan without that penalty (A0), engagement is about equal, and people do more:** +9 active
  min/week and +10 pts tier-weighted sleep (run_003). Small "worse" results (< 2 pts) appear in a few scenarios,
  consistent with harder actions earning less success feedback.
- **The per-user bandit adds no measurable benefit over rules** at 90 days with people opening the app on ~40% of days.
- **Slower step-ups look better in the simulator** (step up after 4–5 successes instead of 3: more activity, no
  engagement cost; sweep_003). Not acted on: it needs a pre-registered test on fresh seeds.

## Next, in order

1. **Record sweep_003 in `docs/ASSUMPTIONS.md`** (`docs/results/sweep_003/summary.md`), including that the earlier
   guess "slower step-ups cost activity" was wrong.
2. **Pre-registered step-up test, 3 → 4:** write the change and the comparisons in `docs/ASSUMPTIONS.md` and commit
   that alone; then run seeds **11–20** (never used before); keep or revert based on that run only.
3. **Task 02b: lapse-risk model** (`docs/tasks/TASK_02b_lapse_risk_model.md`). Read it fully and ask questions
   before coding.
4. **Task 03: API + lean LLM layer** (FastAPI wrapper, SQLite event log, barrier classifier, red-flag keywords,
   templates EN/AR). The API contract is `AGENTS.md` §7.

## Setup on a fresh clone

Python 3.11+.

**Windows (PowerShell)**
```powershell
git clone https://github.com/Zaina-B06/gitex.git
cd gitex
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e "engine[dev]"
pip install -e "sim[dev]"
copy .env.example .env      # only needed from Task 03 on; fill in locally, never commit
```

**macOS / Linux**
```bash
git clone https://github.com/Zaina-B06/gitex.git
cd gitex
python3 -m venv .venv
source .venv/bin/activate
pip install -e "engine[dev]"
pip install -e "sim[dev]"
cp .env.example .env        # only needed from Task 03 on; fill in locally, never commit
```

**Check it works** (from the repo root)
```bash
ruff check engine sim
pytest engine/tests          # 105 tests
pytest sim/tests             # 25 tests
python -m rebound_engine.demo --days 30 --seed 1
```

## Regenerating the simulator outputs

`sim/out/` isn't committed. These reproduce the snapshot in `docs/results/` (same seeds; results should match with
the same package versions). Run from the repo root.

```bash
# All 7 scenarios, arms A/B/C + A0 (about 7–8 minutes), then charts + summaries
python -m sim.run --n 300 --days 90 --seeds 1-10 --arms A B C --all-scenarios --sensitivity --out sim/out/run_005
python -m sim.report --run sim/out/run_005

# Full sensitivity sweep + tornado chart (26 settings × 5 seeds, about 10–15 minutes)
python -m sim.sweep --out sim/out/sweep_002

# Step-up threshold only, with activity gaps (about 2–3 minutes)
python -m sim.sweep --param engine_overrides.STEP_UP_SUCCESSES --values 2 3 4 5 --out sim/out/sweep_003
```

Ctrl+C stops any of these cleanly. Arm-A calibration runs (seed 101 only) are described in `docs/ASSUMPTIONS.md`.

## Working rules

- **Run commands yourself.** Agents write code and give the exact commands; the developer runs them and pastes back
  anything that fails (`AGENTS.md` §8).
- **Pre-register before changing the model or the engine because of results** (`AGENTS.md` §9): write it in
  `docs/ASSUMPTIONS.md`, commit that alone, then run. Calibrate on seed 101 only; evaluate on seeds 1–10, re-test on
  fresh seeds.
- **Never commit `.env`.** Only `.env.example` with empty keys is in the repo.
- Small commits, one feature each; every new number or rule gets a line in `docs/ASSUMPTIONS.md`.
- Ask before changing `AGENTS.md` / `CLAUDE.md`, and keep the two identical.
