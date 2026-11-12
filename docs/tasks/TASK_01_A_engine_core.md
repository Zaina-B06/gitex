# Task 01 — Repo scaffold + engine core (Day 1, Fri 13)

Read `AGENTS.md` first. This task covers §3, §5 and §6.1–6.3 (rules layer only; the bandit comes in Task 02).

## Build

1. **Repo scaffold** matching `AGENTS.md` §3. Root `README.md` with setup commands. `pyproject.toml` for `engine/` (installable as `rebound_engine`, editable install). Dev deps: pytest, ruff.
2. **`models.py`**: Pydantic v2 models for `OnboardingPayload` / `UserProfile` (all fields in §4, with optional ones `Optional` and sensible enums), `Action`, `Event`, `UserState`, `Barrier` enum, `EngagementState` enum.
3. **`data/actions.yaml`**: action library, **at least 16 actions** (solo scope; more can be added later):
   - movement: 4 tiers × (indoor, outdoor) + seated variants for tiers 1–2 + pregnancy-safe flags
   - sleep: 4 tiers (e.g. fixed wake time → wind-down routine → screen curfew → consistent schedule 6/7 nights)
   - every action has `bct_code` + `bct_name` (BCT Taxonomy v1, e.g. 1.4 Action planning, 8.7 Graded tasks, 2.3 Self-monitoring of behaviour, 7.1 Prompts/cues, 8.3 Habit formation), `rationale`, `limits`, and `en` + `ar` titles (Arabic can be a first draft; mark `ar_reviewed: false`).
4. **`actions.py`**: load + validate YAML; `filter_actions(profile, state, context) -> list[Action]`.
5. **`safety.py`**:
   - `screening_flags(profile) -> ScreeningResult` (implements §4.3 rules: tier cap, doctor prompt, sleep-only start)
   - `context_filter(actions, context_flags, hour)` (heat window, fasting, illness, pregnancy, mobility)
   - `detect_red_flags(text) -> bool` (keyword list only for now; Person C adds the LLM check)
6. **`state.py`**: `update_habit_strength`, `compute_engagement_state` (exact rules in §6.1, including "paused/illness days don't count").
7. **`policy.py`**: rules layer only (`AGENTS.md` §6.3 steps 1, 2, 4). `choose_action(profile, state, barrier=None) -> Action`. Leave a `Bandit` interface stub with `select(allowed_actions, user_state)` that currently returns the rules choice.
8. **`engine.py`**: `Engine` facade with `onboard(payload)`, `today(user_id, day)`, `record(event)`, `checkin(user_id, barriers, free_text)`. In-memory store for now, behind a `Store` protocol so the API can swap in SQLite.
9. **`config.py`**: λ, thresholds, tier caps, heat window.
10. **CLI** `python -m rebound_engine.demo --days 30 --seed 1`: one synthetic user, prints a day-by-day table (day, action, outcome, H, state). Outcomes come from a simple random generator, with a forced 4-day lapse on days 15–18.

## Tests (pytest), minimum
- Habit strength: one missed day after 10 completions keeps H > 0.5; H never goes below 0 or above 1.
- State transitions: active → drifting → lapsed → recovering → active on a crafted sequence.
- Screening: chest-pain yes → sleep/gentle actions only; any yes → movement tier ≤ 2.
- Heat mode at 13:00 removes outdoor actions; fasting removes non-`fasting_safe` actions.
- Barrier `time` → tier −1; `illness_pain` → no movement actions.
- Step-up: 3 successes at tier 1 → tier 2; never jumps two tiers.
- Red-flag keywords detected in English and Arabic samples.

## Done when
- Engine installs and imports cleanly; all tests pass.
- The demo CLI shows H dipping during the lapse but not resetting, and the state moving through drifting → lapsed → recovering.
- Every chosen number is noted in `docs/ASSUMPTIONS.md`.

**Give me the commands to run** (install, tests, demo CLI); don't run them and summarise.
