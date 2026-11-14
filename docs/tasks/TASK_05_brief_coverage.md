# Task 05: Personal plans + every behaviour the brief names (owner: Zaina)

Read `AGENTS.md` (= `CLAUDE.md`) and `docs/HANDOFF.md` first.

**Why:** today every user gets the same kind of plan, with only the starting level and safety caps differing, and only movement and sleep. The brief asks for plans built from each person's *goals, preferences, health context and data*, across movement, nutrition, sleep, smoking and recovery, inclusive of health literacy and family context. This task makes Rebound behave differently for each person **from day one**, visibly.

**Rules for every part**
- One part at a time; tests first for every new rule; all suites (`engine`, `sim`, `api`) pass before moving on.
- Safety runs before anything new. Never: diagnosis, medication or dosing advice, calorie or weight targets.
- Sensitive answers (conditions, history) are optional, stored in the sensitive table, never shown to employers, deleted when consent is withdrawn.
- Update `AGENTS.md`/`CLAUDE.md` §4–§7, re-export `api/openapi.json`, record every rule and number in `docs/ASSUMPTIONS.md`, and add a "Frontend changes" note to `docs/HANDOFF.md`.
- Give me the commands; don't run them. No attribution lines in commits.

---

## Part A: Personal plan builder (do first; everything else plugs into it)

1. **Onboarding: "Anything you're managing?"** (optional, multi-select, "why we ask" line): `diabetes`, `high_blood_pressure`, `back_or_joint_pain`, `stress`, `pregnancy` (already asked), `recovering_from_illness_or_injury`, `smoking` (from `smoking_status`). No free-text medical history.
2. **Plan builder** in the engine: `build_plan(profile) -> PlanSummary`, which decides:
   - **Which behaviours come first** (max 3 active; the rest queued): from goals + what they're managing + history (e.g. stress made them stop last time → start with recovery; smoker who chose it → smoking; diabetes → nutrition early).
   - **Which variants of each action**: condition-aware (back pain → low-impact; high blood pressure → no strenuous tiers until cleared; diabetes → nutrition steps about sugary drinks and regular meals; recovering → recovery-first, gentle movement), plus schedule, fasting, mobility, household and reading level.
   - **Starting level** per behaviour (existing logic plus conditions).
   - **Reasons:** a list of plain-language "because you said X → we did Y" lines.
3. **API:** `POST /users` returns `plan_summary` (behaviours in order, reasons); `GET /users/{id}/plan` returns the current one. The plan is re-built when relevant settings change.
4. Tests: two users with different answers get **different** first-week plans and reasons; no condition ever unlocks a harder tier than the health check allows.
5. **No information dumping** (personalisation should feel light, not like a questionnaire or a lecture):
   - "Anything you're managing?" is **one** screen of tap-to-select chips, with Skip.
   - `plan_summary.reasons` has **at most 3** short lines (≤ 12 words each), most important first; the full list is only behind a "See why" link.
   - Each daily action shows **one** line of "why" at most; detail stays in the "Why this?" sheet.
   - Every new onboarding question is optional, and the whole sign-up stays ≤ 5 screens.

## Part A2: Context the app works out by itself (no manual "modes")

1. **Ramadan from the calendar.** For users who said they fast, Ramadan turns on and off automatically from the Hijri calendar: use an offline Umm al-Qura conversion library (e.g. `hijridate`) or a committed table of Ramadan dates for 2026–2028. No network calls. Moon-sighting can shift the start by a day, so the user can tap "Ramadan started today / ended" to correct it. Non-fasting users are unaffected. **Iftar and suhoor times** come from Abu Dhabi sunset and dawn: compute them offline (e.g. the `astral` library with Abu Dhabi coordinates) or from a small committed monthly table, and the user can adjust their usual iftar time. Eid days are rest-friendly.
2. **Shift work from real timings.** Users enter their actual shifts: a weekly pattern (e.g. Sun–Thu 22:00–06:00) or "this week's shifts" (editable in settings). The engine derives from them: action windows (e.g. movement after waking from a night shift, not at 9 am), quiet hours (their sleep after a night shift), and the sleep action (a wind-down before *their* sleep, not a fixed bedtime). When shifts change, windows update the next day.
3. **Heat:** on automatically for the summer months (record which in ASSUMPTIONS); live weather is a later integration.
4. The old manual Ramadan/heat context flags stay only as demo overrides (`/demo/.../advance` with a scenario), so judges can see it in November.
5. Tests: a fasting user's plan changes on the first day of Ramadan with no action from them; a night-shift worker never gets a prompt inside their sleep window; changing shifts moves the windows.

## Part B: New behaviours: nutrition, smoking, recovery

For each: 4 tiers, BCT code, rationale, limits, EN + AR titles (`ar_reviewed: false`), simple-language variant, an `icon` key, condition and family variants where relevant.

1. **Nutrition** (no calorie or weight numbers, ever): water with meals → one extra vegetable or fruit → swap one sugary drink → a home-cooked meal; suhoor and iftar variants.
   - **Recipes:** a curated set of ~20 simple, culturally familiar recipes (Emirati, wider Arab, South Asian) with healthier swaps, tagged (`diabetes_friendly`, `fasting`, `family`, `quick`, `budget`). Suggested when a nutrition step involves cooking. Written by us, not generated by an LLM. No calorie counts. Marked "general guidance, not medical advice".
   - Disordered-eating red flags pause nutrition coaching; pregnancy or diabetes adds "check with your doctor about diet changes".
