# Model card

## Lapse-risk model (Task 02b)

**Status:** trained and evaluated (Drop A, `python -m sim.train_risk --run sim/out/risk_001`). The engine hook was
tested as pre-registered (Drop B, run_008) and **is disabled by default**: the shipped engine runs without a risk
model. The model stays as a tested component; see "Engine hook: result" below.

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
- **Earlier simulator world:** trained when personas could answer check-ins on closed-app days. The reported world
  now allows answers only on open days (`docs/ASSUMPTIONS.md`, "Check-ins answered only on open days"); the model is
  not retrained, so its numbers describe the earlier world. The hook is off in the app either way.
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

#### Results (`sim/out/risk_001`; test seeds 29–30, 36,207 test person-days; copy in `docs/results/risk_001/`)

**Headline:** the model flags **93% of upcoming lapses at least once in the prior week, vs 62% for the current
drifting rule, at a similar alert rate** (15.5% vs 13.7% of days). The median warning is **3 days**, no earlier than
the completion heuristic (4 days).

Logistic regression was chosen (validation AUROC 0.776 vs 0.768 for gradient boosting).

| Predictor | AUROC [95% CI] | PR-AUC | Brier | Alert rate | Recall at alert rate [95% CI] | Precision | Lapses caught (prior 7 days) | Median warning |
|---|---|---|---|---|---|---|---|---|
| **Logistic (chosen)** | **0.769 [0.756, 0.782]** | 0.524 | 0.149 | 15.5% | **0.377 [0.359, 0.395]** | 0.579 | **1,396 / 1,495 (93%)** | 3 days |
| Gradient boosting | 0.761 [0.748, 0.772] | 0.513 | 0.151 | 15.2% | 0.371 [0.353, 0.386] | 0.582 | 1,439 / 1,495 (96%) | 3 days |
| Drifting rule (current engine) | 0.596 [0.588, 0.605] | 0.311 | n/a | 13.7% | 0.284 [0.269, 0.301] | 0.493 | 932 / 1,495 (62%) | 3 days |
| Completion heuristic (7-day rate) | 0.726 [0.709, 0.741] | 0.422 | n/a | 17.1% | 0.350 [0.330, 0.369] | 0.489 | 1,068 / 1,495 (71%) | 4 days |

- **Better ranking than both baselines:** model minus heuristic AUROC is +0.035 to +0.052 (95% persona bootstrap).
  Recall at the alert rate is modestly higher (0.377 vs 0.350 for the heuristic, 0.284 for the drifting rule).
- **Recall vs "lapses caught" are two different questions.** Recall is per day: of all days followed by a lapse,
  what share were flagged (about 38%). Lapses caught is per lapse: was there *any* alert in the week before (93%).
  Since an alert prompts one lighter option and at most one check-in a week, the per-lapse number is the one that
  matters for the app.
- **Warning time:** 3 days for the model, the same as the drifting rule and a day *later* than the heuristic. The
  model catches more lapses but doesn't catch them earlier.
- **Calibration:** Brier 0.149; see `calibration.png`.

**What drives it** (standardised logistic coefficients): share of unanswered actions in the last 2 weeks (+0.74),
habit strength (movement −0.39, sleep −0.28), consecutive misses (+0.35), recent drop in completions, and the last
check-in barrier (tired, illness/pain, time, family). The 14-day completion rate has a *positive* coefficient,
which is collinearity with the other completion features, not a real effect. Explanations therefore only show
features in their intuitive direction, as plain phrases (e.g. "fewer replies in the last 2 weeks", "a few missed
days in a row", "you said you've been tired"); see `REASONS` in `engine/rebound_engine/risk/features.py`. The risk
score itself is unchanged by this.

**Fairness (test seeds):**

| Segment | AUROC range (model) | Recall range (model) | Notes |
|---|---|---|---|
| schedule_type | 0.755–0.792 | 0.332–0.413 | lowest recall: outdoor/manual; highest: students |
| language | 0.762–0.776 | 0.364–0.387 | even across Arabic, English and South Asian |
| mobility_limitation | 0.758–0.790 | **0.250** (mobility aid) – 0.398 | **weaker recall for mobility-aid users** |

Mobility-aid users have the weakest recall (0.250 vs 0.379 for no limitation), though AUROC is similar (0.790). It's
a small group (988 test days, 236 lapse-ahead days), so the number is noisy, but it should be watched in a pilot.
The model beats the completion heuristic in every segment.

### Engine hook: result (run_008, pre-registered as "Arm D" in `docs/ASSUMPTIONS.md`)
With the model plugged in (`Engine(risk_model=...)`), an alert offers each action one tier lighter and, at most
once a week, a gentle check-in. Against Rebound without it (D vs C, seeds 1–10, all 7 scenarios):
- **Lapse rate:** baseline +0.2 pts [−0.1, +0.5], not lower, so the ship rule's first condition fails.
- **Engagement:** ≈ 0 everywhere; nothing worse.
- **Burden:** +0.1 messages per persona-week, within the +0.5 cap.

**Decision: keep the hook out of the app.** `Engine()` without a model is the shipped default.

**Why it didn't help:** in the baseline run, 46% of alert days with a lighter option were days the person didn't open
the app, and on 77% of risk-check-in days every action was already the smallest (tier 1), so there was nothing lighter
to offer. Only about a quarter of alerts put an option in front of the user. A good prediction attached to an in-app
intervention can't reach people who have stopped opening the app.

**Pilot recommendation:** use the risk score to trigger *out-of-app* support (e.g. a WhatsApp-style nudge, a buddy
prompt or a voice note), within the message cap and quiet hours, and test it pre-registered with a micro-randomised
design.

### Known limitations
- **Simulated data only.** It shows the pipeline and the engine hook work. It says nothing about real-world accuracy.
  It must be retrained, and re-validated, on pilot data before any real use.
- **Trained on arm C behaviour.** Once the hook changes what people are shown (arm D), the data the model sees shifts
  away from its training data. In a pilot it would need retraining on data collected with the hook on, and
  monitoring for drift.
- **It predicts the engine's own lapse rule.** The label is the engine's `lapsed` state, and the drifting state is one
  of the features. The model predicts the engine's rule up to a week early; it isn't an independent measure of
  disengagement, and its accuracy is only as meaningful as that rule.
- **No earlier warning than a simple heuristic.** It catches more lapses but with a median 3-day warning, a day
  less than the 7-day completion heuristic.
- **Weaker recall for mobility-aid users** (0.25 vs 0.38) in a small group; noisy, to be re-checked on real data.
- **Prediction isn't impact.** It ranks risk well, but the in-app hook built on it didn't reduce lapses (run_008).
  Its value depends on an intervention that reaches people outside the app.
- **Small, synthetic segments.** Mobility-aid and some language groups are small, so their fairness numbers are noisy.
- The boosting explanations are approximate (see Model).

### Retraining plan (pilot)
1. Log the same engine-visible features for every user-day, with consent.
2. After 8–12 weeks, retrain on pilot data, split by user.
3. Re-check calibration, fairness by segment, and the alert threshold against the message cap.
4. Compare against the drifting rule and the completion heuristic again: keep the model only if it beats both.
