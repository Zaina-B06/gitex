## Simulation results: scenario `low_checkin`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 49.8% [47.6, 52.0] | 74.5% [73.6, 75.3] | 74.2% [72.7, 75.8] | 74.4% [72.7, 76.2] |
| Persistence, week 8 | 36.8% [35.0, 38.6] | 64.0% [61.8, 66.2] | 63.6% [61.0, 66.2] | 63.7% [61.2, 66.2] |
| Persistence, week 12 | 33.3% [31.2, 35.4] | 58.7% [56.7, 60.6] | 58.6% [56.5, 60.7] | 58.5% [56.4, 60.7] |
| Persistence, weeks 4+8+12 | 17.4% [15.6, 19.2] | 44.8% [42.5, 47.1] | 43.6% [40.8, 46.4] | 43.7% [40.8, 46.6] |
| Recovery within 14 days | 36.7% [35.3, 38.1] | 53.7% [52.3, 55.1] | 55.3% [53.7, 56.9] | 55.2% [53.5, 56.9] |
| Recovery within 14 days, after a labelled disruption | 35.8% [33.8, 37.8] | 51.8% [49.5, 54.1] | 53.7% [51.2, 56.2] | 53.4% [50.9, 56.0] |
| Recovery within 14 days, after an unlabelled shock | 40.3% [37.4, 43.2] | 58.4% [55.2, 61.6] | 60.2% [57.8, 62.5] | 60.0% [57.9, 62.0] |
| Recovery within 14 days, no disruption nearby | 36.3% [34.9, 37.7] | 53.3% [50.6, 56.0] | 54.6% [52.0, 57.1] | 54.7% [52.0, 57.4] |
| Median days from lapse to active | 11.6 d [11.0, 12.2] | 8.9 d [8.5, 9.3] | 8.9 d [8.7, 9.1] | 8.8 d [8.5, 9.1] |
| Median days from lapse to recovering | 5.9 d [5.7, 6.1] | 4.5 d [4.2, 4.9] | 4.6 d [4.2, 5.0] | 4.3 d [4.0, 4.6] |
| Δ weekly active minutes (wk1→wk12) | -20.7 min [-21.7, -19.7] | -12.6 min [-13.7, -11.5] | -4.2 min [-5.5, -2.8] | -3.9 min [-5.3, -2.6] |
| Δ tier-weighted sleep nights (wk1→wk12) | -9.0% [-9.3, -8.6] | -5.5% [-5.9, -5.0] | 5.1% [3.6, 6.5] | 4.9% [3.6, 6.3] |
| Δ sleep nights completed, raw (wk1→wk12) | -35.5% [-36.8, -34.2] | -21.5% [-23.3, -19.7] | -25.3% [-27.1, -23.5] | -25.3% [-27.2, -23.4] |
| Retention at end | 62.1% [60.0, 64.3] | 75.9% [73.3, 78.5] | 76.4% [74.2, 78.6] | 76.2% [73.9, 78.5] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.1, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +18.5 pts [+16.3, +20.7] (helps) | +25.2 pts [+23.3, +27.2] (helps) | +14.1 pts [+12.8, +15.4] (helps) |
| C vs A0 | +1.5 pts [+0.0, +3.0] (helps) | -0.1 pts [-0.8, +0.5] (not shown) | +0.3 pts [-0.6, +1.1] (not shown) |
| C vs B | -0.1 pts [-0.5, +0.4] (not shown) | -0.1 pts [-0.7, +0.6] (not shown) | -0.2 pts [-0.5, +0.1] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +25.3 pts [+23.1, +27.5]
- B vs A, persistence, weeks 4+8+12: +26.2 pts [+23.9, +28.4]
- B vs A, recovery within 14 days: +18.6 pts [+16.5, +20.6]
- B vs A, recovery within 14 days, after a labelled disruption: +17.9 pts [+15.1, +20.7]
- B vs A, recovery within 14 days, after an unlabelled shock: +19.9 pts [+17.2, +22.5]
- B vs A, median days from lapse to active: -2.7 d [-3.3, -2.1]
- B vs A, retention at end: +14.3 pts [+13.0, +15.5]
- B vs A, δ weekly active minutes (wk1→wk12): +16.6 min [+15.3, +17.8]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +14.0 pts [+12.7, +15.4]
- C vs A, persistence, week 12: +25.2 pts [+23.3, +27.2]
- C vs A, persistence, weeks 4+8+12: +26.3 pts [+24.1, +28.5]
- C vs A, recovery within 14 days: +18.5 pts [+16.3, +20.7]
- C vs A, recovery within 14 days, after a labelled disruption: +17.6 pts [+14.4, +20.8]
- C vs A, recovery within 14 days, after an unlabelled shock: +19.7 pts [+16.9, +22.4]
- C vs A, median days from lapse to active: -2.8 d [-3.4, -2.2]
- C vs A, retention at end: +14.1 pts [+12.8, +15.4]
- C vs A, δ weekly active minutes (wk1→wk12): +16.8 min [+15.4, +18.2]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +13.9 pts [+12.6, +15.2]
- C vs A0, persistence, week 12: -0.1 pts [-0.8, +0.5]
- C vs A0, persistence, weeks 4+8+12: -1.1 pts [-2.4, +0.3]
- C vs A0, recovery within 14 days: +1.5 pts [+0.0, +3.0]
- C vs A0, recovery within 14 days, after a labelled disruption: +1.6 pts [-0.3, +3.6]
- C vs A0, recovery within 14 days, after an unlabelled shock: +1.5 pts [-0.3, +3.4]
- C vs A0, median days from lapse to active: -0.1 d [-0.5, +0.3]
- C vs A0, retention at end: +0.3 pts [-0.6, +1.1]
- C vs A0, δ weekly active minutes (wk1→wk12): +8.6 min [+7.2, +10.1]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +10.4 pts [+9.2, +11.7]
- C vs B, persistence, week 12: -0.1 pts [-0.7, +0.6]
- C vs B, persistence, weeks 4+8+12: +0.1 pts [-0.2, +0.5]
- C vs B, recovery within 14 days: -0.1 pts [-0.5, +0.4]
- C vs B, recovery within 14 days, after a labelled disruption: -0.3 pts [-1.2, +0.6]
- C vs B, recovery within 14 days, after an unlabelled shock: -0.2 pts [-0.9, +0.5]
- C vs B, median days from lapse to active: -0.1 d [-0.3, +0.1]
- C vs B, retention at end: -0.2 pts [-0.5, +0.1]
- C vs B, δ weekly active minutes (wk1→wk12): +0.2 min [-0.3, +0.7]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): -0.1 pts [-0.5, +0.2]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 19.0% [14.5, 23.5] | 22.0% [15.8, 28.1] | 22.5% [16.5, 28.4] | 22.8% [16.8, 28.8] |
| health_literacy | Recovery within 14 days | 7.5% [4.4, 10.7] | 13.5% [9.2, 17.9] | 14.6% [10.1, 19.0] | 13.9% [9.8, 18.1] |
| health_literacy | Retention at end | 21.8% [17.4, 26.2] | 20.6% [15.8, 25.4] | 19.9% [15.8, 24.0] | 20.1% [15.5, 24.7] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 6.1 min [2.8, 9.5] | 6.1 min [3.7, 8.6] | 15.2 min [10.0, 20.3] | 15.1 min [8.8, 21.3] |
| language | Persistence, week 12 | 8.3% [4.6, 12.0] | 8.7% [5.4, 12.1] | 8.5% [5.4, 11.6] | 7.9% [5.1, 10.6] |
| language | Recovery within 14 days | 6.3% [3.7, 8.8] | 5.6% [3.1, 8.1] | 5.1% [2.4, 7.8] | 4.8% [2.5, 7.1] |
| language | Retention at end | 8.4% [4.7, 12.1] | 6.6% [4.6, 8.6] | 6.5% [5.5, 7.5] | 5.8% [4.0, 7.6] |
| language | Δ weekly active minutes (wk1→wk12) | 5.0 min [3.4, 6.7] | 5.2 min [2.6, 7.8] | 8.5 min [5.5, 11.5] | 8.8 min [6.2, 11.5] |
| mobility_limitation | Persistence, week 12 | 14.0% [9.7, 18.4] | 18.5% [9.3, 27.7] | 22.6% [14.3, 30.8] | 19.8% [10.4, 29.2] |
| mobility_limitation | Recovery within 14 days | 11.5% [7.3, 15.6] | 15.5% [9.8, 21.1] | 9.8% [7.3, 12.4] | 12.5% [10.1, 15.0] |
| mobility_limitation | Retention at end | 20.4% [11.7, 29.2] | 15.1% [9.3, 21.0] | 15.4% [8.3, 22.5] | 15.5% [8.7, 22.2] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.9 min [6.4, 13.5] | 7.9 min [4.5, 11.2] | 10.2 min [5.1, 15.4] | 10.4 min [5.6, 15.3] |
| schedule_type | Persistence, week 12 | 16.2% [12.0, 20.4] | 12.9% [9.9, 15.9] | 13.0% [10.1, 15.8] | 13.2% [10.1, 16.3] |
| schedule_type | Recovery within 14 days | 11.3% [9.0, 13.7] | 14.7% [11.4, 18.0] | 14.4% [10.4, 18.5] | 13.8% [10.2, 17.3] |
| schedule_type | Retention at end | 13.4% [9.8, 17.1] | 11.3% [8.2, 14.4] | 10.8% [7.5, 14.1] | 11.4% [8.6, 14.3] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 11.9 min [8.9, 14.9] | 10.1 min [7.4, 12.8] | 21.2 min [16.3, 26.0] | 20.7 min [15.7, 25.7] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Persistence, week 12 vs A0: -0.1 pts [-0.8, +0.5] (no clear difference)
- Persistence, weeks 4+8+12 vs A0: -1.1 pts [-2.4, +0.3] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: +1.6 pts [-0.3, +3.6] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +1.5 pts [-0.3, +3.4] (no clear difference)
- Median days from lapse to active vs A0: -0.1 d [-0.5, +0.3] (no clear difference)
- Retention at end vs A0: +0.3 pts [-0.6, +1.1] (no clear difference)
