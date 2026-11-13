## Simulation results: scenario `harsh_attrition`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 34.1% [32.8, 35.4] | 59.7% [58.1, 61.4] | 58.0% [56.1, 59.9] | 58.3% [56.5, 60.0] |
| Persistence, week 8 | 21.6% [20.3, 22.8] | 43.3% [41.8, 44.8] | 42.7% [41.6, 43.8] | 42.0% [40.9, 43.1] |
| Persistence, week 12 | 19.0% [17.7, 20.3] | 36.7% [35.0, 38.3] | 36.2% [34.5, 37.9] | 36.1% [34.4, 37.8] |
| Persistence, weeks 4+8+12 | 9.1% [8.4, 9.8] | 25.7% [23.9, 27.4] | 24.4% [22.4, 26.3] | 24.2% [22.5, 25.8] |
| Recovery within 14 days | 29.3% [28.0, 30.7] | 42.6% [41.2, 44.1] | 42.9% [41.4, 44.4] | 42.8% [41.2, 44.4] |
| Recovery within 14 days, after a labelled disruption | 29.7% [27.4, 32.0] | 41.4% [39.0, 43.8] | 41.6% [38.7, 44.5] | 42.3% [39.5, 45.1] |
| Recovery within 14 days, after an unlabelled shock | 31.7% [29.1, 34.2] | 46.3% [41.9, 50.6] | 47.7% [43.7, 51.7] | 48.2% [44.2, 52.2] |
| Recovery within 14 days, no disruption nearby | 28.7% [27.1, 30.2] | 42.3% [40.5, 44.1] | 42.3% [40.6, 44.1] | 41.6% [39.7, 43.4] |
| Median days from lapse to active | 10.9 d [10.2, 11.6] | 9.1 d [8.6, 9.5] | 9.3 d [8.7, 9.9] | 9.5 d [9.0, 10.0] |
| Median days from lapse to recovering | 5.9 d [5.7, 6.1] | 4.8 d [4.5, 5.1] | 4.9 d [4.7, 5.1] | 4.8 d [4.5, 5.1] |
| Δ weekly active minutes (wk1→wk12) | -23.2 min [-24.2, -22.3] | -19.1 min [-20.1, -18.1] | -16.9 min [-17.8, -15.9] | -16.9 min [-17.9, -15.9] |
| Δ tier-weighted sleep nights (wk1→wk12) | -10.2% [-10.5, -10.0] | -8.4% [-8.7, -8.1] | -5.1% [-6.1, -4.2] | -5.2% [-6.0, -4.5] |
| Δ sleep nights completed, raw (wk1→wk12) | -40.5% [-41.6, -39.4] | -33.3% [-34.5, -32.1] | -34.9% [-36.3, -33.6] | -35.1% [-36.4, -33.9] |
| Retention at end | 39.0% [37.3, 40.7] | 53.4% [51.7, 55.2] | 53.6% [52.3, 54.9] | 53.1% [51.7, 54.5] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.1, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +13.5 pts [+11.8, +15.2] (helps) | +17.1 pts [+15.5, +18.8] (helps) | +14.1 pts [+12.3, +15.9] (helps) |
| C vs A0 | +0.2 pts [-1.1, +1.6] (not shown) | -0.5 pts [-1.6, +0.5] (not shown) | -0.3 pts [-1.5, +0.8] (not shown) |
| C vs B | -0.0 pts [-0.7, +0.6] (not shown) | -0.1 pts [-0.8, +0.6] (not shown) | -0.5 pts [-1.1, +0.1] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +17.2 pts [+15.5, +19.0]
- B vs A, persistence, weeks 4+8+12: +15.3 pts [+13.3, +17.3]
- B vs A, recovery within 14 days: +13.5 pts [+12.0, +15.1]
- B vs A, recovery within 14 days, after a labelled disruption: +11.9 pts [+9.2, +14.6]
- B vs A, recovery within 14 days, after an unlabelled shock: +16.1 pts [+12.5, +19.7]
- B vs A, median days from lapse to active: -1.6 d [-2.3, -0.9]
- B vs A, retention at end: +14.6 pts [+13.1, +16.2]
- B vs A, δ weekly active minutes (wk1→wk12): +6.4 min [+5.4, +7.3]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +5.1 pts [+4.2, +6.0]
- C vs A, persistence, week 12: +17.1 pts [+15.5, +18.8]
- C vs A, persistence, weeks 4+8+12: +15.1 pts [+13.4, +16.8]
- C vs A, recovery within 14 days: +13.5 pts [+11.8, +15.2]
- C vs A, recovery within 14 days, after a labelled disruption: +12.7 pts [+10.1, +15.3]
- C vs A, recovery within 14 days, after an unlabelled shock: +16.5 pts [+13.6, +19.4]
- C vs A, median days from lapse to active: -1.4 d [-2.2, -0.6]
- C vs A, retention at end: +14.1 pts [+12.3, +15.9]
- C vs A, δ weekly active minutes (wk1→wk12): +6.3 min [+5.3, +7.3]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +5.0 pts [+4.2, +5.7]
- C vs A0, persistence, week 12: -0.5 pts [-1.6, +0.5]
- C vs A0, persistence, weeks 4+8+12: -1.5 pts [-2.1, -0.9]
- C vs A0, recovery within 14 days: +0.2 pts [-1.1, +1.6]
- C vs A0, recovery within 14 days, after a labelled disruption: +1.0 pts [-1.2, +3.1]
- C vs A0, recovery within 14 days, after an unlabelled shock: +1.9 pts [-1.2, +5.0]
- C vs A0, median days from lapse to active: +0.5 d [+0.1, +0.8]
- C vs A0, retention at end: -0.3 pts [-1.5, +0.8]
- C vs A0, δ weekly active minutes (wk1→wk12): +2.2 min [+1.0, +3.4]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +3.2 pts [+2.6, +3.8]
- C vs B, persistence, week 12: -0.1 pts [-0.8, +0.6]
- C vs B, persistence, weeks 4+8+12: -0.2 pts [-0.7, +0.3]
- C vs B, recovery within 14 days: -0.0 pts [-0.7, +0.6]
- C vs B, recovery within 14 days, after a labelled disruption: +0.8 pts [-0.7, +2.2]
- C vs B, recovery within 14 days, after an unlabelled shock: +0.4 pts [-2.1, +3.0]
- C vs B, median days from lapse to active: +0.2 d [-0.1, +0.5]
- C vs B, retention at end: -0.5 pts [-1.1, +0.1]
- C vs B, δ weekly active minutes (wk1→wk12): -0.0 min [-0.7, +0.6]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): -0.1 pts [-0.4, +0.2]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 12.0% [9.0, 14.9] | 16.4% [10.6, 22.3] | 17.1% [11.8, 22.5] | 17.0% [11.8, 22.3] |
| health_literacy | Recovery within 14 days | 7.5% [4.5, 10.6] | 7.4% [3.8, 10.9] | 6.1% [3.9, 8.4] | 6.7% [3.8, 9.5] |
| health_literacy | Retention at end | 19.3% [14.8, 23.8] | 19.7% [15.6, 23.8] | 20.4% [16.4, 24.5] | 20.0% [16.2, 23.8] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 5.9 min [3.1, 8.7] | 5.1 min [2.4, 7.7] | 8.0 min [4.6, 11.4] | 7.7 min [4.6, 10.9] |
| language | Persistence, week 12 | 6.7% [4.3, 9.1] | 7.5% [5.2, 9.7] | 8.3% [5.3, 11.4] | 9.5% [6.9, 12.1] |
| language | Recovery within 14 days | 5.1% [2.5, 7.6] | 7.4% [4.8, 10.0] | 6.4% [4.3, 8.5] | 6.1% [3.7, 8.6] |
| language | Retention at end | 9.0% [5.1, 12.9] | 9.7% [6.4, 13.1] | 9.9% [5.8, 13.9] | 10.1% [6.3, 14.0] |
| language | Δ weekly active minutes (wk1→wk12) | 5.3 min [3.3, 7.2] | 5.5 min [4.1, 6.9] | 8.6 min [6.1, 11.0] | 8.3 min [5.7, 10.9] |
| mobility_limitation | Persistence, week 12 | 9.4% [6.7, 12.1] | 16.7% [9.1, 24.3] | 15.1% [7.8, 22.3] | 14.5% [7.9, 21.2] |
| mobility_limitation | Recovery within 14 days | 9.4% [6.5, 12.4] | 13.7% [6.3, 21.0] | 11.6% [5.8, 17.5] | 13.8% [6.2, 21.3] |
| mobility_limitation | Retention at end | 18.7% [9.1, 28.3] | 20.2% [10.8, 29.5] | 16.8% [10.9, 22.7] | 17.4% [11.0, 23.7] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.5 min [7.6, 11.4] | 9.5 min [6.2, 12.8] | 9.9 min [6.7, 13.1] | 10.1 min [7.0, 13.1] |
| schedule_type | Persistence, week 12 | 15.4% [12.6, 18.1] | 16.0% [10.9, 21.0] | 15.8% [11.1, 20.6] | 15.5% [9.7, 21.3] |
| schedule_type | Recovery within 14 days | 11.0% [8.3, 13.7] | 14.4% [10.5, 18.3] | 16.9% [13.4, 20.4] | 16.4% [12.7, 20.2] |
| schedule_type | Retention at end | 19.9% [15.2, 24.5] | 14.7% [11.4, 18.1] | 15.0% [11.6, 18.3] | 15.1% [11.6, 18.5] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 9.3 min [5.6, 13.1] | 11.2 min [7.9, 14.4] | 17.7 min [11.1, 24.2] | 16.8 min [10.8, 22.8] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Persistence, week 12 vs A0: -0.5 pts [-1.6, +0.5] (no clear difference)
- Persistence, weeks 4+8+12 vs A0: -1.5 pts [-2.1, -0.9] (Rebound is worse)
- Recovery within 14 days vs A0: +0.2 pts [-1.1, +1.6] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: +1.0 pts [-1.2, +3.1] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +1.9 pts [-1.2, +5.0] (no clear difference)
- Median days from lapse to active vs A0: +0.5 d [+0.1, +0.8] (Rebound is worse)
- Retention at end vs A0: -0.3 pts [-1.5, +0.8] (no clear difference)
