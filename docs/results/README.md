# Results snapshot

Small copies of reviewed simulator outputs (`sim/out/` itself isn't committed). How each was produced, and why, is in
`docs/ASSUMPTIONS.md`; the commands to regenerate them are in `docs/HANDOFF.md`.

| Folder | What | Engine | Status |
|---|---|---|---|
| `run_007/` | All 7 scenarios, seeds 1–10, arms A, A0, B, C | step-up 4 (shipped) | **Report these numbers.** |
| `run_006/` | Pre-registered step-up test: C4 (step-up 4) vs C (step-up 3), fresh seeds 11–20, all scenarios | both | Evidence for the 3 → 4 decision ("keep 4"). |
| `run_005/` | All 7 scenarios, seeds 1–10, arms A, A0, B, C | step-up 3 | Superseded by run_007; kept as history. |
| `sweep_002/` | Full sensitivity sweep + tornado chart, baseline, seeds 1–5 | step-up 3 | Current for sensitivity: what the C vs A / A0 gaps depend on. |
| `risk_001/` | Lapse-risk model (Task 02b Drop A): trained on arm C seeds 21–26, tested on 29–30; summary, ROC, calibration, feature importance | step-up 4 | See `docs/MODEL_CARD.md`. |
| `sweep_003/` | Step-up threshold 2 / 3 / 4 / 5 with activity gaps, seeds 1–5 | varies | Motivated the 3 → 4 test. |

Each `summary.md` has every metric with 95% intervals, the pre-registered headline, equity gaps, burden, and a
"Where Rebound doesn't help" section. `scenarios.md` puts the pre-registered headline for all scenarios in one table.
