## Simulation results: scenario `shock_heavy`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 44.7% [43.0, 46.4] | 68.1% [66.9, 69.3] | 67.0% [65.5, 68.5] | 66.9% [65.6, 68.2] |
| Persistence, week 8 | 31.3% [29.3, 33.2] | 57.4% [55.4, 59.4] | 56.6% [54.2, 58.9] | 56.3% [54.0, 58.6] |
| Persistence, week 12 | 27.3% [25.5, 29.1] | 50.1% [48.0, 52.2] | 48.7% [46.5, 50.9] | 48.6% [46.2, 50.9] |
| Persistence, weeks 4+8+12 | 13.3% [12.0, 14.7] | 35.3% [33.4, 37.1] | 33.9% [31.2, 36.6] | 33.8% [31.3, 36.2] |
| Recovery within 14 days | 35.3% [33.9, 36.7] | 51.2% [49.6, 52.9] | 51.2% [49.6, 52.8] | 51.4% [49.5, 53.2] |
| Recovery within 14 days, after a labelled disruption | 34.3% [32.0, 36.6] | 47.3% [43.6, 51.0] | 47.9% [45.0, 50.8] | 48.0% [45.0, 51.0] |
| Recovery within 14 days, after an unlabelled shock | 38.8% [37.3, 40.3] | 53.7% [51.0, 56.4] | 53.5% [51.3, 55.8] | 53.7% [51.3, 56.1] |
| Recovery within 14 days, no disruption nearby | 32.8% [30.1, 35.5] | 50.6% [47.1, 54.1] | 50.4% [47.7, 53.0] | 50.4% [47.3, 53.6] |
| Median days from lapse to active | 11.8 d [11.1, 12.5] | 9.4 d [9.0, 9.8] | 9.6 d [9.2, 10.0] | 9.4 d [9.0, 9.8] |
| Median days from lapse to recovering | 5.9 d [5.7, 6.1] | 4.9 d [4.7, 5.1] | 4.9 d [4.7, 5.1] | 4.8 d [4.5, 5.1] |
| Δ weekly active minutes (wk1→wk12) | -22.4 min [-23.5, -21.3] | -15.9 min [-17.1, -14.7] | -11.6 min [-13.4, -9.7] | -11.2 min [-13.2, -9.3] |
| Δ tier-weighted sleep nights (wk1→wk12) | -9.8% [-10.1, -9.4] | -6.8% [-7.2, -6.4] | -0.7% [-2.1, 0.8] | -0.6% [-2.1, 0.9] |
| Δ sleep nights completed, raw (wk1→wk12) | -38.7% [-40.3, -37.2] | -26.8% [-28.4, -25.1] | -30.2% [-32.3, -28.2] | -30.4% [-32.7, -28.1] |
| Retention at end | 51.8% [49.7, 53.9] | 67.3% [64.8, 69.7] | 66.7% [63.9, 69.5] | 66.3% [63.6, 69.0] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.1, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +16.0 pts [+13.7, +18.3] (helps) | +21.3 pts [+19.1, +23.4] (helps) | +14.5 pts [+13.1, +15.9] (helps) |
| C vs A0 | +0.1 pts [-0.6, +0.9] (not shown) | -1.5 pts [-2.7, -0.3] (worse) | -0.9 pts [-1.7, -0.1] (worse) |
| C vs B | +0.1 pts [-0.6, +0.9] (not shown) | -0.1 pts [-0.6, +0.3] (not shown) | -0.4 pts [-0.9, +0.1] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +21.4 pts [+19.4, +23.4]
- B vs A, persistence, weeks 4+8+12: +20.5 pts [+18.3, +22.8]
- B vs A, recovery within 14 days: +15.9 pts [+13.9, +17.9]
- B vs A, recovery within 14 days, after a labelled disruption: +13.6 pts [+10.6, +16.6]
- B vs A, recovery within 14 days, after an unlabelled shock: +14.8 pts [+13.4, +16.1]
- B vs A, median days from lapse to active: -2.2 d [-2.9, -1.5]
- B vs A, retention at end: +14.9 pts [+13.3, +16.4]
- B vs A, δ weekly active minutes (wk1→wk12): +10.8 min [+9.1, +12.5]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +9.1 pts [+7.9, +10.3]
- C vs A, persistence, week 12: +21.3 pts [+19.1, +23.4]
- C vs A, persistence, weeks 4+8+12: +20.4 pts [+18.3, +22.5]
- C vs A, recovery within 14 days: +16.0 pts [+13.7, +18.3]
- C vs A, recovery within 14 days, after a labelled disruption: +13.7 pts [+10.2, +17.2]
- C vs A, recovery within 14 days, after an unlabelled shock: +14.9 pts [+13.5, +16.4]
- C vs A, median days from lapse to active: -2.4 d [-3.2, -1.6]
- C vs A, retention at end: +14.5 pts [+13.1, +15.9]
- C vs A, δ weekly active minutes (wk1→wk12): +11.2 min [+9.5, +12.8]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +9.2 pts [+7.9, +10.4]
- C vs A0, persistence, week 12: -1.5 pts [-2.7, -0.3]
- C vs A0, persistence, weeks 4+8+12: -1.5 pts [-2.6, -0.4]
- C vs A0, recovery within 14 days: +0.1 pts [-0.6, +0.9]
- C vs A0, recovery within 14 days, after a labelled disruption: +0.7 pts [-2.0, +3.4]
- C vs A0, recovery within 14 days, after an unlabelled shock: +0.0 pts [-1.0, +1.0]
- C vs A0, median days from lapse to active: +0.0 d [-0.5, +0.5]
- C vs A0, retention at end: -0.9 pts [-1.7, -0.1]
- C vs A0, δ weekly active minutes (wk1→wk12): +4.6 min [+3.4, +5.8]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +6.2 pts [+5.1, +7.3]
- C vs B, persistence, week 12: -0.1 pts [-0.6, +0.3]
- C vs B, persistence, weeks 4+8+12: -0.1 pts [-0.6, +0.4]
- C vs B, recovery within 14 days: +0.1 pts [-0.6, +0.9]
- C vs B, recovery within 14 days, after a labelled disruption: +0.1 pts [-1.3, +1.5]
- C vs B, recovery within 14 days, after an unlabelled shock: +0.2 pts [-0.8, +1.2]
- C vs B, median days from lapse to active: -0.2 d [-0.7, +0.3]
- C vs B, retention at end: -0.4 pts [-0.9, +0.1]
- C vs B, δ weekly active minutes (wk1→wk12): +0.3 min [-0.4, +1.1]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): +0.1 pts [-0.1, +0.3]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 16.0% [12.2, 19.9] | 20.6% [16.8, 24.4] | 21.7% [17.9, 25.4] | 20.3% [16.8, 23.7] |
| health_literacy | Recovery within 14 days | 8.5% [6.0, 11.0] | 12.4% [9.1, 15.8] | 12.5% [9.8, 15.2] | 13.8% [11.0, 16.7] |
| health_literacy | Retention at end | 19.8% [16.0, 23.6] | 19.8% [14.9, 24.7] | 21.2% [16.6, 25.7] | 20.5% [16.1, 24.9] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 6.3 min [3.6, 9.0] | 5.6 min [3.6, 7.7] | 12.9 min [8.4, 17.4] | 11.6 min [6.1, 17.1] |
| language | Persistence, week 12 | 9.2% [6.1, 12.4] | 7.1% [3.3, 10.9] | 8.1% [5.3, 10.8] | 8.5% [5.6, 11.4] |
| language | Recovery within 14 days | 5.8% [4.2, 7.3] | 6.2% [4.0, 8.5] | 6.4% [4.3, 8.4] | 7.4% [5.0, 9.7] |
| language | Retention at end | 10.6% [6.5, 14.8] | 8.1% [5.3, 10.8] | 8.8% [6.9, 10.8] | 9.5% [6.8, 12.2] |
| language | Δ weekly active minutes (wk1→wk12) | 5.5 min [4.0, 7.1] | 4.8 min [2.5, 7.0] | 10.8 min [8.2, 13.3] | 10.6 min [8.0, 13.2] |
| mobility_limitation | Persistence, week 12 | 13.7% [7.1, 20.3] | 18.1% [9.5, 26.6] | 19.1% [7.6, 30.5] | 18.6% [7.0, 30.2] |
| mobility_limitation | Recovery within 14 days | 12.2% [5.9, 18.6] | 16.5% [9.9, 23.1] | 15.2% [10.1, 20.3] | 16.0% [9.6, 22.5] |
| mobility_limitation | Retention at end | 16.2% [8.1, 24.3] | 13.1% [5.4, 20.8] | 16.7% [5.2, 28.3] | 13.0% [3.3, 22.7] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.4 min [5.9, 12.9] | 8.5 min [4.5, 12.4] | 11.4 min [7.2, 15.5] | 11.6 min [7.9, 15.2] |
| schedule_type | Persistence, week 12 | 15.8% [11.3, 20.4] | 13.4% [10.0, 16.9] | 14.6% [10.4, 18.8] | 15.0% [10.8, 19.2] |
| schedule_type | Recovery within 14 days | 11.0% [8.1, 13.9] | 11.9% [8.6, 15.1] | 15.0% [11.4, 18.7] | 14.8% [11.2, 18.5] |
| schedule_type | Retention at end | 17.2% [12.1, 22.3] | 14.1% [10.9, 17.3] | 14.0% [10.2, 17.8] | 15.2% [10.7, 19.6] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 12.1 min [9.5, 14.8] | 10.5 min [7.1, 13.8] | 19.0 min [14.7, 23.4] | 20.7 min [16.7, 24.8] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Persistence, week 12 vs A0: -1.5 pts [-2.7, -0.3] (Rebound is worse)
- Persistence, weeks 4+8+12 vs A0: -1.5 pts [-2.6, -0.4] (Rebound is worse)
- Recovery within 14 days vs A0: +0.1 pts [-0.6, +0.9] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: +0.7 pts [-2.0, +3.4] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +0.0 pts [-1.0, +1.0] (no clear difference)
- Median days from lapse to active vs A0: +0.0 d [-0.5, +0.5] (no clear difference)
- Retention at end vs A0: -0.9 pts [-1.7, -0.1] (Rebound is worse)
