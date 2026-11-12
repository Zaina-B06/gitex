# Task 01-B — Frontend shell + onboarding against mock API (lean, Mon 16)

Read `AGENTS.md` first, especially §4 (onboarding fields) and §7 (API contract). The backend isn't ready yet, so build against a **mock API layer** that returns realistic fake responses with the same shapes.

## Build

1. **`web/`**: React + Vite + TypeScript + Tailwind, mobile-first (designed at 390px wide, still usable on desktop). React Router.
2. **i18n**: English + Arabic from day one (`react-i18next` or similar). Arabic switches the layout to RTL (`dir="rtl"`). Keep all strings in locale files; no hard-coded text.
3. **API client** `src/api/`: typed functions for every endpoint in `AGENTS.md` §7, plus `src/api/mock.ts` used when `VITE_USE_MOCK=true`. TypeScript types mirror the Pydantic models.
4. **Onboarding flow**: multi-step, one group per screen, progress dots, back button:
   1. Language
   2. Goals (movement, sleep; nutrition/smoking shown as "coming soon", disabled)
   3. Basics: age, sex (incl. "prefer not to say"), schedule type, wake/sleep time, work hours (rotating pattern option for shift workers)
   4. Body (optional): height, weight, with the line "Used only to set a safe starting level. Never shown as a target." and a clear Skip.
   5. Health check: the 7 yes/no questions (paraphrased, §4.3), then pregnancy (only if sex = female) and mobility. If any answer is "yes", show a gentle note before continuing.
   6. Activity & sleep baseline
   7. Past experience (optional): tried before?, what helped (multi), what made you stop (multi, barrier taxonomy)
   8. Preferences: indoor/outdoor, alone/with others, home / women-only spaces / any, Ramadan fasting, notification window + quiet hours, channel, accessibility toggles
   9. Data & consent summary: what we collect and why, a toggle per group, "Start"
   Every optional screen has Skip. Every sensitive screen has a one-line "why we ask".
5. **Today screen (static version)**: one action card (title, duration, time window), buttons **Done / Did a smaller version / Skip today**, "Why this?" link, and a **habit-strength ring** (a 0–100% ring, no streak number anywhere).
6. **Why-this sheet**: bottom sheet showing technique name + code, rationale, limits, "turn off this type of suggestion".
7. **Check-in screen**: "Rough few days? What got in the way?" Barrier buttons (§6.2) with icons + optional text box + a voice-note button placeholder. Copy is warm and never blaming.
8. **Design**: calm, high-contrast, large tap targets (≥ 44px), accessible labels, supports large-text mode. No confetti, no streak flames, no guilt copy.

## Done when
- A user can go through all onboarding steps in EN and AR (RTL correct), reach Today, mark Done, open Why-this, and open the check-in, all on mock data.
- Switching `VITE_USE_MOCK=false` points to `http://localhost:8000` with no code changes.
- No hard-coded strings; Lighthouse accessibility score ≥ 90 on the onboarding pages.

**Give me the commands to run** (install, dev server); don't run them and summarise.
