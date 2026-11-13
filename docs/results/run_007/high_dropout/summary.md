## Simulation results: scenario `high_dropout`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 26.2% [24.9, 27.6] | 53.7% [51.9, 55.5] | 53.0% [50.7, 55.3] | 53.0% [50.8, 55.2] |
| Persistence, week 8 | 11.5% [10.2, 12.9] | 34.2% [32.8, 35.6] | 33.8% [32.3, 35.3] | 33.8% [32.1, 35.5] |
| Persistence, week 12 | 7.6% [6.7, 8.4] | 25.6% [24.0, 27.2] | 25.1% [23.5, 26.7] | 24.8% [23.4, 26.3] |
| Persistence, weeks 4+8+12 | 5.5% [4.5, 6.4] | 22.0% [20.4, 23.5] | 20.6% [18.8, 22.4] | 20.4% [18.6, 22.3] |
| Recovery within 14 days | 28.4% [27.0, 29.8] | 41.2% [39.5, 42.9] | 41.8% [40.4, 43.2] | 41.8% [40.6, 42.9] |
| Recovery within 14 days, after a labelled disruption | 31.9% [28.4, 35.4] | 42.7% [40.2, 45.3] | 43.8% [42.1, 45.4] | 43.5% [41.7, 45.4] |
| Recovery within 14 days, after an unlabelled shock | 25.6% [22.6, 28.6] | 40.8% [35.9, 45.7] | 41.9% [38.1, 45.7] | 43.1% [39.3, 47.0] |
| Recovery within 14 days, no disruption nearby | 27.4% [25.9, 28.9] | 40.5% [38.5, 42.5] | 40.7% [38.9, 42.4] | 40.4% [38.8, 41.9] |
| Median days from lapse to active | 7.1 d [6.7, 7.5] | 7.1 d [6.9, 7.3] | 7.0 d [7.0, 7.0] | 7.0 d [7.0, 7.0] |
| Median days from lapse to recovering | 4.0 d [4.0, 4.0] | 3.5 d [3.2, 3.9] | 3.7 d [3.4, 4.0] | 3.6 d [3.2, 4.0] |
| Δ weekly active minutes (wk1→wk12) | -24.9 min [-25.8, -24.0] | -20.7 min [-21.7, -19.7] | -15.6 min [-17.0, -14.2] | -15.1 min [-16.7, -13.6] |
| Δ tier-weighted sleep nights (wk1→wk12) | -11.2% [-11.5, -10.8] | -9.2% [-9.6, -8.9] | -5.5% [-6.3, -4.6] | -5.4% [-6.4, -4.5] |
| Δ sleep nights completed, raw (wk1→wk12) | -44.0% [-45.6, -42.4] | -36.2% [-37.6, -34.9] | -37.8% [-39.3, -36.2] | -38.1% [-39.7, -36.5] |
| Retention at end | 9.1% [7.9, 10.3] | 28.2% [26.7, 29.6] | 28.0% [26.4, 29.6] | 27.9% [26.4, 29.4] |
| Messages per persona-week | 11.5 [11.4, 11.6] | 11.8 [11.7, 11.9] | 12.3 [12.2, 12.4] | 12.3 [12.2, 12.4] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +13.3 pts [+11.8, +14.9] (helps) | +17.3 pts [+15.6, +18.9] (helps) | +18.7 pts [+17.5, +19.9] (helps) |
| C vs A0 | +0.6 pts [-0.6, +1.8] (not shown) | -0.7 pts [-1.3, -0.2] (worse) | -0.3 pts [-1.0, +0.4] (not shown) |
| C vs B | -0.0 pts [-0.8, +0.7] (not shown) | -0.3 pts [-0.9, +0.4] (not shown) | -0.1 pts [-0.6, +0.4] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +17.5 pts [+15.7, +19.4]
- B vs A, persistence, weeks 4+8+12: +15.1 pts [+13.3, +16.9]
- B vs A, recovery within 14 days: +13.4 pts [+11.4, +15.3]
- B vs A, recovery within 14 days, after a labelled disruption: +11.9 pts [+7.8, +15.9]
- B vs A, recovery within 14 days, after an unlabelled shock: +16.3 pts [+12.1, +20.5]
- B vs A, median days from lapse to active: -0.1 d [-0.5, +0.3]
- B vs A, retention at end: +18.9 pts [+17.5, +20.2]
- B vs A, δ weekly active minutes (wk1→wk12): +9.3 min [+8.0, +10.6]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +5.7 pts [+4.8, +6.6]
- C vs A, persistence, week 12: +17.3 pts [+15.6, +18.9]
- C vs A, persistence, weeks 4+8+12: +15.0 pts [+13.1, +16.8]
- C vs A, recovery within 14 days: +13.3 pts [+11.8, +14.9]
- C vs A, recovery within 14 days, after a labelled disruption: +11.6 pts [+8.3, +14.9]
- C vs A, recovery within 14 days, after an unlabelled shock: +17.5 pts [+13.1, +22.0]
- C vs A, median days from lapse to active: -0.1 d [-0.5, +0.3]
- C vs A, retention at end: +18.7 pts [+17.5, +19.9]
- C vs A, δ weekly active minutes (wk1→wk12): +9.8 min [+8.1, +11.4]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +5.7 pts [+4.7, +6.7]
- C vs A0, persistence, week 12: -0.7 pts [-1.3, -0.2]
- C vs A0, persistence, weeks 4+8+12: -1.5 pts [-2.2, -0.8]
- C vs A0, recovery within 14 days: +0.6 pts [-0.6, +1.8]
- C vs A0, recovery within 14 days, after a labelled disruption: +0.8 pts [-1.2, +2.8]
- C vs A0, recovery within 14 days, after an unlabelled shock: +2.3 pts [-1.3, +6.0]
- C vs A0, median days from lapse to active: -0.1 d [-0.3, +0.1]
- C vs A0, retention at end: -0.3 pts [-1.0, +0.4]
- C vs A0, δ weekly active minutes (wk1→wk12): +5.5 min [+4.0, +7.0]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +3.8 pts [+2.9, +4.6]
- C vs B, persistence, week 12: -0.3 pts [-0.9, +0.4]
- C vs B, persistence, weeks 4+8+12: -0.2 pts [-0.7, +0.4]
- C vs B, recovery within 14 days: -0.0 pts [-0.8, +0.7]
- C vs B, recovery within 14 days, after a labelled disruption: -0.3 pts [-1.8, +1.3]
- C vs B, recovery within 14 days, after an unlabelled shock: +1.2 pts [-0.6, +3.0]
- C vs B, median days from lapse to active: +0.0 d [+0.0, +0.0]
- C vs B, retention at end: -0.1 pts [-0.6, +0.4]
- C vs B, δ weekly active minutes (wk1→wk12): +0.5 min [-0.1, +1.0]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): +0.0 pts [-0.2, +0.3]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 6.8% [4.5, 9.2] | 17.3% [12.9, 21.7] | 15.3% [11.6, 19.1] | 15.7% [11.0, 20.5] |
| health_literacy | Recovery within 14 days | 10.8% [7.1, 14.5] | 9.3% [3.9, 14.7] | 8.3% [4.8, 11.7] | 7.7% [4.2, 11.2] |
| health_literacy | Retention at end | 9.2% [6.2, 12.2] | 18.1% [14.2, 22.1] | 16.7% [12.9, 20.5] | 17.4% [12.6, 22.2] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 8.0 min [5.3, 10.7] | 6.6 min [5.0, 8.2] | 9.6 min [5.8, 13.3] | 9.4 min [6.0, 12.7] |
| language | Persistence, week 12 | 3.3% [1.9, 4.7] | 6.4% [3.7, 9.0] | 6.2% [2.9, 9.5] | 5.6% [3.1, 8.1] |
| language | Recovery within 14 days | 7.8% [4.8, 10.8] | 8.5% [4.4, 12.6] | 8.3% [4.3, 12.3] | 7.1% [3.6, 10.6] |
| language | Retention at end | 3.7% [2.6, 4.9] | 7.9% [4.5, 11.3] | 8.0% [3.6, 12.5] | 8.1% [4.4, 11.8] |
| language | Δ weekly active minutes (wk1→wk12) | 5.2 min [3.2, 7.3] | 5.0 min [3.6, 6.3] | 7.8 min [6.1, 9.6] | 6.8 min [4.8, 8.8] |
| mobility_limitation | Persistence, week 12 | 10.1% [6.6, 13.6] | 14.5% [9.2, 19.9] | 12.6% [8.6, 16.6] | 11.9% [7.6, 16.2] |
| mobility_limitation | Recovery within 14 days | 10.8% [5.2, 16.4] | 10.8% [5.6, 16.0] | 13.1% [7.2, 19.1] | 12.2% [7.2, 17.1] |
| mobility_limitation | Retention at end | 11.7% [8.0, 15.3] | 16.2% [11.2, 21.2] | 15.5% [11.2, 19.8] | 15.6% [11.3, 19.8] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 10.4 min [8.3, 12.5] | 10.4 min [6.4, 14.5] | 7.9 min [3.1, 12.7] | 7.8 min [3.3, 12.3] |
| schedule_type | Persistence, week 12 | 10.5% [7.1, 13.9] | 12.8% [8.8, 16.8] | 14.2% [9.9, 18.6] | 13.6% [9.1, 18.1] |
| schedule_type | Recovery within 14 days | 12.3% [9.4, 15.3] | 14.3% [9.6, 19.0] | 15.0% [9.6, 20.4] | 13.9% [8.6, 19.2] |
| schedule_type | Retention at end | 11.1% [8.0, 14.1] | 13.5% [9.7, 17.2] | 14.5% [11.3, 17.8] | 14.4% [10.9, 18.0] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 9.8 min [7.1, 12.5] | 9.5 min [6.5, 12.6] | 15.5 min [9.9, 21.2] | 16.3 min [10.0, 22.6] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.5 [11.4, 11.6] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.3 [12.2, 12.4] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.3 [12.2, 12.4] messages per persona-week

### Where Rebound doesn't help

- Median days from lapse to active vs A: -0.1 d [-0.5, +0.3] (no clear difference)
- Persistence, week 12 vs A0: -0.7 pts [-1.3, -0.2] (Rebound is worse)
- Persistence, weeks 4+8+12 vs A0: -1.5 pts [-2.2, -0.8] (Rebound is worse)
- Recovery within 14 days vs A0: +0.6 pts [-0.6, +1.8] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: +0.8 pts [-1.2, +2.8] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +2.3 pts [-1.3, +6.0] (no clear difference)
- Median days from lapse to active vs A0: -0.1 d [-0.3, +0.1] (no clear difference)
- Retention at end vs A0: -0.3 pts [-1.0, +0.4] (no clear difference)
