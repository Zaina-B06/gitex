## Simulation results: scenario `ramadan_heavy`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 49.5% [47.3, 51.7] | 74.2% [73.3, 75.1] | 74.0% [72.7, 75.2] | 74.1% [72.7, 75.5] |
| Persistence, week 8 | 36.9% [35.1, 38.7] | 63.9% [61.6, 66.1] | 64.0% [61.6, 66.4] | 64.1% [61.8, 66.3] |
| Persistence, week 12 | 33.2% [31.0, 35.4] | 58.7% [56.7, 60.6] | 58.5% [56.5, 60.6] | 58.1% [56.3, 60.0] |
| Persistence, weeks 4+8+12 | 17.6% [15.7, 19.5] | 44.6% [42.4, 46.8] | 44.1% [41.5, 46.6] | 43.5% [41.1, 46.0] |
| Recovery within 14 days | 36.6% [35.2, 38.0] | 53.7% [52.3, 55.1] | 55.1% [53.3, 56.9] | 54.9% [53.1, 56.6] |
| Recovery within 14 days, after a labelled disruption | 35.5% [33.4, 37.7] | 51.9% [50.0, 53.8] | 53.6% [51.7, 55.4] | 53.5% [51.6, 55.4] |
| Recovery within 14 days, after an unlabelled shock | 40.5% [37.4, 43.7] | 58.5% [55.0, 62.1] | 60.5% [58.2, 62.9] | 59.4% [57.8, 61.0] |
| Recovery within 14 days, no disruption nearby | 36.4% [34.6, 38.1] | 53.2% [50.2, 56.2] | 54.2% [51.2, 57.1] | 54.2% [51.2, 57.3] |
| Median days from lapse to active | 11.5 d [10.9, 12.1] | 9.0 d [8.7, 9.3] | 8.9 d [8.7, 9.2] | 8.8 d [8.5, 9.1] |
| Median days from lapse to recovering | 5.8 d [5.5, 6.1] | 4.6 d [4.2, 5.0] | 4.6 d [4.2, 5.0] | 4.7 d [4.3, 5.0] |
| Δ weekly active minutes (wk1→wk12) | -20.7 min [-21.8, -19.7] | -12.6 min [-13.7, -11.5] | -4.6 min [-6.1, -3.1] | -3.9 min [-5.6, -2.2] |
| Δ tier-weighted sleep nights (wk1→wk12) | -9.0% [-9.3, -8.6] | -5.5% [-5.9, -5.0] | 5.0% [3.5, 6.4] | 4.9% [3.4, 6.4] |
| Δ sleep nights completed, raw (wk1→wk12) | -35.5% [-36.8, -34.2] | -21.6% [-23.4, -19.8] | -25.3% [-27.1, -23.5] | -25.5% [-27.3, -23.8] |
| Retention at end | 61.9% [59.9, 64.0] | 75.8% [73.3, 78.2] | 76.1% [73.9, 78.3] | 76.0% [73.9, 78.0] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.1 [12.1, 12.2] | 12.1 [12.1, 12.2] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +18.3 pts [+16.1, +20.4] (helps) | +25.0 pts [+23.7, +26.3] (helps) | +14.0 pts [+12.7, +15.4] (helps) |
| C vs A0 | +1.2 pts [+0.0, +2.4] (helps) | -0.5 pts [-1.4, +0.3] (not shown) | +0.2 pts [-0.5, +0.9] (not shown) |
| C vs B | -0.2 pts [-0.7, +0.3] (not shown) | -0.4 pts [-0.9, +0.1] (not shown) | -0.1 pts [-0.7, +0.4] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +25.4 pts [+24.0, +26.7]
- B vs A, persistence, weeks 4+8+12: +26.5 pts [+24.6, +28.4]
- B vs A, recovery within 14 days: +18.5 pts [+16.3, +20.7]
- B vs A, recovery within 14 days, after a labelled disruption: +18.1 pts [+15.1, +21.0]
- B vs A, recovery within 14 days, after an unlabelled shock: +20.0 pts [+16.5, +23.5]
- B vs A, median days from lapse to active: -2.5 d [-3.1, -2.0]
- B vs A, retention at end: +14.2 pts [+12.6, +15.7]
- B vs A, δ weekly active minutes (wk1→wk12): +16.1 min [+14.9, +17.3]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +13.9 pts [+12.6, +15.2]
- C vs A, persistence, week 12: +25.0 pts [+23.7, +26.3]
- C vs A, persistence, weeks 4+8+12: +25.9 pts [+24.2, +27.7]
- C vs A, recovery within 14 days: +18.3 pts [+16.1, +20.4]
- C vs A, recovery within 14 days, after a labelled disruption: +18.0 pts [+15.5, +20.4]
- C vs A, recovery within 14 days, after an unlabelled shock: +18.8 pts [+15.4, +22.3]
- C vs A, median days from lapse to active: -2.7 d [-3.3, -2.1]
- C vs A, retention at end: +14.0 pts [+12.7, +15.4]
- C vs A, δ weekly active minutes (wk1→wk12): +16.8 min [+15.5, +18.2]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +13.9 pts [+12.4, +15.3]
- C vs A0, persistence, week 12: -0.5 pts [-1.4, +0.3]
- C vs A0, persistence, weeks 4+8+12: -1.1 pts [-2.1, -0.1]
- C vs A0, recovery within 14 days: +1.2 pts [+0.0, +2.4]
- C vs A0, recovery within 14 days, after a labelled disruption: +1.6 pts [-0.2, +3.4]
- C vs A0, recovery within 14 days, after an unlabelled shock: +0.8 pts [-2.1, +3.7]
- C vs A0, median days from lapse to active: -0.2 d [-0.5, +0.1]
- C vs A0, retention at end: +0.2 pts [-0.5, +0.9]
- C vs A0, δ weekly active minutes (wk1→wk12): +8.7 min [+7.2, +10.2]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +10.4 pts [+8.9, +11.9]
- C vs B, persistence, week 12: -0.4 pts [-0.9, +0.1]
- C vs B, persistence, weeks 4+8+12: -0.5 pts [-1.5, +0.4]
- C vs B, recovery within 14 days: -0.2 pts [-0.7, +0.3]
- C vs B, recovery within 14 days, after a labelled disruption: -0.1 pts [-1.0, +0.8]
- C vs B, recovery within 14 days, after an unlabelled shock: -1.2 pts [-2.5, +0.1]
- C vs B, median days from lapse to active: -0.1 d [-0.4, +0.1]
- C vs B, retention at end: -0.1 pts [-0.7, +0.4]
- C vs B, δ weekly active minutes (wk1→wk12): +0.7 min [-0.1, +1.5]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): -0.0 pts [-0.4, +0.4]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 19.4% [14.5, 24.2] | 21.9% [16.0, 27.9] | 21.4% [15.7, 27.0] | 21.5% [16.5, 26.4] |
| health_literacy | Recovery within 14 days | 7.3% [4.3, 10.3] | 13.6% [9.1, 18.2] | 13.8% [10.1, 17.5] | 13.9% [10.2, 17.6] |
| health_literacy | Retention at end | 21.6% [17.2, 26.0] | 20.2% [15.4, 25.0] | 20.6% [15.5, 25.7] | 20.0% [14.8, 25.2] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 6.0 min [2.7, 9.2] | 6.2 min [3.7, 8.7] | 15.0 min [10.2, 19.9] | 14.9 min [9.6, 20.3] |
| language | Persistence, week 12 | 8.2% [4.8, 11.5] | 8.7% [5.4, 12.0] | 8.5% [3.8, 13.2] | 8.9% [5.0, 12.7] |
| language | Recovery within 14 days | 5.4% [2.9, 7.8] | 5.8% [3.4, 8.2] | 6.2% [4.3, 8.1] | 5.7% [3.7, 7.7] |
| language | Retention at end | 8.3% [4.9, 11.7] | 6.9% [4.9, 8.9] | 7.4% [5.3, 9.5] | 7.3% [5.2, 9.5] |
| language | Δ weekly active minutes (wk1→wk12) | 4.8 min [3.1, 6.6] | 5.0 min [2.5, 7.5] | 8.4 min [5.0, 11.7] | 9.5 min [6.3, 12.7] |
| mobility_limitation | Persistence, week 12 | 14.0% [9.9, 18.1] | 18.5% [9.3, 27.7] | 17.8% [9.3, 26.3] | 18.7% [10.2, 27.3] |
| mobility_limitation | Recovery within 14 days | 11.5% [7.6, 15.4] | 15.2% [9.6, 20.9] | 17.0% [12.4, 21.6] | 17.2% [12.0, 22.4] |
| mobility_limitation | Retention at end | 20.2% [11.2, 29.1] | 15.0% [9.2, 20.9] | 15.9% [8.9, 22.9] | 16.6% [10.0, 23.1] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 10.0 min [6.4, 13.7] | 7.8 min [4.5, 11.2] | 9.5 min [4.6, 14.3] | 10.5 min [5.6, 15.4] |
| schedule_type | Persistence, week 12 | 15.0% [10.6, 19.4] | 12.6% [9.7, 15.5] | 12.5% [9.1, 15.9] | 12.8% [9.0, 16.6] |
| schedule_type | Recovery within 14 days | 11.1% [8.1, 14.0] | 14.8% [11.6, 18.0] | 14.2% [10.4, 18.0] | 12.0% [9.1, 14.8] |
| schedule_type | Retention at end | 13.5% [9.8, 17.1] | 11.1% [8.2, 14.0] | 11.3% [7.8, 14.7] | 10.8% [6.7, 15.0] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 11.5 min [8.5, 14.4] | 10.2 min [7.7, 12.7] | 22.0 min [16.8, 27.2] | 20.9 min [15.5, 26.2] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.1 [12.1, 12.2] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.1 [12.1, 12.2] messages per persona-week

### Where Rebound doesn't help

- Persistence, week 12 vs A0: -0.5 pts [-1.4, +0.3] (no clear difference)
- Persistence, weeks 4+8+12 vs A0: -1.1 pts [-2.1, -0.1] (Rebound is worse)
- Recovery within 14 days, after a labelled disruption vs A0: +1.6 pts [-0.2, +3.4] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +0.8 pts [-2.1, +3.7] (no clear difference)
- Median days from lapse to active vs A0: -0.2 d [-0.5, +0.1] (no clear difference)
- Retention at end vs A0: +0.2 pts [-0.5, +0.9] (no clear difference)
