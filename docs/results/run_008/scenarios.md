## Pre-registered headline across scenarios

"helps" = whole 95% interval of the difference above zero; "worse" = whole interval below zero; otherwise "not shown".

| Scenario | Comparison | Recovery within 14 days | Persistence, week 12 | Retention at end |
|---|---|---|---|---|
| baseline | C vs A | +18.5 pts [+16.4, +20.7] (helps) | +25.2 pts [+23.8, +26.5] (helps) | +13.8 pts [+12.5, +15.1] (helps) |
| baseline | C vs A0 | +1.5 pts [+0.4, +2.6] (helps) | -0.2 pts [-1.0, +0.6] (not shown) | -0.0 pts [-0.7, +0.7] (not shown) |
| harsh_attrition | C vs A | +13.9 pts [+12.2, +15.7] (helps) | +17.5 pts [+15.8, +19.3] (helps) | +14.4 pts [+12.6, +16.1] (helps) |
| harsh_attrition | C vs A0 | +0.6 pts [-0.4, +1.7] (not shown) | -0.1 pts [-0.8, +0.5] (not shown) | -0.1 pts [-1.1, +0.9] (not shown) |
| high_dropout | C vs A | +13.3 pts [+11.8, +14.9] (helps) | +17.3 pts [+15.6, +18.9] (helps) | +18.7 pts [+17.5, +19.9] (helps) |
| high_dropout | C vs A0 | +0.6 pts [-0.6, +1.8] (not shown) | -0.7 pts [-1.3, -0.2] (worse) | -0.3 pts [-1.0, +0.4] (not shown) |
| hot_summer | C vs A | +19.2 pts [+16.9, +21.4] (helps) | +25.1 pts [+23.7, +26.6] (helps) | +13.4 pts [+12.0, +14.7] (helps) |
| hot_summer | C vs A0 | +1.8 pts [+0.5, +3.1] (helps) | -0.2 pts [-0.8, +0.4] (not shown) | -0.3 pts [-1.0, +0.5] (not shown) |
| low_checkin | C vs A | +18.5 pts [+16.3, +20.7] (helps) | +25.2 pts [+23.3, +27.2] (helps) | +14.1 pts [+12.8, +15.4] (helps) |
| low_checkin | C vs A0 | +1.5 pts [+0.0, +3.0] (helps) | -0.1 pts [-0.8, +0.5] (not shown) | +0.3 pts [-0.6, +1.1] (not shown) |
| ramadan_heavy | C vs A | +18.3 pts [+16.1, +20.4] (helps) | +25.0 pts [+23.7, +26.3] (helps) | +14.0 pts [+12.7, +15.4] (helps) |
| ramadan_heavy | C vs A0 | +1.2 pts [+0.0, +2.4] (helps) | -0.5 pts [-1.4, +0.3] (not shown) | +0.2 pts [-0.5, +0.9] (not shown) |
| shock_heavy | C vs A | +16.7 pts [+14.9, +18.6] (helps) | +21.6 pts [+19.9, +23.4] (helps) | +15.1 pts [+13.5, +16.6] (helps) |
| shock_heavy | C vs A0 | +0.8 pts [+0.2, +1.5] (helps) | -1.1 pts [-2.0, -0.3] (worse) | -0.4 pts [-1.2, +0.5] (not shown) |

Recovery after unlabelled shocks vs labelled disruptions (C vs A, C vs A0):

