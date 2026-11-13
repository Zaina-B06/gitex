## Simulation results: scenario `ramadan_heavy`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 49.5% [47.3, 51.7] | 74.2% [73.3, 75.1] | 73.4% [72.1, 74.6] | 73.7% [72.3, 75.0] |
| Persistence, week 8 | 36.9% [35.1, 38.7] | 63.9% [61.6, 66.1] | 63.8% [61.4, 66.2] | 63.5% [60.8, 66.2] |
| Persistence, week 12 | 33.2% [31.0, 35.4] | 58.7% [56.7, 60.6] | 58.4% [56.2, 60.6] | 57.9% [55.7, 60.0] |
| Persistence, weeks 4+8+12 | 17.6% [15.7, 19.5] | 44.6% [42.4, 46.8] | 43.5% [41.0, 46.0] | 43.0% [40.5, 45.5] |
| Recovery within 14 days | 36.6% [35.2, 38.0] | 53.7% [52.3, 55.1] | 54.6% [53.0, 56.2] | 54.8% [53.2, 56.4] |
| Recovery within 14 days, after a labelled disruption | 35.5% [33.4, 37.7] | 51.9% [50.0, 53.8] | 53.2% [51.0, 55.3] | 54.0% [52.1, 55.8] |
| Recovery within 14 days, after an unlabelled shock | 40.5% [37.4, 43.7] | 58.5% [55.0, 62.1] | 60.6% [58.4, 62.7] | 59.5% [58.1, 60.9] |
| Recovery within 14 days, no disruption nearby | 36.4% [34.6, 38.1] | 53.2% [50.2, 56.2] | 53.3% [50.7, 55.9] | 53.4% [50.5, 56.3] |
| Median days from lapse to active | 11.5 d [10.9, 12.1] | 9.0 d [8.7, 9.3] | 8.9 d [8.7, 9.1] | 9.1 d [8.9, 9.3] |
| Median days from lapse to recovering | 5.8 d [5.5, 6.1] | 4.6 d [4.2, 5.0] | 4.5 d [4.1, 4.9] | 4.3 d [4.0, 4.6] |
| Δ weekly active minutes (wk1→wk12) | -20.7 min [-21.8, -19.7] | -12.6 min [-13.7, -11.5] | -5.6 min [-6.9, -4.2] | -5.3 min [-6.9, -3.7] |
| Δ tier-weighted sleep nights (wk1→wk12) | -9.0% [-9.3, -8.6] | -5.5% [-5.9, -5.0] | 3.5% [1.9, 5.0] | 3.2% [1.9, 4.6] |
| Δ sleep nights completed, raw (wk1→wk12) | -35.5% [-36.8, -34.2] | -21.6% [-23.4, -19.8] | -26.0% [-27.9, -24.1] | -25.9% [-27.7, -24.1] |
| Retention at end | 61.9% [59.9, 64.0] | 75.8% [73.3, 78.2] | 75.8% [73.6, 78.0] | 75.8% [73.5, 78.0] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.1, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit 3cc111b)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +18.2 pts [+15.8, +20.6] (helps) | +24.7 pts [+23.1, +26.3] (helps) | +13.8 pts [+12.3, +15.4] (helps) |
| C vs A0 | +1.1 pts [-0.0, +2.3] (not shown) | -0.8 pts [-1.8, +0.2] (not shown) | +0.0 pts [-0.5, +0.5] (not shown) |
| C vs B | +0.2 pts [-0.7, +1.1] (not shown) | -0.5 pts [-1.0, -0.1] (worse) | -0.0 pts [-0.5, +0.5] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +25.2 pts [+23.6, +26.9]
- B vs A, persistence, weeks 4+8+12: +25.9 pts [+24.1, +27.7]
- B vs A, recovery within 14 days: +18.0 pts [+16.0, +20.0]
- B vs A, recovery within 14 days, after a labelled disruption: +17.6 pts [+14.7, +20.6]
- B vs A, recovery within 14 days, after an unlabelled shock: +20.0 pts [+16.7, +23.3]
- B vs A, median days from lapse to active: -2.6 d [-3.2, -2.0]
- B vs A, retention at end: +13.9 pts [+12.3, +15.5]
- B vs A, δ weekly active minutes (wk1→wk12): +15.2 min [+14.0, +16.3]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +12.4 pts [+11.0, +13.8]
- C vs A, persistence, week 12: +24.7 pts [+23.1, +26.3]
- C vs A, persistence, weeks 4+8+12: +25.4 pts [+23.8, +27.1]
- C vs A, recovery within 14 days: +18.2 pts [+15.8, +20.6]
- C vs A, recovery within 14 days, after a labelled disruption: +18.5 pts [+15.7, +21.2]
- C vs A, recovery within 14 days, after an unlabelled shock: +18.9 pts [+15.4, +22.5]
- C vs A, median days from lapse to active: -2.4 d [-3.0, -1.8]
- C vs A, retention at end: +13.8 pts [+12.3, +15.4]
- C vs A, δ weekly active minutes (wk1→wk12): +15.5 min [+14.2, +16.8]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +12.2 pts [+11.0, +13.4]
- C vs A0, persistence, week 12: -0.8 pts [-1.8, +0.2]
- C vs A0, persistence, weeks 4+8+12: -1.6 pts [-3.0, -0.2]
- C vs A0, recovery within 14 days: +1.1 pts [-0.0, +2.3]
- C vs A0, recovery within 14 days, after a labelled disruption: +2.1 pts [+0.7, +3.4]
- C vs A0, recovery within 14 days, after an unlabelled shock: +0.9 pts [-1.5, +3.4]
- C vs A0, median days from lapse to active: +0.1 d [-0.1, +0.3]
- C vs A0, retention at end: +0.0 pts [-0.5, +0.5]
- C vs A0, δ weekly active minutes (wk1→wk12): +7.3 min [+6.0, +8.7]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +8.7 pts [+7.5, +9.9]
- C vs B, persistence, week 12: -0.5 pts [-1.0, -0.1]
- C vs B, persistence, weeks 4+8+12: -0.5 pts [-1.1, +0.2]
- C vs B, recovery within 14 days: +0.2 pts [-0.7, +1.1]
- C vs B, recovery within 14 days, after a labelled disruption: +0.8 pts [-0.5, +2.2]
- C vs B, recovery within 14 days, after an unlabelled shock: -1.1 pts [-2.5, +0.3]
- C vs B, median days from lapse to active: +0.2 d [-0.1, +0.5]
- C vs B, retention at end: -0.0 pts [-0.5, +0.5]
- C vs B, δ weekly active minutes (wk1→wk12): +0.3 min [-0.3, +0.9]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): -0.2 pts [-0.6, +0.1]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 19.4% [14.5, 24.2] | 21.9% [16.0, 27.9] | 21.3% [15.6, 27.0] | 21.1% [15.5, 26.8] |
| health_literacy | Recovery within 14 days | 7.3% [4.3, 10.3] | 13.6% [9.1, 18.2] | 13.6% [9.6, 17.7] | 13.8% [10.7, 17.0] |
| health_literacy | Retention at end | 21.6% [17.2, 26.0] | 20.2% [15.4, 25.0] | 20.7% [15.6, 25.8] | 19.5% [14.3, 24.8] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 6.0 min [2.7, 9.2] | 6.2 min [3.7, 8.7] | 15.1 min [10.4, 19.8] | 14.8 min [9.6, 20.0] |
| language | Persistence, week 12 | 8.2% [4.8, 11.5] | 8.7% [5.4, 12.0] | 9.0% [5.3, 12.7] | 9.4% [5.2, 13.5] |
| language | Recovery within 14 days | 5.4% [2.9, 7.8] | 5.8% [3.4, 8.2] | 6.2% [4.0, 8.4] | 6.4% [3.9, 8.8] |
| language | Retention at end | 8.3% [4.9, 11.7] | 6.9% [4.9, 8.9] | 7.2% [5.1, 9.3] | 6.6% [4.2, 8.9] |
| language | Δ weekly active minutes (wk1→wk12) | 4.8 min [3.1, 6.6] | 5.0 min [2.5, 7.5] | 10.1 min [5.9, 14.3] | 10.6 min [7.2, 14.1] |
| mobility_limitation | Persistence, week 12 | 14.0% [9.9, 18.1] | 18.5% [9.3, 27.7] | 19.0% [11.1, 26.9] | 17.8% [9.9, 25.6] |
| mobility_limitation | Recovery within 14 days | 11.5% [7.6, 15.4] | 15.2% [9.6, 20.9] | 17.0% [13.0, 21.0] | 18.9% [13.4, 24.5] |
| mobility_limitation | Retention at end | 20.2% [11.2, 29.1] | 15.0% [9.2, 20.9] | 15.7% [9.0, 22.3] | 14.8% [8.8, 20.9] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 10.0 min [6.4, 13.7] | 7.8 min [4.5, 11.2] | 9.2 min [4.4, 14.0] | 9.6 min [4.6, 14.6] |
| schedule_type | Persistence, week 12 | 15.0% [10.6, 19.4] | 12.6% [9.7, 15.5] | 12.9% [9.0, 16.9] | 13.2% [9.4, 16.9] |
| schedule_type | Recovery within 14 days | 11.1% [8.1, 14.0] | 14.8% [11.6, 18.0] | 13.4% [10.3, 16.4] | 12.2% [10.7, 13.8] |
| schedule_type | Retention at end | 13.5% [9.8, 17.1] | 11.1% [8.2, 14.0] | 11.3% [6.7, 15.8] | 11.6% [7.4, 15.9] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 11.5 min [8.5, 14.4] | 10.2 min [7.7, 12.7] | 21.0 min [16.0, 25.9] | 21.8 min [17.8, 25.8] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Persistence, week 12 vs A0: -0.8 pts [-1.8, +0.2] (no clear difference)
- Persistence, weeks 4+8+12 vs A0: -1.6 pts [-3.0, -0.2] (Rebound is worse)
- Recovery within 14 days vs A0: +1.1 pts [-0.0, +2.3] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +0.9 pts [-1.5, +3.4] (no clear difference)
- Median days from lapse to active vs A0: +0.1 d [-0.1, +0.3] (no clear difference)
- Retention at end vs A0: +0.0 pts [-0.5, +0.5] (no clear difference)
