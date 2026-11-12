# Solo build plan (one developer + coding agent)

Do the tasks **in this order**. Each one ends with something that runs. Don't start the next task until the current one's "Done when" checks pass.

| Day | Task file | Outcome |
|---|---|---|
| Fri 13 | `TASK_01_A_engine_core.md` | Engine package + rules + tests + 30-day CLI demo |
| Sat 14 | Task 02 (written after Task 01 works): simulator + bandit + metrics | 90-day A/B/C comparison with curves |
| Sun 15 | Task 03: thin FastAPI wrapper + SQLite event log + **lean** LLM layer (barrier classifier + red-flag keywords + ~6 templates, EN/AR) | Full flow works over HTTP |
| Mon 16 | `TASK_01_B_frontend_shell.md` (lean version, see cuts) wired to the real API | Clickable journey on a phone |
| Tue 17 | Task 05: demo time-travel + outcome dashboard + simple employer page | Judges can watch a lapse and a recovery |
| Wed 18 | Polish + deploy (Vercel + Render/Fly) + Arabic pass | Public links work |
| Thu 19 | Docs (from `TASK_01_C` §5 skeleton) + 3-min demo video | Submission package |
| Fri 20 | Buffer + submit early | Done |

## Solo cuts (already decided)
- **Onboarding: 5 screens, not 9.** (1) Language + goals, (2) Basics + optional body, (3) Health check (7 yes/no + pregnancy + mobility), (4) Baseline + past experience, (5) Preferences + consent. Same fields, fewer screens.
- **LLM layer is lean:** buttons are the main check-in input, LLM only for the free-text box; red flags = keyword list (guaranteed) + LLM (bonus). Eval set of ~40 examples, not 80.
- **Languages:** English + Arabic only. No third language, no voice notes (show a disabled "coming soon" button).
- **Employer view:** one page with aggregate numbers and the k ≥ 10 rule, no filters.
- **If behind schedule, cut next:** bandit → keep rules-only in the app, show the bandit only in the simulation results.

## Never cut
Lapse → check-in → smaller action → recovery flow · simulator results · safety screening + red flags · documentation.
