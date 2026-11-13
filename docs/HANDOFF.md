# Handoff: where Rebound stands

Last updated 2026-11-13. Deadline: working prototype + technical docs + assumptions/limitations due **20 Nov 2026**.
Read `AGENTS.md` (identical to `CLAUDE.md`) first: product spec, rules and conventions. The build plan is
`docs/tasks/PLAN.md`.

## Done

| Task | What exists | Key commits |
|---|---|---|
| **Task 01: engine core** | `engine/rebound_engine`: Pydantic models, 17-action library (`engine/data/actions.yaml`), safety layer (screening, context filters, red flags EN/AR), habit strength + engagement state, rules policy (shrink on slip, consecutive step-up/down), Engine facade with a `Store` protocol, 30-day demo CLI. One movement and one sleep action per goal per day. | `b21699a` → `e22630f` |
| **Task 02 Drop 1: simulator** | Thompson-sampling bandit in the engine (`policy_mode="bandit"`), quiet hours, fast store. `sim/`: personas + hidden traits, behaviour model (daily app-open step, novelty decay, pre-registered success feedback δ = 0.05), arms A (streak app) / A0 (no streak penalty) / B (rules) / C (bandit), independent safety audit, metrics with 95% intervals, charts + summary. | `758341a`, `3cc111b` (pre-registration), `5ddb921` |
| **Task 02 Drop 2: robustness** | 7 scenarios (incl. `harsh_attrition`), unlabelled shocks the engine never sees, recovery split by what preceded a lapse, sensitivity sweep + tornado chart, `--all-scenarios`, clean Ctrl+C. | `abcbf8b` |
| **Step-up 3 → 4** | sweep_003 recorded; change pre-registered, then tested as arm C4 on fresh seeds 11–20 (run_006): decision "keep 4". Engine now steps up after **4** consecutive completions; tests read the threshold from config; AGENTS.md §6.3 updated; reported results re-run (run_007). | `97b94ef`, `cac4f73` (pre-registration), `a657d17`, `d051f30`, `f13f9dd`, `b402774`, `ead1934` |
| **Task 02b: lapse-risk model** | Drop A: engine-visible features (`engine/rebound_engine/risk/`), training + evaluation (`sim/train_risk.py`), plain-language alert reasons, model card. Drop B: `Engine(risk_model=...)` hook and arms D / D50, tested as pre-registered (run_008): **decision "keep the hook out of the app"**. The hook is **disabled by default** (`Engine()` without a model is the shipped engine); the model stays as a tested component. | `644b54f` (pre-registration), `c46b25a`, `23a0663`, `ec5f211`, `ee05a3e`, `760ce45`, `ca2440d` |

All parameters, calibration and results are in `docs/ASSUMPTIONS.md`. A snapshot of the reviewed outputs is in
`docs/results/` (index: `docs/results/README.md`). **Report run_011**: the shipped engine, seeds 1–10, all scenarios,
check-ins answered only on days the app is open. run_007 is the earlier world (check-ins answered on any day).

## Key findings (run_011, shipped engine; simulation, so relative, not real-world effect sizes)

- **Against a streak app that penalises misses, Rebound improves recovery (+13 to +19 pts), week-12 persistence
  (+17 to +25 pts) and retention (+13 to +19 pts) in all 7 scenarios, and people do more** (+16.9 active min/week,
  +13.9 pts tier-weighted sleep in baseline). Safety audit: 0 unsafe actions and 0 quiet-hour messages everywhere.
- **That engagement advantage depends entirely on the abstinence-violation assumption** (missing a day on a streak
  app lowers motivation). With no such effect it disappears: C vs A persistence −1.0 pts [−3.0, +1.0] (sweep_002).
- **Against a kind fixed plan (A0): about equal on engagement, no reliable recovery edge, and people do more:**
  +8.7 active min/week and +10.4 pts tier-weighted sleep in baseline (helps in 7/7). Recovery vs A0 is "helps" in
  1/7 scenarios in run_011, 5/7 in run_007 and 7/7 in run_010 (other seeds), so it isn't robust across seed sets.
  Four small "worse" results of 105 (≤ 1.0 pt): persistence wk 12 vs A0 in baseline, high_dropout and shock_heavy;
  retention vs B in ramadan_heavy (`docs/ASSUMPTIONS.md`, "Reported results … run_011").
- **Check-ins only count on days the app is open** (pre-registered, adopted whatever the result): answered check-ins
  fall from 84% to 60% in baseline. C vs A is unchanged; the recovery edge over A0 is what moved.
- **The per-user bandit adds no measurable benefit over rules** at 90 days with people opening the app on ~40% of days.
- **Step-up after 4 (not 3) was adopted by a pre-registered test:** seeds 1–5 informed it (sweep_003), seeds 11–20
  confirmed it (run_006: about +2 active min/week vs step-up 3 in every scenario, no engagement cost), seeds 1–10
  re-report the shipped engine (run_007, now run_011).
