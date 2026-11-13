## Simulation results: scenario `shock_heavy`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 44.7% [43.0, 46.4] | 68.1% [66.9, 69.3] | 67.4% [66.0, 68.8] | 67.6% [66.2, 69.1] |
| Persistence, week 8 | 31.3% [29.3, 33.2] | 57.4% [55.4, 59.4] | 57.0% [54.6, 59.5] | 57.1% [54.4, 59.7] |
| Persistence, week 12 | 27.3% [25.5, 29.1] | 50.1% [48.0, 52.2] | 49.3% [47.5, 51.2] | 49.2% [47.4, 51.1] |
| Persistence, weeks 4+8+12 | 13.3% [12.0, 14.7] | 35.3% [33.4, 37.1] | 34.6% [32.3, 36.8] | 34.6% [32.4, 36.9] |
| Recovery within 14 days | 35.3% [33.9, 36.7] | 51.2% [49.6, 52.9] | 50.9% [49.1, 52.7] | 51.3% [49.6, 53.0] |
| Recovery within 14 days, after a labelled disruption | 34.3% [32.0, 36.6] | 47.3% [43.6, 51.0] | 48.3% [45.9, 50.6] | 48.5% [46.3, 50.8] |
| Recovery within 14 days, after an unlabelled shock | 38.8% [37.3, 40.3] | 53.7% [51.0, 56.4] | 52.9% [50.3, 55.4] | 53.1% [50.2, 56.0] |
| Recovery within 14 days, no disruption nearby | 32.8% [30.1, 35.5] | 50.6% [47.1, 54.1] | 50.1% [47.2, 52.9] | 50.9% [48.6, 53.3] |
| Median days from lapse to active | 11.8 d [11.1, 12.5] | 9.4 d [9.0, 9.8] | 9.6 d [9.2, 10.0] | 9.5 d [9.1, 9.9] |
| Median days from lapse to recovering | 5.9 d [5.7, 6.1] | 4.9 d [4.7, 5.1] | 4.9 d [4.7, 5.1] | 4.9 d [4.7, 5.1] |
| Δ weekly active minutes (wk1→wk12) | -22.4 min [-23.5, -21.3] | -15.9 min [-17.1, -14.7] | -10.0 min [-11.8, -8.3] | -9.8 min [-11.6, -8.0] |
| Δ tier-weighted sleep nights (wk1→wk12) | -9.8% [-10.1, -9.4] | -6.8% [-7.2, -6.4] | 0.8% [-0.5, 2.1] | 0.9% [-0.3, 2.2] |
| Δ sleep nights completed, raw (wk1→wk12) | -38.7% [-40.3, -37.2] | -26.8% [-28.4, -25.1] | -29.6% [-31.7, -27.4] | -29.6% [-31.6, -27.6] |
| Retention at end | 51.8% [49.7, 53.9] | 67.3% [64.8, 69.7] | 67.4% [65.2, 69.5] | 67.2% [64.8, 69.6] |
| Lapse rate (≥ 1 lapse in the run) | 98.2% [97.8, 98.6] | 91.8% [90.7, 92.9] | 92.5% [91.4, 93.6] | 92.4% [91.2, 93.6] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.1, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +16.0 pts [+14.0, +18.0] (helps) | +21.9 pts [+20.2, +23.6] (helps) | +15.3 pts [+14.0, +16.6] (helps) |
| C vs A0 | +0.1 pts [-1.1, +1.3] (not shown) | -0.8 pts [-1.7, -0.0] (worse) | -0.1 pts [-0.8, +0.6] (not shown) |
| C vs B | +0.5 pts [-0.2, +1.1] (not shown) | -0.1 pts [-0.5, +0.3] (not shown) | -0.2 pts [-0.7, +0.3] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +22.0 pts [+20.3, +23.8]
- B vs A, persistence, weeks 4+8+12: +21.2 pts [+19.6, +22.8]
- B vs A, recovery within 14 days: +15.5 pts [+13.3, +17.7]
- B vs A, recovery within 14 days, after a labelled disruption: +13.9 pts [+10.9, +17.0]
- B vs A, recovery within 14 days, after an unlabelled shock: +14.1 pts [+12.2, +16.0]
- B vs A, median days from lapse to active: -2.2 d [-3.1, -1.3]
- B vs A, retention at end: +15.5 pts [+14.2, +16.9]
- B vs A, δ weekly active minutes (wk1→wk12): +12.3 min [+10.8, +13.8]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +10.6 pts [+9.5, +11.7]
- B vs A, lapse rate (≥ 1 lapse in the run): -5.7 pts [-6.7, -4.8]
- B vs A, messages per persona-week: +0.5 [+0.5, +0.5]
- C vs A, persistence, week 12: +21.9 pts [+20.2, +23.6]
- C vs A, persistence, weeks 4+8+12: +21.3 pts [+19.6, +23.0]
- C vs A, recovery within 14 days: +16.0 pts [+14.0, +18.0]
- C vs A, recovery within 14 days, after a labelled disruption: +14.2 pts [+11.3, +17.2]
- C vs A, recovery within 14 days, after an unlabelled shock: +14.3 pts [+12.3, +16.3]
- C vs A, median days from lapse to active: -2.3 d [-3.1, -1.5]
- C vs A, retention at end: +15.3 pts [+14.0, +16.6]
- C vs A, δ weekly active minutes (wk1→wk12): +12.6 min [+11.0, +14.2]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +10.7 pts [+9.6, +11.8]
- C vs A, lapse rate (≥ 1 lapse in the run): -5.8 pts [-6.8, -4.7]
- C vs A, messages per persona-week: +0.5 [+0.5, +0.5]
- C vs A0, persistence, week 12: -0.8 pts [-1.7, -0.0]
- C vs A0, persistence, weeks 4+8+12: -0.6 pts [-1.4, +0.1]
- C vs A0, recovery within 14 days: +0.1 pts [-1.1, +1.3]
- C vs A0, recovery within 14 days, after a labelled disruption: +1.2 pts [-1.3, +3.8]
- C vs A0, recovery within 14 days, after an unlabelled shock: -0.6 pts [-2.0, +0.8]
- C vs A0, median days from lapse to active: +0.1 d [-0.4, +0.6]
- C vs A0, retention at end: -0.1 pts [-0.8, +0.6]
- C vs A0, δ weekly active minutes (wk1→wk12): +6.1 min [+4.8, +7.4]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +7.7 pts [+6.8, +8.7]
- C vs A0, lapse rate (≥ 1 lapse in the run): +0.6 pts [+0.1, +1.1]
- C vs A0, messages per persona-week: +0.4 [+0.4, +0.4]
- C vs B, persistence, week 12: -0.1 pts [-0.5, +0.3]
- C vs B, persistence, weeks 4+8+12: +0.1 pts [-0.4, +0.6]
- C vs B, recovery within 14 days: +0.5 pts [-0.2, +1.1]
- C vs B, recovery within 14 days, after a labelled disruption: +0.3 pts [-1.0, +1.6]
- C vs B, recovery within 14 days, after an unlabelled shock: +0.2 pts [-0.7, +1.1]
- C vs B, median days from lapse to active: -0.1 d [-0.5, +0.3]
- C vs B, retention at end: -0.2 pts [-0.7, +0.3]
- C vs B, δ weekly active minutes (wk1→wk12): +0.3 min [-0.6, +1.2]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): +0.1 pts [-0.1, +0.3]
- C vs B, lapse rate (≥ 1 lapse in the run): -0.0 pts [-0.3, +0.3]
- C vs B, messages per persona-week: +0.0 [-0.0, +0.0]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 16.0% [12.2, 19.9] | 20.6% [16.8, 24.4] | 20.3% [15.2, 25.3] | 21.3% [15.9, 26.6] |
| health_literacy | Recovery within 14 days | 8.5% [6.0, 11.0] | 12.4% [9.1, 15.8] | 11.0% [8.7, 13.3] | 11.2% [8.5, 14.0] |
| health_literacy | Retention at end | 19.8% [16.0, 23.6] | 19.8% [14.9, 24.7] | 20.3% [15.0, 25.6] | 20.8% [15.4, 26.2] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 6.3 min [3.6, 9.0] | 5.6 min [3.6, 7.7] | 12.3 min [6.8, 17.7] | 11.5 min [6.7, 16.4] |
| language | Persistence, week 12 | 9.2% [6.1, 12.4] | 7.1% [3.3, 10.9] | 7.7% [4.1, 11.2] | 7.7% [4.6, 10.9] |
| language | Recovery within 14 days | 5.8% [4.2, 7.3] | 6.2% [4.0, 8.5] | 6.2% [3.5, 8.9] | 6.2% [3.8, 8.6] |
| language | Retention at end | 10.6% [6.5, 14.8] | 8.1% [5.3, 10.8] | 7.6% [5.4, 9.7] | 7.4% [5.1, 9.7] |
| language | Δ weekly active minutes (wk1→wk12) | 5.5 min [4.0, 7.1] | 4.8 min [2.5, 7.0] | 9.9 min [8.6, 11.2] | 9.9 min [7.9, 11.8] |
| mobility_limitation | Persistence, week 12 | 13.7% [7.1, 20.3] | 18.1% [9.5, 26.6] | 16.9% [9.0, 24.9] | 17.7% [10.3, 25.2] |
| mobility_limitation | Recovery within 14 days | 12.2% [5.9, 18.6] | 16.5% [9.9, 23.1] | 16.2% [9.8, 22.6] | 15.8% [9.1, 22.6] |
| mobility_limitation | Retention at end | 16.2% [8.1, 24.3] | 13.1% [5.4, 20.8] | 10.2% [3.7, 16.7] | 11.8% [4.0, 19.7] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.4 min [5.9, 12.9] | 8.5 min [4.5, 12.4] | 9.5 min [5.0, 14.1] | 10.8 min [6.3, 15.3] |
| schedule_type | Persistence, week 12 | 15.8% [11.3, 20.4] | 13.4% [10.0, 16.9] | 15.7% [11.3, 20.1] | 15.6% [12.1, 19.0] |
| schedule_type | Recovery within 14 days | 11.0% [8.1, 13.9] | 11.9% [8.6, 15.1] | 15.3% [13.2, 17.5] | 13.4% [9.5, 17.2] |
| schedule_type | Retention at end | 17.2% [12.1, 22.3] | 14.1% [10.9, 17.3] | 15.8% [11.0, 20.6] | 14.9% [9.9, 19.9] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 12.1 min [9.5, 14.8] | 10.5 min [7.1, 13.8] | 19.2 min [14.4, 24.0] | 19.6 min [16.5, 22.7] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Messages per persona-week vs A: +0.5 [+0.5, +0.5] (Rebound is worse)
- Persistence, week 12 vs A0: -0.8 pts [-1.7, -0.0] (Rebound is worse)
- Persistence, weeks 4+8+12 vs A0: -0.6 pts [-1.4, +0.1] (no clear difference)
- Recovery within 14 days vs A0: +0.1 pts [-1.1, +1.3] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: +1.2 pts [-1.3, +3.8] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: -0.6 pts [-2.0, +0.8] (no clear difference)
- Median days from lapse to active vs A0: +0.1 d [-0.4, +0.6] (no clear difference)
- Retention at end vs A0: -0.1 pts [-0.8, +0.6] (no clear difference)
- Lapse rate (≥ 1 lapse in the run) vs A0: +0.6 pts [+0.1, +1.1] (Rebound is worse)
- Messages per persona-week vs A0: +0.4 [+0.4, +0.4] (Rebound is worse)
