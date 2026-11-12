# Task 02b — Lapse-risk predictor (after Task 02 works)

Read `AGENTS.md` first. This adds the "predict" half of the challenge theme ("To Sense is to Predict"): instead of only reacting once a user is drifting, the engine **predicts who is likely to lapse in the next 7 days** and adapts early.

## Honesty rules (put these in the docs too)
- The model is trained on **simulated** history only. It demonstrates the pipeline and the engine hook, not real-world accuracy. It would be retrained on pilot data.
- Train and test on **different personas** (split by persona and by seed), never by day within a persona, or the results will leak.
- Report it next to a **rules-only baseline** (the current drifting rule) so its added value is clear.

## Build (`engine/rebound_engine/risk/` for inference, `sim/train_risk.py` for training)

1. **Features** (computed from engine-visible events only; never hidden traits or unlabelled shocks), over the last 14 days:
   completion rate (last 3 / 7 / 14 days) and its trend, consecutive misses, partial share, response latency proxy (no_response share), current tier vs. max tier reached, H per behaviour and its 7-day slope, days since last check-in and the last barrier, context flags (ramadan, heat, travel, illness), schedule_type, has_screening_flag, day-of-week pattern (weekend dip).
2. **Label:** lapsed state reached within the next 7 days (1/0). Exclude days where the persona is already lapsed or churned.
3. **Models:** logistic regression (interpretable baseline) and gradient boosting (scikit-learn `HistGradientBoostingClassifier`; LightGBM is fine if installed). Pick by validation AUROC; keep both results.
4. **Evaluation** on held-out personas/seeds: AUROC, PR-AUC, calibration curve, Brier score, and recall at a fixed alert rate (e.g. the top 15% of risk scores). Break down by segment (`schedule_type`, `language`, `mobility_limitation`) for fairness. Include the rules-only baseline (drifting flag as the predictor).
5. **Explainability:** top features (coefficients for LR; permutation importance for GB). For each alert, store the top 3 contributing features so the app can show "We noticed fewer completions this week and a schedule change".
6. **Engine hook:** `Engine(risk_model=...)`. If predicted risk > threshold (config) and the state is still `active`: pre-emptively offer the next action one tier smaller **as an option** ("Busy week ahead? Here's a lighter version"), and send a gentle check-in at most once per 7 days. Never punitive, never more messages than the burden cap.
7. **Simulator arm D:** Rebound full + risk model. Compare with C on persistence, lapse rate, recovery and burden across all scenarios from Task 02, with intervals.
8. **Model card:** add a section to `docs/MODEL_CARD.md` covering intended use, training data (synthetic), metrics, segment breakdown, known limitations and the retraining plan.

## Tests
- No feature uses hidden traits or shock information (assert the feature function only receives engine-visible data).
- Persona-level split: no persona appears in both train and test.
- The model file loads and predicts deterministically.
- The engine hook respects the safety layer and the message cap.

## Done when
- `python -m sim.train_risk --run sim/out/run_001` trains, evaluates and saves `models/lapse_risk.joblib` plus `metrics_risk.json` and charts (ROC, calibration, feature importance).
- Arm D results appear in the report next to A, B and C.
- The model card section is written.

**Give me the commands to run**; don't run them and summarise. Don't commit until I've reviewed the results.
