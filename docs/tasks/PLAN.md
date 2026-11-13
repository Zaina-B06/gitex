# Solo build plan (one developer + coding agent)

Do the tasks **in this order**. Each one ends with something that runs. Don't start the next task until the current one's "Done when" checks pass.

| Day | Task file | Outcome |
|---|---|---|
| Fri 13 (done) | `TASK_01_A_engine_core.md`, `TASK_02_simulator_bandit.md`, `TASK_02b_lapse_risk_model.md` | Engine + simulator + bandit + scenarios + sweep + lapse-risk model; results in `docs/ASSUMPTIONS.md`, `docs/MODEL_CARD.md` |
| Sat 14 | Task 03: thin FastAPI wrapper + SQLite event log + **lean** LLM layer (barrier classifier + red-flag keywords + ~6 templates, EN/AR). `Engine()` without a risk model. | Full flow works over HTTP |
| Sun 15 | `TASK_01_B_frontend_shell.md` (lean version, see cuts) wired to the real API | Clickable journey on a phone |
| Mon 16 | Demo controls (time travel, scenarios) + outcome dashboard (from `docs/results/run_007`) + simple employer page | Judges can watch a lapse and a recovery |
| Tue 17 | Polish + deploy (Vercel + Render/Fly) + Arabic pass | Public links work |
| Wed 18 | Docs (from `TASK_01_C` §5 skeleton) + 3-min demo video | Submission package |
| Thu 19 | Buffer | Fix list cleared |
| Fri 20 | Submit early | Done |

## Solo cuts (already decided)
- **Onboarding: 5 screens, not 9.** (1) Language + goals, (2) Basics + optional body, (3) Health check (7 yes/no + pregnancy + mobility), (4) Baseline + past experience, (5) Preferences + consent. Same fields, fewer screens.
- **LLM layer is lean:** buttons are the main check-in input, LLM only for the free-text box; red flags = keyword list (guaranteed) + LLM (bonus). Eval set of ~40 examples, not 80.
- **Languages:** English + Arabic only. No third language, no voice notes (show a disabled "coming soon" button).
- **Employer view:** one page with aggregate numbers and the k ≥ 10 rule, no filters.
- **Lapse-risk hook is off in the app** (pre-registered test, run_008): the model is shown only as a prediction result.
- **If behind schedule, cut next:** bandit → keep rules-only in the app, show the bandit only in the simulation results.

## Never cut
Lapse → check-in → smaller action → recovery flow · simulator results · safety screening + red flags · documentation.