- baseline: C vs A after a labelled disruption: +18.2 pts [+14.9, +21.6]; C vs A after an unlabelled shock: +19.7 pts [+16.7, +22.7]; C vs A0 after a labelled disruption: +2.2 pts [-0.7, +5.1]; C vs A0 after an unlabelled shock: +1.6 pts [-0.6, +3.8]
- harsh_attrition: C vs A after a labelled disruption: +12.4 pts [+9.8, +15.0]; C vs A after an unlabelled shock: +16.9 pts [+14.5, +19.4]; C vs A0 after a labelled disruption: +0.7 pts [-1.1, +2.5]; C vs A0 after an unlabelled shock: +2.3 pts [-0.3, +5.0]
- high_dropout: C vs A after a labelled disruption: +11.6 pts [+8.3, +14.9]; C vs A after an unlabelled shock: +17.5 pts [+13.1, +22.0]; C vs A0 after a labelled disruption: +0.8 pts [-1.2, +2.8]; C vs A0 after an unlabelled shock: +2.3 pts [-1.3, +6.0]
- hot_summer: C vs A after a labelled disruption: +19.3 pts [+16.3, +22.3]; C vs A after an unlabelled shock: +19.9 pts [+17.3, +22.5]; C vs A0 after a labelled disruption: +3.0 pts [+0.6, +5.4]; C vs A0 after an unlabelled shock: +1.9 pts [-0.1, +4.0]
- low_checkin: C vs A after a labelled disruption: +17.6 pts [+14.4, +20.8]; C vs A after an unlabelled shock: +19.7 pts [+16.9, +22.4]; C vs A0 after a labelled disruption: +1.6 pts [-0.3, +3.6]; C vs A0 after an unlabelled shock: +1.5 pts [-0.3, +3.4]
- ramadan_heavy: C vs A after a labelled disruption: +18.0 pts [+15.5, +20.4]; C vs A after an unlabelled shock: +18.8 pts [+15.4, +22.3]; C vs A0 after a labelled disruption: +1.6 pts [-0.2, +3.4]; C vs A0 after an unlabelled shock: +0.8 pts [-2.1, +3.7]
- shock_heavy: C vs A after a labelled disruption: +14.2 pts [+10.6, +17.7]; C vs A after an unlabelled shock: +15.4 pts [+13.7, +17.2]; C vs A0 after a labelled disruption: +1.2 pts [-1.3, +3.7]; C vs A0 after an unlabelled shock: +0.5 pts [-0.3, +1.3]

## Pre-registered lapse-risk hook test: D (and D50) vs C

Ship rule (docs/ASSUMPTIONS.md, "Arm D"), D vs C only: (1) lapse rate "helps" (lower) in baseline; (2) no engagement measure "worse" in any scenario; (3) messages per persona-week up by at most +0.5 on average in every scenario. D50 (50/50 pick) is the sensitivity version.

