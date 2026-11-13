## Simulation results: scenario `low_checkin`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 49.8% [47.6, 52.0] | 74.5% [73.6, 75.3] | 73.7% [72.1, 75.4] | 73.9% [72.3, 75.5] |
| Persistence, week 8 | 36.8% [35.0, 38.6] | 64.0% [61.8, 66.2] | 63.8% [61.5, 66.1] | 63.7% [61.4, 66.0] |
| Persistence, week 12 | 33.3% [31.2, 35.4] | 58.7% [56.7, 60.6] | 58.3% [56.1, 60.6] | 58.5% [56.4, 60.7] |
| Persistence, weeks 4+8+12 | 17.4% [15.6, 19.2] | 44.8% [42.5, 47.1] | 43.2% [40.3, 46.2] | 43.8% [40.9, 46.8] |
| Recovery within 14 days | 36.7% [35.3, 38.1] | 53.7% [52.3, 55.1] | 55.2% [53.7, 56.6] | 55.1% [53.6, 56.6] |
| Recovery within 14 days, after a labelled disruption | 35.8% [33.8, 37.8] | 51.8% [49.5, 54.1] | 53.4% [50.8, 56.0] | 54.6% [52.2, 57.0] |
| Recovery within 14 days, after an unlabelled shock | 40.3% [37.4, 43.2] | 58.4% [55.2, 61.6] | 60.5% [58.2, 62.7] | 59.7% [56.6, 62.8] |
| Recovery within 14 days, no disruption nearby | 36.3% [34.9, 37.7] | 53.3% [50.6, 56.0] | 54.4% [52.3, 56.4] | 53.6% [51.0, 56.2] |
| Median days from lapse to active | 11.6 d [11.0, 12.2] | 8.9 d [8.5, 9.3] | 8.9 d [8.5, 9.3] | 8.9 d [8.7, 9.1] |
| Median days from lapse to recovering | 5.9 d [5.7, 6.1] | 4.5 d [4.2, 4.9] | 4.5 d [4.1, 4.8] | 4.4 d [4.0, 4.8] |
| Δ weekly active minutes (wk1→wk12) | -20.7 min [-21.7, -19.7] | -12.6 min [-13.7, -11.5] | -5.9 min [-7.4, -4.3] | -5.5 min [-6.7, -4.2] |
| Δ tier-weighted sleep nights (wk1→wk12) | -9.0% [-9.3, -8.6] | -5.5% [-5.9, -5.0] | 3.4% [2.0, 4.8] | 3.5% [2.3, 4.8] |
| Δ sleep nights completed, raw (wk1→wk12) | -35.5% [-36.8, -34.2] | -21.5% [-23.3, -19.7] | -26.0% [-27.9, -24.0] | -25.8% [-27.6, -24.0] |
| Retention at end | 62.1% [60.0, 64.3] | 75.9% [73.3, 78.5] | 76.3% [74.0, 78.5] | 76.1% [74.2, 78.1] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.1, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +18.4 pts [+16.3, +20.6] (helps) | +25.2 pts [+23.3, +27.1] (helps) | +14.0 pts [+12.7, +15.3] (helps) |
| C vs A0 | +1.4 pts [-0.2, +2.9] (not shown) | -0.1 pts [-1.1, +0.8] (not shown) | +0.2 pts [-0.6, +1.0] (not shown) |
| C vs B | -0.0 pts [-0.5, +0.4] (not shown) | +0.2 pts [-0.3, +0.7] (not shown) | -0.1 pts [-0.6, +0.4] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +25.0 pts [+23.0, +27.1]
- B vs A, persistence, weeks 4+8+12: +25.8 pts [+23.6, +28.0]
- B vs A, recovery within 14 days: +18.4 pts [+16.6, +20.3]
- B vs A, recovery within 14 days, after a labelled disruption: +17.6 pts [+14.5, +20.7]
- B vs A, recovery within 14 days, after an unlabelled shock: +20.2 pts [+17.5, +22.9]
- B vs A, median days from lapse to active: -2.7 d [-3.3, -2.1]
- B vs A, retention at end: +14.1 pts [+12.9, +15.4]
- B vs A, δ weekly active minutes (wk1→wk12): +14.9 min [+13.7, +16.0]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +12.4 pts [+11.1, +13.7]
- C vs A, persistence, week 12: +25.2 pts [+23.3, +27.1]
- C vs A, persistence, weeks 4+8+12: +26.4 pts [+24.3, +28.5]
- C vs A, recovery within 14 days: +18.4 pts [+16.3, +20.6]
- C vs A, recovery within 14 days, after a labelled disruption: +18.8 pts [+15.6, +22.0]
- C vs A, recovery within 14 days, after an unlabelled shock: +19.4 pts [+15.6, +23.2]
- C vs A, median days from lapse to active: -2.7 d [-3.3, -2.1]
- C vs A, retention at end: +14.0 pts [+12.7, +15.3]
- C vs A, δ weekly active minutes (wk1→wk12): +15.3 min [+13.9, +16.7]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +12.5 pts [+11.3, +13.7]
- C vs A0, persistence, week 12: -0.1 pts [-1.1, +0.8]
- C vs A0, persistence, weeks 4+8+12: -1.0 pts [-2.4, +0.5]
- C vs A0, recovery within 14 days: +1.4 pts [-0.2, +2.9]
- C vs A0, recovery within 14 days, after a labelled disruption: +2.8 pts [+0.8, +4.8]
- C vs A0, recovery within 14 days, after an unlabelled shock: +1.3 pts [-1.0, +3.6]
- C vs A0, median days from lapse to active: +0.0 d [-0.5, +0.5]
- C vs A0, retention at end: +0.2 pts [-0.6, +1.0]
- C vs A0, δ weekly active minutes (wk1→wk12): +7.1 min [+5.7, +8.5]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +9.0 pts [+7.9, +10.2]
- C vs B, persistence, week 12: +0.2 pts [-0.3, +0.7]
- C vs B, persistence, weeks 4+8+12: +0.6 pts [+0.2, +1.0]
- C vs B, recovery within 14 days: -0.0 pts [-0.5, +0.4]
- C vs B, recovery within 14 days, after a labelled disruption: +1.2 pts [+0.5, +1.9]
- C vs B, recovery within 14 days, after an unlabelled shock: -0.7 pts [-2.1, +0.6]
- C vs B, median days from lapse to active: +0.0 d [-0.3, +0.3]
- C vs B, retention at end: -0.1 pts [-0.6, +0.4]
- C vs B, δ weekly active minutes (wk1→wk12): +0.4 min [-0.6, +1.5]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): +0.1 pts [-0.2, +0.5]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 19.0% [14.5, 23.5] | 22.0% [15.8, 28.1] | 22.2% [16.4, 28.0] | 22.4% [16.6, 28.2] |
| health_literacy | Recovery within 14 days | 7.5% [4.4, 10.7] | 13.5% [9.2, 17.9] | 15.1% [9.9, 20.4] | 14.7% [10.7, 18.8] |
| health_literacy | Retention at end | 21.8% [17.4, 26.2] | 20.6% [15.8, 25.4] | 19.1% [14.9, 23.4] | 20.7% [16.0, 25.5] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 6.1 min [2.8, 9.5] | 6.1 min [3.7, 8.6] | 14.4 min [9.5, 19.4] | 13.0 min [7.1, 19.0] |
| language | Persistence, week 12 | 8.3% [4.6, 12.0] | 8.7% [5.4, 12.1] | 8.4% [5.2, 11.7] | 9.2% [5.6, 12.8] |
| language | Recovery within 14 days | 6.3% [3.7, 8.8] | 5.6% [3.1, 8.1] | 4.9% [3.0, 6.9] | 5.6% [2.9, 8.4] |
| language | Retention at end | 8.4% [4.7, 12.1] | 6.6% [4.6, 8.6] | 7.0% [5.7, 8.2] | 6.0% [4.0, 8.0] |
| language | Δ weekly active minutes (wk1→wk12) | 5.0 min [3.4, 6.7] | 5.2 min [2.6, 7.8] | 8.7 min [4.4, 12.9] | 8.4 min [5.6, 11.3] |
| mobility_limitation | Persistence, week 12 | 14.0% [9.7, 18.4] | 18.5% [9.3, 27.7] | 21.2% [12.7, 29.6] | 21.1% [13.2, 29.0] |
| mobility_limitation | Recovery within 14 days | 11.5% [7.3, 15.6] | 15.5% [9.8, 21.1] | 10.4% [8.3, 12.5] | 13.8% [9.9, 17.6] |
| mobility_limitation | Retention at end | 20.4% [11.7, 29.2] | 15.1% [9.3, 21.0] | 15.4% [8.4, 22.5] | 17.2% [9.8, 24.5] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.9 min [6.4, 13.5] | 7.9 min [4.5, 11.2] | 9.7 min [5.3, 14.1] | 10.0 min [5.2, 14.8] |
| schedule_type | Persistence, week 12 | 16.2% [12.0, 20.4] | 12.9% [9.9, 15.9] | 13.9% [10.1, 17.6] | 13.8% [10.8, 16.8] |
| schedule_type | Recovery within 14 days | 11.3% [9.0, 13.7] | 14.7% [11.4, 18.0] | 13.4% [10.0, 16.7] | 12.7% [8.5, 17.0] |
| schedule_type | Retention at end | 13.4% [9.8, 17.1] | 11.3% [8.2, 14.4] | 10.7% [7.4, 14.1] | 11.9% [8.4, 15.3] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 11.9 min [8.9, 14.9] | 10.1 min [7.4, 12.8] | 21.2 min [16.2, 26.2] | 21.9 min [17.9, 25.9] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Persistence, week 12 vs A0: -0.1 pts [-1.1, +0.8] (no clear difference)
- Persistence, weeks 4+8+12 vs A0: -1.0 pts [-2.4, +0.5] (no clear difference)
- Recovery within 14 days vs A0: +1.4 pts [-0.2, +2.9] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +1.3 pts [-1.0, +3.6] (no clear difference)
- Median days from lapse to active vs A0: +0.0 d [-0.5, +0.5] (no clear difference)
- Retention at end vs A0: +0.2 pts [-0.6, +1.0] (no clear difference)
