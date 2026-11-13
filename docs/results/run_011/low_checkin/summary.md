## Simulation results: scenario `low_checkin`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 49.8% [47.6, 52.0] | 74.5% [73.6, 75.3] | 73.5% [72.0, 75.1] | 73.8% [72.5, 75.2] |
| Persistence, week 8 | 36.8% [35.0, 38.6] | 64.0% [61.8, 66.2] | 64.2% [61.5, 66.9] | 63.9% [61.5, 66.4] |
| Persistence, week 12 | 33.3% [31.2, 35.4] | 58.7% [56.7, 60.6] | 58.4% [56.9, 60.0] | 58.2% [56.7, 59.7] |
| Persistence, weeks 4+8+12 | 17.4% [15.6, 19.2] | 44.8% [42.5, 47.1] | 43.8% [40.9, 46.7] | 43.6% [40.9, 46.2] |
| Recovery within 14 days | 36.7% [35.3, 38.1] | 53.7% [52.3, 55.1] | 54.6% [53.1, 56.0] | 55.3% [54.2, 56.4] |
| Recovery within 14 days, after a labelled disruption | 35.8% [33.8, 37.8] | 51.8% [49.5, 54.1] | 53.5% [51.7, 55.2] | 54.1% [52.8, 55.5] |
| Recovery within 14 days, after an unlabelled shock | 40.3% [37.4, 43.2] | 58.4% [55.2, 61.6] | 58.9% [55.8, 62.1] | 60.4% [57.6, 63.2] |
| Recovery within 14 days, no disruption nearby | 36.3% [34.9, 37.7] | 53.3% [50.6, 56.0] | 53.7% [51.7, 55.8] | 54.0% [51.8, 56.3] |
| Median days from lapse to active | 11.6 d [11.0, 12.2] | 8.9 d [8.5, 9.3] | 8.8 d [8.5, 9.1] | 8.9 d [8.4, 9.4] |
| Median days from lapse to recovering | 5.9 d [5.7, 6.1] | 4.5 d [4.2, 4.9] | 4.3 d [4.0, 4.6] | 4.5 d [4.1, 4.9] |
| Δ weekly active minutes (wk1→wk12) | -20.7 min [-21.7, -19.7] | -12.6 min [-13.7, -11.5] | -4.6 min [-6.0, -3.2] | -4.0 min [-5.3, -2.6] |
| Δ tier-weighted sleep nights (wk1→wk12) | -9.0% [-9.3, -8.6] | -5.5% [-5.9, -5.0] | 4.9% [3.5, 6.4] | 5.0% [3.7, 6.3] |
| Δ sleep nights completed, raw (wk1→wk12) | -35.5% [-36.8, -34.2] | -21.5% [-23.3, -19.7] | -25.4% [-27.4, -23.4] | -25.3% [-27.4, -23.1] |
| Retention at end | 62.1% [60.0, 64.3] | 75.9% [73.3, 78.5] | 75.6% [73.9, 77.3] | 75.9% [73.9, 77.8] |
| Lapse rate (≥ 1 lapse in the run) | 96.6% [95.7, 97.5] | 86.1% [84.8, 87.5] | 87.5% [86.2, 88.9] | 87.5% [86.0, 88.9] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.1, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +18.6 pts [+16.9, +20.2] (helps) | +24.9 pts [+23.1, +26.7] (helps) | +13.7 pts [+12.8, +14.7] (helps) |
| C vs A0 | +1.5 pts [+0.5, +2.6] (helps) | -0.5 pts [-1.2, +0.2] (not shown) | -0.1 pts [-0.9, +0.8] (not shown) |
| C vs B | +0.7 pts [-0.2, +1.6] (not shown) | -0.2 pts [-0.6, +0.2] (not shown) | +0.3 pts [-0.2, +0.8] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +25.1 pts [+23.4, +26.9]
- B vs A, persistence, weeks 4+8+12: +26.3 pts [+24.2, +28.4]
- B vs A, recovery within 14 days: +17.9 pts [+16.2, +19.6]
- B vs A, recovery within 14 days, after a labelled disruption: +17.7 pts [+15.3, +20.0]
- B vs A, recovery within 14 days, after an unlabelled shock: +18.6 pts [+15.2, +22.0]
- B vs A, median days from lapse to active: -2.8 d [-3.3, -2.3]
- B vs A, retention at end: +13.4 pts [+12.3, +14.6]
- B vs A, δ weekly active minutes (wk1→wk12): +16.1 min [+14.9, +17.3]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +13.9 pts [+12.6, +15.2]
- B vs A, lapse rate (≥ 1 lapse in the run): -9.0 pts [-10.2, -7.8]
- B vs A, messages per persona-week: +0.5 [+0.5, +0.5]
- C vs A, persistence, week 12: +24.9 pts [+23.1, +26.7]
- C vs A, persistence, weeks 4+8+12: +26.1 pts [+24.3, +28.0]
- C vs A, recovery within 14 days: +18.6 pts [+16.9, +20.2]
- C vs A, recovery within 14 days, after a labelled disruption: +18.3 pts [+15.7, +21.0]
- C vs A, recovery within 14 days, after an unlabelled shock: +20.1 pts [+16.2, +23.9]
- C vs A, median days from lapse to active: -2.7 d [-3.3, -2.1]
- C vs A, retention at end: +13.7 pts [+12.8, +14.7]
- C vs A, δ weekly active minutes (wk1→wk12): +16.8 min [+15.5, +18.0]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +14.0 pts [+12.8, +15.2]
- C vs A, lapse rate (≥ 1 lapse in the run): -9.1 pts [-10.3, -7.9]
- C vs A, messages per persona-week: +0.5 [+0.5, +0.5]
- C vs A0, persistence, week 12: -0.5 pts [-1.2, +0.2]
- C vs A0, persistence, weeks 4+8+12: -1.2 pts [-2.2, -0.2]
- C vs A0, recovery within 14 days: +1.5 pts [+0.5, +2.6]
- C vs A0, recovery within 14 days, after a labelled disruption: +2.3 pts [-0.0, +4.7]
- C vs A0, recovery within 14 days, after an unlabelled shock: +2.0 pts [+0.2, +3.7]
- C vs A0, median days from lapse to active: +0.0 d [-0.5, +0.5]
- C vs A0, retention at end: -0.1 pts [-0.9, +0.8]
- C vs A0, δ weekly active minutes (wk1→wk12): +8.6 min [+7.2, +10.0]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +10.5 pts [+9.3, +11.6]
- C vs A0, lapse rate (≥ 1 lapse in the run): +1.3 pts [+0.8, +1.8]
- C vs A0, messages per persona-week: +0.4 [+0.4, +0.4]
- C vs B, persistence, week 12: -0.2 pts [-0.6, +0.2]
- C vs B, persistence, weeks 4+8+12: -0.2 pts [-0.8, +0.4]
- C vs B, recovery within 14 days: +0.7 pts [-0.2, +1.6]
- C vs B, recovery within 14 days, after a labelled disruption: +0.7 pts [-0.3, +1.7]
- C vs B, recovery within 14 days, after an unlabelled shock: +1.5 pts [-0.8, +3.7]
- C vs B, median days from lapse to active: +0.1 d [-0.3, +0.5]
- C vs B, retention at end: +0.3 pts [-0.2, +0.8]
- C vs B, δ weekly active minutes (wk1→wk12): +0.6 min [-0.1, +1.4]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): +0.1 pts [-0.2, +0.3]
- C vs B, lapse rate (≥ 1 lapse in the run): -0.1 pts [-0.3, +0.2]
- C vs B, messages per persona-week: -0.0 [-0.0, +0.0]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 19.0% [14.5, 23.5] | 22.0% [15.8, 28.1] | 20.7% [15.1, 26.4] | 20.6% [15.0, 26.1] |
| health_literacy | Recovery within 14 days | 7.5% [4.4, 10.7] | 13.5% [9.2, 17.9] | 13.1% [8.1, 18.1] | 12.7% [8.5, 16.9] |
| health_literacy | Retention at end | 21.8% [17.4, 26.2] | 20.6% [15.8, 25.4] | 20.9% [15.8, 26.0] | 20.2% [15.7, 24.7] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 6.1 min [2.8, 9.5] | 6.1 min [3.7, 8.6] | 15.7 min [10.5, 20.8] | 14.8 min [8.6, 21.0] |
| language | Persistence, week 12 | 8.3% [4.6, 12.0] | 8.7% [5.4, 12.1] | 9.4% [5.6, 13.2] | 9.3% [5.7, 12.9] |
| language | Recovery within 14 days | 6.3% [3.7, 8.8] | 5.6% [3.1, 8.1] | 5.8% [3.2, 8.3] | 5.3% [2.6, 8.1] |
| language | Retention at end | 8.4% [4.7, 12.1] | 6.6% [4.6, 8.6] | 6.9% [4.8, 9.0] | 7.5% [5.4, 9.7] |
| language | Δ weekly active minutes (wk1→wk12) | 5.0 min [3.4, 6.7] | 5.2 min [2.6, 7.8] | 8.8 min [6.1, 11.4] | 8.8 min [6.0, 11.5] |
| mobility_limitation | Persistence, week 12 | 14.0% [9.7, 18.4] | 18.5% [9.3, 27.7] | 16.8% [7.7, 25.8] | 16.2% [8.2, 24.2] |
| mobility_limitation | Recovery within 14 days | 11.5% [7.3, 15.6] | 15.5% [9.8, 21.1] | 17.1% [10.9, 23.3] | 16.2% [8.9, 23.4] |
| mobility_limitation | Retention at end | 20.4% [11.7, 29.2] | 15.1% [9.3, 21.0] | 16.5% [9.8, 23.1] | 16.8% [10.2, 23.3] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.9 min [6.4, 13.5] | 7.9 min [4.5, 11.2] | 9.1 min [4.0, 14.2] | 10.7 min [5.3, 16.0] |
| schedule_type | Persistence, week 12 | 16.2% [12.0, 20.4] | 12.9% [9.9, 15.9] | 14.1% [11.4, 16.9] | 14.2% [11.1, 17.3] |
| schedule_type | Recovery within 14 days | 11.3% [9.0, 13.7] | 14.7% [11.4, 18.0] | 12.0% [10.6, 13.5] | 13.2% [11.2, 15.2] |
| schedule_type | Retention at end | 13.4% [9.8, 17.1] | 11.3% [8.2, 14.4] | 11.8% [8.7, 14.9] | 10.8% [8.0, 13.6] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 11.9 min [8.9, 14.9] | 10.1 min [7.4, 12.8] | 20.7 min [16.4, 25.0] | 21.6 min [17.6, 25.5] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Messages per persona-week vs A: +0.5 [+0.5, +0.5] (Rebound is worse)
- Persistence, week 12 vs A0: -0.5 pts [-1.2, +0.2] (no clear difference)
- Persistence, weeks 4+8+12 vs A0: -1.2 pts [-2.2, -0.2] (Rebound is worse)
- Recovery within 14 days, after a labelled disruption vs A0: +2.3 pts [-0.0, +4.7] (no clear difference)
- Median days from lapse to active vs A0: +0.0 d [-0.5, +0.5] (no clear difference)
- Retention at end vs A0: -0.1 pts [-0.9, +0.8] (no clear difference)
- Lapse rate (≥ 1 lapse in the run) vs A0: +1.3 pts [+0.8, +1.8] (Rebound is worse)
- Messages per persona-week vs A0: +0.4 [+0.4, +0.4] (Rebound is worse)
