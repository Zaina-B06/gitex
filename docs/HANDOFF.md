# Handoff: where Rebound stands

Last updated 2026-11-14. Deadline: working prototype + technical docs + assumptions/limitations due **20 Nov 2026**.
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
| **Task 03: API** | `api/`: FastAPI over the same `Engine()` (rules, no risk model); `SQLiteStore` (sensitive profile groups in their own table); per-user bearer tokens (hashed); calendar-day clock per time zone, unopened days filled in as no-response; all §7 routes + export; consent withdrawal deletes answers; one check-in a day, adjusted action replaces today's; demo `advance` / `seed` (`DEMO_MODE`, `DEMO_KEY`); `/dashboard/outcomes` (from `sim.export_dashboard`) and `/dashboard/employer` (`ORG_KEY`, k ≥ 10). `api/openapi.json` and `docs/results/dashboard.json` committed. Check-in free text goes through `api/llm_client.py` (keyword fallback until the LLM package lands). | `2004608` → `812ad7f` |
| **Check-in rule** | Pre-registered: personas answer check-ins only on days they open the app. Tested on seeds 31–40 (run_009 vs run_010), adopted as decided beforehand, reported results re-run (run_011). | `76e62a6` (pre-registration), `d11b3b2`, `24b2c4d`, `998ae6a` |

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

1. **Sun 15–Mon 16, frontend (teammate, `TASK_04_frontend.md`):** shell wired to the real API, then demo panel,
   results dashboard, employer page. See "For the frontend" below.
2. **Sun 15–Tue 17, LLM layer (teammate, `TASK_01_C_llm_safety_docs.md`, lean):** classifier, templates, safety lists,
   eval set. See "For the LLM layer" below.
3. **Tue 17:** deploy. **Wed 18:** docs + demo video. **Thu 19:** buffer. **Fri 20:** submit.

### Frontend changes (Task 05)
- **Part A, personal plan:**
  - **Onboarding:** add one optional "Anything you're managing?" screen of tap-to-select chips with Skip. Put it on
    an existing screen (e.g. with the health check) so sign-up stays ≤ 5 screens. Send
    `conditions: {managing: [...]}` with values `diabetes`, `high_blood_pressure`, `back_or_joint_pain`, `stress`,
    `recovering_from_illness_or_injury`. Pregnancy and smoking chips map to `screening.pregnant` and
    `history.smoking_status`. Consent group: `conditions`.
  - **Plan card:** `POST /users` now returns `plan_summary: {behaviours, reasons, all_reasons}`, and
    `GET /users/{id}/plan` returns the same. Show `reasons` (at most 3 short lines), with `all_reasons` behind a
    "See why" link. The text is already in the user's language.
  - **Settings:** `PATCH /settings` takes `conditions` and returns the re-built `plan_summary`.
- **Part A2, automatic context (no manual Ramadan/heat switches for users):**
  - **Ramadan, Eid, heat:** turn on by themselves from the date. `GET /state` `context_flags` shows `ramadan`, `eid`
    or `heat`; `today.messages` includes the Eid greeting.
  - **Moon-sighting correction:** for fasting users during Ramadan's first and last days, show two buttons, "Ramadan
    started today" and "Ramadan is over (today is Eid)". They call `PATCH /settings` with
    `{"ramadan": "started_today" | "ended_today"}` and apply the same day; 409 means no Ramadan is near.
  - **Preferences:** `preferences.iftar_time` ("HH:MM") lets users adjust iftar.
  - **Shifts:** shift workers enter a weekly pattern, `basics.shifts: [{days: ["sun",…], start, end}]`, at onboarding
    or with `PATCH /settings {"shifts": [...]}` (`[]` clears it). Windows move the next day.
  - **Demo panel:** the Ramadan and heat-wave demo buttons keep using `advance` scenarios; they're overrides.
