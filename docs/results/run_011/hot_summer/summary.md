## Simulation results: scenario `hot_summer`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 49.5% [47.5, 51.5] | 74.1% [73.2, 75.0] | 73.5% [72.1, 74.9] | 73.3% [72.1, 74.5] |
| Persistence, week 8 | 36.8% [34.8, 38.8] | 63.6% [61.4, 65.9] | 63.6% [61.1, 66.0] | 63.6% [61.4, 65.8] |
| Persistence, week 12 | 33.4% [31.4, 35.4] | 58.8% [56.8, 60.7] | 58.3% [56.3, 60.3] | 58.3% [56.6, 60.1] |
| Persistence, weeks 4+8+12 | 17.5% [15.8, 19.2] | 44.6% [42.3, 46.9] | 43.1% [40.6, 45.7] | 43.4% [41.1, 45.7] |
| Recovery within 14 days | 36.0% [34.7, 37.3] | 53.4% [52.1, 54.6] | 54.3% [53.0, 55.7] | 54.6% [53.4, 55.7] |
| Recovery within 14 days, after a labelled disruption | 35.0% [33.1, 36.9] | 51.4% [49.1, 53.6] | 53.3% [51.0, 55.5] | 53.6% [50.8, 56.4] |
| Recovery within 14 days, after an unlabelled shock | 39.9% [37.0, 42.7] | 57.8% [55.1, 60.5] | 58.5% [55.8, 61.2] | 58.9% [56.7, 61.1] |
| Recovery within 14 days, no disruption nearby | 35.6% [34.3, 36.8] | 53.0% [50.3, 55.8] | 53.4% [50.8, 56.1] | 53.5% [51.4, 55.7] |
| Median days from lapse to active | 11.8 d [11.1, 12.5] | 9.1 d [8.7, 9.5] | 9.1 d [8.7, 9.5] | 9.1 d [8.6, 9.5] |
| Median days from lapse to recovering | 6.0 d [6.0, 6.0] | 4.8 d [4.5, 5.1] | 4.4 d [4.0, 4.8] | 4.5 d [4.1, 4.9] |
| Δ weekly active minutes (wk1→wk12) | -20.0 min [-21.0, -19.1] | -11.7 min [-12.9, -10.6] | -3.5 min [-5.0, -1.9] | -2.4 min [-4.0, -0.8] |
| Δ tier-weighted sleep nights (wk1→wk12) | -8.9% [-9.2, -8.6] | -5.5% [-5.9, -5.0] | 5.0% [3.6, 6.5] | 5.1% [3.7, 6.5] |
| Δ sleep nights completed, raw (wk1→wk12) | -35.3% [-36.6, -34.0] | -21.5% [-23.3, -19.7] | -24.8% [-26.7, -22.8] | -24.6% [-26.5, -22.6] |
| Retention at end | 62.3% [60.1, 64.6] | 76.0% [73.3, 78.6] | 75.8% [73.7, 77.9] | 75.5% [73.0, 77.9] |
| Lapse rate (≥ 1 lapse in the run) | 96.6% [95.7, 97.5] | 86.2% [84.9, 87.6] | 87.6% [86.1, 89.1] | 87.8% [86.5, 89.1] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.1, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +18.6 pts [+16.6, +20.6] (helps) | +24.9 pts [+23.3, +26.6] (helps) | +13.1 pts [+11.8, +14.5] (helps) |
| C vs A0 | +1.2 pts [-0.1, +2.5] (not shown) | -0.4 pts [-1.1, +0.2] (not shown) | -0.5 pts [-1.1, +0.1] (not shown) |
| C vs B | +0.2 pts [-0.9, +1.3] (not shown) | +0.1 pts [-0.6, +0.8] (not shown) | -0.3 pts [-1.0, +0.3] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +24.9 pts [+23.0, +26.7]
- B vs A, persistence, weeks 4+8+12: +25.6 pts [+23.6, +27.7]
- B vs A, recovery within 14 days: +18.4 pts [+16.6, +20.1]
- B vs A, recovery within 14 days, after a labelled disruption: +18.3 pts [+15.5, +21.0]
- B vs A, recovery within 14 days, after an unlabelled shock: +18.7 pts [+16.8, +20.5]
- B vs A, median days from lapse to active: -2.7 d [-3.4, -2.0]
- B vs A, retention at end: +13.5 pts [+12.3, +14.7]
- B vs A, δ weekly active minutes (wk1→wk12): +16.5 min [+15.2, +17.9]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +14.0 pts [+12.6, +15.3]
- B vs A, lapse rate (≥ 1 lapse in the run): -9.0 pts [-10.3, -7.7]
- B vs A, messages per persona-week: +0.5 [+0.4, +0.5]
- C vs A, persistence, week 12: +24.9 pts [+23.3, +26.6]
- C vs A, persistence, weeks 4+8+12: +25.9 pts [+24.0, +27.7]
- C vs A, recovery within 14 days: +18.6 pts [+16.6, +20.6]
- C vs A, recovery within 14 days, after a labelled disruption: +18.5 pts [+15.1, +22.0]
- C vs A, recovery within 14 days, after an unlabelled shock: +19.1 pts [+16.0, +22.2]
- C vs A, median days from lapse to active: -2.8 d [-3.4, -2.1]
- C vs A, retention at end: +13.1 pts [+11.8, +14.5]
- C vs A, δ weekly active minutes (wk1→wk12): +17.6 min [+16.1, +19.1]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +14.0 pts [+12.7, +15.3]
- C vs A, lapse rate (≥ 1 lapse in the run): -8.8 pts [-9.9, -7.7]
- C vs A, messages per persona-week: +0.5 [+0.4, +0.5]
- C vs A0, persistence, week 12: -0.4 pts [-1.1, +0.2]
- C vs A0, persistence, weeks 4+8+12: -1.2 pts [-2.0, -0.5]
- C vs A0, recovery within 14 days: +1.2 pts [-0.1, +2.5]
- C vs A0, recovery within 14 days, after a labelled disruption: +2.2 pts [-0.4, +4.8]
- C vs A0, recovery within 14 days, after an unlabelled shock: +1.1 pts [-1.5, +3.8]
- C vs A0, median days from lapse to active: -0.1 d [-0.5, +0.4]
- C vs A0, retention at end: -0.5 pts [-1.1, +0.1]
- C vs A0, δ weekly active minutes (wk1→wk12): +9.3 min [+7.7, +11.0]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +10.6 pts [+9.3, +11.9]
- C vs A0, lapse rate (≥ 1 lapse in the run): +1.6 pts [+1.2, +1.9]
- C vs A0, messages per persona-week: +0.4 [+0.4, +0.4]
- C vs B, persistence, week 12: +0.1 pts [-0.6, +0.8]
- C vs B, persistence, weeks 4+8+12: +0.2 pts [-0.4, +0.8]
- C vs B, recovery within 14 days: +0.2 pts [-0.9, +1.3]
- C vs B, recovery within 14 days, after a labelled disruption: +0.3 pts [-1.5, +2.1]
- C vs B, recovery within 14 days, after an unlabelled shock: +0.4 pts [-1.8, +2.6]
- C vs B, median days from lapse to active: -0.1 d [-0.3, +0.2]
- C vs B, retention at end: -0.3 pts [-1.0, +0.3]
- C vs B, δ weekly active minutes (wk1→wk12): +1.1 min [+0.2, +1.9]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): +0.1 pts [-0.3, +0.4]
- C vs B, lapse rate (≥ 1 lapse in the run): +0.2 pts [-0.0, +0.4]
- C vs B, messages per persona-week: +0.0 [-0.0, +0.0]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 18.7% [14.5, 22.9] | 21.8% [15.5, 28.0] | 20.7% [15.2, 26.2] | 21.4% [15.2, 27.7] |
| health_literacy | Recovery within 14 days | 7.4% [4.4, 10.4] | 13.0% [8.6, 17.3] | 13.7% [9.6, 17.8] | 12.9% [8.9, 16.8] |
| health_literacy | Retention at end | 21.4% [17.3, 25.6] | 20.7% [15.9, 25.5] | 20.6% [15.7, 25.5] | 21.0% [16.3, 25.7] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 5.7 min [2.5, 9.0] | 6.0 min [3.9, 8.1] | 15.0 min [10.2, 19.9] | 14.4 min [8.3, 20.4] |
| language | Persistence, week 12 | 8.3% [4.8, 11.8] | 9.1% [5.7, 12.6] | 9.5% [6.4, 12.5] | 9.5% [5.9, 13.0] |
| language | Recovery within 14 days | 5.3% [2.9, 7.7] | 5.9% [3.5, 8.3] | 6.6% [4.6, 8.6] | 6.8% [5.1, 8.5] |
| language | Retention at end | 8.1% [5.0, 11.2] | 6.5% [4.4, 8.6] | 6.6% [4.8, 8.5] | 7.0% [5.2, 8.8] |
| language | Δ weekly active minutes (wk1→wk12) | 5.0 min [3.3, 6.7] | 5.0 min [2.4, 7.5] | 9.9 min [7.1, 12.7] | 9.2 min [6.2, 12.2] |
| mobility_limitation | Persistence, week 12 | 14.2% [9.9, 18.5] | 18.6% [9.4, 27.8] | 19.0% [10.8, 27.2] | 19.6% [11.8, 27.3] |
| mobility_limitation | Recovery within 14 days | 11.5% [7.6, 15.4] | 15.4% [9.9, 20.9] | 14.3% [9.2, 19.4] | 15.2% [10.8, 19.6] |
| mobility_limitation | Retention at end | 20.6% [11.9, 29.3] | 15.2% [9.3, 21.1] | 16.0% [9.4, 22.5] | 15.3% [9.4, 21.1] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.6 min [5.9, 13.2] | 7.6 min [4.1, 11.0] | 10.2 min [4.4, 16.0] | 11.9 min [5.6, 18.2] |
| schedule_type | Persistence, week 12 | 16.5% [11.9, 21.0] | 13.1% [10.2, 16.0] | 12.7% [8.3, 17.1] | 13.4% [9.3, 17.5] |
| schedule_type | Recovery within 14 days | 11.1% [8.7, 13.5] | 14.2% [11.0, 17.3] | 13.3% [11.0, 15.5] | 13.6% [11.6, 15.5] |
| schedule_type | Retention at end | 13.6% [9.8, 17.3] | 11.3% [8.2, 14.4] | 11.1% [7.1, 15.0] | 10.6% [6.7, 14.6] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 11.6 min [8.6, 14.5] | 10.1 min [7.2, 12.9] | 20.6 min [16.0, 25.1] | 21.1 min [16.3, 25.8] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Messages per persona-week vs A: +0.5 [+0.4, +0.5] (Rebound is worse)
- Persistence, week 12 vs A0: -0.4 pts [-1.1, +0.2] (no clear difference)
- Persistence, weeks 4+8+12 vs A0: -1.2 pts [-2.0, -0.5] (Rebound is worse)
- Recovery within 14 days vs A0: +1.2 pts [-0.1, +2.5] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: +2.2 pts [-0.4, +4.8] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +1.1 pts [-1.5, +3.8] (no clear difference)
- Median days from lapse to active vs A0: -0.1 d [-0.5, +0.4] (no clear difference)
- Retention at end vs A0: -0.5 pts [-1.1, +0.1] (no clear difference)
- Lapse rate (≥ 1 lapse in the run) vs A0: +1.6 pts [+1.2, +1.9] (Rebound is worse)
- Messages per persona-week vs A0: +0.4 [+0.4, +0.4] (Rebound is worse)
