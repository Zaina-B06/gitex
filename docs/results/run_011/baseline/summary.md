## Simulation results: scenario `baseline`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 49.8% [47.6, 52.0] | 74.5% [73.6, 75.3] | 73.8% [72.3, 75.2] | 74.0% [72.4, 75.5] |
| Persistence, week 8 | 36.8% [35.0, 38.6] | 64.0% [61.8, 66.2] | 63.7% [61.2, 66.1] | 63.8% [61.3, 66.2] |
| Persistence, week 12 | 33.3% [31.2, 35.4] | 58.7% [56.7, 60.6] | 58.2% [56.3, 60.1] | 58.2% [56.4, 60.0] |
| Persistence, weeks 4+8+12 | 17.4% [15.6, 19.2] | 44.8% [42.5, 47.1] | 43.2% [40.7, 45.7] | 43.1% [40.6, 45.6] |
| Recovery within 14 days | 36.7% [35.3, 38.1] | 53.7% [52.3, 55.1] | 54.6% [53.2, 55.9] | 54.8% [53.5, 56.0] |
| Recovery within 14 days, after a labelled disruption | 35.8% [33.8, 37.8] | 51.8% [49.5, 54.1] | 53.6% [51.5, 55.6] | 53.9% [51.8, 56.1] |
| Recovery within 14 days, after an unlabelled shock | 40.3% [37.4, 43.2] | 58.4% [55.2, 61.6] | 58.8% [56.1, 61.4] | 58.9% [56.7, 61.1] |
| Recovery within 14 days, no disruption nearby | 36.3% [34.9, 37.7] | 53.3% [50.6, 56.0] | 53.6% [51.1, 56.1] | 53.7% [51.3, 56.1] |
| Median days from lapse to active | 11.6 d [11.0, 12.2] | 8.9 d [8.5, 9.3] | 9.1 d [8.6, 9.5] | 9.0 d [8.5, 9.5] |
| Median days from lapse to recovering | 5.9 d [5.7, 6.1] | 4.5 d [4.2, 4.9] | 4.5 d [4.1, 4.8] | 4.5 d [4.1, 4.8] |
| Δ weekly active minutes (wk1→wk12) | -20.7 min [-21.7, -19.7] | -12.6 min [-13.7, -11.5] | -4.5 min [-5.9, -3.1] | -3.8 min [-5.3, -2.4] |
| Δ tier-weighted sleep nights (wk1→wk12) | -9.0% [-9.3, -8.6] | -5.5% [-5.9, -5.0] | 4.8% [3.4, 6.2] | 5.0% [3.8, 6.2] |
| Δ sleep nights completed, raw (wk1→wk12) | -35.5% [-36.8, -34.2] | -21.5% [-23.3, -19.7] | -25.1% [-27.1, -23.2] | -25.0% [-27.0, -23.1] |
| Retention at end | 62.1% [60.0, 64.3] | 75.9% [73.3, 78.5] | 75.8% [73.7, 77.9] | 75.5% [73.3, 77.7] |
| Lapse rate (≥ 1 lapse in the run) | 96.6% [95.7, 97.5] | 86.1% [84.8, 87.5] | 87.6% [86.1, 89.1] | 87.4% [85.9, 88.9] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.1, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +18.1 pts [+16.0, +20.1] (helps) | +24.9 pts [+23.1, +26.6] (helps) | +13.4 pts [+12.0, +14.7] (helps) |
| C vs A0 | +1.0 pts [-0.2, +2.2] (not shown) | -0.5 pts [-0.9, -0.1] (worse) | -0.4 pts [-1.2, +0.3] (not shown) |
| C vs B | +0.2 pts [-0.4, +0.8] (not shown) | -0.0 pts [-0.6, +0.5] (not shown) | -0.3 pts [-0.7, +0.0] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +24.9 pts [+22.9, +26.9]
- B vs A, persistence, weeks 4+8+12: +25.8 pts [+23.9, +27.6]
- B vs A, recovery within 14 days: +17.8 pts [+16.0, +19.7]
- B vs A, recovery within 14 days, after a labelled disruption: +17.8 pts [+14.8, +20.7]
- B vs A, recovery within 14 days, after an unlabelled shock: +18.5 pts [+15.5, +21.5]
- B vs A, median days from lapse to active: -2.5 d [-3.1, -2.0]
- B vs A, retention at end: +13.7 pts [+12.4, +15.0]
- B vs A, δ weekly active minutes (wk1→wk12): +16.2 min [+15.0, +17.5]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +13.8 pts [+12.5, +15.1]
- B vs A, lapse rate (≥ 1 lapse in the run): -9.0 pts [-10.2, -7.7]
- B vs A, messages per persona-week: +0.5 [+0.4, +0.5]
- C vs A, persistence, week 12: +24.9 pts [+23.1, +26.6]
- C vs A, persistence, weeks 4+8+12: +25.7 pts [+24.0, +27.3]
- C vs A, recovery within 14 days: +18.1 pts [+16.0, +20.1]
- C vs A, recovery within 14 days, after a labelled disruption: +18.1 pts [+14.8, +21.5]
- C vs A, recovery within 14 days, after an unlabelled shock: +18.6 pts [+15.5, +21.7]
- C vs A, median days from lapse to active: -2.6 d [-3.2, -2.0]
- C vs A, retention at end: +13.4 pts [+12.0, +14.7]
- C vs A, δ weekly active minutes (wk1→wk12): +16.9 min [+15.6, +18.2]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +13.9 pts [+12.8, +15.0]
- C vs A, lapse rate (≥ 1 lapse in the run): -9.2 pts [-10.4, -8.0]
- C vs A, messages per persona-week: +0.5 [+0.4, +0.5]
- C vs A0, persistence, week 12: -0.5 pts [-0.9, -0.1]
- C vs A0, persistence, weeks 4+8+12: -1.7 pts [-2.6, -0.8]
- C vs A0, recovery within 14 days: +1.0 pts [-0.2, +2.2]
- C vs A0, recovery within 14 days, after a labelled disruption: +2.1 pts [-0.3, +4.6]
- C vs A0, recovery within 14 days, after an unlabelled shock: +0.5 pts [-1.2, +2.3]
- C vs A0, median days from lapse to active: +0.1 d [-0.3, +0.5]
- C vs A0, retention at end: -0.4 pts [-1.2, +0.3]
- C vs A0, δ weekly active minutes (wk1→wk12): +8.7 min [+7.3, +10.1]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +10.4 pts [+9.3, +11.5]
- C vs A0, lapse rate (≥ 1 lapse in the run): +1.3 pts [+0.8, +1.8]
- C vs A0, messages per persona-week: +0.4 [+0.4, +0.4]
- C vs B, persistence, week 12: -0.0 pts [-0.6, +0.5]
- C vs B, persistence, weeks 4+8+12: -0.1 pts [-0.5, +0.3]
- C vs B, recovery within 14 days: +0.2 pts [-0.4, +0.8]
- C vs B, recovery within 14 days, after a labelled disruption: +0.4 pts [-0.7, +1.5]
- C vs B, recovery within 14 days, after an unlabelled shock: +0.1 pts [-1.0, +1.3]
- C vs B, median days from lapse to active: -0.1 d [-0.2, +0.1]
- C vs B, retention at end: -0.3 pts [-0.7, +0.0]
- C vs B, δ weekly active minutes (wk1→wk12): +0.7 min [-0.2, +1.6]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): +0.1 pts [-0.3, +0.6]
- C vs B, lapse rate (≥ 1 lapse in the run): -0.2 pts [-0.6, +0.2]
- C vs B, messages per persona-week: -0.0 [-0.0, +0.0]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 19.0% [14.5, 23.5] | 22.0% [15.8, 28.1] | 20.6% [14.7, 26.6] | 21.5% [15.8, 27.1] |
| health_literacy | Recovery within 14 days | 7.5% [4.4, 10.7] | 13.5% [9.2, 17.9] | 13.8% [9.6, 18.0] | 13.9% [9.7, 18.2] |
| health_literacy | Retention at end | 21.8% [17.4, 26.2] | 20.6% [15.8, 25.4] | 20.7% [15.6, 25.8] | 21.4% [17.0, 25.9] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 6.1 min [2.8, 9.5] | 6.1 min [3.7, 8.6] | 14.6 min [9.7, 19.6] | 15.8 min [9.8, 21.9] |
| language | Persistence, week 12 | 8.3% [4.6, 12.0] | 8.7% [5.4, 12.1] | 9.5% [6.2, 12.8] | 9.7% [6.7, 12.7] |
| language | Recovery within 14 days | 6.3% [3.7, 8.8] | 5.6% [3.1, 8.1] | 6.6% [4.3, 8.8] | 6.0% [3.7, 8.4] |
| language | Retention at end | 8.4% [4.7, 12.1] | 6.6% [4.6, 8.6] | 6.4% [4.5, 8.3] | 6.5% [4.4, 8.6] |
| language | Δ weekly active minutes (wk1→wk12) | 5.0 min [3.4, 6.7] | 5.2 min [2.6, 7.8] | 9.5 min [6.3, 12.6] | 8.4 min [5.2, 11.6] |
| mobility_limitation | Persistence, week 12 | 14.0% [9.7, 18.4] | 18.5% [9.3, 27.7] | 18.8% [10.6, 27.1] | 19.5% [11.5, 27.5] |
| mobility_limitation | Recovery within 14 days | 11.5% [7.3, 15.6] | 15.5% [9.8, 21.1] | 15.5% [10.2, 20.7] | 15.8% [11.7, 19.8] |
| mobility_limitation | Retention at end | 20.4% [11.7, 29.2] | 15.1% [9.3, 21.0] | 16.5% [10.0, 23.0] | 14.6% [8.7, 20.5] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.9 min [6.4, 13.5] | 7.9 min [4.5, 11.2] | 9.5 min [3.9, 15.1] | 11.3 min [5.1, 17.5] |
| schedule_type | Persistence, week 12 | 16.2% [12.0, 20.4] | 12.9% [9.9, 15.9] | 12.9% [8.4, 17.5] | 13.2% [9.4, 17.0] |
| schedule_type | Recovery within 14 days | 11.3% [9.0, 13.7] | 14.7% [11.4, 18.0] | 13.8% [11.8, 15.9] | 14.0% [11.1, 16.9] |
| schedule_type | Retention at end | 13.4% [9.8, 17.1] | 11.3% [8.2, 14.4] | 11.4% [7.2, 15.6] | 11.6% [7.4, 15.7] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 11.9 min [8.9, 14.9] | 10.1 min [7.4, 12.8] | 20.8 min [17.0, 24.6] | 21.1 min [17.0, 25.2] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Messages per persona-week vs A: +0.5 [+0.4, +0.5] (Rebound is worse)
- Persistence, week 12 vs A0: -0.5 pts [-0.9, -0.1] (Rebound is worse)
- Persistence, weeks 4+8+12 vs A0: -1.7 pts [-2.6, -0.8] (Rebound is worse)
- Recovery within 14 days vs A0: +1.0 pts [-0.2, +2.2] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: +2.1 pts [-0.3, +4.6] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +0.5 pts [-1.2, +2.3] (no clear difference)
- Median days from lapse to active vs A0: +0.1 d [-0.3, +0.5] (no clear difference)
- Retention at end vs A0: -0.4 pts [-1.2, +0.3] (no clear difference)
- Lapse rate (≥ 1 lapse in the run) vs A0: +1.3 pts [+0.8, +1.8] (Rebound is worse)
- Messages per persona-week vs A0: +0.4 [+0.4, +0.4] (Rebound is worse)
