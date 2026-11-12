# Assumptions, dependencies and limitations

Every number or rule the engine uses that `AGENTS.md` doesn't fully pin down. Values live in
`engine/rebound_engine/config.py`.

## Assumptions

### Daily plan
| Choice | Value | Why |
|---|---|---|
| Actions per day | one per goal: movement in its prompt window (morning by default), sleep in the evening | Both behaviours get daily practice. |
| Closing a day | a day closes when every action shown that day has an outcome; if the user never answers, the next day's `today()` records the leftovers as `no_response` and closes it | Engagement and tier changes need the whole day. Without this, a user who stops responding would never lapse. |
| Users told to see a doctor | get gentle (tier 1) movement plus sleep from day 1 | The old "sleep first" ordering doesn't apply now that both are shown daily. The tier-1 cap keeps movement gentle. |

### Habit strength
| Choice | Value | Why |
|---|---|---|
| λ (decay) | 0.9 | Given in AGENTS.md §6.1. One miss after 10 completions keeps H ≈ 0.59. |
| a_t | full 1.0, partial 0.5, skip/no response 0 | Given in §6.1. |
| Starting H₀ | movement 0.5 × active_days_per_week / 7; sleep 0.5 × (sleep_quality_self − 1) / 4 | The baseline says something about existing habits, but a self-report isn't a habit, so it's scaled to at most 0.5 (`HABIT_START_SCALE`). |
| Illness / paused days | H and engagement both untouched | §6.1 says these days don't update H. They're also left out of the 7-day window, so a sick week can't trigger "lapsed". |

### Engagement state
| Choice | Value | Why |
|---|---|---|
| Window | last 7 *counted* days (paused/illness skipped) | §6.1. |
| Completion rate | done actions (incl. partials) ÷ actions shown, over the window | With two goals a day this weighs both equally. For one goal it's exactly the spec's "x/7". |
| Thresholds | active ≥ 4/7, drifting 2/7–<4/7, lapsed ≤ 1/7 (as rates) | Given in §6.1. |
| Silent day (for "≥ 3 no-responses in a row → lapsed") | a counted day where *every* action got no_response | Skipping is still a response; only silence counts toward the lapse. |
| Recovering | was lapsed, now ≥ 2 days with a completion in the last 4 counted days | §6.1 counted per day. Becomes active once the rate is ≥ 4/7. |
| First week | rate over the days so far; no state change before 3 counted days | With counts, a new user would be "lapsed" on day 1. |
| "Drop ≥ 50% vs previous 7 days" | not coded as a separate rule | It can't change the result: ≥ 4/7 now and ≤ half the previous week would need ≥ 8/7 before. Revisit if partials get weighted 0.5. |
| Check-in | when the state *enters* drifting or lapsed, a `checkin_sent` event is logged and `checkin_due` is set. It's answered the next time the user responds; answering clears it | One check-in per slip, not a daily nag. |

