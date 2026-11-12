## Simulation results: scenario `baseline`

300 personas × 90 days × 10 seeds. Every number is the mean across seeds with a 95% interval for that mean.

| Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|
| Persistence, week 4 | 49.8% [47.6, 52.0] | 74.5% [73.6, 75.3] | 73.3% [72.1, 74.5] | 73.4% [72.1, 74.6] |
| Persistence, week 8 | 36.8% [35.0, 38.6] | 64.0% [61.8, 66.2] | 63.6% [61.0, 66.1] | 63.6% [60.9, 66.3] |
| Persistence, week 12 | 33.3% [31.2, 35.4] | 58.7% [56.7, 60.6] | 58.3% [56.2, 60.5] | 58.1% [56.2, 60.0] |
| Persistence, weeks 4+8+12 | 17.4% [15.6, 19.2] | 44.8% [42.5, 47.1] | 42.9% [40.3, 45.6] | 43.1% [40.5, 45.7] |
| Recovery within 14 days | 36.7% [35.3, 38.1] | 53.7% [52.3, 55.1] | 54.9% [53.2, 56.6] | 54.9% [53.3, 56.5] |
| Recovery within 14 days, after a labelled disruption | 35.8% [33.8, 37.8] | 51.8% [49.5, 54.1] | 53.5% [50.6, 56.4] | 53.7% [51.2, 56.3] |
| Recovery within 14 days, after an unlabelled shock | 40.3% [37.4, 43.2] | 58.4% [55.2, 61.6] | 60.4% [57.9, 62.9] | 60.2% [58.6, 61.8] |
| Recovery within 14 days, no disruption nearby | 36.3% [34.9, 37.7] | 53.3% [50.6, 56.0] | 53.8% [51.5, 56.2] | 53.6% [51.0, 56.3] |
| Median days from lapse to active | 11.6 d [11.0, 12.2] | 8.9 d [8.5, 9.3] | 9.0 d [9.0, 9.0] | 9.0 d [8.8, 9.2] |
| Median days from lapse to recovering | 5.9 d [5.7, 6.1] | 4.5 d [4.2, 4.9] | 4.4 d [4.0, 4.8] | 4.4 d [4.0, 4.8] |
| Δ weekly active minutes (wk1→wk12) | -20.7 min [-21.7, -19.7] | -12.6 min [-13.7, -11.5] | -5.6 min [-7.1, -4.2] | -5.2 min [-6.8, -3.5] |
| Δ tier-weighted sleep nights (wk1→wk12) | -9.0% [-9.3, -8.6] | -5.5% [-5.9, -5.0] | 3.2% [1.8, 4.7] | 3.1% [1.8, 4.4] |
| Δ sleep nights completed, raw (wk1→wk12) | -35.5% [-36.8, -34.2] | -21.5% [-23.3, -19.7] | -26.0% [-27.8, -24.2] | -26.0% [-27.8, -24.2] |
| Retention at end | 62.1% [60.0, 64.3] | 75.9% [73.3, 78.5] | 75.8% [73.6, 78.0] | 75.6% [73.5, 77.6] |
| Messages per persona-week | 11.7 [11.6, 11.8] | 11.8 [11.7, 11.9] | 12.2 [12.1, 12.3] | 12.2 [12.1, 12.3] |
| Messages in quiet hours | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| Share of messages in quiet hours | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] | 0.0% [0.0, 0.0] |
| Safety violations | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

Raw Δ sleep nights completed favours arms that ask for less (A keeps the easiest sleep action), so the comparisons use the tier-weighted version.

### Pre-registered headline (docs/ASSUMPTIONS.md, commit dc054ab)

Rebound "helps" on a measure only if the whole 95% interval of the difference is above zero; "worse" if it is entirely below zero; otherwise "not shown".

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|
| C vs A | +18.2 pts [+15.8, +20.6] (helps) | +24.8 pts [+23.1, +26.5] (helps) | +13.4 pts [+12.0, +14.8] (helps) |
| C vs A0 | +1.2 pts [-0.1, +2.4] (not shown) | -0.6 pts [-1.5, +0.4] (not shown) | -0.4 pts [-1.2, +0.5] (not shown) |
| C vs B | -0.0 pts [-1.0, +0.9] (not shown) | -0.2 pts [-0.9, +0.4] (not shown) | -0.2 pts [-0.9, +0.4] (not shown) |

