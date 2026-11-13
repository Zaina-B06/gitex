## Simulation results: scenario `harsh_attrition`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 34.1% [32.8, 35.4] | 59.7% [58.1, 61.4] | 58.8% [57.5, 60.2] | 58.9% [57.3, 60.4] |
| Persistence, week 8 | 21.6% [20.3, 22.8] | 43.3% [41.8, 44.8] | 42.8% [41.5, 44.1] | 43.0% [41.7, 44.4] |
| Persistence, week 12 | 19.0% [17.7, 20.3] | 36.7% [35.0, 38.3] | 36.5% [35.0, 38.1] | 36.4% [34.6, 38.1] |
| Persistence, weeks 4+8+12 | 9.1% [8.4, 9.8] | 25.7% [23.9, 27.4] | 24.7% [23.1, 26.4] | 24.8% [23.1, 26.6] |
| Recovery within 14 days | 29.3% [28.0, 30.7] | 42.6% [41.2, 44.1] | 42.6% [41.5, 43.7] | 42.1% [40.7, 43.5] |
| Recovery within 14 days, after a labelled disruption | 29.7% [27.4, 32.0] | 41.4% [39.0, 43.8] | 41.8% [39.5, 44.1] | 40.6% [38.0, 43.2] |
| Recovery within 14 days, after an unlabelled shock | 31.7% [29.1, 34.2] | 46.3% [41.9, 50.6] | 48.1% [44.2, 52.0] | 46.7% [42.6, 50.8] |
| Recovery within 14 days, no disruption nearby | 28.7% [27.1, 30.2] | 42.3% [40.5, 44.1] | 41.5% [40.1, 43.0] | 41.7% [39.9, 43.6] |
| Median days from lapse to active | 10.9 d [10.2, 11.6] | 9.1 d [8.6, 9.5] | 9.7 d [9.1, 10.3] | 9.4 d [8.8, 10.0] |
| Median days from lapse to recovering | 5.9 d [5.7, 6.1] | 4.8 d [4.5, 5.1] | 5.0 d [5.0, 5.0] | 5.0 d [5.0, 5.0] |
| Δ weekly active minutes (wk1→wk12) | -23.2 min [-24.2, -22.3] | -19.1 min [-20.1, -18.1] | -14.8 min [-15.8, -13.8] | -14.8 min [-16.0, -13.7] |
| Δ tier-weighted sleep nights (wk1→wk12) | -10.2% [-10.5, -10.0] | -8.4% [-8.7, -8.1] | -3.7% [-4.7, -2.7] | -3.9% [-4.8, -3.0] |
| Δ sleep nights completed, raw (wk1→wk12) | -40.5% [-41.6, -39.4] | -33.3% [-34.5, -32.1] | -34.7% [-35.9, -33.5] | -35.0% [-36.2, -33.8] |
| Retention at end | 39.0% [37.3, 40.7] | 53.4% [51.7, 55.2] | 53.4% [51.7, 55.1] | 53.5% [51.9, 55.1] |
| Lapse rate (≥ 1 lapse in the run) | 98.4% [98.0, 98.9] | 93.7% [92.4, 95.0] | 94.3% [93.2, 95.5] | 94.2% [93.1, 95.4] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.2, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +12.8 pts [+11.2, +14.3] (helps) | +17.4 pts [+15.5, +19.3] (helps) | +14.5 pts [+12.8, +16.2] (helps) |
| C vs A0 | -0.5 pts [-1.4, +0.3] (not shown) | -0.3 pts [-0.8, +0.2] (not shown) | +0.1 pts [-0.5, +0.6] (not shown) |
| C vs B | -0.5 pts [-1.2, +0.2] (not shown) | -0.2 pts [-0.7, +0.4] (not shown) | +0.1 pts [-0.5, +0.7] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +17.5 pts [+15.8, +19.3]
- B vs A, persistence, weeks 4+8+12: +15.6 pts [+13.9, +17.3]
- B vs A, recovery within 14 days: +13.3 pts [+12.2, +14.4]
- B vs A, recovery within 14 days, after a labelled disruption: +12.1 pts [+9.8, +14.4]
- B vs A, recovery within 14 days, after an unlabelled shock: +16.4 pts [+14.0, +18.9]
- B vs A, median days from lapse to active: -1.2 d [-2.0, -0.4]
- B vs A, retention at end: +14.4 pts [+12.8, +16.0]
- B vs A, δ weekly active minutes (wk1→wk12): +8.5 min [+7.3, +9.6]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +6.5 pts [+5.5, +7.5]
- B vs A, lapse rate (≥ 1 lapse in the run): -4.1 pts [-5.0, -3.2]
- B vs A, messages per persona-week: +0.5 [+0.5, +0.6]
- C vs A, persistence, week 12: +17.4 pts [+15.5, +19.3]
- C vs A, persistence, weeks 4+8+12: +15.7 pts [+13.8, +17.7]
- C vs A, recovery within 14 days: +12.8 pts [+11.2, +14.3]
- C vs A, recovery within 14 days, after a labelled disruption: +10.9 pts [+8.7, +13.2]
- C vs A, recovery within 14 days, after an unlabelled shock: +15.0 pts [+12.8, +17.3]
- C vs A, median days from lapse to active: -1.5 d [-2.1, -0.9]
- C vs A, retention at end: +14.5 pts [+12.8, +16.2]
- C vs A, δ weekly active minutes (wk1→wk12): +8.4 min [+7.2, +9.6]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +6.4 pts [+5.4, +7.3]
- C vs A, lapse rate (≥ 1 lapse in the run): -4.2 pts [-5.2, -3.2]
- C vs A, messages per persona-week: +0.5 [+0.5, +0.6]
- C vs A0, persistence, week 12: -0.3 pts [-0.8, +0.2]
- C vs A0, persistence, weeks 4+8+12: -0.8 pts [-1.7, +0.0]
- C vs A0, recovery within 14 days: -0.5 pts [-1.4, +0.3]
- C vs A0, recovery within 14 days, after a labelled disruption: -0.8 pts [-2.0, +0.5]
- C vs A0, recovery within 14 days, after an unlabelled shock: +0.4 pts [-1.6, +2.5]
- C vs A0, median days from lapse to active: +0.3 d [+0.0, +0.7]
- C vs A0, retention at end: +0.1 pts [-0.5, +0.6]
- C vs A0, δ weekly active minutes (wk1→wk12): +4.3 min [+3.0, +5.5]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +4.6 pts [+3.7, +5.4]
- C vs A0, lapse rate (≥ 1 lapse in the run): +0.5 pts [+0.2, +0.9]
- C vs A0, messages per persona-week: +0.5 [+0.4, +0.5]
- C vs B, persistence, week 12: -0.2 pts [-0.7, +0.4]
- C vs B, persistence, weeks 4+8+12: +0.1 pts [-0.3, +0.5]
- C vs B, recovery within 14 days: -0.5 pts [-1.2, +0.2]
- C vs B, recovery within 14 days, after a labelled disruption: -1.2 pts [-2.0, -0.4]
- C vs B, recovery within 14 days, after an unlabelled shock: -1.4 pts [-2.7, -0.1]
- C vs B, median days from lapse to active: -0.3 d [-0.8, +0.2]
- C vs B, retention at end: +0.1 pts [-0.5, +0.7]
- C vs B, δ weekly active minutes (wk1→wk12): -0.1 min [-0.5, +0.4]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): -0.1 pts [-0.4, +0.1]
- C vs B, lapse rate (≥ 1 lapse in the run): -0.1 pts [-0.3, +0.1]
- C vs B, messages per persona-week: -0.0 [-0.0, -0.0]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 12.0% [9.0, 14.9] | 16.4% [10.6, 22.3] | 17.1% [11.6, 22.5] | 17.1% [11.5, 22.8] |
| health_literacy | Recovery within 14 days | 7.5% [4.5, 10.6] | 7.4% [3.8, 10.9] | 8.4% [6.0, 10.9] | 8.6% [6.0, 11.2] |
| health_literacy | Retention at end | 19.3% [14.8, 23.8] | 19.7% [15.6, 23.8] | 19.1% [14.1, 24.0] | 18.5% [13.5, 23.6] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 5.9 min [3.1, 8.7] | 5.1 min [2.4, 7.7] | 8.6 min [4.8, 12.5] | 8.5 min [4.8, 12.2] |
| language | Persistence, week 12 | 6.7% [4.3, 9.1] | 7.5% [5.2, 9.7] | 8.4% [5.9, 11.0] | 8.9% [6.1, 11.8] |
| language | Recovery within 14 days | 5.1% [2.5, 7.6] | 7.4% [4.8, 10.0] | 6.8% [4.4, 9.2] | 6.1% [3.9, 8.4] |
| language | Retention at end | 9.0% [5.1, 12.9] | 9.7% [6.4, 13.1] | 8.8% [6.2, 11.4] | 8.5% [5.9, 11.1] |
| language | Δ weekly active minutes (wk1→wk12) | 5.3 min [3.3, 7.2] | 5.5 min [4.1, 6.9] | 8.2 min [5.6, 10.7] | 8.0 min [5.4, 10.6] |
| mobility_limitation | Persistence, week 12 | 9.4% [6.7, 12.1] | 16.7% [9.1, 24.3] | 16.1% [9.0, 23.2] | 15.6% [9.1, 22.2] |
| mobility_limitation | Recovery within 14 days | 9.4% [6.5, 12.4] | 13.7% [6.3, 21.0] | 13.1% [6.1, 20.1] | 12.5% [4.5, 20.6] |
| mobility_limitation | Retention at end | 18.7% [9.1, 28.3] | 20.2% [10.8, 29.5] | 18.0% [10.9, 25.2] | 19.2% [12.2, 26.2] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.5 min [7.6, 11.4] | 9.5 min [6.2, 12.8] | 9.4 min [6.0, 12.9] | 9.9 min [6.2, 13.5] |
| schedule_type | Persistence, week 12 | 15.4% [12.6, 18.1] | 16.0% [10.9, 21.0] | 14.3% [9.3, 19.3] | 13.8% [8.5, 19.0] |
| schedule_type | Recovery within 14 days | 11.0% [8.3, 13.7] | 14.4% [10.5, 18.3] | 17.6% [14.8, 20.4] | 18.0% [15.0, 21.0] |
| schedule_type | Retention at end | 19.9% [15.2, 24.5] | 14.7% [11.4, 18.1] | 14.1% [10.7, 17.5] | 14.7% [11.8, 17.6] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 9.3 min [5.6, 13.1] | 11.2 min [7.9, 14.4] | 17.1 min [11.4, 22.9] | 17.5 min [11.7, 23.3] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.2, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Messages per persona-week vs A: +0.5 [+0.5, +0.6] (Rebound is worse)
- Persistence, week 12 vs A0: -0.3 pts [-0.8, +0.2] (no clear difference)
- Persistence, weeks 4+8+12 vs A0: -0.8 pts [-1.7, +0.0] (no clear difference)
- Recovery within 14 days vs A0: -0.5 pts [-1.4, +0.3] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: -0.8 pts [-2.0, +0.5] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +0.4 pts [-1.6, +2.5] (no clear difference)
- Median days from lapse to active vs A0: +0.3 d [+0.0, +0.7] (Rebound is worse)
- Retention at end vs A0: +0.1 pts [-0.5, +0.6] (no clear difference)
- Lapse rate (≥ 1 lapse in the run) vs A0: +0.5 pts [+0.2, +0.9] (Rebound is worse)
- Messages per persona-week vs A0: +0.5 [+0.4, +0.5] (Rebound is worse)
