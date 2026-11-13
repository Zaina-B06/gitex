## Simulation results: scenario `shock_heavy`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 44.7% [43.0, 46.4] | 68.1% [66.9, 69.3] | 67.6% [66.4, 68.8] | 67.8% [66.3, 69.4] |
| Persistence, week 8 | 31.3% [29.3, 33.2] | 57.4% [55.4, 59.4] | 56.9% [54.6, 59.2] | 56.7% [54.5, 59.0] |
| Persistence, week 12 | 27.3% [25.5, 29.1] | 50.1% [48.0, 52.2] | 49.2% [47.4, 51.1] | 48.9% [46.8, 51.1] |
| Persistence, weeks 4+8+12 | 13.3% [12.0, 14.7] | 35.3% [33.4, 37.1] | 34.5% [32.1, 36.9] | 34.3% [31.8, 36.8] |
| Recovery within 14 days | 35.3% [33.9, 36.7] | 51.2% [49.6, 52.9] | 51.8% [50.2, 53.3] | 52.1% [50.5, 53.6] |
| Recovery within 14 days, after a labelled disruption | 34.3% [32.0, 36.6] | 47.3% [43.6, 51.0] | 48.5% [45.6, 51.4] | 48.5% [45.3, 51.6] |
| Recovery within 14 days, after an unlabelled shock | 38.8% [37.3, 40.3] | 53.7% [51.0, 56.4] | 53.9% [51.5, 56.3] | 54.2% [51.6, 56.8] |
| Recovery within 14 days, no disruption nearby | 32.8% [30.1, 35.5] | 50.6% [47.1, 54.1] | 51.1% [48.7, 53.6] | 51.6% [48.6, 54.6] |
| Median days from lapse to active | 11.8 d [11.1, 12.5] | 9.4 d [9.0, 9.8] | 9.2 d [8.9, 9.6] | 9.2 d [8.9, 9.5] |
| Median days from lapse to recovering | 5.9 d [5.7, 6.1] | 4.9 d [4.7, 5.1] | 4.9 d [4.7, 5.1] | 4.9 d [4.7, 5.1] |
| Δ weekly active minutes (wk1→wk12) | -22.4 min [-23.5, -21.3] | -15.9 min [-17.1, -14.7] | -10.1 min [-12.0, -8.2] | -9.9 min [-11.8, -8.0] |
| Δ tier-weighted sleep nights (wk1→wk12) | -9.8% [-10.1, -9.4] | -6.8% [-7.2, -6.4] | 0.8% [-0.6, 2.2] | 0.9% [-0.6, 2.3] |
| Δ sleep nights completed, raw (wk1→wk12) | -38.7% [-40.3, -37.2] | -26.8% [-28.4, -25.1] | -29.8% [-31.8, -27.7] | -29.8% [-31.9, -27.8] |
| Retention at end | 51.8% [49.7, 53.9] | 67.3% [64.8, 69.7] | 67.2% [64.6, 69.8] | 66.9% [64.2, 69.6] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.1, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +16.7 pts [+14.9, +18.6] (helps) | +21.6 pts [+19.9, +23.4] (helps) | +15.1 pts [+13.5, +16.6] (helps) |
| C vs A0 | +0.8 pts [+0.2, +1.5] (helps) | -1.1 pts [-2.0, -0.3] (worse) | -0.4 pts [-1.2, +0.5] (not shown) |
| C vs B | +0.3 pts [-0.2, +0.8] (not shown) | -0.3 pts [-0.8, +0.2] (not shown) | -0.3 pts [-0.7, +0.2] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +21.9 pts [+20.2, +23.7]
- B vs A, persistence, weeks 4+8+12: +21.2 pts [+19.3, +23.1]
- B vs A, recovery within 14 days: +16.4 pts [+14.5, +18.3]
- B vs A, recovery within 14 days, after a labelled disruption: +14.2 pts [+11.1, +17.3]
- B vs A, recovery within 14 days, after an unlabelled shock: +15.1 pts [+13.5, +16.7]
- B vs A, median days from lapse to active: -2.5 d [-3.2, -1.9]
- B vs A, retention at end: +15.3 pts [+13.9, +16.7]
- B vs A, δ weekly active minutes (wk1→wk12): +12.3 min [+10.6, +14.0]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +10.5 pts [+9.3, +11.8]
- C vs A, persistence, week 12: +21.6 pts [+19.9, +23.4]
- C vs A, persistence, weeks 4+8+12: +21.0 pts [+19.1, +22.9]
- C vs A, recovery within 14 days: +16.7 pts [+14.9, +18.6]
- C vs A, recovery within 14 days, after a labelled disruption: +14.2 pts [+10.6, +17.7]
- C vs A, recovery within 14 days, after an unlabelled shock: +15.4 pts [+13.7, +17.2]
- C vs A, median days from lapse to active: -2.6 d [-3.3, -1.9]
- C vs A, retention at end: +15.1 pts [+13.5, +16.6]
- C vs A, δ weekly active minutes (wk1→wk12): +12.5 min [+10.7, +14.3]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +10.6 pts [+9.3, +11.9]
- C vs A0, persistence, week 12: -1.1 pts [-2.0, -0.3]
- C vs A0, persistence, weeks 4+8+12: -0.9 pts [-2.0, +0.1]
- C vs A0, recovery within 14 days: +0.8 pts [+0.2, +1.5]
- C vs A0, recovery within 14 days, after a labelled disruption: +1.2 pts [-1.3, +3.7]
- C vs A0, recovery within 14 days, after an unlabelled shock: +0.5 pts [-0.3, +1.3]
- C vs A0, median days from lapse to active: -0.2 d [-0.5, +0.1]
- C vs A0, retention at end: -0.4 pts [-1.2, +0.5]
- C vs A0, δ weekly active minutes (wk1→wk12): +6.0 min [+4.5, +7.4]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +7.7 pts [+6.5, +8.8]
- C vs B, persistence, week 12: -0.3 pts [-0.8, +0.2]
- C vs B, persistence, weeks 4+8+12: -0.2 pts [-0.7, +0.4]
- C vs B, recovery within 14 days: +0.3 pts [-0.2, +0.8]
- C vs B, recovery within 14 days, after a labelled disruption: -0.0 pts [-1.6, +1.5]
- C vs B, recovery within 14 days, after an unlabelled shock: +0.3 pts [-0.2, +0.9]
- C vs B, median days from lapse to active: -0.1 d [-0.2, +0.1]
- C vs B, retention at end: -0.3 pts [-0.7, +0.2]
- C vs B, δ weekly active minutes (wk1→wk12): +0.2 min [-0.4, +0.9]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): +0.1 pts [-0.2, +0.4]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 16.0% [12.2, 19.9] | 20.6% [16.8, 24.4] | 21.0% [17.9, 24.2] | 21.1% [17.2, 25.0] |
| health_literacy | Recovery within 14 days | 8.5% [6.0, 11.0] | 12.4% [9.1, 15.8] | 14.0% [11.8, 16.1] | 13.2% [11.2, 15.2] |
| health_literacy | Retention at end | 19.8% [16.0, 23.6] | 19.8% [14.9, 24.7] | 20.2% [15.2, 25.2] | 19.7% [15.3, 24.0] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 6.3 min [3.6, 9.0] | 5.6 min [3.6, 7.7] | 12.1 min [6.8, 17.4] | 12.2 min [7.3, 17.1] |
| language | Persistence, week 12 | 9.2% [6.1, 12.4] | 7.1% [3.3, 10.9] | 7.7% [4.7, 10.7] | 8.4% [5.3, 11.4] |
| language | Recovery within 14 days | 5.8% [4.2, 7.3] | 6.2% [4.0, 8.5] | 6.1% [3.7, 8.5] | 6.4% [4.0, 8.7] |
| language | Retention at end | 10.6% [6.5, 14.8] | 8.1% [5.3, 10.8] | 8.2% [5.7, 10.6] | 8.8% [6.4, 11.1] |
| language | Δ weekly active minutes (wk1→wk12) | 5.5 min [4.0, 7.1] | 4.8 min [2.5, 7.0] | 10.7 min [8.3, 13.1] | 10.8 min [8.6, 12.9] |
| mobility_limitation | Persistence, week 12 | 13.7% [7.1, 20.3] | 18.1% [9.5, 26.6] | 19.9% [9.1, 30.8] | 19.8% [9.0, 30.7] |
| mobility_limitation | Recovery within 14 days | 12.2% [5.9, 18.6] | 16.5% [9.9, 23.1] | 14.9% [9.3, 20.6] | 14.8% [8.5, 21.2] |
| mobility_limitation | Retention at end | 16.2% [8.1, 24.3] | 13.1% [5.4, 20.8] | 15.9% [5.4, 26.4] | 13.1% [3.1, 23.1] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.4 min [5.9, 12.9] | 8.5 min [4.5, 12.4] | 10.3 min [6.6, 14.0] | 11.2 min [6.8, 15.7] |
| schedule_type | Persistence, week 12 | 15.8% [11.3, 20.4] | 13.4% [10.0, 16.9] | 13.6% [10.0, 17.2] | 13.3% [10.3, 16.2] |
| schedule_type | Recovery within 14 days | 11.0% [8.1, 13.9] | 11.9% [8.6, 15.1] | 14.5% [12.0, 16.9] | 14.1% [11.7, 16.5] |
| schedule_type | Retention at end | 17.2% [12.1, 22.3] | 14.1% [10.9, 17.3] | 14.0% [10.6, 17.5] | 12.4% [9.0, 15.8] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 12.1 min [9.5, 14.8] | 10.5 min [7.1, 13.8] | 20.0 min [16.5, 23.4] | 19.1 min [16.3, 21.9] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Persistence, week 12 vs A0: -1.1 pts [-2.0, -0.3] (Rebound is worse)
- Persistence, weeks 4+8+12 vs A0: -0.9 pts [-2.0, +0.1] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: +1.2 pts [-1.3, +3.7] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +0.5 pts [-0.3, +1.3] (no clear difference)
- Median days from lapse to active vs A0: -0.2 d [-0.5, +0.1] (no clear difference)
- Retention at end vs A0: -0.4 pts [-1.2, +0.5] (no clear difference)
