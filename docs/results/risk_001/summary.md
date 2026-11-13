## Lapse-risk model (Task 02b, Drop A)

Trained on arm C, baseline scenario, seeds [21, 22, 23, 24, 25, 26]; threshold set on validation seeds [27, 28]; all numbers below are on test seeds [29, 30] (different personas). Simulated data only: this shows the pipeline works, not real-world accuracy.

Chosen by validation AUROC: **logistic** (validation AUROC: logistic 0.776, gradient_boosting 0.768).

| Predictor | AUROC [95% CI] | PR-AUC | Brier | Alert rate | Recall [95% CI] | Precision | Lapses caught | Median warning (days) |
|---|---|---|---|---|---|---|---|---|
| logistic | 0.769 [0.756, 0.782] | 0.524 | 0.149 | 15.5% | 0.377 [0.359, 0.395] | 0.579 | 1396/1495 (93%) | 3.0 |
| gradient_boosting | 0.761 [0.748, 0.772] | 0.513 | 0.151 | 15.2% | 0.371 [0.353, 0.386] | 0.582 | 1439/1495 (96%) | 3.0 |
| drifting_rule | 0.596 [0.588, 0.605] | 0.311 | n/a | 13.7% | 0.284 [0.269, 0.301] | 0.493 | 932/1495 (62%) | 3.0 |
| completion_heuristic | 0.726 [0.709, 0.741] | 0.422 | n/a | 17.1% | 0.350 [0.330, 0.369] | 0.489 | 1068/1495 (71%) | 4.0 |

Chosen model minus completion heuristic, AUROC: 95% CI [+0.035, +0.052] (persona bootstrap).

Alert rate is the share of test days flagged. Lapses caught: an alert in the 7 days before the engine entered `lapsed`. Warning: days from the first such alert to the lapse.

### Fairness (test seeds)

| Segment | Value | Rows | Lapses ahead | Model AUROC | Model recall | Heuristic AUROC | Heuristic recall |
|---|---|---|---|---|---|---|---|
| schedule_type | home_caregiver | 5512 | 1276 | 0.766 | 0.360 | 0.717 | 0.312 |
| schedule_type | office | 12475 | 3132 | 0.755 | 0.378 | 0.724 | 0.362 |
| schedule_type | outdoor_manual | 6139 | 1268 | 0.777 | 0.332 | 0.735 | 0.320 |
| schedule_type | shift | 4782 | 1198 | 0.757 | 0.390 | 0.704 | 0.321 |
| schedule_type | student | 7299 | 1762 | 0.792 | 0.413 | 0.742 | 0.397 |
| language | ar | 13597 | 3241 | 0.767 | 0.387 | 0.730 | 0.355 |
| language | en | 13075 | 2927 | 0.776 | 0.364 | 0.726 | 0.336 |
| language | south_asian | 9535 | 2468 | 0.762 | 0.381 | 0.720 | 0.360 |
| mobility_limitation | mobility_aid | 988 | 236 | 0.790 | 0.250 | 0.741 | 0.199 |
| mobility_limitation | none | 32322 | 7651 | 0.770 | 0.379 | 0.725 | 0.353 |
| mobility_limitation | some | 2897 | 749 | 0.758 | 0.398 | 0.736 | 0.363 |

### Top features (logistic)

- no_response_share_14: +0.741
- h_movement: -0.387
- consecutive_misses: +0.352
- n_shown_7: +0.306
- h_sleep: -0.282
- comp_rate_14: +0.266
- comp_trend: -0.213
- last_barrier_energy_fatigue: +0.174
- last_barrier_illness_pain: +0.139
- h_slope_movement: -0.128
