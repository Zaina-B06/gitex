# Task 02 — Simulator + bandit + outcome metrics (Sat 14)

Read `AGENTS.md` first. Task 01 is done: the engine (rules layer, state, safety) passes its tests. This task adds the learning layer to the engine and builds the synthetic population that evaluates it. **The simulator must call the real `Engine`, never a copy of its logic.**

## Part 1 — Bandit in the engine (`engine/rebound_engine/policy.py`)

The rules layer keeps control of **tier** (shrink, step-up, step-down) and **safety**. The bandit only chooses *which allowed action at the current tier* and *which time window*.

- Arms: `(action_id, time_window)` where `time_window ∈ {morning, afternoon, evening}` (sleep actions: evening only). Arms come only from the safety-filtered, current-tier action set.
- Thompson sampling with Beta(α, β) per arm per user. Prior α = β = 1. **Warm start:** +1 α for arms whose BCT matches one of the user's `past_helpers` (map helper → BCT codes in config).
- Reward: completed = 1, partial = 0.5 (fractional update: α += r, β += 1 − r), skipped/no_response = 0.
- `Engine(policy_mode="rules" | "bandit")`. `rules` mode = Task 01 behaviour (deterministic choice, default window from profile).
- Seeded RNG passed in; no global randomness.
- Tests: on a toy 3-arm problem with true rates 0.2/0.5/0.8, the best arm is chosen > 70% of the time after 200 rounds (fixed seed); the bandit never returns an arm outside the allowed set; warm start raises the initial choice share of a helper-matched arm.

## Part 2 — Synthetic population (`sim/`)

### Personas (`sim/personas.py`)
`generate_personas(n=300, seed)` returns a list of (`OnboardingPayload`, `HiddenTraits`). Distributions live in `sim/config.yaml` and are documented in `docs/ASSUMPTIONS.md`.
- Segments: `schedule_type` (office, shift, outdoor_manual, home_caregiver, student), `language` (ar, en; plus a `south_asian` label that uses English in the app), `health_literacy` (low/med/high), `mobility_limitation`, `sex`, age 18–70, ~15% with screening flags, pregnancy only for some female personas, ~40% fasting in Ramadan, varied `past_helpers` / `past_stop_reasons`.
- `HiddenTraits` (the engine never sees these): `motivation_mean`, `motivation_volatility`, `capacity_tier` per behaviour (highest tier the persona can sustain), `bct_responsiveness` (per BCT code, ~N(0, 0.5)), `preferred_window`, `true_barrier_weights`, `checkin_answer_rate`, `streak_sensitivity` (see the baseline below).

### Behaviour model (`sim/user_model.py`)
Each day, for each action shown:
- `motivation_t` = AR(1) mean-reverting random walk around `motivation_mean`, plus disruption shocks.
- P(complete) = sigmoid(b0 + b1·motivation_t + b2·true_habit + b3·tier_fit + b4·bct_responsiveness[bct] + b5·window_match − disruption_penalties). `tier_fit` is strongly negative when tier > capacity_tier.
- Outcome draw: completed / partial / skipped / no_response. The no_response share rises as motivation falls.
- `true_habit` is the persona's own hidden habit state, updated from outcomes (separate from the engine's H).
- **Dropout:** 14 consecutive days of no responses → the persona churns permanently.
- **Check-ins:** answered with probability `checkin_answer_rate`; the answer is the persona's true current barrier with p = 0.8, otherwise a random barrier.
- **Disruptions** (rates in config, by segment): Ramadan days 30–59 for fasting personas (windows shift; non-fasting-safe actions get a penalty if shown), summer heat (outdoor penalty, highest for outdoor_manual), illness episodes 3–7 days (Poisson), travel, workload spikes (shift workers more).

### Arms (`sim/arms.py`)
- **A. Static streak app (baseline):** fixed goal = tier 3 (or the safety cap if lower), fixed reminder time, no shrinking, no check-ins, a visible streak that resets on a miss. Model the **abstinence-violation effect** as a motivation drop of `streak_sensitivity` after a streak reset.
- **B. Rebound rules-only:** `Engine(policy_mode="rules")`.
- **C. Rebound full:** `Engine(policy_mode="bandit")`.
- **Sensitivity run (required):** re-run A with `streak_sensitivity = 0`. If Rebound's advantage disappears, we report that honestly; judges will trust the results more for it.

### Runner (`sim/run.py`)
`python -m sim.run --n 300 --days 90 --seeds 1-10 --arms A B C --scenario baseline --out sim/out/run_001 [--sensitivity] [--all-scenarios]`
- Writes `events.parquet` (or CSV), `personas.parquet`, `metrics.json`, `config_snapshot.yaml`.
- Must finish one scenario (300 × 90 × 3 arms × 10 seeds) in under ~5 minutes on a laptop; use multiprocessing across seeds; print a progress bar.