### All arm comparisons (difference, 95% interval)

- B vs A, persistence, week 12: +25.0 pts [+23.4, +26.7]
- B vs A, persistence, weeks 4+8+12: +25.5 pts [+23.7, +27.3]
- B vs A, recovery within 14 days: +18.2 pts [+16.1, +20.3]
- B vs A, recovery within 14 days, after a labelled disruption: +17.7 pts [+14.3, +21.1]
- B vs A, recovery within 14 days, after an unlabelled shock: +20.1 pts [+17.4, +22.7]
- B vs A, median days from lapse to active: -2.6 d [-3.2, -2.0]
- B vs A, retention at end: +13.7 pts [+12.3, +15.0]
- B vs A, δ weekly active minutes (wk1→wk12): +15.1 min [+13.8, +16.4]
- B vs A, δ tier-weighted sleep nights (wk1→wk12): +12.2 pts [+10.8, +13.6]
- C vs A, persistence, week 12: +24.8 pts [+23.1, +26.5]
- C vs A, persistence, weeks 4+8+12: +25.7 pts [+23.7, +27.6]
- C vs A, recovery within 14 days: +18.2 pts [+15.8, +20.6]
- C vs A, recovery within 14 days, after a labelled disruption: +17.9 pts [+14.2, +21.7]
- C vs A, recovery within 14 days, after an unlabelled shock: +19.9 pts [+17.1, +22.6]
- C vs A, median days from lapse to active: -2.6 d [-3.3, -1.9]
- C vs A, retention at end: +13.4 pts [+12.0, +14.8]
- C vs A, δ weekly active minutes (wk1→wk12): +15.6 min [+13.9, +17.2]
- C vs A, δ tier-weighted sleep nights (wk1→wk12): +12.1 pts [+10.8, +13.3]
- C vs A0, persistence, week 12: -0.6 pts [-1.5, +0.4]
- C vs A0, persistence, weeks 4+8+12: -1.7 pts [-3.2, -0.2]
- C vs A0, recovery within 14 days: +1.2 pts [-0.1, +2.4]
- C vs A0, recovery within 14 days, after a labelled disruption: +1.9 pts [-0.8, +4.6]
- C vs A0, recovery within 14 days, after an unlabelled shock: +1.7 pts [-0.4, +3.9]
- C vs A0, median days from lapse to active: +0.1 d [-0.3, +0.5]
- C vs A0, retention at end: -0.4 pts [-1.2, +0.5]
- C vs A0, δ weekly active minutes (wk1→wk12): +7.4 min [+5.7, +9.1]
- C vs A0, δ tier-weighted sleep nights (wk1→wk12): +8.6 pts [+7.4, +9.8]
- C vs B, persistence, week 12: -0.2 pts [-0.9, +0.4]
- C vs B, persistence, weeks 4+8+12: +0.2 pts [-0.7, +1.0]
- C vs B, recovery within 14 days: -0.0 pts [-1.0, +0.9]
- C vs B, recovery within 14 days, after a labelled disruption: +0.2 pts [-1.6, +2.0]
- C vs B, recovery within 14 days, after an unlabelled shock: -0.2 pts [-2.7, +2.3]
- C vs B, median days from lapse to active: +0.0 d [-0.2, +0.2]
- C vs B, retention at end: -0.2 pts [-0.9, +0.4]
- C vs B, δ weekly active minutes (wk1→wk12): +0.5 min [-0.2, +1.2]
- C vs B, δ tier-weighted sleep nights (wk1→wk12): -0.1 pts [-0.5, +0.3]

### Equity: best-minus-worst segment gap (lower is fairer)

