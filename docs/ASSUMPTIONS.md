# Assumptions, dependencies and limitations

Every number or rule the engine uses that `AGENTS.md` doesn't fully pin down. Values live in
`engine/rebound_engine/config.py`.

## Assumptions

### Habit strength
| Choice | Value | Why |
|---|---|---|
| λ (decay) | 0.9 | Given in AGENTS.md §6.1. One miss after 10 completions keeps H ≈ 0.59. |
| a_t | full 1.0, partial 0.5, skip/no response 0 | Given in §6.1. |
| Starting H | 0.0 | No habit is assumed; the baseline answers set the starting *tier* instead. |
| Behaviour not shown that day | H unchanged | Only one action per day; not offering sleep shouldn't count as missing it. |
| Illness / paused days | H and engagement both untouched, for every behaviour | §6.1 says these days don't update H. We also leave them out of the 7-day window so a sick week can't trigger "lapsed". |

### Engagement state
| Choice | Value | Why |
|---|---|---|
| Window | last 7 *counted* days (paused/illness days skipped) | One action per day, so counted days ≈ calendar days. |
| Thresholds | active ≥ 4/7, drifting 2–3/7, lapsed ≤ 1/7 or ≥ 3 no-responses in a row | Given in §6.1. |
| First week | uses the completion *rate* over the days so far; no state change before 3 counted days | With counts, a new user would be "lapsed" on day 1. |
| "Drop ≥ 50% vs previous 7 days" | not coded as a separate rule | It can't change the result: to be ≥ 4/7 now *and* ≤ half the previous week, the previous week would need ≥ 8/7. Any such drop is already "drifting" or "lapsed". Revisit if we move to weighted (partial = 0.5) counts. |
| Recovering | was lapsed, now ≥ 2 completions in last 4 counted days | Given. A lapsed user stays lapsed until this happens; recovering becomes active once the 7-day rate is ≥ 4/7. |
| Check-in due | when the state *changes into* drifting or lapsed; cleared by a check-in | One check-in per slip, not a daily nag. |

### Tiers and step-up
| Choice | Value | Why |
|---|---|---|
| Starting movement tier | 0–2 active days → 1, 3–4 → 2, 5–7 → 3 | Start small; never start at tier 4. |
| Age ≥ 65 | start at tier 1 | §4.1 "balance-friendly start". Tier 1 includes a held balance exercise. |
| BMI band (internal only) | ≥ 30 → start ≤ 2, ≥ 40 → start 1 | Caps the *starting* intensity only; never shown, never a goal. Not clinically validated. |
| Sleep starting tier | 1 | The sleep tiers are a progression of habits, so everyone starts at the anchor (fixed wake time). |
| Screening cap | any yes → movement ≤ 2; chest pain or dizziness/fainting → movement ≤ 1 | §4.3. We treat "gentle" as tier 1. |
| Screening cap duration | permanent for now | No clinician-clearance flow yet (out of scope for the prototype). |
| Step-up | 3 *full* completions at the current tier (not necessarily consecutive) → +1 tier | §6.3. Partials don't count. Completions of a lower-tier fallback (e.g. during Ramadan) don't count either, so the tier can't climb while the user is doing easier actions. |
| Tier floor/ceiling | 1–4 | Spec. |
| Auto tier drop on lapse | none | Only check-in barriers lower the tier (§6.3). Step-up goes one tier at a time, so a user can't jump back to their pre-lapse tier. |

### Safety and context
| Choice | Value | Why |
|---|---|---|
| Heat window | 11:00–16:00, end exclusive | §6.3. |
| Pregnancy "prefer not to say" | gets the pregnancy-safe subset | Safer default. |
| Mobility limitation "some" | seated movement actions only (same as "uses aid") | Safer default; there are seated variants only for tiers 1–2, so these users are capped at tier 2. |
| Illness flag | removes movement until the user says they're OK (`Engine.set_context(..., illness, False)`) | §6.3. |
| Red flags | keyword substring match after normalising case, Arabic diacritics and alef forms | False positives are acceptable; misses are not. The LLM check comes in Task 03, when this list moves to `llm/safety.yaml`. |
| Red flag outcome | coaching paused, `red_flag` event logged, free text not stored | §6.4 + data minimisation. |

### Rules layer
| Choice | Value | Why |
|---|---|---|
| Several barriers ticked | only the highest-priority one is applied: illness_pain > environment > energy_fatigue > schedule_change > time > forgot > low_motivation > social_family > other | Safety-relevant barriers first, so e.g. ["time", "illness_pain"] pauses movement instead of just shrinking it. One clear adjustment per check-in; the API returns a single `barrier`. |
| `time` | −1 tier on the behaviour last shown | §6.3. |
| `energy_fatigue` | −1 movement tier; sleep first and only `low_energy_ok` actions until the next full completion | §6.3. |
| `schedule_change` | move to the next prompt window (morning → midday → evening → morning) | §6.3. |
| `forgot` | next prompt window *and* switch channel app ↔ whatsapp_style | §6.3. Voice notes are disabled in the prototype. |
| `environment` | indoor/home only from now on | §6.3. The user can change it in settings. |
| `low_motivation` | show the user's own reason + offer a buddy | §6.3. Uses `history.motivation_reason` (optional, ≤ 200 chars, AGENTS.md §4.5). It's free text, so it's red-flag checked at onboarding; a hit pauses coaching and logs a `red_flag` event. |
| `social_family`, `other` | no plan change, thank-you message | No rule in the spec. |
| Prompt windows | morning = wake + 1 h, midday = 13:00, evening = sleep − 3 h | Simple defaults; quiet hours and the notification window are applied by the API/frontend later. |
| Behaviour order | alternate movement and sleep; users told to see a doctor start with sleep | One action per day, both goals get equal practice. |

### Demo generator (`python -m rebound_engine.demo`)
Days 11–14: 25% full completion (motivation dip). Days 15–18: no response (forced lapse). Other days:
80% full (−5% per tier above 1), 10% partial, 5% no response, the rest skipped. The user answers a
due check-in with a random barrier from {time, energy_fatigue, forgot, low_motivation}. These numbers
are for illustration only; Task 02's simulator replaces them.

## Dependencies
- Python 3.11+, Pydantic v2, PyYAML. Dev: pytest, ruff.

## Limitations
- The bandit is a stub (`RulesBandit`) until Task 02.
- The action library is a first draft: 17 actions, Arabic titles not yet reviewed (`ar_reviewed: false`),
  rationale and limits English only.
- Screening questions are paraphrased from PAR-Q+ and are not a clinical tool.
- The in-memory store loses data on restart; the API swaps in SQLite (Task 03).
