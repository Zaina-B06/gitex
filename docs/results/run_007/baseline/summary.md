## Simulation results: scenario `baseline`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 49.8% [47.6, 52.0] | 74.5% [73.6, 75.3] | 73.8% [72.5, 75.1] | 74.1% [72.8, 75.5] |
| Persistence, week 8 | 36.8% [35.0, 38.6] | 64.0% [61.8, 66.2] | 63.7% [61.1, 66.3] | 63.6% [61.1, 66.1] |
| Persistence, week 12 | 33.3% [31.2, 35.4] | 58.7% [56.7, 60.6] | 59.0% [56.8, 61.2] | 58.5% [56.5, 60.5] |
| Persistence, weeks 4+8+12 | 17.4% [15.6, 19.2] | 44.8% [42.5, 47.1] | 43.8% [41.0, 46.7] | 43.3% [40.7, 45.8] |
| Recovery within 14 days | 36.7% [35.3, 38.1] | 53.7% [52.3, 55.1] | 55.4% [53.6, 57.1] | 55.2% [53.6, 56.9] |
| Recovery within 14 days, after a labelled disruption | 35.8% [33.8, 37.8] | 51.8% [49.5, 54.1] | 53.9% [51.0, 56.8] | 54.0% [51.3, 56.7] |
| Recovery within 14 days, after an unlabelled shock | 40.3% [37.4, 43.2] | 58.4% [55.2, 61.6] | 60.3% [58.0, 62.6] | 60.0% [58.5, 61.4] |
| Recovery within 14 days, no disruption nearby | 36.3% [34.9, 37.7] | 53.3% [50.6, 56.0] | 54.5% [52.2, 56.8] | 54.2% [51.9, 56.4] |
| Median days from lapse to active | 11.6 d [11.0, 12.2] | 8.9 d [8.5, 9.3] | 8.6 d [8.2, 9.0] | 9.0 d [8.5, 9.5] |
| Median days from lapse to recovering | 5.9 d [5.7, 6.1] | 4.5 d [4.2, 4.9] | 4.5 d [4.1, 4.9] | 4.3 d [4.0, 4.6] |
| Δ weekly active minutes (wk1→wk12) | -20.7 min [-21.7, -19.7] | -12.6 min [-13.7, -11.5] | -4.3 min [-5.7, -2.9] | -3.9 min [-5.4, -2.3] |
| Δ tier-weighted sleep nights (wk1→wk12) | -9.0% [-9.3, -8.6] | -5.5% [-5.9, -5.0] | 4.9% [3.5, 6.4] | 4.9% [3.5, 6.4] |
| Δ sleep nights completed, raw (wk1→wk12) | -35.5% [-36.8, -34.2] | -21.5% [-23.3, -19.7] | -25.3% [-26.9, -23.6] | -25.3% [-26.9, -23.7] |
| Retention at end | 62.1% [60.0, 64.3] | 75.9% [73.3, 78.5] | 76.0% [73.7, 78.3] | 75.9% [73.8, 78.1] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.1 [12.1, 12.2] | 12.1 [12.1, 12.2] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +18.5 pts [+16.4, +20.7] (helps) | +25.2 pts [+23.8, +26.5] (helps) | +13.8 pts [+12.5, +15.1] (helps) |
| C vs A0 | +1.5 pts [+0.4, +2.6] (helps) | -0.2 pts [-1.0, +0.6] (not shown) | -0.0 pts [-0.7, +0.7] (not shown) |
| C vs B | -0.1 pts [-0.8, +0.5] (not shown) | -0.5 pts [-1.1, +0.1] (not shown) | -0.1 pts [-0.5, +0.4] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +25.7 pts [+24.0, +27.3]
- B vs A, persistence, weeks 4+8+12: +26.4 pts [+24.3, +28.5]
- B vs A, recovery within 14 days: +18.7 pts [+16.4, +20.9]
- B vs A, recovery within 14 days, after a labelled disruption: +18.1 pts [+14.6, +21.6]
- B vs A, recovery within 14 days, after an unlabelled shock: +20.0 pts [+17.3, +22.7]
- B vs A, median days from lapse to active: -3.0 d [-3.8, -2.2]
- B vs A, retention at end: +13.9 pts [+12.4, +15.3]
- B vs A, δ weekly active minutes (wk1→wk12): +16.4 min [+15.1, +17.8]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +13.9 pts [+12.5, +15.2]
- C vs A, persistence, week 12: +25.2 pts [+23.8, +26.5]
- C vs A, persistence, weeks 4+8+12: +25.8 pts [+24.2, +27.5]
- C vs A, recovery within 14 days: +18.5 pts [+16.4, +20.7]
- C vs A, recovery within 14 days, after a labelled disruption: +18.2 pts [+14.9, +21.6]
- C vs A, recovery within 14 days, after an unlabelled shock: +19.7 pts [+16.7, +22.7]
- C vs A, median days from lapse to active: -2.6 d [-3.4, -1.8]
- C vs A, retention at end: +13.8 pts [+12.5, +15.1]
- C vs A, δ weekly active minutes (wk1→wk12): +16.9 min [+15.6, +18.1]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +13.9 pts [+12.5, +15.3]
- C vs A0, persistence, week 12: -0.2 pts [-1.0, +0.6]
- C vs A0, persistence, weeks 4+8+12: -1.5 pts [-2.8, -0.3]
- C vs A0, recovery within 14 days: +1.5 pts [+0.4, +2.6]
- C vs A0, recovery within 14 days, after a labelled disruption: +2.2 pts [-0.7, +5.1]
- C vs A0, recovery within 14 days, after an unlabelled shock: +1.6 pts [-0.6, +3.8]
- C vs A0, median days from lapse to active: +0.1 d [-0.3, +0.5]
- C vs A0, retention at end: -0.0 pts [-0.7, +0.7]
- C vs A0, δ weekly active minutes (wk1→wk12): +8.7 min [+7.5, +9.9]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +10.4 pts [+9.0, +11.8]
- C vs B, persistence, week 12: -0.5 pts [-1.1, +0.1]
- C vs B, persistence, weeks 4+8+12: -0.6 pts [-1.4, +0.3]
- C vs B, recovery within 14 days: -0.1 pts [-0.8, +0.5]
- C vs B, recovery within 14 days, after a labelled disruption: +0.1 pts [-0.7, +1.0]
- C vs B, recovery within 14 days, after an unlabelled shock: -0.3 pts [-2.0, +1.4]
- C vs B, median days from lapse to active: +0.4 d [+0.0, +0.8]
- C vs B, retention at end: -0.1 pts [-0.5, +0.4]
- C vs B, δ weekly active minutes (wk1→wk12): +0.4 min [-0.2, +1.1]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): -0.0 pts [-0.4, +0.3]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 19.0% [14.5, 23.5] | 22.0% [15.8, 28.1] | 20.5% [14.5, 26.5] | 21.5% [16.3, 26.7] |
| health_literacy | Recovery within 14 days | 7.5% [4.4, 10.7] | 13.5% [9.2, 17.9] | 14.5% [10.4, 18.6] | 14.2% [9.7, 18.7] |
| health_literacy | Retention at end | 21.8% [17.4, 26.2] | 20.6% [15.8, 25.4] | 19.8% [15.3, 24.4] | 19.6% [15.1, 24.1] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 6.1 min [2.8, 9.5] | 6.1 min [3.7, 8.6] | 14.4 min [8.9, 19.9] | 14.7 min [8.6, 20.8] |
| language | Persistence, week 12 | 8.3% [4.6, 12.0] | 8.7% [5.4, 12.1] | 9.4% [5.4, 13.4] | 8.9% [4.6, 13.3] |
| language | Recovery within 14 days | 6.3% [3.7, 8.8] | 5.6% [3.1, 8.1] | 5.4% [3.4, 7.4] | 4.8% [2.4, 7.3] |
| language | Retention at end | 8.4% [4.7, 12.1] | 6.6% [4.6, 8.6] | 7.1% [5.2, 9.0] | 6.3% [4.2, 8.4] |
| language | Δ weekly active minutes (wk1→wk12) | 5.0 min [3.4, 6.7] | 5.2 min [2.6, 7.8] | 8.8 min [5.5, 12.1] | 8.9 min [5.7, 12.1] |
| mobility_limitation | Persistence, week 12 | 14.0% [9.7, 18.4] | 18.5% [9.3, 27.7] | 19.6% [9.9, 29.3] | 19.1% [9.8, 28.3] |
| mobility_limitation | Recovery within 14 days | 11.5% [7.3, 15.6] | 15.5% [9.8, 21.1] | 18.4% [13.8, 22.9] | 16.2% [11.5, 20.9] |
| mobility_limitation | Retention at end | 20.4% [11.7, 29.2] | 15.1% [9.3, 21.0] | 15.8% [8.9, 22.6] | 16.0% [9.1, 22.8] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.9 min [6.4, 13.5] | 7.9 min [4.5, 11.2] | 9.1 min [4.3, 14.0] | 9.8 min [4.9, 14.7] |
| schedule_type | Persistence, week 12 | 16.2% [12.0, 20.4] | 12.9% [9.9, 15.9] | 12.9% [9.3, 16.5] | 13.1% [9.3, 17.0] |
| schedule_type | Recovery within 14 days | 11.3% [9.0, 13.7] | 14.7% [11.4, 18.0] | 13.4% [9.9, 16.8] | 12.2% [9.0, 15.4] |
| schedule_type | Retention at end | 13.4% [9.8, 17.1] | 11.3% [8.2, 14.4] | 11.7% [7.8, 15.6] | 11.5% [7.7, 15.2] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 11.9 min [8.9, 14.9] | 10.1 min [7.4, 12.8] | 21.6 min [17.7, 25.5] | 20.3 min [15.5, 25.1] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.1 [12.1, 12.2] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.1 [12.1, 12.2] messages per persona-week

### Where Rebound doesn't help

- Persistence, week 12 vs A0: -0.2 pts [-1.0, +0.6] (no clear difference)
- Persistence, weeks 4+8+12 vs A0: -1.5 pts [-2.8, -0.3] (Rebound is worse)
- Recovery within 14 days, after a labelled disruption vs A0: +2.2 pts [-0.7, +5.1] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +1.6 pts [-0.6, +3.8] (no clear difference)
- Median days from lapse to active vs A0: +0.1 d [-0.3, +0.5] (no clear difference)
- Retention at end vs A0: -0.0 pts [-0.7, +0.7] (no clear difference)