| Scenario | Comparison | Lapse rate (≥ 1 lapse in the run) | Persistence, week 12 | Recovery within 14 days | Retention at end | Messages per persona-week |
|---|---|---|---|---|---|---|
| baseline | D vs C | +0.2 pts [-0.1, +0.5] (not shown) | +0.1 pts [-0.8, +0.9] (not shown) | +0.0 pts [-0.7, +0.7] (not shown) | +0.3 pts [-0.4, +1.0] (not shown) | +0.1 [+0.1, +0.1] (within cap) |
| baseline | D50 vs C | +0.1 pts [+0.0, +0.3] (worse) | -0.3 pts [-1.1, +0.4] (not shown) | +0.3 pts [-0.2, +0.8] (not shown) | +0.3 pts [-0.3, +1.0] (not shown) | +0.1 [+0.1, +0.1] (within cap) |
| baseline | D vs A | -9.1 pts [-10.2, -7.9] (helps) | +25.2 pts [+23.7, +26.8] (helps) | +18.5 pts [+16.9, +20.2] (helps) | +14.1 pts [+12.5, +15.7] (helps) | +0.5 [+0.5, +0.6] (worse) |
| baseline | D vs A0 | +1.4 pts [+1.0, +1.7] (worse) | -0.1 pts [-0.9, +0.7] (not shown) | +1.5 pts [+0.7, +2.4] (helps) | +0.3 pts [-0.3, +0.9] (not shown) | +0.5 [+0.4, +0.5] (within cap) |
| harsh_attrition | D vs C | +0.0 pts [-0.2, +0.2] (not shown) | -0.3 pts [-1.3, +0.7] (not shown) | +0.0 pts [-0.5, +0.5] (not shown) | +0.1 pts [-0.5, +0.7] (not shown) | +0.1 [+0.1, +0.1] (within cap) |
| harsh_attrition | D50 vs C | -0.0 pts [-0.2, +0.2] (not shown) | -0.4 pts [-1.0, +0.2] (not shown) | -0.3 pts [-1.0, +0.4] (not shown) | +0.1 pts [-0.8, +1.0] (not shown) | +0.1 [+0.1, +0.1] (within cap) |
| harsh_attrition | D vs A | -4.3 pts [-5.3, -3.3] (helps) | +17.3 pts [+15.5, +19.0] (helps) | +13.9 pts [+12.2, +15.7] (helps) | +14.5 pts [+12.9, +16.1] (helps) | +0.6 [+0.6, +0.7] (worse) |
| harsh_attrition | D vs A0 | +0.4 pts [+0.1, +0.8] (worse) | -0.4 pts [-1.4, +0.6] (not shown) | +0.6 pts [-0.4, +1.6] (not shown) | +0.0 pts [-0.6, +0.7] (not shown) | +0.5 [+0.5, +0.6] (worse) |
| high_dropout | D vs C | -0.1 pts [-0.3, +0.2] (not shown) | +0.0 pts [-0.5, +0.6] (not shown) | +0.3 pts [-0.3, +1.0] (not shown) | -0.3 pts [-0.9, +0.3] (not shown) | +0.1 [+0.1, +0.2] (within cap) |
| high_dropout | D50 vs C | +0.1 pts [-0.2, +0.3] (not shown) | +0.2 pts [-0.4, +0.8] (not shown) | +0.4 pts [-0.3, +1.2] (not shown) | -0.2 pts [-0.8, +0.4] (not shown) | +0.1 [+0.1, +0.2] (within cap) |
| high_dropout | D vs A | -4.8 pts [-5.7, -3.8] (helps) | +17.3 pts [+15.4, +19.2] (helps) | +13.7 pts [+12.0, +15.4] (helps) | +18.4 pts [+17.2, +19.7] (helps) | +0.9 [+0.9, +1.0] (worse) |
| high_dropout | D vs A0 | +0.6 pts [+0.3, +1.0] (worse) | -0.7 pts [-1.3, -0.1] (worse) | +0.9 pts [-0.0, +1.8] (not shown) | -0.6 pts [-1.3, +0.1] (not shown) | +0.6 [+0.5, +0.6] (worse) |
| hot_summer | D vs C | -0.0 pts [-0.3, +0.2] (not shown) | +0.3 pts [-0.5, +1.0] (not shown) | -0.1 pts [-0.7, +0.6] (not shown) | +0.5 pts [+0.1, +0.9] (helps) | +0.1 [+0.1, +0.1] (within cap) |
| hot_summer | D50 vs C | -0.1 pts [-0.4, +0.2] (not shown) | +0.0 pts [-0.6, +0.6] (not shown) | +0.1 pts [-0.7, +0.8] (not shown) | +0.7 pts [+0.3, +1.0] (helps) | +0.1 [+0.1, +0.1] (within cap) |
| hot_summer | D vs A | -9.0 pts [-10.2, -7.7] (helps) | +25.4 pts [+23.9, +26.9] (helps) | +19.1 pts [+17.1, +21.1] (helps) | +13.9 pts [+12.8, +15.0] (helps) | +0.5 [+0.5, +0.6] (worse) |
| hot_summer | D vs A0 | +1.4 pts [+1.1, +1.7] (worse) | +0.0 pts [-0.8, +0.8] (not shown) | +1.7 pts [+0.7, +2.7] (helps) | +0.2 pts [-0.6, +1.1] (not shown) | +0.5 [+0.4, +0.5] (within cap) |
| low_checkin | D vs C | +0.2 pts [-0.2, +0.5] (not shown) | +0.1 pts [-0.4, +0.7] (not shown) | -0.0 pts [-1.0, +1.0] (not shown) | -0.3 pts [-0.7, +0.2] (not shown) | +0.1 [+0.1, +0.1] (within cap) |
| low_checkin | D50 vs C | +0.2 pts [-0.0, +0.3] (not shown) | -0.2 pts [-0.8, +0.4] (not shown) | +0.4 pts [-0.6, +1.4] (not shown) | -0.4 pts [-1.1, +0.2] (not shown) | +0.1 [+0.1, +0.1] (within cap) |
| low_checkin | D vs A | -9.0 pts [-10.2, -7.9] (helps) | +25.4 pts [+23.5, +27.2] (helps) | +18.5 pts [+16.9, +20.1] (helps) | +13.8 pts [+12.4, +15.2] (helps) | +0.6 [+0.5, +0.6] (worse) |
| low_checkin | D vs A0 | +1.4 pts [+0.9, +1.9] (worse) | +0.0 pts [-0.7, +0.7] (not shown) | +1.5 pts [+0.4, +2.5] (helps) | +0.0 pts [-0.7, +0.7] (not shown) | +0.5 [+0.5, +0.5] (within cap) |
| ramadan_heavy | D vs C | +0.2 pts [-0.1, +0.6] (not shown) | -0.2 pts [-1.0, +0.7] (not shown) | +0.4 pts [-0.4, +1.1] (not shown) | -0.2 pts [-0.8, +0.5] (not shown) | +0.1 [+0.1, +0.1] (within cap) |
| ramadan_heavy | D50 vs C | +0.2 pts [-0.1, +0.5] (not shown) | +0.1 pts [-0.4, +0.6] (not shown) | +0.7 pts [-0.3, +1.7] (not shown) | +0.2 pts [-0.5, +0.8] (not shown) | +0.1 [+0.1, +0.1] (within cap) |
| ramadan_heavy | D vs A | -9.1 pts [-10.4, -7.7] (helps) | +24.8 pts [+23.1, +26.5] (helps) | +18.7 pts [+16.9, +20.4] (helps) | +13.9 pts [+12.3, +15.5] (helps) | +0.5 [+0.5, +0.6] (worse) |
| ramadan_heavy | D vs A0 | +1.3 pts [+0.9, +1.8] (worse) | -0.7 pts [-1.7, +0.3] (not shown) | +1.6 pts [+0.8, +2.4] (helps) | +0.0 pts [-0.5, +0.6] (not shown) | +0.5 [+0.4, +0.5] (within cap) |
| shock_heavy | D vs C | +0.1 pts [-0.1, +0.3] (not shown) | +0.1 pts [-0.5, +0.7] (not shown) | -0.1 pts [-0.6, +0.4] (not shown) | -0.0 pts [-0.7, +0.6] (not shown) | +0.1 [+0.1, +0.1] (within cap) |
| shock_heavy | D50 vs C | +0.0 pts [-0.2, +0.2] (not shown) | +0.1 pts [-0.6, +0.8] (not shown) | +0.1 pts [-0.5, +0.7] (not shown) | +0.3 pts [-0.3, +0.9] (not shown) | +0.1 [+0.1, +0.1] (within cap) |
| shock_heavy | D vs A | -5.7 pts [-6.7, -4.7] (helps) | +21.7 pts [+19.6, +23.8] (helps) | +16.6 pts [+14.5, +18.7] (helps) | +15.0 pts [+13.3, +16.8] (helps) | +0.6 [+0.5, +0.6] (worse) |
| shock_heavy | D vs A0 | +0.7 pts [+0.2, +1.1] (worse) | -1.0 pts [-2.0, -0.1] (worse) | +0.7 pts [+0.1, +1.4] (helps) | -0.4 pts [-1.4, +0.6] (not shown) | +0.5 [+0.5, +0.5] (within cap) |

**Decision: keep the hook out of the app.**

- (1) fails: baseline lapse rate is 'not shown', not 'helps'
