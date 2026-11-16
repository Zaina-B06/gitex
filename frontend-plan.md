# Rebound Frontend Plan — Team Checklist Integration

## 1. Architectural Overview & Design Language
- **Design Style**: "Soft Dunes, Quiet Resilience"
  - Typography: **Fraunces** strictly reserved for titles, big numbers, and greetings (`font-serif`); **Instrument Sans** and **Readex Pro** for UI prose, controls, and Arabic RTL.
  - Animations: Spring-based transitions (`framer-motion`), soft squish and ring glows on action completion.
  - Strict Prohibitions: No streaks, no flame icons, no confetti, no sand particle animations, no comeback counters, no day-count tiles, no "N in a row" copy.
  - Privacy & Storage: Zero local persistence of sensitive health screening answers or check-in free text. All caches and tokens cleared on sign-out and account deletion.

## 2. API & Schema Discrepancies (Items to Confirm with Zaina)
To ensure the UI is immediately functional and won't crash when running against the current `api/openapi.json`, the frontend implements **defensive fallbacks and mock adapters** for all unmerged backend endpoints:

| Feature Area | Checklist Item | Current `api/openapi.json` State | Frontend Adaptation / Fallback Strategy |
|---|---|---|---|
| **Onboarding Content** | `GET /content/onboarding` | Endpoint does not exist | Try fetching `/content/onboarding`; if 404/network fails, load built-in default questions, "why we ask" copy, and reading level previews |
| **New Goals** | `nutrition`, `recovery`, `smoking` in Goals | `Behaviour` enum is `["movement", "sleep"]` | Allow user selection in UI; map UI selections to engine's supported goals and store auxiliary goals in preferences until backend enum expands |
| **Managing Chips** | "Conditions" consent and managed conditions chips | `ConsentGroup` lacks `"conditions"` | Store in profile state / preferences; omit unsupported key on API consent calls or handle 422 safely |
| **Preferences** | `reading_level`, `household`, `caregiver`, `family_fasting`, `iftar_time`, `read_aloud`, `encouragement` | Missing from `Preferences` schema (`additionalProperties: false`) | Transmit via `preferences` in `PATCH /settings` (which allows `additionalProperties: true`) and local UI state |
| **Plan Summary** | `plan_summary` in `OnboardOut` & `GET /users/{id}/plan` | Neither exists | Synthesize plan summary reasons dynamically based on profile (recovering, multiple goals, Ramadan) and provide "See why" bottom sheet |
| **Action Icons** | `icon` string field on `Action` / `ScheduledAction` | Field does not exist on `Action` | Map action id, BCT code, or behavior to icon set (`family`, `water`, `fruit`, `plate`, `no_smoking`, `rest`, `walk`, `sleep`) with neutral fallback icon |
| **Meal Recipes** | `today.recipes` | Field does not exist on `TodayOut` | Provide contextual recipe sheet for nutrition actions |
| **Ramadan Buttons** | `PATCH /settings {"ramadan": "started_today" \| "ended_today"}` | Context accepts boolean `{"ramadan": true \| false}` | Send `{ "context": { "ramadan": true } }` or `{ "context": { "ramadan": false } }`; hide button cleanly on 409 |
| **Barriers** | `stressed`, `no_healthy_food`, `craving`, `people_smoking` | Not in `Barrier` enum | Send nearest schema barrier (e.g. `energy_fatigue`, `environment`, `other`) and attach detailed selection to free-text payload until schema is updated |
| **Encouragement** | `encouragement: { moment, message }` on `/events` and `/today` | Field does not exist on `TodayOut` | Implement soft non-blocking encouragement toast component with daily throttle and settings toggle |
| **Community Events** | `GET /users/{id}/community/events` | Endpoint does not exist | Provide community tab with mock events dataset featuring Abu Dhabi/Al Ain, source links, check dates, and `example: true` tags |
| **Demo Persona Descriptors** | Descriptors for Ahmed, Sara, Mariam | `SeedPersona` has only `name, user_id, token` | Decorate seed personas in demo panel with rich descriptors highlighting differences in family, fasting, and caregiving roles |

---

## 3. Implementation Order & Component Matrix

### Phase 1: Removals & Core Cleansing
- Strip streak counters, flame icons, sand particles, confetti, comeback counts, and "N in a row" phrases.
- Update `en.json` and `ar.json` with all missing localization keys.
- Add cache clearance on logout/delete.

### Phase 2: Today Screen Modernization
- Support up to 3 action cards in API order.
- Implement icon lookup table: `family`, `water`, `fruit`, `plate`, `no_smoking`, `rest`, `walk`, `sleep`, plus neutral fallback.
- Recipe bottom sheet for meal actions with required medical disclaimer.
- Context banners (`Ramadan`, `Eid`, `Heat`) and interactive moon sighting Ramadan start/end buttons.
- In-browser `speechSynthesis` read-aloud button on each card (`ar-AE` / `en-US`), auto-canceling on navigation.
- Action actions: Done (squish + ring glow), Did a smaller version (`POST /events` with `type: "partial"`), Skip.

### Phase 3: Demo Panel & Personas
- `POST /demo/seed` with `X-Demo-Key` overlay (sessionStorage only).
- Persona switcher showing Ahmed (lives with children, fasting), Sara, Mariam (caregiver) with distinct descriptors.
- Fast-forward buttons: skip a day (good), skip a day (mixed), skip 4 days (lapse), Ramadan demo, heat-wave demo.
- Guided demo auto-play support.

### Phase 4: Check-in & Emergency Care Screen
- Daily limit enforcement (friendly styling on 409).
- Modern barrier matrix: 10 standard buttons + 2 smoking buttons (conditional on smoking status).
- Lighter plan card preview on check-in completion, replacing today's cards and re-fetching `/today`.
- Red-flag interceptor: Full-screen calm Care Screen with tap-to-call buttons for **Call 998** (UAE Emergency) and **Call 800 SAKINA** (800 725462, 24/7 mental health).
- Persistent "I need help" button across all screens.

### Phase 5: Sign-up Flow Redesign (Max 5 Screens)
- Screen 1: Language + 4 Goals (`movement`, `sleep`, `nutrition`, `recovery`, conditional `smoking`).
- Screen 2: "Anything you're managing?" chips (diabetes, high BP, joint pain, stress, illness/injury) with plain language consent.
- Screen 3: Health screening questions loaded dynamically from `/content/onboarding` (with built-in fallback).
- Screen 4: Reading level ("standard" vs "simple") with live sample cards; Baseline and reason.
- Screen 5: Family context (household, caregiver, family fasting), shift worker schedule (weekly times + iftar time), and consents.

### Phase 6: Plan Card ("Your plan, built for you")
- Summary lines (max 3), `all_reasons` in bottom sheet, and rotation note.
- Rendered on post-onboarding transition and Today screen.

### Phase 7: Encouragement & Community Page
- Encouragement toast pop-up (max 1/day, non-blocking, dismissible).
- New nav tab `Community` with filter chips (city, behaviour, household), source links, verified dates, and clear example tags.

### Phase 8: Settings, Progress & Dashboards
- Settings screen: Conditions editor (rebuilds plan), shifts, iftar time, language, reading level, read aloud, family settings, encouragement toggle, consent withdrawal (friendly 409 handling), "I'm OK now", JSON data export, and type-to-confirm account deletion.
- Progress: Habit-strength rings, 21-day trend chart, plain weekly summary without counts.
- Results: Simulator outcomes with plain statements, "in simulation" footnote, and visible "Where Rebound doesn't help" section.
- Employer: Aggregate metrics, privacy guarantees, friendly message on 403.