- **Lapse prediction works; the in-app hook doesn't.** The model flags 93% of upcoming lapses in the prior week vs 62%
  for the drifting rule, at a similar alert rate (`docs/MODEL_CARD.md`). But offering a lighter option on alert didn't
  lower the lapse rate (run_008, D vs C ≈ 0). 46% of alert days with an option were closed-app days, and most at-risk
  users were already at tier 1. Pilot recommendation: trigger *out-of-app* support (WhatsApp-style nudge, buddy) from
  the risk score.
- **Rebound vs a static easy plan (A0): lapse rate is slightly higher** (baseline +1.3 pts [+0.8, +1.8] in run_011),
  consistent with Rebound asking for more; with no reliable recovery edge, that's a cost to state plainly.

## Next, in order (see `docs/tasks/PLAN.md`)

1. **Task 03 (Sat 14): API + lean LLM layer.** FastAPI wrapper, SQLite event log, barrier classifier, red-flag
   keywords, templates EN/AR. The API contract is `AGENTS.md` §7. The API uses `Engine()` **without** a risk model.
2. **Sun 15:** frontend shell wired to the API (`TASK_01_B_frontend_shell.md`, lean version).
3. **Mon 16:** demo controls (time travel) + outcome dashboard + simple employer page.
4. **Tue 17:** deploy. **Wed 18:** docs + demo video. **Thu 19:** buffer. **Fri 20:** submit.

## Setup on a fresh clone

Python 3.11+.

**Windows (PowerShell)**
```powershell
git clone https://github.com/Zaina-B06/gitex.git
cd gitex
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e "engine[dev,risk]"
pip install -e "sim[dev]"
copy .env.example .env      # only needed from Task 03 on; fill in locally, never commit
```

**macOS / Linux**
```bash
git clone https://github.com/Zaina-B06/gitex.git
cd gitex
python3 -m venv .venv
source .venv/bin/activate
pip install -e "engine[dev,risk]"
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
# The reported world from now on: check-ins answered only on open days (default). About 7–8 minutes.
python -m sim.run --n 300 --days 90 --seeds 1-10 --arms A B C --all-scenarios --sensitivity --out sim/out/run_011
python -m sim.report --run sim/out/run_011

# The earlier world (run_007): check-ins answered on any day
python -m sim.run --n 300 --days 90 --seeds 1-10 --arms A B C --all-scenarios --sensitivity --set traits.checkin_needs_open_app=false --out sim/out/run_007
python -m sim.report --run sim/out/run_007

# The check-in rule test (pre-registered): same seeds 31-40, flag off vs on
python -m sim.run --n 300 --days 90 --seeds 31-40 --arms A B C --all-scenarios --sensitivity --set traits.checkin_needs_open_app=false --out sim/out/run_009
python -m sim.run --n 300 --days 90 --seeds 31-40 --arms A B C --all-scenarios --sensitivity --out sim/out/run_010
```

Ctrl+C stops any of these cleanly. Arm-A calibration runs (seed 101 only) are described in `docs/ASSUMPTIONS.md`.

**Older snapshots were made with step-up 3** (run_005, run_006, sweep_002, sweep_003). To reproduce them exactly, check
out the last commit before the engine change, `d051f30`, then run (a throwaway worktree keeps your branch untouched):

```bash
git worktree add ../gitex-stepup3 d051f30 && cd ../gitex-stepup3
# then, with the same venv active (pip install -e "engine[dev]" -e "sim[dev]" inside the worktree first):
python -m sim.run --n 300 --days 90 --seeds 11-20 --arms A C C4 --all-scenarios --sensitivity --out sim/out/run_006
python -m sim.report --run sim/out/run_006                                   # step-up test, decision "keep 4"
python -m sim.sweep --out sim/out/sweep_002                                  # full sweep, ~10–15 min
python -m sim.sweep --param engine_overrides.STEP_UP_SUCCESSES --values 2 3 4 5 --out sim/out/sweep_003
```

On the current engine the sweeps still run, but their baseline is now step-up 4, and C4 equals C.

## Working rules

- **Run commands yourself.** Agents write code and give the exact commands; the developer runs them and pastes back
  anything that fails (`AGENTS.md` §8).
- **Pre-register before changing the model or the engine because of results** (`AGENTS.md` §9): write it in
  `docs/ASSUMPTIONS.md`, commit that alone, then run. Calibrate on seed 101 only; evaluate on seeds 1–10, re-test on
  fresh seeds.
- **Never commit `.env`.** Only `.env.example` with empty keys is in the repo.
- Small commits, one feature each; every new number or rule gets a line in `docs/ASSUMPTIONS.md`.
- Ask before changing `AGENTS.md` / `CLAUDE.md`, and keep the two identical.
