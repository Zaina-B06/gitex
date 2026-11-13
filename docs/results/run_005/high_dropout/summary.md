## Simulation results: scenario `high_dropout`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 26.2% [24.9, 27.6] | 53.7% [51.9, 55.5] | 52.3% [49.8, 54.7] | 52.6% [50.2, 54.9] |
| Persistence, week 8 | 11.5% [10.2, 12.9] | 34.2% [32.8, 35.6] | 33.0% [31.4, 34.5] | 32.9% [31.4, 34.4] |
| Persistence, week 12 | 7.6% [6.7, 8.4] | 25.6% [24.0, 27.2] | 24.6% [23.1, 26.1] | 24.7% [23.4, 26.1] |
| Persistence, weeks 4+8+12 | 5.5% [4.5, 6.4] | 22.0% [20.4, 23.5] | 20.3% [18.5, 22.1] | 20.4% [18.8, 22.0] |
| Recovery within 14 days | 28.4% [27.0, 29.8] | 41.2% [39.5, 42.9] | 41.2% [40.1, 42.4] | 41.2% [40.2, 42.3] |
| Recovery within 14 days, after a labelled disruption | 31.9% [28.4, 35.4] | 42.7% [40.2, 45.3] | 43.3% [41.7, 44.9] | 43.0% [41.7, 44.4] |
| Recovery within 14 days, after an unlabelled shock | 25.6% [22.6, 28.6] | 40.8% [35.9, 45.7] | 41.9% [37.7, 46.0] | 42.4% [38.1, 46.6] |
| Recovery within 14 days, no disruption nearby | 27.4% [25.9, 28.9] | 40.5% [38.5, 42.5] | 39.8% [38.4, 41.2] | 39.8% [37.9, 41.8] |
| Median days from lapse to active | 7.1 d [6.7, 7.5] | 7.1 d [6.9, 7.3] | 7.0 d [6.7, 7.2] | 7.1 d [6.9, 7.3] |
| Median days from lapse to recovering | 4.0 d [4.0, 4.0] | 3.5 d [3.2, 3.9] | 3.5 d [3.1, 3.9] | 3.5 d [3.1, 3.9] |
| Δ weekly active minutes (wk1→wk12) | -24.9 min [-25.8, -24.0] | -20.7 min [-21.7, -19.7] | -17.3 min [-18.6, -16.0] | -16.8 min [-18.0, -15.6] |
| Δ tier-weighted sleep nights (wk1→wk12) | -11.2% [-11.5, -10.8] | -9.2% [-9.6, -8.9] | -6.7% [-7.5, -5.9] | -6.8% [-7.5, -6.1] |
| Δ sleep nights completed, raw (wk1→wk12) | -44.0% [-45.6, -42.4] | -36.2% [-37.6, -34.9] | -38.1% [-39.5, -36.7] | -38.4% [-40.0, -36.7] |
| Retention at end | 9.1% [7.9, 10.3] | 28.2% [26.7, 29.6] | 27.5% [26.1, 28.9] | 27.4% [26.1, 28.8] |
| Messages per persona-week | 11.5 [11.4, 11.6] | 11.8 [11.7, 11.9] | 12.3 [12.2, 12.4] | 12.3 [12.2, 12.4] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +12.8 pts [+11.1, +14.5] (helps) | +17.2 pts [+15.6, +18.7] (helps) | +18.3 pts [+17.1, +19.5] (helps) |
| C vs A0 | +0.0 pts [-1.0, +1.0] (not shown) | -0.8 pts [-1.4, -0.2] (worse) | -0.7 pts [-1.3, -0.2] (worse) |
| C vs B | +0.0 pts [-0.6, +0.6] (not shown) | +0.2 pts [-0.4, +0.8] (not shown) | -0.0 pts [-0.7, +0.6] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +17.0 pts [+15.4, +18.6]
- B vs A, persistence, weeks 4+8+12: +14.8 pts [+13.2, +16.5]
- B vs A, recovery within 14 days: +12.8 pts [+11.1, +14.5]
- B vs A, recovery within 14 days, after a labelled disruption: +11.4 pts [+7.7, +15.1]
- B vs A, recovery within 14 days, after an unlabelled shock: +16.3 pts [+12.1, +20.5]
- B vs A, median days from lapse to active: -0.1 d [-0.4, +0.1]
- B vs A, retention at end: +18.3 pts [+17.3, +19.4]
- B vs A, δ weekly active minutes (wk1→wk12): +7.6 min [+6.5, +8.7]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +4.5 pts [+3.7, +5.2]
- C vs A, persistence, week 12: +17.2 pts [+15.6, +18.7]
- C vs A, persistence, weeks 4+8+12: +15.0 pts [+13.3, +16.6]
- C vs A, recovery within 14 days: +12.8 pts [+11.1, +14.5]
- C vs A, recovery within 14 days, after a labelled disruption: +11.1 pts [+7.6, +14.6]
- C vs A, recovery within 14 days, after an unlabelled shock: +16.8 pts [+11.9, +21.7]
- C vs A, median days from lapse to active: +0.0 d [-0.3, +0.3]
- C vs A, retention at end: +18.3 pts [+17.1, +19.5]
- C vs A, δ weekly active minutes (wk1→wk12): +8.1 min [+7.0, +9.1]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +4.4 pts [+3.7, +5.0]
- C vs A0, persistence, week 12: -0.8 pts [-1.4, -0.2]
- C vs A0, persistence, weeks 4+8+12: -1.5 pts [-2.3, -0.8]
- C vs A0, recovery within 14 days: +0.0 pts [-1.0, +1.0]
- C vs A0, recovery within 14 days, after a labelled disruption: +0.3 pts [-1.7, +2.3]
- C vs A0, recovery within 14 days, after an unlabelled shock: +1.6 pts [-2.0, +5.2]
- C vs A0, median days from lapse to active: +0.0 d [+0.0, +0.0]
- C vs A0, retention at end: -0.7 pts [-1.3, -0.2]
- C vs A0, δ weekly active minutes (wk1→wk12): +3.8 min [+3.0, +4.7]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +2.4 pts [+2.0, +2.9]
- C vs B, persistence, week 12: +0.2 pts [-0.4, +0.8]
- C vs B, persistence, weeks 4+8+12: +0.1 pts [-0.4, +0.6]
- C vs B, recovery within 14 days: +0.0 pts [-0.6, +0.6]
- C vs B, recovery within 14 days, after a labelled disruption: -0.3 pts [-1.4, +0.9]
- C vs B, recovery within 14 days, after an unlabelled shock: +0.5 pts [-1.5, +2.5]
- C vs B, median days from lapse to active: +0.1 d [-0.1, +0.4]
- C vs B, retention at end: -0.0 pts [-0.7, +0.6]
- C vs B, δ weekly active minutes (wk1→wk12): +0.5 min [-0.1, +1.1]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): -0.1 pts [-0.4, +0.2]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 6.8% [4.5, 9.2] | 17.3% [12.9, 21.7] | 15.7% [11.4, 20.1] | 15.4% [11.3, 19.5] |
| health_literacy | Recovery within 14 days | 10.8% [7.1, 14.5] | 9.3% [3.9, 14.7] | 9.4% [6.0, 12.7] | 8.9% [5.7, 12.1] |
| health_literacy | Retention at end | 9.2% [6.2, 12.2] | 18.1% [14.2, 22.1] | 17.1% [13.4, 20.9] | 17.1% [13.7, 20.6] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 8.0 min [5.3, 10.7] | 6.6 min [5.0, 8.2] | 9.4 min [6.7, 12.2] | 9.9 min [6.9, 12.9] |
| language | Persistence, week 12 | 3.3% [1.9, 4.7] | 6.4% [3.7, 9.0] | 7.1% [3.9, 10.3] | 6.8% [3.5, 10.0] |
| language | Recovery within 14 days | 7.8% [4.8, 10.8] | 8.5% [4.4, 12.6] | 8.2% [4.4, 11.9] | 7.5% [3.8, 11.2] |
| language | Retention at end | 3.7% [2.6, 4.9] | 7.9% [4.5, 11.3] | 8.4% [4.3, 12.5] | 8.0% [3.8, 12.2] |
| language | Δ weekly active minutes (wk1→wk12) | 5.2 min [3.2, 7.3] | 5.0 min [3.6, 6.3] | 7.2 min [4.9, 9.5] | 7.4 min [5.8, 9.0] |
| mobility_limitation | Persistence, week 12 | 10.1% [6.6, 13.6] | 14.5% [9.2, 19.9] | 12.2% [8.3, 16.2] | 12.4% [7.4, 17.4] |
| mobility_limitation | Recovery within 14 days | 10.8% [5.2, 16.4] | 10.8% [5.6, 16.0] | 12.5% [7.1, 17.9] | 12.7% [7.2, 18.2] |
| mobility_limitation | Retention at end | 11.7% [8.0, 15.3] | 16.2% [11.2, 21.2] | 14.8% [10.4, 19.1] | 15.9% [10.9, 20.9] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 10.4 min [8.3, 12.5] | 10.4 min [6.4, 14.5] | 8.6 min [4.0, 13.2] | 8.5 min [4.1, 13.0] |
| schedule_type | Persistence, week 12 | 10.5% [7.1, 13.9] | 12.8% [8.8, 16.8] | 14.0% [10.0, 18.1] | 13.9% [9.7, 18.0] |
| schedule_type | Recovery within 14 days | 12.3% [9.4, 15.3] | 14.3% [9.6, 19.0] | 14.3% [8.4, 20.2] | 13.7% [8.6, 18.9] |
| schedule_type | Retention at end | 11.1% [8.0, 14.1] | 13.5% [9.7, 17.2] | 13.7% [10.2, 17.3] | 13.6% [10.5, 16.7] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 9.8 min [7.1, 12.5] | 9.5 min [6.5, 12.6] | 16.3 min [10.9, 21.7] | 16.5 min [10.1, 22.8] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.5 [11.4, 11.6] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.3 [12.2, 12.4] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.3 [12.2, 12.4] messages per persona-week

### Where Rebound doesn't help

- Median days from lapse to active vs A: +0.0 d [-0.3, +0.3] (no clear difference)
- Persistence, week 12 vs A0: -0.8 pts [-1.4, -0.2] (Rebound is worse)
- Persistence, weeks 4+8+12 vs A0: -1.5 pts [-2.3, -0.8] (Rebound is worse)
- Recovery within 14 days vs A0: +0.0 pts [-1.0, +1.0] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: +0.3 pts [-1.7, +2.3] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +1.6 pts [-2.0, +5.2] (no clear difference)
- Median days from lapse to active vs A0: +0.0 d [+0.0, +0.0] (no clear difference)
- Retention at end vs A0: -0.7 pts [-1.3, -0.2] (Rebound is worse)
