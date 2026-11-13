## Simulation results: scenario `high_dropout`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 26.2% [24.9, 27.6] | 53.7% [51.9, 55.5] | 52.6% [50.5, 54.8] | 53.0% [50.7, 55.2] |
| Persistence, week 8 | 11.5% [10.2, 12.9] | 34.2% [32.8, 35.6] | 33.2% [31.5, 35.0] | 33.5% [31.7, 35.3] |
| Persistence, week 12 | 7.6% [6.7, 8.4] | 25.6% [24.0, 27.2] | 24.4% [22.9, 25.9] | 24.6% [23.2, 26.0] |
| Persistence, weeks 4+8+12 | 5.5% [4.5, 6.4] | 22.0% [20.4, 23.5] | 20.3% [18.8, 21.9] | 20.5% [18.8, 22.2] |
| Recovery within 14 days | 28.4% [27.0, 29.8] | 41.2% [39.5, 42.9] | 41.2% [39.5, 42.8] | 41.2% [39.9, 42.6] |
| Recovery within 14 days, after a labelled disruption | 31.9% [28.4, 35.4] | 42.7% [40.2, 45.3] | 43.2% [40.5, 46.0] | 42.5% [40.0, 45.0] |
| Recovery within 14 days, after an unlabelled shock | 25.6% [22.6, 28.6] | 40.8% [35.9, 45.7] | 41.9% [38.6, 45.2] | 42.0% [38.6, 45.4] |
| Recovery within 14 days, no disruption nearby | 27.4% [25.9, 28.9] | 40.5% [38.5, 42.5] | 39.8% [37.4, 42.2] | 40.4% [37.9, 42.8] |
| Median days from lapse to active | 7.1 d [6.7, 7.5] | 7.1 d [6.9, 7.3] | 7.0 d [7.0, 7.0] | 7.0 d [7.0, 7.0] |
| Median days from lapse to recovering | 4.0 d [4.0, 4.0] | 3.5 d [3.2, 3.9] | 3.5 d [3.1, 3.9] | 3.6 d [3.2, 4.0] |
| Δ weekly active minutes (wk1→wk12) | -24.9 min [-25.8, -24.0] | -20.7 min [-21.7, -19.7] | -15.9 min [-17.4, -14.3] | -15.4 min [-16.7, -14.0] |
| Δ tier-weighted sleep nights (wk1→wk12) | -11.2% [-11.5, -10.8] | -9.2% [-9.6, -8.9] | -5.6% [-6.5, -4.8] | -5.5% [-6.4, -4.6] |
| Δ sleep nights completed, raw (wk1→wk12) | -44.0% [-45.6, -42.4] | -36.2% [-37.6, -34.9] | -38.2% [-39.6, -36.7] | -38.2% [-39.7, -36.7] |
| Retention at end | 9.1% [7.9, 10.3] | 28.2% [26.7, 29.6] | 27.6% [26.0, 29.1] | 27.7% [25.9, 29.5] |
| Lapse rate (≥ 1 lapse in the run) | 98.8% [98.4, 99.2] | 93.4% [92.3, 94.5] | 94.2% [93.2, 95.3] | 94.2% [93.2, 95.2] |
| Messages per persona-week | 11.5 [11.4, 11.6] | 11.8 [11.7, 11.9] | 12.3 [12.2, 12.4] | 12.3 [12.2, 12.4] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +12.8 pts [+10.9, +14.7] (helps) | +17.0 pts [+15.5, +18.6] (helps) | +18.5 pts [+17.1, +20.0] (helps) |
| C vs A0 | +0.0 pts [-0.9, +1.0] (not shown) | -1.0 pts [-1.6, -0.4] (worse) | -0.5 pts [-1.1, +0.1] (not shown) |
| C vs B | +0.1 pts [-0.7, +0.8] (not shown) | +0.2 pts [-0.4, +0.7] (not shown) | +0.1 pts [-0.3, +0.5] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +16.9 pts [+15.2, +18.5]
- B vs A, persistence, weeks 4+8+12: +14.9 pts [+13.2, +16.5]
- B vs A, recovery within 14 days: +12.7 pts [+10.6, +14.9]
- B vs A, recovery within 14 days, after a labelled disruption: +11.3 pts [+7.3, +15.4]
- B vs A, recovery within 14 days, after an unlabelled shock: +16.3 pts [+12.4, +20.2]
- B vs A, median days from lapse to active: -0.1 d [-0.5, +0.3]
- B vs A, retention at end: +18.4 pts [+17.1, +19.8]
- B vs A, δ weekly active minutes (wk1→wk12): +9.0 min [+7.5, +10.5]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +5.5 pts [+4.6, +6.5]
- B vs A, lapse rate (≥ 1 lapse in the run): -4.6 pts [-5.4, -3.7]
- B vs A, messages per persona-week: +0.8 [+0.8, +0.9]
- C vs A, persistence, week 12: +17.0 pts [+15.5, +18.6]
- C vs A, persistence, weeks 4+8+12: +15.0 pts [+13.4, +16.7]
- C vs A, recovery within 14 days: +12.8 pts [+10.9, +14.7]
- C vs A, recovery within 14 days, after a labelled disruption: +10.6 pts [+7.0, +14.2]
- C vs A, recovery within 14 days, after an unlabelled shock: +16.4 pts [+12.5, +20.2]
- C vs A, median days from lapse to active: -0.1 d [-0.5, +0.3]
- C vs A, retention at end: +18.5 pts [+17.1, +20.0]
- C vs A, δ weekly active minutes (wk1→wk12): +9.5 min [+8.1, +11.0]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +5.7 pts [+4.7, +6.7]
- C vs A, lapse rate (≥ 1 lapse in the run): -4.6 pts [-5.4, -3.8]
- C vs A, messages per persona-week: +0.8 [+0.8, +0.9]
- C vs A0, persistence, week 12: -1.0 pts [-1.6, -0.4]
- C vs A0, persistence, weeks 4+8+12: -1.5 pts [-2.1, -0.8]
- C vs A0, recovery within 14 days: +0.0 pts [-0.9, +1.0]
- C vs A0, recovery within 14 days, after a labelled disruption: -0.3 pts [-1.4, +0.9]
- C vs A0, recovery within 14 days, after an unlabelled shock: +1.2 pts [-2.4, +4.8]
- C vs A0, median days from lapse to active: -0.1 d [-0.3, +0.1]
- C vs A0, retention at end: -0.5 pts [-1.1, +0.1]
- C vs A0, δ weekly active minutes (wk1→wk12): +5.3 min [+3.9, +6.7]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +3.8 pts [+3.0, +4.5]
- C vs A0, lapse rate (≥ 1 lapse in the run): +0.8 pts [+0.4, +1.2]
- C vs A0, messages per persona-week: +0.5 [+0.5, +0.5]
- C vs B, persistence, week 12: +0.2 pts [-0.4, +0.7]
- C vs B, persistence, weeks 4+8+12: +0.2 pts [-0.2, +0.6]
- C vs B, recovery within 14 days: +0.1 pts [-0.7, +0.8]
- C vs B, recovery within 14 days, after a labelled disruption: -0.7 pts [-2.4, +0.9]
- C vs B, recovery within 14 days, after an unlabelled shock: +0.1 pts [-1.5, +1.7]
- C vs B, median days from lapse to active: +0.0 d [+0.0, +0.0]
- C vs B, retention at end: +0.1 pts [-0.3, +0.5]
- C vs B, δ weekly active minutes (wk1→wk12): +0.5 min [-0.1, +1.1]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): +0.2 pts [-0.0, +0.3]
- C vs B, lapse rate (≥ 1 lapse in the run): -0.1 pts [-0.3, +0.2]
- C vs B, messages per persona-week: +0.0 [-0.0, +0.0]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 6.8% [4.5, 9.2] | 17.3% [12.9, 21.7] | 16.2% [12.2, 20.1] | 16.7% [12.4, 21.0] |
| health_literacy | Recovery within 14 days | 10.8% [7.1, 14.5] | 9.3% [3.9, 14.7] | 9.8% [5.0, 14.5] | 8.5% [4.4, 12.7] |
| health_literacy | Retention at end | 9.2% [6.2, 12.2] | 18.1% [14.2, 22.1] | 17.8% [13.8, 21.9] | 17.8% [13.8, 21.8] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 8.0 min [5.3, 10.7] | 6.6 min [5.0, 8.2] | 9.6 min [6.7, 12.5] | 9.5 min [5.9, 13.1] |
| language | Persistence, week 12 | 3.3% [1.9, 4.7] | 6.4% [3.7, 9.0] | 6.3% [3.4, 9.2] | 5.7% [3.1, 8.3] |
| language | Recovery within 14 days | 7.8% [4.8, 10.8] | 8.5% [4.4, 12.6] | 7.9% [4.2, 11.5] | 8.1% [4.3, 12.0] |
| language | Retention at end | 3.7% [2.6, 4.9] | 7.9% [4.5, 11.3] | 8.7% [4.9, 12.5] | 8.6% [4.8, 12.3] |
| language | Δ weekly active minutes (wk1→wk12) | 5.2 min [3.2, 7.3] | 5.0 min [3.6, 6.3] | 6.6 min [4.5, 8.7] | 6.1 min [3.7, 8.5] |
| mobility_limitation | Persistence, week 12 | 10.1% [6.6, 13.6] | 14.5% [9.2, 19.9] | 11.9% [8.5, 15.4] | 13.1% [8.6, 17.5] |
| mobility_limitation | Recovery within 14 days | 10.8% [5.2, 16.4] | 10.8% [5.6, 16.0] | 15.5% [9.9, 21.0] | 14.4% [8.5, 20.4] |
| mobility_limitation | Retention at end | 11.7% [8.0, 15.3] | 16.2% [11.2, 21.2] | 15.7% [11.4, 20.0] | 15.0% [11.3, 18.6] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 10.4 min [8.3, 12.5] | 10.4 min [6.4, 14.5] | 8.7 min [4.0, 13.4] | 8.1 min [3.5, 12.7] |
| schedule_type | Persistence, week 12 | 10.5% [7.1, 13.9] | 12.8% [8.8, 16.8] | 14.0% [9.9, 18.1] | 12.8% [8.1, 17.5] |
| schedule_type | Recovery within 14 days | 12.3% [9.4, 15.3] | 14.3% [9.6, 19.0] | 15.2% [11.2, 19.2] | 15.2% [11.2, 19.3] |
| schedule_type | Retention at end | 11.1% [8.0, 14.1] | 13.5% [9.7, 17.2] | 15.3% [12.7, 17.9] | 13.7% [10.2, 17.2] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 9.8 min [7.1, 12.5] | 9.5 min [6.5, 12.6] | 16.9 min [11.2, 22.7] | 15.7 min [9.8, 21.7] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.5 [11.4, 11.6] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.3 [12.2, 12.4] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.3 [12.2, 12.4] messages per persona-week

### Where Rebound doesn't help

- Median days from lapse to active vs A: -0.1 d [-0.5, +0.3] (no clear difference)
- Messages per persona-week vs A: +0.8 [+0.8, +0.9] (Rebound is worse)
- Persistence, week 12 vs A0: -1.0 pts [-1.6, -0.4] (Rebound is worse)
- Persistence, weeks 4+8+12 vs A0: -1.5 pts [-2.1, -0.8] (Rebound is worse)
- Recovery within 14 days vs A0: +0.0 pts [-0.9, +1.0] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: -0.3 pts [-1.4, +0.9] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +1.2 pts [-2.4, +4.8] (no clear difference)
- Median days from lapse to active vs A0: -0.1 d [-0.3, +0.1] (no clear difference)
- Retention at end vs A0: -0.5 pts [-1.1, +0.1] (no clear difference)
- Lapse rate (≥ 1 lapse in the run) vs A0: +0.8 pts [+0.4, +1.2] (Rebound is worse)
- Messages per persona-week vs A0: +0.5 [+0.5, +0.5] (Rebound is worse)
