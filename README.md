# Rebound

Adaptive behaviour-change engine for the Future Health Digital Innovation Challenge 2026
("Sustaining Healthy Behaviors"). One small movement or sleep action per day, a habit-strength
score that decays instead of resetting, drift detection, blame-free check-ins, and safety rules
that run before any personalisation. See `AGENTS.md` for the full spec and `docs/tasks/` for the build plan.

## Layout

| Folder | What |
|---|---|
| `engine/` | Pure Python engine package (`rebound_engine`) + action library + tests |
| `sim/` | Synthetic population simulator (Task 02) |
| `api/` | FastAPI wrapper + SQLite event log (Task 03) |
| `llm/` | Barrier classifier + message templates (Task 03) |
| `web/` | React + Vite + Tailwind app (Task 01-B) |
| `docs/` | Assumptions, data sources, task files |

## Setup (engine)

Needs Python 3.11+. From the repo root:

```bash
python -m venv .venv
# Windows (PowerShell):  .venv\Scripts\Activate.ps1
# macOS/Linux:           source .venv/bin/activate
pip install -e "engine[dev]"
pip install -e "sim[dev]"                     # simulator: numpy, pandas, pyarrow, matplotlib
```

## Run

```bash
pytest engine/tests                          # engine tests
pytest sim/tests                             # simulator tests
ruff check engine sim                        # lint
python -m rebound_engine.demo --days 30 --seed 1   # 30-day single-user demo

# Simulation (from the repo root): 300 personas x 90 days x 10 seeds, arms A/B/C + sensitivity arm A0
python -m sim.run --n 300 --days 90 --seeds 1-10 --arms A B C --scenario baseline --out sim/out/run_001 --sensitivity
python -m sim.report --run sim/out/run_001     # charts in sim/out/run_001/charts + summary.md
```

The demo prints one row per day: action, outcome, habit strength (H) per behaviour and engagement
state. Days 11–14 are a motivation dip and days 15–18 a forced lapse, so you should see H dip without
resetting, and the state move through drifting, lapsed and recovering.