- **Part B, new behaviours:**
  - **Onboarding goals:** offer all five: movement, sleep, nutrition, smoking (only show it if `smoking_status` is
    `current`) and recovery.
  - **Today:** at most 3 cards a day, in plan order. With more goals, the third card changes daily; show `plan_summary.rotation_note` (already in the user's language) on the plan card. Each action now
    has `simple` (plain title), `icon` (fixed key) and `tags`.
  - **Recipes:** `today.recipes` maps an action id to a recipe for cooking steps; show it with its `note`
    ("General guidance, not medical advice"). There's also a browsable `GET /recipes?tag=`.
  - **Check-in:** add buttons for `craving`, `stress`, `others_smoking` and `no_healthy_food_nearby`.
- **Community events (read-only):** a "Community" page reading
  `GET /users/{id}/community/events` with the Bearer token. It's already filtered to the user's goals,
  women-only preference, mobility (wheelchair users see wheelchair-accessible events only; "some" limitation sees them first) and language. Optional
  filters: `household`, `behaviour`, `city`. No user posts and no location tracking.
  - **Real programmes:** show "Source" (link) and "Checked on <last_checked>", plus a line asking users to confirm
    times with the organiser.
  - **Examples:** entries with `example: true` must keep their "Example:" title and be visibly marked, never shown
    as real events.
- **Part C, encouragement:** `POST /events` and `GET /today` may return
  `encouragement: {moment, message, behaviour?}`. Show it as a small, dismissible pop-up, without counts or
  confetti-style "streak" visuals. It's at most one a day. Settings has a toggle, `preferences.encouragement`
  (default on).
- Re-generate types from `api/openapi.json`.

## Future scope (not in the prototype)

- **Wearable integration** through a native app (Apple Health, Health Connect); the web app can't read them. The
  API's input side is the next step (`POST /users/{id}/signals`, Task 05 "Later").
- **Nearby healthy options on a map** (OpenStreetMap: greengrocers, supermarkets, parks), opt-in, location never
  stored; offered for the `no_healthy_food_nearby` barrier.
- **Chat nudges** (WhatsApp-style) for people who stop opening the app, triggered by the lapse-risk score; the
  run_008 result points here rather than to in-app offers.
- **Moderated community groups and support buddies** (a buddy sees only good news), instead of open user posts.
- **User-submitted recipes**, reviewed before publishing.
- **Live weather for heat mode**, replacing the fixed May–September rule.

### For the frontend (Task 04)
- **Types:** generate them from `api/openapi.json` (includes the demo routes). Run the API with
  `uvicorn api.main:app --reload`; set `DEV_MODE=true` (or `DEMO_MODE=true`) in `.env` so `http://localhost:5173` is
  allowed by CORS.
- **Auth:** `POST /users` returns `token` once. Store it; send `Authorization: Bearer <token>` on every
  `/users/{id}/*` and `/demo/users/{id}/advance` call. A 401 means a lost or wrong token.
- **Today:** `actions[]` (plan order, at most 3 a day), each with `hour` and `explanation_id`; `messages[]` are already
  rendered in the user's language. After a check-in, `adjusted_actions[]` *replace* today's actions; re-fetch `/today`.
- **Check-in:** at most one per day (409 on a second); free text is optional and a red flag always gets through.
  On `red_flag: true`, show `message` (care guidance, 998 and 800 SAKINA) and no coaching.
- **Settings:** `PATCH /settings` with `preferences`, `consents`, `context` (e.g. `{"heat": true}`,
  `{"illness": false}` = "I'm OK now"). Withdrawing a consent deletes those answers; screening can't be withdrawn
  (409). `GET /users/{id}/export` and `DELETE /users/{id}` cover "view / export / delete".
- **Demo panel:** `POST /demo/seed` needs `X-Demo-Key`; it returns 3 personas with tokens and a **fresh `org_id`**
  every call (not `demo`). `advance` takes `{days, pattern: good|mixed|lapse, scenario?: ramadan|heat}` and returns
  a day-by-day `log`. A lapse needs ≥ 3 unanswered days to show; "Skip 4 days (lapse)" is enough.
- **Results page:** read `GET /dashboard/outcomes` (run_011). Use the new wording: big gains vs the streak app (and that
  this depends on the streak-penalty assumption); **about equal to a kind fixed plan on engagement, no reliable
  recovery edge, more activity**; bandit adds nothing measurable; "Where Rebound doesn't help" visible.
- **Employer page:** `GET /dashboard/employer?org_id=<from seed>` with `X-Org-Key`; show the friendly message on 403.
- **Not in the API:** changing `channel` in settings has no effect yet (documented limitation).

### For the LLM layer (TASK_01_C)
- **Plug-in point:** `api/llm_client.py` imports `llm.classify_barrier` if it exists, else uses the keyword fallback.
  It currently expects `classify_barrier(text) -> Barrier | None`. TASK_01_C specifies
  `classify_barrier(text, lang) -> {barrier, confidence, red_flag, ...}`: when the package lands, adapt the small
  `_LLM` wrapper in `llm_client.py` (pass the user's language, map low confidence to `None`). Provider errors already
  fall back to keywords.
- **Red flags:** the engine's keyword list (`engine/rebound_engine/safety.py`) runs first and is the guarantee;
  red-flag text is never sent to the classifier. An LLM red-flag check is a bonus and isn't wired into the API yet.
- **Messages:** `api/messages.py` holds EN/AR text for the engine's message keys (Arabic unreviewed). The templates
  should replace it with the same keys, keeping 998 / 800 SAKINA in the red-flag message.
- **Keys:** `.env.example` has `LLM_PROVIDER` and the provider keys; the API runs without them.

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
pip install -e "api[dev]"
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
pip install -e "api[dev]"
cp .env.example .env        # only needed from Task 03 on; fill in locally, never commit
```

**Check it works** (from the repo root)
```bash
ruff check engine sim api
pytest engine/tests          # 240 tests
pytest sim/tests             # 49 tests
pytest api/tests             # 96 tests
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
