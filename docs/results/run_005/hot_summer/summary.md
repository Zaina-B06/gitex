## Simulation results: scenario `hot_summer`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 49.5% [47.5, 51.5] | 74.1% [73.2, 75.0] | 73.2% [72.0, 74.5] | 73.3% [72.1, 74.6] |
| Persistence, week 8 | 36.8% [34.8, 38.8] | 63.6% [61.4, 65.9] | 63.4% [60.9, 65.9] | 63.2% [60.8, 65.6] |
| Persistence, week 12 | 33.4% [31.4, 35.4] | 58.8% [56.8, 60.7] | 58.3% [56.4, 60.2] | 58.1% [56.2, 60.0] |
| Persistence, weeks 4+8+12 | 17.5% [15.8, 19.2] | 44.6% [42.3, 46.9] | 42.8% [40.1, 45.6] | 43.0% [40.5, 45.6] |
| Recovery within 14 days | 36.0% [34.7, 37.3] | 53.4% [52.1, 54.6] | 54.7% [53.2, 56.2] | 54.5% [52.8, 56.1] |
| Recovery within 14 days, after a labelled disruption | 35.0% [33.1, 36.9] | 51.4% [49.1, 53.6] | 53.1% [50.2, 55.9] | 53.3% [51.0, 55.6] |
| Recovery within 14 days, after an unlabelled shock | 39.9% [37.0, 42.7] | 57.8% [55.1, 60.5] | 59.7% [57.2, 62.2] | 59.1% [57.4, 60.8] |
| Recovery within 14 days, no disruption nearby | 35.6% [34.3, 36.8] | 53.0% [50.3, 55.8] | 53.9% [51.7, 56.2] | 53.5% [51.1, 55.9] |
| Median days from lapse to active | 11.8 d [11.1, 12.5] | 9.1 d [8.7, 9.5] | 9.1 d [8.9, 9.3] | 9.1 d [8.9, 9.3] |
| Median days from lapse to recovering | 6.0 d [6.0, 6.0] | 4.8 d [4.5, 5.1] | 4.4 d [4.0, 4.8] | 4.4 d [4.0, 4.8] |
| Δ weekly active minutes (wk1→wk12) | -20.0 min [-21.0, -19.1] | -11.7 min [-12.9, -10.6] | -4.3 min [-5.9, -2.8] | -2.9 min [-4.3, -1.4] |
| Δ tier-weighted sleep nights (wk1→wk12) | -8.9% [-9.2, -8.6] | -5.5% [-5.9, -5.0] | 3.5% [2.1, 5.0] | 3.7% [2.3, 5.0] |
| Δ sleep nights completed, raw (wk1→wk12) | -35.3% [-36.6, -34.0] | -21.5% [-23.3, -19.7] | -25.7% [-27.5, -23.9] | -25.3% [-27.0, -23.5] |
| Retention at end | 62.3% [60.1, 64.6] | 76.0% [73.3, 78.6] | 75.6% [73.6, 77.7] | 75.6% [73.3, 77.9] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.1, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit dc054ab)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +18.5 pts [+16.3, +20.7] (helps) | +24.7 pts [+23.2, +26.2] (helps) | +13.3 pts [+11.9, +14.6] (helps) |
| C vs A0 | +1.1 pts [-0.2, +2.5] (not shown) | -0.7 pts [-1.2, -0.1] (worse) | -0.4 pts [-0.9, +0.2] (not shown) |
| C vs B | -0.2 pts [-1.0, +0.6] (not shown) | -0.2 pts [-0.7, +0.4] (not shown) | -0.0 pts [-0.9, +0.8] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +24.9 pts [+23.3, +26.4]
- B vs A, persistence, weeks 4+8+12: +25.3 pts [+23.2, +27.5]
- B vs A, recovery within 14 days: +18.7 pts [+16.8, +20.7]
- B vs A, recovery within 14 days, after a labelled disruption: +18.0 pts [+14.6, +21.4]
- B vs A, recovery within 14 days, after an unlabelled shock: +19.8 pts [+17.6, +22.1]
- B vs A, median days from lapse to active: -2.7 d [-3.4, -2.0]
- B vs A, retention at end: +13.3 pts [+12.1, +14.5]
- B vs A, δ weekly active minutes (wk1→wk12): +15.7 min [+14.2, +17.1]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +12.4 pts [+11.1, +13.8]
- C vs A, persistence, week 12: +24.7 pts [+23.2, +26.2]
- C vs A, persistence, weeks 4+8+12: +25.5 pts [+23.5, +27.6]
- C vs A, recovery within 14 days: +18.5 pts [+16.3, +20.7]
- C vs A, recovery within 14 days, after a labelled disruption: +18.3 pts [+15.5, +21.0]
- C vs A, recovery within 14 days, after an unlabelled shock: +19.3 pts [+16.6, +21.9]
- C vs A, median days from lapse to active: -2.7 d [-3.4, -2.0]
- C vs A, retention at end: +13.3 pts [+11.9, +14.6]
- C vs A, δ weekly active minutes (wk1→wk12): +17.1 min [+15.7, +18.6]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +12.6 pts [+11.3, +13.8]
- C vs A0, persistence, week 12: -0.7 pts [-1.2, -0.1]
- C vs A0, persistence, weeks 4+8+12: -1.6 pts [-2.7, -0.4]
- C vs A0, recovery within 14 days: +1.1 pts [-0.2, +2.5]
- C vs A0, recovery within 14 days, after a labelled disruption: +1.9 pts [-0.4, +4.2]
- C vs A0, recovery within 14 days, after an unlabelled shock: +1.3 pts [-0.6, +3.2]
- C vs A0, median days from lapse to active: +0.0 d [-0.3, +0.3]
- C vs A0, retention at end: -0.4 pts [-0.9, +0.2]
- C vs A0, δ weekly active minutes (wk1→wk12): +8.9 min [+7.5, +10.2]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +9.1 pts [+8.0, +10.3]
- C vs B, persistence, week 12: -0.2 pts [-0.7, +0.4]
- C vs B, persistence, weeks 4+8+12: +0.2 pts [-0.4, +0.8]
- C vs B, recovery within 14 days: -0.2 pts [-1.0, +0.6]
- C vs B, recovery within 14 days, after a labelled disruption: +0.2 pts [-1.3, +1.7]
- C vs B, recovery within 14 days, after an unlabelled shock: -0.6 pts [-2.2, +1.1]
- C vs B, median days from lapse to active: +0.0 d [+0.0, +0.0]
- C vs B, retention at end: -0.0 pts [-0.9, +0.8]
- C vs B, δ weekly active minutes (wk1→wk12): +1.5 min [+0.5, +2.4]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): +0.1 pts [-0.1, +0.4]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 18.7% [14.5, 22.9] | 21.8% [15.5, 28.0] | 21.1% [15.4, 26.7] | 21.1% [15.7, 26.5] |
| health_literacy | Recovery within 14 days | 7.4% [4.4, 10.4] | 13.0% [8.6, 17.3] | 13.3% [9.2, 17.4] | 14.0% [9.7, 18.3] |
| health_literacy | Retention at end | 21.4% [17.3, 25.6] | 20.7% [15.9, 25.5] | 20.8% [16.1, 25.4] | 20.1% [15.8, 24.4] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 5.7 min [2.5, 9.0] | 6.0 min [3.9, 8.1] | 15.0 min [10.1, 19.9] | 14.5 min [8.4, 20.7] |
| language | Persistence, week 12 | 8.3% [4.8, 11.8] | 9.1% [5.7, 12.6] | 9.1% [6.0, 12.1] | 9.4% [5.9, 13.0] |
| language | Recovery within 14 days | 5.3% [2.9, 7.7] | 5.9% [3.5, 8.3] | 5.8% [3.4, 8.2] | 5.4% [2.4, 8.4] |
| language | Retention at end | 8.1% [5.0, 11.2] | 6.5% [4.4, 8.6] | 6.5% [4.5, 8.5] | 6.7% [4.7, 8.7] |
| language | Δ weekly active minutes (wk1→wk12) | 5.0 min [3.3, 6.7] | 5.0 min [2.4, 7.5] | 8.8 min [5.3, 12.2] | 9.2 min [5.2, 13.2] |
| mobility_limitation | Persistence, week 12 | 14.2% [9.9, 18.5] | 18.6% [9.4, 27.8] | 19.6% [10.7, 28.6] | 20.2% [11.5, 28.9] |
| mobility_limitation | Recovery within 14 days | 11.5% [7.6, 15.4] | 15.4% [9.9, 20.9] | 16.8% [12.5, 21.1] | 16.1% [9.7, 22.5] |
| mobility_limitation | Retention at end | 20.6% [11.9, 29.3] | 15.2% [9.3, 21.1] | 14.4% [7.4, 21.5] | 15.5% [9.7, 21.3] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.6 min [5.9, 13.2] | 7.6 min [4.1, 11.0] | 10.1 min [5.0, 15.3] | 10.3 min [5.0, 15.6] |
| schedule_type | Persistence, week 12 | 16.5% [11.9, 21.0] | 13.1% [10.2, 16.0] | 14.1% [10.5, 17.8] | 14.2% [10.7, 17.6] |
| schedule_type | Recovery within 14 days | 11.1% [8.7, 13.5] | 14.2% [11.0, 17.3] | 13.6% [10.9, 16.4] | 14.3% [11.5, 17.1] |
| schedule_type | Retention at end | 13.6% [9.8, 17.3] | 11.3% [8.2, 14.4] | 12.3% [7.4, 17.1] | 11.5% [7.5, 15.6] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 11.6 min [8.6, 14.5] | 10.1 min [7.2, 12.9] | 21.1 min [15.7, 26.5] | 21.1 min [16.2, 26.0] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Persistence, week 12 vs A0: -0.7 pts [-1.2, -0.1] (Rebound is worse)
- Persistence, weeks 4+8+12 vs A0: -1.6 pts [-2.7, -0.4] (Rebound is worse)
- Recovery within 14 days vs A0: +1.1 pts [-0.2, +2.5] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: +1.9 pts [-0.4, +4.2] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +1.3 pts [-0.6, +3.2] (no clear difference)
- Median days from lapse to active vs A0: +0.0 d [-0.3, +0.3] (no clear difference)
- Retention at end vs A0: -0.4 pts [-0.9, +0.2] (no clear difference)
