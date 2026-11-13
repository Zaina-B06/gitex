# Model card

## Lapse-risk model (Task 02b)

**Status:** Drop A, training and evaluation only. Results come from `python -m sim.train_risk --run sim/out/risk_001`
(`sim/out/risk_001/risk/summary.md` and `metrics_risk.json`) and are copied into this section after review. The
engine hook and simulator arm D are Drop B, pre-registered in `docs/ASSUMPTIONS.md` ("Arm D").

### Intended use
Predict, for a user who isn't lapsed today, the probability that the engine's engagement state becomes `lapsed`
within the next 7 days, so Rebound can offer a lighter option and a gentle check-in **before** the slip. It is a
prompt to make things easier, never a judgement: it must not be used to rank, score or report on individuals, and
employers never see it (AGENTS.md §2.6).

### Model
- **Candidates:** logistic regression (standardised features; interpretable) and gradient boosting (scikit-learn
  `HistGradientBoostingClassifier`, 200 iterations, `random_state=0`). The one with the higher validation AUROC is
  saved; both are reported.
- **Alert threshold:** the risk score that flags 15% of validation days (`RISK_ALERT_RATE`), frozen into the model
  file.
- **Explanations:** for each alert, the top 3 features pushing risk up. Logistic: exact contributions (standardised
  coefficient × standardised value). Boosting: permutation importance × distance from average (an approximation).
  These feed messages like "We noticed fewer completions this week and a schedule change".
- **File:** `models/lapse_risk.joblib` (not committed). Loading needs `pip install -e "engine[risk]"`. The engine runs
  without it.

### Training data
- **Synthetic only:** arm C (Rebound full, shipped engine) in the baseline scenario, 300 personas × 90 days, seeds
  21–30. These seeds are never used for evaluation (1–10), the step-up test (11–20) or calibration (101).
- **Split by seed, so by persona:** train 21–26, validation 27–28 (model choice, threshold), test 29–30 (every
  reported number). No persona appears in two splits (tested).
- **Label:** the engine's state is `lapsed` on any of the next 7 days. Rows where the person is already lapsed, has
  churned, or has no full 7-day window left are excluded.

### Features (engine-visible only)
Computed by `rebound_engine.risk.compute_features(profile, state, events, day)`, from what the engine itself holds.
The same function is used in training and in the app. It never receives hidden traits, unlabelled shocks or
simulator ground truth (tested). Over the last 14 days:
- **Completion:** rate over 3 / 7 / 14 days and the trend, consecutive misses, share of partials, share of
  no-responses, actions shown in 7 days.
- **Plan:** current tier per behaviour, and the gap to the highest tier reached.
- **Habit strength:** H per behaviour and its 7-day change.
- **Check-ins:** days since the last check-in and its barrier, whether a check-in is due.
- **Context:** Ramadan, heat and illness flags; schedule type; whether any screening question was "yes"; current
  engagement state; weekend vs weekday completion gap.

Travel isn't a feature: the engine never gets a travel flag, only check-in answers. The weekend gap is included for
real data but is uninformative here: the simulator has no weekly rhythm.

### Evaluation (test seeds 29–30)
Reported against two baselines:
- **Drifting rule:** the engine's own `drifting` state as the alert.
- **Completion heuristic:** last-7-day completion rate below a threshold set on validation at the same 15% alert rate.

Measures, with 95% persona-bootstrap intervals where noted:
- AUROC (CI) and PR-AUC; Brier score for the two models; calibration curve.
- Alert rate, and recall at the alert rate (CI).
- Lapses caught (an alert in the 7 days before the lapse), and the median warning time (days from the first alert to
  the lapse), for the model and each baseline.
- AUROC and recall by `schedule_type`, `language` and `mobility_limitation`.

*Results: to be filled in from `sim/out/risk_001/risk/summary.md` after the Drop A run.*

### Known limitations
- **Simulated data only.** It shows the pipeline and the engine hook work. It says nothing about real-world accuracy.
  It must be retrained, and re-validated, on pilot data before any real use.
- **Trained on arm C behaviour.** Once the hook changes what people are shown (arm D), the data the model sees shifts
  away from its training data. In a pilot it would need retraining on data collected with the hook on, and
  monitoring for drift.
- **Partly circular target.** The label is the engine's own lapse rule, and the drifting state is one of the features.
  The model predicts the engine's rule a week early; it isn't an independent measure of disengagement.
- **Small, synthetic segments.** Mobility-aid and some language groups are small, so their fairness numbers are noisy.
- The boosting explanations are approximate (see Model).

### Retraining plan (pilot)
1. Log the same engine-visible features for every user-day, with consent.
2. After 8–12 weeks, retrain on pilot data, split by user.
3. Re-check calibration, fairness by segment, and the alert threshold against the message cap.
4. Compare against the drifting rule and the completion heuristic again: keep the model only if it beats both.
