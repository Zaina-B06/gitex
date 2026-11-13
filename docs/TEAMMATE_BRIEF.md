# Start here

## What is this?
**Rebound** is our hackathon app (Future Health Challenge, due **Fri 20 Nov**).
It helps people build healthy habits. Unlike streak apps, a bad week never resets you to zero: the app makes things easier and helps you get back on track.

## What we did so far

**1. Built the "brain" (`engine/`)**
- Every day the user gets 2 small tasks: one movement task, one sleep task.
- A habit score goes up when you do them, and fades slowly (never to zero) when you don't.
- If you start slipping, the tasks get easier and the app asks "what got in the way?"
- When you come back, tasks get harder again, slowly (after 4 done in a row).
- Safety: a health check at sign-up limits how hard tasks can be. It adjusts for Ramadan, heat, pregnancy and wheelchair users. If someone types something worrying (chest pain, self-harm), coaching stops and help numbers are shown.

**2. Tested it with 300 fake people (`sim/`)**
- We had no real users, so we simulated 300 people for 90 days, in 7 situations (normal, Ramadan, heat, people quitting fast…).
- We compared Rebound with a normal streak app, and with a "kind" app that never punishes misses.
- Results: Rebound **beats the streak app in every situation** (more people come back after a bad week, more stay active, fewer quit). Against the kind app it's **about equal**, but people do **more exercise**.
- We were careful to be honest: we wrote down each test *before* running it, and we report where Rebound doesn't help.

**3. Tried some machine learning**
- Built a model that predicts who will slip next week. It's accurate (it catches 93% of slips, vs 62% for the old rule).
- But acting on it inside the app didn't help (most people who slip just don't open the app), so it's **switched off**.

**4. Built the server (`api/`)**
- Sign-up, today's tasks, mark done, check-ins, settings, export/delete my data.
- Login tokens, privacy (health data stored separately), and a demo mode that skips days so judges can watch someone slip and recover in 2 minutes.
- A results dashboard and an employer view (shows only group totals, never individuals).

**Everything above is done and tested.** All decisions are written in `docs/ASSUMPTIONS.md`.

## What's left
- **Frontend**: follow `docs/tasks/TASK_04_frontend.md`
- **LLM layer** (optional): follow `docs/tasks/TASK_01_C_llm_safety_docs.md`

## Setup (once)
```bash
git clone https://github.com/Zaina-B06/gitex.git
cd gitex
python -m venv .venv
.venv\Scripts\Activate.ps1          # Mac: source .venv/bin/activate
pip install -e "engine[dev,risk]" -e "sim[dev]" -e "api[dev]"
```
Copy `.env.example` to `.env`, then add your own keys:
```bash
python -c "import secrets; print('DEMO_KEY=' + secrets.token_urlsafe(24)); print('ORG_KEY=' + secrets.token_urlsafe(24))"
```
Paste the two lines it prints into `.env`, and add `DEMO_MODE=true`.

## Run it
```bash
uvicorn api.main:app --reload
```
Open **http://127.0.0.1:8000/docs** to see and try every endpoint.

## Start working
1. Make your own branch: `git checkout -b frontend`
2. Give your coding agent this:
   > Read CLAUDE.md, docs/TEAMMATE_BRIEF.md and docs/HANDOFF.md. Then read my task file fully and ask me questions before writing code. Give me commands to run; don't run them yourself. No "Co-Authored-By" lines in commits.

## Rules
- Don't edit `engine/` or `api/`: ask Zaina.
- Never commit `.env`.
- Don't overclaim results. Say "in simulation", never "clinically proven".

Stuck? Ask Zaina.