## Part 3 — Metrics (`sim/metrics.py`)

All definitions from PRD §8, computed per arm and per seed (report mean and min–max across seeds):
- **Persistence:** % of personas with ≥ 3 active days in week 4, week 8 and week 12 (a day is active if any action is completed or partial).
- **Recovery rate:** % of lapse episodes followed by a return to active within 14 days. **Time to recover:** median days from lapse onset to recovering. For arm A, define a lapse with the same 7-day rule applied to its events.
- **Behaviour change:** Δ weekly active minutes (sum of `duration_min` for completed movement; partial = half) from week 1 to week 12; sleep: share of nights with the sleep action completed, week 1 vs week 12.
- **Retention:** % not churned at day 90.
- **Equity:** every metric above by `schedule_type`, `language`, `mobility_limitation`, `health_literacy`; plus the gap between the best- and worst-served segment.
- **Burden:** messages per persona per week; messages sent in quiet hours (must be 0 for B and C).
- **Safety audit:** count of shown actions that break a persona's safety constraints (must be 0 for B and C). Fail the run loudly if it isn't.

`python -m sim.report --run sim/out/run_001` writes PNG charts to `sim/out/run_001/charts/`: persistence by week per arm, recovery-time distribution per arm, the equity table as a heatmap, and the sensitivity comparison. It also prints a short markdown summary that we'll paste into the docs.

## Part 4 — Scenarios, random shocks and uncertainty

One run with one number proves little. The evaluation must show **multiple possible outcomes** and handle randomness explicitly.

### 4.1 Scenarios (`sim/scenarios.yaml`)
Each scenario overrides config values. The runner takes `--scenario <name>` or `--all-scenarios`.
| Scenario | What changes |
|---|---|
| `baseline` | Default config |
| `ramadan_heavy` | 70% of personas fasting; Ramadan days 20–49 |
| `hot_summer` | Heat on for days 1–60; outdoor penalty ×2 |
| `low_checkin` | `checkin_answer_rate` halved for everyone |
| `high_dropout` | Dropout after 7 silent days instead of 14; lower motivation_mean |
| `shock_heavy` | Unlabelled shock rate ×3 (see 4.2) |

### 4.2 Unlabelled random shocks
Besides the known disruptions (whose context flags the engine may be told about), add **shocks the engine is never told about**: random life events (family emergency, job change, low mood spell) that cut motivation by a random amount for a random 2–14 days. Each persona gets a random number of them at random times (Poisson, seeded). The engine must detect them only from behaviour. Report recovery metrics **separately for labelled disruptions and unlabelled shocks**.

### 4.3 Uncertainty, reported clearly
- Default to **10 seeds**. Every metric is reported as mean with a 95% interval across seeds (percentile bootstrap over personas within a seed is a bonus).
- Arm comparisons are reported as a **difference with its interval** (e.g. "C vs A persistence at week 12: +18 pts [+14, +22]"), never as a bare number.
- Charts show the interval as bands or error bars.

### 4.4 Sensitivity sweep
`python -m sim.sweep --param <name> --values ...`, plus a default sweep over the 6 most influential parameters (`streak_sensitivity`, `motivation_volatility`, `checkin_answer_rate`, the `bct_responsiveness` spread, shock rate, the `tier_fit` penalty). Output a **tornado chart**: how much the C-vs-A persistence gap moves as each parameter goes from low to high. If any setting makes the gap ≤ 0, list it in the summary under "Where Rebound doesn't help".

### 4.5 Optional calibration
If a public, openly licensed wearable dataset is available, use it only to set the day-to-day variance and autocorrelation of activity in the user model. Record the dataset and its licence in `docs/DATA_SOURCES.md`. Skip this if it takes more than an hour.

## Tests
- Same seed → identical `metrics.json`.
- Each scenario changes only the parameters it declares (diff against `baseline`).
- Unlabelled shocks never appear in anything the engine receives (no context flag, no event field).
- Persona distributions match config within tolerance (n = 300).
- Safety audit = 0 for B and C over a full run.
- No quiet-hour messages in B and C.
- A churned persona never gets another event.

## Done when
- All tests pass (engine + sim).
- The full run + report produce charts and a summary table **for every scenario**, with intervals on every number, plus the tornado chart and a "Where Rebound doesn't help" section.
- `docs/ASSUMPTIONS.md` lists every simulation parameter and why we chose it, including that arm A's abstinence-violation effect is an assumption tested by the sensitivity run.

**Give me the commands to run**; don't run them and summarise. Don't commit until I've reviewed the results.
