## Simulation results: scenario `harsh_attrition`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 34.1% [32.8, 35.4] | 59.7% [58.1, 61.4] | 58.6% [56.5, 60.7] | 59.1% [57.1, 61.1] |
| Persistence, week 8 | 21.6% [20.3, 22.8] | 43.3% [41.8, 44.8] | 43.1% [41.8, 44.5] | 42.8% [41.6, 44.0] |
| Persistence, week 12 | 19.0% [17.7, 20.3] | 36.7% [35.0, 38.3] | 36.5% [35.0, 37.9] | 36.5% [34.8, 38.3] |
| Persistence, weeks 4+8+12 | 9.1% [8.4, 9.8] | 25.7% [23.9, 27.4] | 24.7% [22.8, 26.6] | 24.9% [22.9, 26.9] |
| Recovery within 14 days | 29.3% [28.0, 30.7] | 42.6% [41.2, 44.1] | 43.1% [41.5, 44.6] | 43.3% [41.7, 44.8] |
| Recovery within 14 days, after a labelled disruption | 29.7% [27.4, 32.0] | 41.4% [39.0, 43.8] | 41.7% [38.7, 44.8] | 42.1% [39.2, 44.9] |
| Recovery within 14 days, after an unlabelled shock | 31.7% [29.1, 34.2] | 46.3% [41.9, 50.6] | 47.7% [43.4, 52.0] | 48.6% [45.1, 52.1] |
| Recovery within 14 days, no disruption nearby | 28.7% [27.1, 30.2] | 42.3% [40.5, 44.1] | 42.6% [41.3, 43.9] | 42.4% [40.8, 44.0] |
| Median days from lapse to active | 10.9 d [10.2, 11.6] | 9.1 d [8.6, 9.5] | 9.2 d [8.7, 9.7] | 9.2 d [8.7, 9.7] |
| Median days from lapse to recovering | 5.9 d [5.7, 6.1] | 4.8 d [4.5, 5.1] | 5.0 d [5.0, 5.0] | 5.0 d [5.0, 5.0] |
| Δ weekly active minutes (wk1→wk12) | -23.2 min [-24.2, -22.3] | -19.1 min [-20.1, -18.1] | -14.8 min [-15.8, -13.9] | -14.7 min [-16.0, -13.4] |
| Δ tier-weighted sleep nights (wk1→wk12) | -10.2% [-10.5, -10.0] | -8.4% [-8.7, -8.1] | -3.6% [-4.5, -2.7] | -3.6% [-4.5, -2.6] |
| Δ sleep nights completed, raw (wk1→wk12) | -40.5% [-41.6, -39.4] | -33.3% [-34.5, -32.1] | -34.6% [-35.7, -33.5] | -34.6% [-35.7, -33.5] |
| Retention at end | 39.0% [37.3, 40.7] | 53.4% [51.7, 55.2] | 53.8% [52.6, 55.1] | 53.4% [51.9, 54.9] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.1, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +13.9 pts [+12.2, +15.7] (helps) | +17.5 pts [+15.8, +19.3] (helps) | +14.4 pts [+12.6, +16.1] (helps) |
| C vs A0 | +0.6 pts [-0.4, +1.7] (not shown) | -0.1 pts [-0.8, +0.5] (not shown) | -0.1 pts [-1.1, +0.9] (not shown) |
| C vs B | +0.2 pts [-0.3, +0.7] (not shown) | +0.1 pts [-0.3, +0.4] (not shown) | -0.5 pts [-0.9, -0.0] (worse) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +17.5 pts [+15.9, +19.0]
- B vs A, persistence, weeks 4+8+12: +15.6 pts [+13.7, +17.5]
- B vs A, recovery within 14 days: +13.7 pts [+12.1, +15.3]
- B vs A, recovery within 14 days, after a labelled disruption: +12.1 pts [+9.3, +14.8]
- B vs A, recovery within 14 days, after an unlabelled shock: +16.0 pts [+12.6, +19.5]
- B vs A, median days from lapse to active: -1.7 d [-2.4, -1.0]
- B vs A, retention at end: +14.8 pts [+13.2, +16.5]
- B vs A, δ weekly active minutes (wk1→wk12): +8.4 min [+7.2, +9.6]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +6.6 pts [+5.7, +7.6]
- C vs A, persistence, week 12: +17.5 pts [+15.8, +19.3]
- C vs A, persistence, weeks 4+8+12: +15.8 pts [+13.7, +17.9]
- C vs A, recovery within 14 days: +13.9 pts [+12.2, +15.7]
- C vs A, recovery within 14 days, after a labelled disruption: +12.4 pts [+9.8, +15.0]
- C vs A, recovery within 14 days, after an unlabelled shock: +16.9 pts [+14.5, +19.4]
- C vs A, median days from lapse to active: -1.7 d [-2.3, -1.1]
- C vs A, retention at end: +14.4 pts [+12.6, +16.1]
- C vs A, δ weekly active minutes (wk1→wk12): +8.5 min [+7.1, +10.0]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +6.6 pts [+5.7, +7.6]
- C vs A0, persistence, week 12: -0.1 pts [-0.8, +0.5]
- C vs A0, persistence, weeks 4+8+12: -0.8 pts [-1.6, +0.0]
- C vs A0, recovery within 14 days: +0.6 pts [-0.4, +1.7]
- C vs A0, recovery within 14 days, after a labelled disruption: +0.7 pts [-1.1, +2.5]
- C vs A0, recovery within 14 days, after an unlabelled shock: +2.3 pts [-0.3, +5.0]
- C vs A0, median days from lapse to active: +0.1 d [-0.1, +0.4]
- C vs A0, retention at end: -0.1 pts [-1.1, +0.9]
- C vs A0, δ weekly active minutes (wk1→wk12): +4.4 min [+3.2, +5.6]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +4.8 pts [+4.0, +5.7]
- C vs B, persistence, week 12: +0.1 pts [-0.3, +0.4]
- C vs B, persistence, weeks 4+8+12: +0.2 pts [-0.2, +0.6]
- C vs B, recovery within 14 days: +0.2 pts [-0.3, +0.7]
- C vs B, recovery within 14 days, after a labelled disruption: +0.3 pts [-0.4, +1.1]
- C vs B, recovery within 14 days, after an unlabelled shock: +0.9 pts [-0.5, +2.3]
- C vs B, median days from lapse to active: +0.0 d [-0.3, +0.3]
- C vs B, retention at end: -0.5 pts [-0.9, -0.0]
- C vs B, δ weekly active minutes (wk1→wk12): +0.1 min [-0.5, +0.8]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): -0.0 pts [-0.2, +0.2]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 12.0% [9.0, 14.9] | 16.4% [10.6, 22.3] | 18.1% [13.1, 23.1] | 18.8% [13.7, 23.9] |
| health_literacy | Recovery within 14 days | 7.5% [4.5, 10.6] | 7.4% [3.8, 10.9] | 6.3% [3.9, 8.7] | 6.9% [4.6, 9.3] |
| health_literacy | Retention at end | 19.3% [14.8, 23.8] | 19.7% [15.6, 23.8] | 20.1% [16.0, 24.3] | 20.6% [16.6, 24.5] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 5.9 min [3.1, 8.7] | 5.1 min [2.4, 7.7] | 8.3 min [4.6, 12.0] | 8.7 min [5.6, 11.8] |
| language | Persistence, week 12 | 6.7% [4.3, 9.1] | 7.5% [5.2, 9.7] | 8.2% [5.4, 11.0] | 9.0% [6.3, 11.7] |
| language | Recovery within 14 days | 5.1% [2.5, 7.6] | 7.4% [4.8, 10.0] | 5.5% [3.5, 7.4] | 6.3% [4.0, 8.6] |
| language | Retention at end | 9.0% [5.1, 12.9] | 9.7% [6.4, 13.1] | 10.0% [5.5, 14.4] | 10.1% [6.4, 13.8] |
| language | Δ weekly active minutes (wk1→wk12) | 5.3 min [3.3, 7.2] | 5.5 min [4.1, 6.9] | 8.1 min [5.5, 10.7] | 8.4 min [6.3, 10.4] |
| mobility_limitation | Persistence, week 12 | 9.4% [6.7, 12.1] | 16.7% [9.1, 24.3] | 14.9% [7.5, 22.4] | 14.7% [7.9, 21.4] |
| mobility_limitation | Recovery within 14 days | 9.4% [6.5, 12.4] | 13.7% [6.3, 21.0] | 13.5% [5.6, 21.4] | 14.4% [6.2, 22.6] |
| mobility_limitation | Retention at end | 18.7% [9.1, 28.3] | 20.2% [10.8, 29.5] | 17.2% [11.9, 22.5] | 16.7% [10.2, 23.2] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.5 min [7.6, 11.4] | 9.5 min [6.2, 12.8] | 8.8 min [5.5, 12.1] | 8.8 min [5.5, 12.1] |
| schedule_type | Persistence, week 12 | 15.4% [12.6, 18.1] | 16.0% [10.9, 21.0] | 15.1% [10.6, 19.5] | 13.8% [8.7, 18.9] |
| schedule_type | Recovery within 14 days | 11.0% [8.3, 13.7] | 14.4% [10.5, 18.3] | 15.9% [12.5, 19.3] | 15.8% [12.1, 19.5] |
| schedule_type | Retention at end | 19.9% [15.2, 24.5] | 14.7% [11.4, 18.1] | 14.5% [11.2, 17.7] | 14.7% [12.2, 17.2] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 9.3 min [5.6, 13.1] | 11.2 min [7.9, 14.4] | 17.0 min [10.8, 23.2] | 18.2 min [12.6, 23.7] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Persistence, week 12 vs A0: -0.1 pts [-0.8, +0.5] (no clear difference)
- Persistence, weeks 4+8+12 vs A0: -0.8 pts [-1.6, +0.0] (no clear difference)
- Recovery within 14 days vs A0: +0.6 pts [-0.4, +1.7] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: +0.7 pts [-1.1, +2.5] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +2.3 pts [-0.3, +5.0] (no clear difference)
- Median days from lapse to active vs A0: +0.1 d [-0.1, +0.4] (no clear difference)
- Retention at end vs A0: -0.1 pts [-1.1, +0.9] (no clear difference)
