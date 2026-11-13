## Simulation results: scenario `ramadan_heavy`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 49.5% [47.3, 51.7] | 74.2% [73.3, 75.1] | 73.9% [72.5, 75.2] | 74.3% [72.8, 75.9] |
| Persistence, week 8 | 36.9% [35.1, 38.7] | 63.9% [61.6, 66.1] | 63.9% [61.7, 66.1] | 63.7% [61.5, 65.9] |
| Persistence, week 12 | 33.2% [31.0, 35.4] | 58.7% [56.7, 60.6] | 58.4% [56.4, 60.4] | 58.4% [56.6, 60.2] |
| Persistence, weeks 4+8+12 | 17.6% [15.7, 19.5] | 44.6% [42.4, 46.8] | 43.6% [41.1, 46.1] | 43.4% [41.0, 45.8] |
| Recovery within 14 days | 36.6% [35.2, 38.0] | 53.7% [52.3, 55.1] | 54.1% [52.5, 55.8] | 54.7% [53.1, 56.3] |
| Recovery within 14 days, after a labelled disruption | 35.5% [33.4, 37.7] | 51.9% [50.0, 53.8] | 52.4% [50.7, 54.2] | 53.1% [51.4, 54.9] |
| Recovery within 14 days, after an unlabelled shock | 40.5% [37.4, 43.7] | 58.5% [55.0, 62.1] | 59.1% [56.7, 61.5] | 60.0% [57.3, 62.7] |
| Recovery within 14 days, no disruption nearby | 36.4% [34.6, 38.1] | 53.2% [50.2, 56.2] | 53.6% [50.0, 57.2] | 53.8% [50.5, 57.1] |
| Median days from lapse to active | 11.5 d [10.9, 12.1] | 9.0 d [8.7, 9.3] | 9.0 d [8.5, 9.5] | 9.1 d [8.6, 9.6] |
| Median days from lapse to recovering | 5.8 d [5.5, 6.1] | 4.6 d [4.2, 5.0] | 4.4 d [4.0, 4.8] | 4.6 d [4.2, 5.0] |
| Δ weekly active minutes (wk1→wk12) | -20.7 min [-21.8, -19.7] | -12.6 min [-13.7, -11.5] | -4.4 min [-5.7, -3.1] | -4.1 min [-5.6, -2.7] |
| Δ tier-weighted sleep nights (wk1→wk12) | -9.0% [-9.3, -8.6] | -5.5% [-5.9, -5.0] | 5.0% [3.7, 6.4] | 4.9% [3.7, 6.2] |
| Δ sleep nights completed, raw (wk1→wk12) | -35.5% [-36.8, -34.2] | -21.6% [-23.4, -19.8] | -25.0% [-27.1, -23.0] | -25.1% [-27.2, -23.1] |
| Retention at end | 61.9% [59.9, 64.0] | 75.8% [73.3, 78.2] | 76.1% [73.9, 78.2] | 75.7% [73.6, 77.9] |
| Lapse rate (≥ 1 lapse in the run) | 96.6% [95.7, 97.5] | 86.2% [84.8, 87.5] | 87.5% [85.9, 89.1] | 87.5% [85.9, 89.0] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.1, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +18.1 pts [+15.8, +20.4] (helps) | +25.2 pts [+23.6, +26.8] (helps) | +13.8 pts [+12.5, +15.1] (helps) |
| C vs A0 | +1.0 pts [-0.4, +2.4] (not shown) | -0.3 pts [-0.8, +0.2] (not shown) | -0.0 pts [-0.6, +0.5] (not shown) |
| C vs B | +0.5 pts [+0.0, +1.0] (helps) | -0.0 pts [-0.5, +0.5] (not shown) | -0.3 pts [-0.7, -0.0] (worse) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +25.2 pts [+23.6, +26.9]
- B vs A, persistence, weeks 4+8+12: +26.0 pts [+24.2, +27.8]
- B vs A, recovery within 14 days: +17.5 pts [+15.3, +19.8]
- B vs A, recovery within 14 days, after a labelled disruption: +16.9 pts [+13.8, +20.1]
- B vs A, recovery within 14 days, after an unlabelled shock: +18.5 pts [+15.1, +22.0]
- B vs A, median days from lapse to active: -2.5 d [-3.1, -1.9]
- B vs A, retention at end: +14.1 pts [+12.7, +15.5]
- B vs A, δ weekly active minutes (wk1→wk12): +16.3 min [+15.2, +17.5]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +14.0 pts [+12.8, +15.2]
- B vs A, lapse rate (≥ 1 lapse in the run): -9.0 pts [-10.4, -7.7]
- B vs A, messages per persona-week: +0.5 [+0.4, +0.5]
- C vs A, persistence, week 12: +25.2 pts [+23.6, +26.8]
- C vs A, persistence, weeks 4+8+12: +25.8 pts [+24.1, +27.5]
- C vs A, recovery within 14 days: +18.1 pts [+15.8, +20.4]
- C vs A, recovery within 14 days, after a labelled disruption: +17.6 pts [+14.5, +20.8]
- C vs A, recovery within 14 days, after an unlabelled shock: +19.5 pts [+15.7, +23.3]
- C vs A, median days from lapse to active: -2.4 d [-3.1, -1.7]
- C vs A, retention at end: +13.8 pts [+12.5, +15.1]
- C vs A, δ weekly active minutes (wk1→wk12): +16.6 min [+15.3, +17.9]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +13.9 pts [+12.8, +15.0]
- C vs A, lapse rate (≥ 1 lapse in the run): -9.1 pts [-10.5, -7.7]
- C vs A, messages per persona-week: +0.5 [+0.4, +0.5]
- C vs A0, persistence, week 12: -0.3 pts [-0.8, +0.2]
- C vs A0, persistence, weeks 4+8+12: -1.2 pts [-1.9, -0.5]
- C vs A0, recovery within 14 days: +1.0 pts [-0.4, +2.4]
- C vs A0, recovery within 14 days, after a labelled disruption: +1.2 pts [-1.0, +3.4]
- C vs A0, recovery within 14 days, after an unlabelled shock: +1.5 pts [+0.2, +2.8]
- C vs A0, median days from lapse to active: +0.1 d [-0.3, +0.5]
- C vs A0, retention at end: -0.0 pts [-0.6, +0.5]
- C vs A0, δ weekly active minutes (wk1→wk12): +8.5 min [+6.9, +10.0]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +10.4 pts [+9.3, +11.6]
- C vs A0, lapse rate (≥ 1 lapse in the run): +1.3 pts [+0.8, +1.8]
- C vs A0, messages per persona-week: +0.4 [+0.4, +0.4]
- C vs B, persistence, week 12: -0.0 pts [-0.5, +0.5]
- C vs B, persistence, weeks 4+8+12: -0.2 pts [-0.8, +0.4]
- C vs B, recovery within 14 days: +0.5 pts [+0.0, +1.0]
- C vs B, recovery within 14 days, after a labelled disruption: +0.7 pts [+0.3, +1.1]
- C vs B, recovery within 14 days, after an unlabelled shock: +1.0 pts [-0.4, +2.3]
- C vs B, median days from lapse to active: +0.1 d [-0.1, +0.3]
- C vs B, retention at end: -0.3 pts [-0.7, -0.0]
- C vs B, δ weekly active minutes (wk1→wk12): +0.3 min [-0.3, +0.8]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): -0.1 pts [-0.5, +0.3]
- C vs B, lapse rate (≥ 1 lapse in the run): -0.1 pts [-0.3, +0.2]
- C vs B, messages per persona-week: -0.0 [-0.0, +0.0]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 19.4% [14.5, 24.2] | 21.9% [16.0, 27.9] | 21.0% [15.5, 26.5] | 21.9% [17.0, 26.8] |
| health_literacy | Recovery within 14 days | 7.3% [4.3, 10.3] | 13.6% [9.1, 18.2] | 13.9% [10.1, 17.8] | 13.5% [8.9, 18.0] |
| health_literacy | Retention at end | 21.6% [17.2, 26.0] | 20.2% [15.4, 25.0] | 20.9% [16.4, 25.5] | 22.0% [17.6, 26.4] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 6.0 min [2.7, 9.2] | 6.2 min [3.7, 8.7] | 15.6 min [10.6, 20.7] | 14.5 min [9.1, 20.0] |
| language | Persistence, week 12 | 8.2% [4.8, 11.5] | 8.7% [5.4, 12.0] | 10.3% [7.1, 13.5] | 9.9% [6.6, 13.3] |
| language | Recovery within 14 days | 5.4% [2.9, 7.8] | 5.8% [3.4, 8.2] | 6.1% [4.0, 8.2] | 5.2% [3.4, 7.1] |
| language | Retention at end | 8.3% [4.9, 11.7] | 6.9% [4.9, 8.9] | 6.5% [4.8, 8.2] | 7.2% [5.8, 8.6] |
| language | Δ weekly active minutes (wk1→wk12) | 4.8 min [3.1, 6.6] | 5.0 min [2.5, 7.5] | 9.9 min [6.3, 13.4] | 9.2 min [6.5, 11.9] |
| mobility_limitation | Persistence, week 12 | 14.0% [9.9, 18.1] | 18.5% [9.3, 27.7] | 21.3% [11.9, 30.8] | 20.7% [11.4, 30.0] |
| mobility_limitation | Recovery within 14 days | 11.5% [7.6, 15.4] | 15.2% [9.6, 20.9] | 16.6% [9.4, 23.8] | 13.5% [6.9, 20.0] |
| mobility_limitation | Retention at end | 20.2% [11.2, 29.1] | 15.0% [9.2, 20.9] | 17.0% [10.9, 23.0] | 15.7% [10.0, 21.3] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 10.0 min [6.4, 13.7] | 7.8 min [4.5, 11.2] | 10.0 min [4.3, 15.6] | 11.1 min [5.5, 16.7] |
| schedule_type | Persistence, week 12 | 15.0% [10.6, 19.4] | 12.6% [9.7, 15.5] | 12.5% [9.0, 15.9] | 13.4% [9.5, 17.3] |
| schedule_type | Recovery within 14 days | 11.1% [8.1, 14.0] | 14.8% [11.6, 18.0] | 14.5% [11.6, 17.3] | 15.5% [12.3, 18.8] |
| schedule_type | Retention at end | 13.5% [9.8, 17.1] | 11.1% [8.2, 14.0] | 11.9% [8.1, 15.6] | 11.6% [7.3, 15.9] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 11.5 min [8.5, 14.4] | 10.2 min [7.7, 12.7] | 21.5 min [17.3, 25.6] | 21.5 min [16.4, 26.6] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Messages per persona-week vs A: +0.5 [+0.4, +0.5] (Rebound is worse)
- Persistence, week 12 vs A0: -0.3 pts [-0.8, +0.2] (no clear difference)
- Persistence, weeks 4+8+12 vs A0: -1.2 pts [-1.9, -0.5] (Rebound is worse)
- Recovery within 14 days vs A0: +1.0 pts [-0.4, +2.4] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: +1.2 pts [-1.0, +3.4] (no clear difference)
- Median days from lapse to active vs A0: +0.1 d [-0.3, +0.5] (no clear difference)
- Retention at end vs A0: -0.0 pts [-0.6, +0.5] (no clear difference)
- Lapse rate (≥ 1 lapse in the run) vs A0: +1.3 pts [+0.8, +1.8] (Rebound is worse)
- Messages per persona-week vs A0: +0.4 [+0.4, +0.4] (Rebound is worse)
