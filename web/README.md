# web — Rebound app (React + Vite + Tailwind)

Mobile-first app over the API in `api/`. Every screen calls the real backend; there is no mock mode.

## Run locally
1. Backend, from the repo root: `python -m uvicorn api.main:app --reload` (port 8000).
2. Frontend, from `web/`: `npm install` once, then `npm run dev` → http://localhost:5173.
   Vite proxies `/api/*` to `http://127.0.0.1:8000`, so no CORS setup is needed in dev.

`.env.example` → `.env.local`: `VITE_API_URL` (blank in dev; the deployed API URL in production) and
`VITE_DEMO_MODE=true` for the demo bar (jump to any screen, start over as a new user).

After the API changes, regenerate types: `npm run types` (reads `../api/openapi.json`).

## Screens
- **Welcome:** language, then "Start my plan", "Sign in" (`POST /auth/login`) or "Try a demo person"
  (`POST /demo/seed`, needs the demo key).
- **Sign-up (4–5 steps, empty ones dropped):** about you (optional "your week in your own words" →
  `POST /content/onboarding/suggest` pre-fills answers to confirm; optional name, saved as
  `preferences.display_name`; optional height/weight, never shown), goals and conditions, health check (always
  in full, never pre-filled), activity/sleep baseline (only for movement or sleep), what helps (reading level,
  household, fasting, and the follow-up questions whose `show_if` rules match) → `POST /users` → your plan →
  "Save your progress" (optional username + password).
- **Phone frame:** 390 × min(844, screen − 32) px, centred; full screen under 500px wide; no scrollbars inside.
- **Tabs:** Today (steps, Done / Did less / Skip, "Why this?"), My plan (a card per goal: level, good days to the
  next level, last change and today's note; the weekly recap; calendar; plan reasons), Meals (`GET /recipes`),
  Community, Settings in groups (Profile · Health · Routine · Family · Messages · Privacy & data · Help).
- **Demo bar** (`VITE_DEMO_MODE=true`): switch person, good day, mixed day, skip 4 days, Ramadan, heat
  (`POST /demo/users/{id}/advance`), jump to any screen.
- **Check-in:** buttons or free text → `POST /checkin`; also as a chat (`/chat`). Red flags go to the Care screen
  (998, 800 SAKINA). "Need help?" is on Today and My plan.

Choices and their reasons: `docs/ASSUMPTIONS.md`, "Frontend (web/)".