| Segment | Metric | A · streak app | A0 · streak app, no AVE | B · Rebound rules | C · Rebound full |
|---|---|---|---|---|---|
| health_literacy | Persistence, week 12 | 19.0% [14.5, 23.5] | 22.0% [15.8, 28.1] | 21.0% [15.2, 26.7] | 20.0% [13.9, 26.0] |
| health_literacy | Recovery within 14 days | 7.5% [4.4, 10.7] | 13.5% [9.2, 17.9] | 13.9% [9.5, 18.4] | 14.0% [10.1, 17.9] |
| health_literacy | Retention at end | 21.8% [17.4, 26.2] | 20.6% [15.8, 25.4] | 20.2% [15.6, 24.7] | 19.6% [15.5, 23.6] |
| health_literacy | Δ weekly active minutes (wk1→wk12) | 6.1 min [2.8, 9.5] | 6.1 min [3.7, 8.6] | 14.5 min [8.9, 20.1] | 14.3 min [9.3, 19.3] |
| language | Persistence, week 12 | 8.3% [4.6, 12.0] | 8.7% [5.4, 12.1] | 9.1% [5.8, 12.4] | 8.6% [4.7, 12.6] |
| language | Recovery within 14 days | 6.3% [3.7, 8.8] | 5.6% [3.1, 8.1] | 5.4% [3.0, 7.8] | 6.4% [3.2, 9.7] |
| language | Retention at end | 8.4% [4.7, 12.1] | 6.6% [4.6, 8.6] | 6.7% [4.7, 8.6] | 6.5% [4.0, 9.0] |
| language | Δ weekly active minutes (wk1→wk12) | 5.0 min [3.4, 6.7] | 5.2 min [2.6, 7.8] | 8.3 min [4.5, 12.2] | 9.7 min [6.2, 13.3] |
| mobility_limitation | Persistence, week 12 | 14.0% [9.7, 18.4] | 18.5% [9.3, 27.7] | 20.9% [11.9, 29.9] | 20.7% [12.0, 29.4] |
| mobility_limitation | Recovery within 14 days | 11.5% [7.3, 15.6] | 15.5% [9.8, 21.1] | 16.6% [12.5, 20.7] | 14.8% [10.2, 19.4] |
| mobility_limitation | Retention at end | 20.4% [11.7, 29.2] | 15.1% [9.3, 21.0] | 14.5% [7.5, 21.5] | 15.4% [9.6, 21.3] |
| mobility_limitation | Δ weekly active minutes (wk1→wk12) | 9.9 min [6.4, 13.5] | 7.9 min [4.5, 11.2] | 9.7 min [4.7, 14.6] | 9.8 min [4.6, 15.0] |
| schedule_type | Persistence, week 12 | 16.2% [12.0, 20.4] | 12.9% [9.9, 15.9] | 13.3% [9.5, 17.2] | 13.6% [10.4, 16.9] |
| schedule_type | Recovery within 14 days | 11.3% [9.0, 13.7] | 14.7% [11.4, 18.0] | 14.1% [11.4, 16.9] | 14.1% [12.0, 16.1] |
| schedule_type | Retention at end | 13.4% [9.8, 17.1] | 11.3% [8.2, 14.4] | 11.7% [7.2, 16.2] | 11.1% [7.0, 15.2] |
| schedule_type | Δ weekly active minutes (wk1→wk12) | 11.9 min [8.9, 14.9] | 10.1 min [7.4, 12.8] | 21.0 min [16.3, 25.7] | 21.7 min [17.6, 25.9] |

### Safety and burden

- A · streak app: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.7 [11.6, 11.8] messages per persona-week
- A0 · streak app, no AVE: 0 safety violations (max over seeds), 0 quiet-hour messages, 11.8 [11.7, 11.9] messages per persona-week
- B · Rebound rules: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week
- C · Rebound full: 0 safety violations (max over seeds), 0 quiet-hour messages, 12.2 [12.1, 12.3] messages per persona-week

### Where Rebound doesn't help

- Persistence, week 12 vs A0: -0.6 pts [-1.5, +0.4] (no clear difference)
- Persistence, weeks 4+8+12 vs A0: -1.7 pts [-3.2, -0.2] (Rebound is worse)
- Recovery within 14 days vs A0: +1.2 pts [-0.1, +2.4] (no clear difference)
- Recovery within 14 days, after a labelled disruption vs A0: +1.9 pts [-0.8, +4.6] (no clear difference)
- Recovery within 14 days, after an unlabelled shock vs A0: +1.7 pts [-0.4, +3.9] (no clear difference)
- Median days from lapse to active vs A0: +0.1 d [-0.3, +0.5] (no clear difference)
- Retention at end vs A0: -0.4 pts [-1.2, +0.5] (no clear difference)
