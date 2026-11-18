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
- **Sign-up (5 steps):** about you (optional first name, kept on the device only; optional height/weight, never
  shown), goals and conditions, health check (text from `GET /content/onboarding`, adapts to sex and conditions),
  activity/sleep baseline (only for the goals picked), what helps (reading level, household, fasting) →
  `POST /users` → your plan.
- **Tabs:** Today (steps, Done / Did less / Skip, "Why this?"), My plan (calendar of past days, thought for today,
  plan reasons), Meals (`GET /recipes`), Community, Settings (profile, edit my answers, progress report as PDF or
  CSV, export, delete).
- **Check-in:** buttons or free text → `POST /checkin`; also as a chat (`/chat`). Red flags go to the Care screen
  (998, 800 SAKINA). "Need help?" is on Today and My plan.

Choices and their reasons: `docs/ASSUMPTIONS.md`, "Frontend (web/)".
