# Task 04 — Frontend (owner: teammate)

Read `AGENTS.md` (§4 onboarding fields, §7 API contract) and `docs/HANDOFF.md` first.
**`docs/tasks/TASK_01_B_frontend_shell.md` has the detailed screen spec. Build that, with the changes below**, which came from decisions made after it was written.

You can start immediately against mock data; the backend (Task 03) is being built in parallel. When `api/openapi.json` lands in the repo, generate TypeScript types from it (e.g. `openapi-typescript`) and replace the hand-written types.

## Changes vs TASK_01_B
1. **Onboarding is 5 screens, not 9.** Same fields, grouped: (1) language + goals, (2) basics + optional body, (3) health check (7 yes/no + pregnancy if female + mobility), (4) baseline + past experience + "your own reason" (optional, ≤ 200 chars, "We'll remind you of this on tough days"), (5) preferences + consent.
2. **Two actions a day.** The Today screen shows one card per goal: movement (daytime) and sleep (evening). Each card has Done / Did a smaller version / Skip today and "why this?".
3. **API returns lists:** `today.actions[]` and `checkin.adjusted_actions[]`.
4. **No streaks anywhere.** Show a habit-strength ring per goal (0–100%), and count comebacks as wins on Progress.
5. **Cut for scope:** no third language, no voice notes (show a disabled "coming soon" button).

## Part 2 (after the core screens work)
6. **Demo panel** (shown only when `VITE_DEMO_MODE=true`): buttons for "Skip 7 days (good week)", "Skip 4 days (lapse)", "Start Ramadan", "Heat wave", calling `/demo/users/{id}/advance`. Show the returned day-by-day log so judges can watch drifting → lapsed → check-in → recovery in 2 minutes. A "Load demo persona" picker uses `/demo/seed`.
7. **Results dashboard** page reading `GET /dashboard/outcomes`: headline cards (recovery, persistence, retention vs the streak app, with ranges), activity gains vs the fixed plan, the 7-world table, the safety audit (0 violations), the risk-model card (93% of lapses flagged vs 62%), and a clearly visible **"Where Rebound doesn't help"** section. Use the wording in `docs/Rebound_Results_Explained.pdf` if it's in the repo; otherwise docs/ASSUMPTIONS.md.
8. **Employer page** reading `GET /dashboard/employer?org_id=<org_id>` with the `X-Org-Key` header (`ORG_KEY` from `.env`). Use the `org_id` returned by `POST /demo/seed`; every seed call creates a fresh org, so there is no fixed `demo` id. Aggregates only, and a friendly message when the API returns 403 (fewer than 10 people). A 401 means a missing or wrong org key.

## Done when
- Full journey clickable on a phone-sized screen in English and Arabic (RTL correct), against mocks and then the real API.
- Demo panel shows a lapse and a recovery end to end.
- Dashboard and employer pages render from the API.
- No hard-coded strings; large tap targets; Lighthouse accessibility ≥ 90 on onboarding.

**Give the developer the commands to run**; don't run them and summarise. No attribution lines in commits.