### Tiers
| Choice | Value | Why |
|---|---|---|
| Starting movement tier | 0–2 active days → 1, 3–4 → 2, 5–7 → 3 | Start small; never start at tier 4. |
| Age ≥ 65 | start at tier 1 | §4.1 "balance-friendly start". Tier 1 includes a held balance exercise. |
| BMI band (internal only) | ≥ 30 → start ≤ 2, ≥ 40 → start 1 | Caps the *starting* intensity only. Never shown, never a goal. Not clinically validated. |
| Sleep starting tier | 1 | The sleep tiers are a progression of habits; everyone starts at the anchor (fixed wake time). |
| Screening cap | any yes → movement ≤ 2; chest pain or dizziness/fainting → movement ≤ 1 | §4.3. "Gentle" = tier 1. Permanent for now (no clinician-clearance flow yet). |
| Step-up | 3 *consecutive* full completions at the current tier → +1 (`STEP_UP_SUCCESSES`) | skipped/no_response reset the count to 0; partial neither adds nor resets. |
| Step-up gate | only while the state is active or recovering | After a lapse, no step-up until the user is recovering and has 3 consecutive completions since coming back. This also blocks step-up while drifting, because we've just shrunk the plan. |
| Step-down | 2 consecutive skipped/no_response at the current tier while active → −1 (`STEP_DOWN_FAILURES`) | A partial breaks the run of misses (it's a response). Drifting/lapsed are handled by shrink-on-slip instead. |
| Shrink on slip | entering drifting → every tier −1 (`DRIFT_TIER_DROP`); entering lapsed → every tier back to 1 | Make the next action easier as soon as a slip shows. Floor is tier 1. |
| Any tier change | resets both counters | A new tier starts fresh. |
| Step up then straight back down | intended: a step-up followed by 2 misses drops the tier again right away (e.g. tier 1 → 2 → 1 over three days) | The engine backs off quickly when a new tier proves too hard. No hold period after a step-up. |
| Lower-tier fallbacks | an outcome on an action below the current tier (e.g. Ramadan removed the usual one) doesn't change the counters | The tier shouldn't climb or fall because of a context swap. |
| Tier range | 1–4 | Spec. |

### Safety and context
| Choice | Value | Why |
|---|---|---|
| Heat window | 11:00–16:00, end exclusive | §6.3. Sleep actions are checked at their evening hour. |
| Pregnancy "prefer not to say" | gets the pregnancy-safe subset | Safer default. |
| Mobility limitation "some" | seated movement actions only (same as "uses aid") | Safer default. Seated variants exist only for tiers 1–2, so these users top out at tier 2. |
| Illness flag | removes movement until the user says they're OK (`Engine.set_context(..., illness, False)`) | §6.3. |
| Red flags | keyword substring match after normalising case, Arabic diacritics and alef forms | False positives are acceptable; misses are not. The LLM check comes in Task 03, when this list moves to `llm/safety.yaml`. |
| Red flag outcome | coaching paused, `red_flag` event logged, free text not stored | §6.4 + data minimisation. |
| `motivation_reason` | red-flag checked at onboarding; a hit pauses coaching and logs `red_flag` (onboarding still succeeds) | It's the only free text in onboarding (AGENTS.md §4.5). |

### Rules layer
| Choice | Value | Why |
|---|---|---|
| Several barriers ticked | only the highest-priority one is applied: illness_pain > environment > energy_fatigue > schedule_change > time > forgot > low_motivation > social_family > other | Safety-relevant first, so ["time", "illness_pain"] pauses movement instead of just shrinking it. One clear adjustment per check-in. |
| `time` | −1 tier on both behaviours | Lack of time affects the whole plan. |
| `energy_fatigue` | −1 movement tier; only `low_energy_ok` actions until the next full completion | §6.3. "Prioritise sleep" now means movement shrinks while sleep stays as it is, since both are shown daily. |
| `schedule_change` | move the movement window (morning → midday → evening → morning) | §6.3. Sleep stays in the evening. |
| `forgot` | next movement window *and* switch channel app ↔ whatsapp_style | §6.3. Voice notes are disabled in the prototype. |
| `environment` | indoor/home only from now on | §6.3. The user can change it in settings. |
| `low_motivation` | show `history.motivation_reason` + offer a buddy | §6.3. |
| `social_family`, `other` | no plan change, thank-you message | No rule in the spec. |
| Prompt windows | morning = wake + 1 h, midday = 13:00, evening = sleep − 3 h | Simple defaults. Quiet hours and the notification window are applied by the API/frontend later. |

### Demo generator (`python -m rebound_engine.demo`)
Per action, every day: days 11–14 25% full completion (motivation dip); days 15–18 no response
(forced lapse); other days 80% full (−5% per tier above 1), 10% partial, 5% no response, the rest
skipped. A due check-in is answered with a random barrier from {time, energy_fatigue, forgot,
low_motivation} on the first day the user responds. Illustration only; Task 02's simulator replaces it.

## Dependencies
- Python 3.11+, Pydantic v2, PyYAML. Dev: pytest, ruff.

## Limitations
- The bandit is a stub (`RulesBandit`) until Task 02.
- The action library is a first draft: 17 actions, Arabic titles not yet reviewed (`ar_reviewed: false`),
  rationale and limits English only.
- Screening questions are paraphrased from PAR-Q+ and are not a clinical tool.
- The in-memory store loses data on restart; the API swaps in SQLite (Task 03).
- The engine now returns a list of actions per day and per check-in. The AGENTS.md §7 API contract still
  says `action` / `adjusted_action` (singular) and needs updating before Task 03.
