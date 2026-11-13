# Task 03 — API + storage (owner: Hamza)

Read `AGENTS.md` (esp. §7 API contract, §8 conventions) and `docs/HANDOFF.md` first.
The engine and simulator are done. This task wraps the engine in a FastAPI service so the app can use it.
**The API calls `Engine` methods; it never reimplements engine logic.** It uses `Engine()` without a risk model (the hook is off; see ASSUMPTIONS.md, "Arm D").

## Build (`api/`)

1. **App:** FastAPI + Pydantic v2, reusing engine models for request/response shapes. CORS for `http://localhost:5173` and the deployed frontend URL (from `.env`). OpenAPI at `/docs`; commit an exported `api/openapi.json` so the frontend can generate types.
2. **Storage:** `SQLiteStore` implementing the engine's existing `Store` protocol (path from `DATABASE_URL`, default `sqlite:///rebound.db`). It must pass the same store tests as the in-memory store. Sensitive profile groups (body, health check, history) in a separate table from behaviour events.
3. **Endpoints** (§7, with action lists):
   - `POST /users` (onboarding) → `{user_id, state, today: {actions: [...]}}`
   - `GET /users/{id}/today` → `{actions: [{action, explanation_id}], state_summary}`
   - `POST /users/{id}/events` `{action_id, type: completed|partial|skipped}` → `{state}`
   - `POST /users/{id}/checkin` `{barriers: [...], free_text?}` → `{barrier, adjusted_actions, message, red_flag}`
   - `GET /users/{id}/state` → habit strength, engagement state, tiers, recent history
   - `GET /actions/{id}/explain` → BCT code/name, rationale, limits, how to turn off
   - `PATCH /users/{id}/settings`, `DELETE /users/{id}` (deletes everything for that user)
4. **Clock:** real users follow calendar days in their time zone. Each user also has a `day_offset` used only by demo endpoints.
5. **Demo endpoints** (only when `DEMO_MODE=true`):
   - `POST /demo/users/{id}/advance` `{days, pattern: "good"|"lapse"|"mixed", scenario?: "ramadan"|"heat"}` fills the skipped days with outcomes and flags, then returns the new state and a day-by-day log for the UI.
   - `POST /demo/seed` creates 3 demo personas (e.g. Ahmed the shift worker, an office worker, a user with a mobility limitation) and a demo org of 12 synthetic users.
6. **Check-in text:** if `free_text` is given, call `llm.classify_barrier` through an interface; with no LLM configured, use a `FakeLLM`/keyword fallback (buttons still decide). Red flags always run the engine's keyword check first. The LLM package is a separate task (`TASK_01_C_llm_safety_docs.md`); the API must work without it.
7. **Dashboard data:** `sim/out` is git-ignored, so add `python -m sim.export_dashboard --run sim/out/run_007 --out docs/results/dashboard.json` (small JSON: headline table, activity numbers, scenario table, safety audit, risk-model metrics from risk_001). `GET /dashboard/outcomes` serves that file.
8. **Employer view:** `GET /dashboard/employer?org_id=` returns aggregates only (active share, average habit strength, top barriers); **403 if the org has fewer than 10 users**. No endpoint returns individual data to an org.

## Tests (pytest + TestClient)
- Full journey: onboard → today (2 actions) → complete → advance with "lapse" → drifting/lapsed state → check-in → adjusted actions → recovery.
- A red-flag phrase in free text → `red_flag: true`, care message, no coaching action.
- `DELETE` removes every row for the user.
- Employer endpoint: 403 below 10 users; no user IDs in the response.
- Quiet hours respected in `today`.
- `SQLiteStore` passes the shared store tests.

## Done when
- `uvicorn api.main:app --reload` serves everything; `/docs` shows all endpoints; tests pass.
- `api/openapi.json` and `docs/results/dashboard.json` are committed.
- `README` has the run command; `.env.example` has `DATABASE_URL`, `DEMO_MODE`, `FRONTEND_URL`, LLM keys.

**Give me the commands to run**; don't run them yourself. No attribution lines in commits.