2. **Smoking (reduce → quit):** delay the first cigarette by 15 min → one fewer today → a smoke-free hour (after meals or iftar) → a smoke-free day; plus cue-avoidance and substitution steps. A slip shrinks the plan like any other lapse. No medication or nicotine-replacement advice. A "want help quitting?" message points to a doctor or pharmacist and, **only if verified from an official UAE government or health-authority source**, a quit service (URL in a code comment; if you can't verify one, tell me and use the doctor/pharmacist wording only).
3. **Recovery** (rest and stress, *not* mental-health treatment): a 2-minute breathing break → a screen-free 15 minutes → a planned rest day after hard days → a short daylight walk; gentle "recovering from illness" variants. Self-harm red flags keep their existing escalation (800-SAKINA).
4. **New barriers:** `craving`, `stress`, `others_smoking`, `no_healthy_food_nearby`, each with a rules adjustment.
5. **Burden cap:** at most 3 actions per day; the plan builder rotates extra goals.
6. Limitations: "Nutrition, smoking and recovery are engine-tested but not yet simulation-evaluated."

## Part C: Encouragement moments (replaces streaks, positively)

1. Engine emits an `encouragement` event with a `moment` key at real moments only: `first_day_done`, `three_good_days`, `comeback` (first completion after drifting or lapsed: "We missed you, glad you're back"), `habit_strength_50`, `first_week_done`, `tried_something_new`.
2. Messages (EN + AR + simple variants) in `api/messages.py`, several per moment and rotated.
3. **Rules:** at most one per day; **never** show counts, never "don't break your streak", never mention how many days were missed; no encouragement during a paused or red-flag state. Users can turn them off.
4. Returned in `/today` and `/events` responses as `encouragement: {moment, message}`; the frontend shows a small pop-up. ASSUMPTIONS: BCT codes (e.g. 10.4 social reward, 2.2 feedback on behaviour) with rationale and limits, so requirement 3 is covered visibly.

## Part D: Health literacy (properly)

1. Preference `reading_level: "standard" | "simple"` at onboarding, showing a plain example of each.
2. Every user-facing string (actions, messages, reasons, encouragement, safety texts) gets a simple variant: short words, one idea per sentence, no jargon.
3. **Measurable:** a test computes a readability score on all English simple variants and fails above a target (e.g. Flesch-Kincaid grade ≤ 6; record the target in ASSUMPTIONS).
4. **Arabic without a native reviewer (be honest about it):** keep Arabic strings short and simple (less to get wrong); add a script that back-translates every Arabic string to English with an LLM and flags any whose meaning drifted, for manual fixing; label Arabic in the app and docs as "draft translation, pending native review"; and list the safety-critical strings (red flags, care messages, health check) first, so any Arabic speaker who can spare 15 minutes reviews those before the demo.
5. `icon` key on every action (fixed list) and a `read_aloud` preference; the frontend uses the browser's built-in speech.

## Part E: Family context

1. Onboarding (optional): `household`: `alone | family | children | older_relatives`; `caregiver: bool`; `family_fasting: bool`.
2. Family variants preferred when relevant (e.g. "walk with your children after maghrib", "a family water jug on the table", "a smoke-free room at home", family-friendly recipes).
3. Barrier `social_family` → a family-inclusive variant instead of only a smaller step.

## Later: the user's chosen data (integration-ready, honest scope). Only after A–E

A web app can't read Apple Health or Google's health data directly; that needs a native app. So build the **input side** and demo it with synthetic data:
1. Consent group `devices` (opt-in, withdrawable, deletes stored signals).
2. `POST /users/{id}/signals` `{source: "wearable"|"screening"|"manual"|"file", date, steps?, sleep_minutes?, screening?: {blood_pressure_flag?, glucose_flag?}}`, plus CSV import.
3. Engine: steps or sleep above the action's threshold auto-complete that action; screening flags feed the plan builder like the health check ("your screening suggests a gentler start; check with your doctor").
4. `/demo/seed` and `advance` generate synthetic device data, labelled synthetic.
5. README/HANDOFF framing: "Rebound is an engine with an API that existing patient apps, wearables and screening programs plug into; our app is a reference front end."

---

## Later (after A–E and the chosen-data part)
- **Nearby healthy options** via OpenStreetMap (free): greengrocers, supermarkets, parks; opt-in, location never stored; offered for `no_healthy_food_nearby`. No claims about how healthy any shop is.
- Support buddy (family or colleague sees only good news); channel switch to chat after silent days; live weather for heat.

## Order
A → A2 → B → C → D → E. Then, only if time allows, the chosen-data part and the later items.

## Done when
- A–E implemented with tests; all suites pass.
- Two demo personas with different health contexts show visibly different plans, reasons and steps.
- Docs, `openapi.json` and the HANDOFF "Frontend changes" section are updated.
- A short paragraph for the pitch mapping each part to the brief's requirements.
