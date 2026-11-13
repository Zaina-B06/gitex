## Simulation results: scenario `hot_summer`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 49.5% [47.5, 51.5] | 74.1% [73.2, 75.0] | 73.7% [72.3, 75.0] | 73.7% [72.4, 74.9] |
| Persistence, week 8 | 36.8% [34.8, 38.8] | 63.6% [61.4, 65.9] | 63.4% [60.8, 66.0] | 63.6% [61.3, 65.9] |
| Persistence, week 12 | 33.4% [31.4, 35.4] | 58.8% [56.8, 60.7] | 58.9% [56.7, 61.1] | 58.5% [56.5, 60.5] |
| Persistence, weeks 4+8+12 | 17.5% [15.8, 19.2] | 44.6% [42.3, 46.9] | 43.6% [40.8, 46.4] | 43.6% [41.1, 46.0] |
| Recovery within 14 days | 36.0% [34.7, 37.3] | 53.4% [52.1, 54.6] | 55.2% [53.4, 56.9] | 55.1% [53.4, 56.9] |
| Recovery within 14 days, after a labelled disruption | 35.0% [33.1, 36.9] | 51.4% [49.1, 53.6] | 53.5% [50.2, 56.7] | 54.4% [51.8, 57.0] |
| Recovery within 14 days, after an unlabelled shock | 39.9% [37.0, 42.7] | 57.8% [55.1, 60.5] | 59.8% [57.4, 62.2] | 59.7% [57.7, 61.7] |
| Recovery within 14 days, no disruption nearby | 35.6% [34.3, 36.8] | 53.0% [50.3, 55.8] | 54.5% [52.3, 56.8] | 53.9% [51.3, 56.4] |
| Median days from lapse to active | 11.8 d [11.1, 12.5] | 9.1 d [8.7, 9.5] | 8.8 d [8.5, 9.1] | 8.8 d [8.3, 9.3] |
| Median days from lapse to recovering | 6.0 d [6.0, 6.0] | 4.8 d [4.5, 5.1] | 4.5 d [4.1, 4.8] | 4.4 d [4.0, 4.8] |
| Δ weekly active minutes (wk1→wk12) | -20.0 min [-21.0, -19.1] | -11.7 min [-12.9, -10.6] | -3.1 min [-4.6, -1.6] | -1.9 min [-3.5, -0.3] |
| Δ tier-weighted sleep nights (wk1→wk12) | -8.9% [-9.2, -8.6] | -5.5% [-5.9, -5.0] | 5.1% [3.7, 6.6] | 5.1% [3.6, 6.5] |
| Δ sleep nights completed, raw (wk1→wk12) | -35.3% [-36.6, -34.0] | -21.5% [-23.3, -19.7] | -25.0% [-26.6, -23.4] | -24.7% [-26.5, -22.9] |
| Retention at end | 62.3% [60.1, 64.6] | 76.0% [73.3, 78.6] | 75.9% [73.8, 78.1] | 75.7% [73.5, 77.9] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.1 [12.1, 12.2] | 12.1 [12.1, 12.2] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +19.2 pts [+16.9, +21.4] (helps) | +25.1 pts [+23.7, +26.6] (helps) | +13.4 pts [+12.0, +14.7] (helps) |
| C vs A0 | +1.8 pts [+0.5, +3.1] (helps) | -0.2 pts [-0.8, +0.4] (not shown) | -0.3 pts [-1.0, +0.5] (not shown) |
| C vs B | -0.0 pts [-0.8, +0.7] (not shown) | -0.4 pts [-1.0, +0.2] (not shown) | -0.2 pts [-1.1, +0.6] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +25.5 pts [+23.8, +27.2]
- B vs A, persistence, weeks 4+8+12: +26.1 pts [+23.8, +28.4]
- B vs A, recovery within 14 days: +19.2 pts [+17.0, +21.3]
- B vs A, recovery within 14 days, after a labelled disruption: +18.5 pts [+14.8, +22.1]
- B vs A, recovery within 14 days, after an unlabelled shock: +19.9 pts [+18.2, +21.7]
- B vs A, median days from lapse to active: -3.0 d [-3.7, -2.3]
- B vs A, retention at end: +13.6 pts [+12.3, +14.9]
- B vs A, δ weekly active minutes (wk1→wk12): +16.9 min [+15.6, +18.2]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +14.1 pts [+12.7, +15.4]
- C vs A, persistence, week 12: +25.1 pts [+23.7, +26.6]
- C vs A, persistence, weeks 4+8+12: +26.1 pts [+24.0, +28.1]
- C vs A, recovery within 14 days: +19.2 pts [+16.9, +21.4]
- C vs A, recovery within 14 days, after a labelled disruption: +19.3 pts [+16.3, +22.3]
- C vs A, recovery within 14 days, after an unlabelled shock: +19.9 pts [+17.3, +22.5]
- C vs A, median days from lapse to active: -3.0 d [-3.7, -2.3]
- C vs A, retention at end: +13.4 pts [+12.0, +14.7]
- C vs A, δ weekly active minutes (wk1→wk12): +18.1 min [+16.7, +19.5]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +14.0 pts [+12.6, +15.3]
- C vs A0, persistence, week 12: -0.2 pts [-0.8, +0.4]
- C vs A0, persistence, weeks 4+8+12: -1.0 pts [-2.2, +0.1]
- C vs A0, recovery within 14 days: +1.8 pts [+0.5, +3.1]
- C vs A0, recovery within 14 days, after a labelled disruption: +3.0 pts [+0.6, +5.4]
- C vs A0, recovery within 14 days, after an unlabelled shock: +1.9 pts [-0.1, +4.0]
- C vs A0, median days from lapse to active: -0.3 d [-0.8, +0.2]
- C vs A0, retention at end: -0.3 pts [-1.0, +0.5]
- C vs A0, δ weekly active minutes (wk1→wk12): +9.8 min [+8.3, +11.3]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +10.5 pts [+9.2, +11.9]
- C vs B, persistence, week 12: -0.4 pts [-1.0, +0.2]
- C vs B, persistence, weeks 4+8+12: -0.0 pts [-0.8, +0.7]
- C vs B, recovery within 14 days: -0.0 pts [-0.8, +0.7]
- C vs B, recovery within 14 days, after a labelled disruption: +0.9 pts [-0.4, +2.2]
- C vs B, recovery within 14 days, after an unlabelled shock: -0.1 pts [-2.0, +1.8]
- C vs B, median days from lapse to active: +0.0 d [-0.3, +0.3]
- C vs B, retention at end: -0.2 pts [-1.1, +0.6]
- C vs B, δ weekly active minutes (wk1→wk12): +1.2 min [+0.4, +2.0]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): -0.1 pts [-0.4, +0.2]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 18.7% [14.5, 22.9] | 21.8% [15.5, 28.0] | 20.8% [15.4, 26.1] | 20.5% [15.0, 26.0] |
| health_literacy | Recovery within 14 days | 7.4% [4.4, 10.4] | 13.0% [8.6, 17.3] | 13.9% [9.7, 18.0] | 13.5% [9.4, 17.7] |
| health_literacy | Retention at end | 21.4% [17.3, 25.6] | 20.7% [15.9, 25.5] | 20.3% [15.7, 24.9] | 19.1% [14.5, 23.7] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 5.7 min [2.5, 9.0] | 6.0 min [3.9, 8.1] | 15.1 min [10.2, 19.9] | 14.1 min [8.2, 20.0] |
| language | Persistence, week 12 | 8.3% [4.8, 11.8] | 9.1% [5.7, 12.6] | 9.4% [5.9, 12.8] | 9.1% [5.4, 12.8] |
| language | Recovery within 14 days | 5.3% [2.9, 7.7] | 5.9% [3.5, 8.3] | 5.5% [3.6, 7.3] | 4.8% [2.3, 7.3] |
| language | Retention at end | 8.1% [5.0, 11.2] | 6.5% [4.4, 8.6] | 6.7% [4.6, 8.8] | 7.0% [4.8, 9.2] |
| language | Δ weekly active minutes (wk1→wk12) | 5.0 min [3.3, 6.7] | 5.0 min [2.4, 7.5] | 9.5 min [6.1, 12.9] | 9.4 min [6.1, 12.7] |
| mobility_limitation | Persistence, week 12 | 14.2% [9.9, 18.5] | 18.6% [9.4, 27.8] | 19.5% [9.9, 29.1] | 18.8% [9.4, 28.3] |
| mobility_limitation | Recovery within 14 days | 11.5% [7.6, 15.4] | 15.4% [9.9, 20.9] | 17.8% [13.4, 22.2] | 17.1% [12.1, 22.1] |
| mobility_limitation | Retention at end | 20.6% [11.9, 29.3] | 15.2% [9.3, 21.1] | 15.7% [8.8, 22.5] | 16.5% [10.1, 22.9] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.6 min [5.9, 13.2] | 7.6 min [4.1, 11.0] | 9.7 min [4.6, 14.9] | 11.4 min [6.0, 16.8] |
| schedule_type | Persistence, week 12 | 16.5% [11.9, 21.0] | 13.1% [10.2, 16.0] | 12.9% [8.9, 16.8] | 11.8% [8.1, 15.5] |
| schedule_type | Recovery within 14 days | 11.1% [8.7, 13.5] | 14.2% [11.0, 17.3] | 13.4% [10.3, 16.6] | 11.6% [9.5, 13.6] |
| schedule_type | Retention at end | 13.6% [9.8, 17.3] | 11.3% [8.2, 14.4] | 11.9% [7.7, 16.1] | 11.2% [6.2, 16.2] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 11.6 min [8.6, 14.5] | 10.1 min [7.2, 12.9] | 21.3 min [16.6, 25.9] | 21.5 min [15.9, 27.1] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.1 [12.1, 12.2] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.1 [12.1, 12.2] messages per persona-week

### Where Rebound doesn't help

- Persistence, week 12 vs A0: -0.2 pts [-0.8, +0.4] (no clear difference)
- Persistence, weeks 4+8+12 vs A0: -1.0 pts [-2.2, +0.1] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +1.9 pts [-0.1, +4.0] (no clear difference)
- Median days from lapse to active vs A0: -0.3 d [-0.8, +0.2] (no clear difference)
- Retention at end vs A0: -0.3 pts [-1.0, +0.5] (no clear difference)
