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
| `schedule_change` | rules mode: move the movement window (morning → afternoon → evening → morning). Bandit mode: one failure (β + 1) on every arm in the last movement window | §6.3. Sleep stays in the evening. In bandit mode the bandit owns the window. |
| `forgot` | as `schedule_change` for the window, *and* switch channel app ↔ whatsapp_style | §6.3. Voice notes are disabled in the prototype. |
| `environment` | indoor/home only from now on | §6.3. The user can change it in settings. |
| `low_motivation` | show `history.motivation_reason` + offer a buddy | §6.3. |
| `social_family`, `other` | no plan change, thank-you message | No rule in the spec. |
| Prompt windows | morning = wake + 1 h, afternoon = 13:00, evening = sleep − 3 h | Simple defaults. |
| Quiet hours | a window whose hour falls in the user's quiet hours is never used (both modes). Rules mode takes the next free window after its default. If every window is quiet, the prompt moves to the hour quiet hours end | PRD §8 burden target: 0 messages in quiet hours. Hour granularity. The notification window isn't used yet. |

### Bandit (Task 02, `policy_mode="bandit"`)
| Choice | Value | Why |
|---|---|---|
| Arms | (action, window) pairs at the tier the rules layer chose, from the safety-filtered set *at that window's hour* | Task 02 Part 1. The rules layer keeps tier and safety; the bandit only picks which action and when. Heat is checked per window, so an outdoor afternoon arm can't exist in heat mode. |
| Prior | Beta(1, 1) per arm per user | Task 02. Uninformative. |
| Warm start | +1 α for arms whose BCT matches a `past_helpers` entry: small_steps → 8.7, reminders → 7.1, tracking → 2.3, routine_anchor → 8.3 and 1.4. buddy / rewards / other → none (no such actions yet) | Task 02. One extra pseudo-success: a nudge, not a commitment. |
| Reward | completed 1, partial 0.5, skipped / no_response 0; α += r, β += 1 − r. Paused / illness outcomes don't update | Task 02. |
| Randomness | `random.Random` passed into `Engine(rng=...)`; default seed 0 | Reproducible; no global randomness. |
| Rules mode | unchanged from Task 01: top-ranked action at the default window | Arm B. |
| History in state | last 21 days of outcomes kept in `UserState.history` | Engagement needs ≤ 7 counted days; the event log keeps everything. Keeps state small for the simulator. |

### Demo generator (`python -m rebound_engine.demo`)
Per action, every day: days 11–14 25% full completion (motivation dip); days 15–18 no response
(forced lapse); other days 80% full (−5% per tier above 1), 10% partial, 5% no response, the rest
skipped. A due check-in is answered with a random barrier from {time, energy_fatigue, forgot,
low_motivation} on the first day the user responds. Illustration only; Task 02's simulator replaces it.

## Simulation (Task 02)

All values live in `sim/config.yaml`. They are plausible, not fitted to Abu Dhabi data (PRD §15), so the results
show *relative* advantage, not real-world effect sizes.

### Population (300 personas per seed)
| Parameter | Value | Why |
|---|---|---|
| schedule_type | office 35%, shift 15%, outdoor/manual 15%, home/caregiver 15%, student 20% | Rough working-age mix; every segment big enough to report. |
| language | Arabic 40%, English 35%, South Asian 25% (uses English in the app) | Mixed UAE population; the South Asian label exists for equity reporting. |
| health_literacy | low 25%, medium 50%, high 25% | Symmetric spread. Shifts motivation by −0.3 / 0 / +0.3. |
| mobility_limitation | none 90%, some 7%, aid 3% | Roughly in line with disability prevalence. Small groups are reported but left out of the best–worst gap below n = 5. |
| sex, age | female 45%, male 50%, prefer not 5%; age uniform 18–70 | Adult working population. |
| goals | both 70%, movement only 20%, sleep only 10% | Most users pick both. |
| Screening flag | 15% answer yes to one question; 20% of those to chest pain or dizziness | Task 02 "~15%". |
| Pregnancy | 8% of female personas aged 18–45 | Small but present, so the pregnancy filter is exercised. |
| Fasting in Ramadan | 40% | Task 02. |
| Active days / sleep quality | skewed low (most 0–3 days; quality mostly 2–4) | People who sign up for a habit app usually aren't already active. |
| Wake / sleep hours | by schedule; half of shift workers on nights (wake 14:00, sleep 06:00) | Quiet hours = sleep → wake, so night-shift personas test daytime quiet hours. |

### Hidden traits (the engine never sees these)
| Parameter | Value | Why |
|---|---|---|
| motivation_mean | Normal(0, 0.8) on the logit scale, + literacy shift | Wide spread of baseline motivation. |
| motivation_volatility | Uniform(0.2, 0.8) | Some personas are steady, some swing day to day. |
| Motivation AR(1) persistence | 0.85 | Moods last days, not hours; mean-reverting (PRD §8). |
| capacity_tier | movement: 1 + round(3 × active_days / 7) ± 1; sleep: round(4 × quality / 5) ± 1; clipped to 1–4; ≤ 2 with a mobility limitation | The baseline says roughly what someone can sustain, with individual error the engine has to discover. |
| bct_responsiveness | Normal(0, 0.5) per BCT code | Task 02. Individual differences in what works; what the bandit has to learn. |
| preferred_window | by schedule (e.g. office: evening 60%) | Matching it helps (b_window). Fasting personas prefer evening during Ramadan. |
| true_barrier_weights | Dirichlet(1), + 3 on stated past stop reasons, + schedule boosts | Past reasons predict future ones; shift → schedule changes, caregivers → family/time. |
| checkin_answer_rate | Beta(6, 4), mean 0.6 | PRD §15 assumes a "meaningful rate"; tested lower in the `low_checkin` scenario (Drop 2). |
| streak_sensitivity | Uniform(0.3, 1.0) motivation drop after a streak reset (arm A only) | **An assumption.** The abstinence-violation effect (Marlatt & Gordon) is real, but its size here is a guess. The required sensitivity arm A0 sets it to 0. |

### Behaviour model
Each day the persona first decides whether to open the app at all:
P(open) = sigmoid(1.6 + 1.5·motivation). On a closed-app day every action gets no response. On an open day,
each action shown gets P(complete) = sigmoid(b0 + 1.0·motivation + 2.0·hidden habit + 1.0·tier_fit +
1.0·BCT responsiveness + 0.5·window match − penalties).
| Parameter | Value | Why |
|---|---|---|
| Daily app-open step | open_base 1.6, slope 1.5 | Disengagement happens a day at a time (people stop opening the app), not one action at a time. Without it, 14 silent days in a row almost never happened and nobody churned. |
| Novelty decay | motivation mean falls by Uniform(0, 2.0) per persona, with a 21-day time constant | Interest wears off after the first weeks. Some personas barely fade, others fade a lot. |
| Success feedback | δ = 0.05: completion + δ, partial + δ/2, seen-but-missed − δ, open days only, every arm | Pre-registered; see "Success feedback" below. |
| tier_fit | +0.3 per tier below capacity (max +0.9); −1.5 per tier above | Easier tasks are more likely done; overshooting capacity is strongly penalised (Task 02). |
| Partial | 25% of non-completions | "Did a smaller version" is common. |
| no_response share of misses on an open day | sigmoid(−1.5 − motivation) | Low motivation → silence rather than an active skip (Task 02). Most silence now comes from closed-app days. |
| b0 | 1.5 | Calibrated (below). |
| Hidden habit | h = 0.95 h + 0.05 a, starting at 0.3 × baseline | Slower than the engine's λ = 0.9: real habits form over weeks (Lally et al. 2010). |
| Dropout | 14 consecutive days with every action unanswered → churn for good | Task 02. Days with nothing shown don't count either way. |
| Check-in answer | answered with p = checkin_answer_rate; the true barrier with p = 0.8, else random | Task 02. The true barrier follows the active disruption (illness → illness_pain, travel → schedule_change, workload → time, Ramadan → energy_fatigue), otherwise the persona's barrier weights. |
| "I'm OK now" | the day after an illness episode ends, the simulated user clears the engine's illness flag | Matches the app's "I'm OK" button. |

### Calibration
The first uncalibrated run gave ~97% week-12 persistence and 100% retention in *every* arm: a ceiling where no arm
could be told apart. We calibrated arm A (the streak app) only, to targets **we chose as plausible**. They aren't
cited figures: a habit app where most people still do something at week 12 isn't credible, and neither is one
where nearly everyone leaves.

| Target for arm A | Chosen | Reached on seed 101 |
|---|---|---|
| Share of shown actions completed | ~45% | 42% |
| Persistence, week 12 | ~40% | 41% |
| Retention at day 90 (not churned) | ~60% | 67% |

- **Calibration seed:** 101 only, 100 personas, arm A only. The evaluation uses seeds 1–10, which were never used for
  tuning, so the reported numbers aren't fitted to themselves.
- **What was tuned:** `b0` (0 → 1.5), `no_response_base` (−0.5 → −1.5), and the two new mechanisms above (daily
  app-open step, `open_base` 1.6 after adding success feedback; novelty decay up to 2.0; δ was never tuned). B and C were never looked at during tuning.
- **Why not exact:** completion and retention pull against each other in this model. We stopped at the first
  setting within a few points of all three targets rather than over-fit one seed.
- **Harsher world (Drop 2 scenario `harsh_attrition`, targets ~30% persistence and ~40% retention for A):** closest
  found on seed 101 (with success feedback) is `open_base` 1.25 with novelty drop up to 3.0, giving 24% persistence and 42% retention.
  In this model persistence and retention move together, so we kept the retention target and accepted lower
  persistence.

### Success feedback: pre-registered before any run (committed on its own, before the code)
**Why it's added.** In the calibrated no-feedback model (run_002) only motivation decides whether a persona opens
the app, and nothing an arm does changes motivation, except arm A's streak penalty. So persistence, recovery and
retention were identical in A0, B and C *by construction*. Real people aren't like that: succeeding at a task builds
the belief that you can do it, and failing erodes it (self-efficacy; mastery experiences are its strongest source,
Bandura 1977/1997). A good plan should be *able* to keep someone engaged, and a bad one to lose them.

**The rule (identical in every arm, A included).** After each action on a day the persona opened the app:
- completed: motivation + δ
- partial: motivation + δ/2
- skipped or no response: motivation − δ

Closed-app days give no feedback: not opening isn't a failed attempt. The change carries into the next day through
the AR(1) motivation process.

**δ = 0.05 (logit scale), fixed now and not tuned.** Reasoning:
- **Small per event.** It's well below the daily motivation noise (sd 0.2–0.8) and far below arm A's streak penalty
  (0.3–1.0 per reset). One success or failure barely matters; only patterns do.
- **Bounded when it compounds.** With AR(1) persistence 0.85, a constant daily input x settles at x ÷ 0.15. Two
  actions a day, all succeeding, gives +0.10/day → about +0.67 at most; all failing gives about −0.67. That's the same
  size as the spread between low and high health literacy (0.6), a plausible ceiling for how much success alone moves
  someone.
- **A realistic gap is modest.** If one arm's completion share is 20 points higher than another's, the steady-state
  difference is about 2 × 0.2 × 2δ ÷ 0.15 ≈ 0.27 logit.

**Headline comparisons (fixed now).** C vs A, C vs A0, C vs B on **recovery within 14 days**, **persistence at
week 12** and **retention at day 90**: 9 differences, reported with their 95% intervals whatever the direction. We
say Rebound "helps" on a measure only if the interval for the difference is entirely above zero. Everything else
in the report is secondary.

**What happens next, in this order:** (1) commit this section and the config value alone; (2) implement;
(3) recalibrate arm A on seed 101 only, changing `open_base` (and `b0` only if needed) to the same targets, never
δ; (4) run seeds 1–10 once (run_003). In Drop 2 the sensitivity sweep includes δ = 0, 0.025, 0.05 and 0.1, so it
shows how the advantage over A0 depends on this assumption.

### Where Rebound doesn't help: the no-feedback world (run_002, commit 70a181d)
Before success feedback, nothing an arm did could change motivation (except A's streak penalty), so engagement was
the same in A0, B and C by construction. Seeds 1–10, 300 personas, 90 days:

| C vs … | Persistence wk 12 | Recovery 14 d | Retention | Δ active min | Δ tier-weighted sleep |
|---|---|---|---|---|---|
| A (streak app) | +25.2 pts [+23.2, +27.2] | +19.5 [+17.9, +21.1] | +12.4 [+11.2, +13.7] | +12.2 min | +10.2 pts |
| A0 (no streak penalty) | −0.5 [−1.0, +0.0] | +0.8 [−0.2, +1.8] | +0.3 [−0.5, +1.1] | +4.7 min [+3.7, +5.7] | +7.1 pts [+6.2, +8.0] |
| B (rules only) | −0.1 [−0.7, +0.5] | +0.4 [−0.3, +1.0] | −0.2 [−0.7, +0.3] | −0.2 | −0.2 |

**Reading:** in that world, Rebound's whole engagement advantage over A comes from the assumed streak penalty. Its
own gain is more activity per engaged user (more minutes, harder sleep actions). This stays in the evaluation as
the lower bound on what Rebound adds.

**The bandit:** a per-user Thompson bandit learns little in 90 days when people open the app on ~40% of days (C vs
B ≈ 0 on everything). We state that as is; it would need shared priors across similar users (PRD §6.4) or longer use.

### Results: baseline with success feedback (run_003)
Seeds 1–10 (never used for tuning), 300 personas, 90 days, δ = 0.05 as pre-registered, `open_base` 1.6.

**Headline (draft):** Against a streak app that penalises misses, Rebound improves recovery, persistence and
retention. Against a static plan without that penalty, it keeps engagement equal while increasing how much people
do (+9 active min/week, +10 pts tier-weighted sleep). The bandit adds no measurable benefit over rules at 90 days
and this sample size.

**Pre-registered comparisons** (differences in percentage points, 95% interval; "helps" = whole interval above 0):

| Comparison | Recovery within 14 days | Persistence, week 12 | Retention at day 90 |
|---|---|---|---|
| C vs A | +18.9 [+17.5, +20.3] helps | +25.6 [+23.3, +27.9] helps | +13.6 [+11.8, +15.4] helps |
| C vs A0 | +1.3 [+0.2, +2.4] helps, **weak evidence** | −0.5 [−1.5, +0.5] not shown | +0.2 [−0.6, +1.0] not shown |
| C vs B | −0.1 [−0.5, +0.3] not shown | −0.1 [−0.6, +0.3] not shown | +0.1 [−0.4, +0.6] not shown |

C vs A0 recovery passes the rule, but it's 1 of 9 tests with no multiple-comparison correction, and the interval
nearly touches zero. We don't claim it as a finding.

**Secondary (not pre-registered):** C vs A0: +8.9 active min/week [+7.7, +10.2], +9.8 pts tier-weighted sleep nights
[+8.6, +10.9], −1.4 pts persistent in all of weeks 4, 8 and 12 [−2.3, −0.5] (Rebound slightly worse).

**Why engagement is equal to A0: a trade-off, not a bug.** On days the app was opened (seeds 1–10):

| Arm | Movement completed / mean tier | Sleep completed / mean tier |
|---|---|---|
| A0 (static, easy plan) | 89% / 1.6 | 95% / 1.0 |
| C (Rebound) | 83% / 2.2 | 86% / 2.5 |

Rebound steps people up, so they complete a bit less often and get less positive success feedback than with A0's
fixed easy plan. Shrinking after a slip helps; harder actions cost. The two roughly cancel for engagement, while
Rebound users do more. How eagerly the engine steps up (3 consecutive successes) is a product question; it's in the
Drop 2 sensitivity sweep (2 / 3 / 4 / 5) rather than tuned to these results.

### Disruptions (labelled)
| Parameter | Value | Why |
|---|---|---|
| Ramadan | days 30–59 for fasting personas; −1.5 if a non-fasting-safe action is shown; preferred window becomes evening | Task 02 / PRD §8. The engine is told (calendar). |
| Heat | days 61–90; outdoor action −1.0 in 11:00–16:00, −0.5 outside it; ×1.5 for outdoor/manual workers | Late summer. The engine is told (weather). |
| Illness | Poisson, 1 episode per 90 days, 3–7 days; −3.0 movement, −0.5 sleep | PRD §8. The engine learns of it only from a check-in answer. |
| Travel | Poisson 0.5 per 90 days (office 0.8), 2–5 days, −0.7 | Check-in only. |
| Workload spike | Poisson 1 per 90 days (shift 2.5), 3–7 days, motivation −0.6 | Shift workers get more. Check-in only. |
| Common random numbers | each persona has the same traits and disruption schedule in every arm. Motivation noise and the daily app-open draw use their own random stream (one fixed pair of draws per day), separate from outcome draws and check-in answers | Arm differences come from the arms, not from luck. Only two things move motivation: A's streak penalty (arm A only, by design) and success feedback (same rule in every arm, driven only by outcomes). Tested: with δ = 0 the open/no-open sequence is identical in A0, B and C for the whole run and in A until its first streak reset; with δ = 0.05 it's identical until the arms' outcomes first differ. |

### Arms
| Arm | What it is |
|---|---|
| A · static streak app | Rebound's *starting* plan for that persona (same starting tier, safety cap and screening/pregnancy/mobility rules), fixed for 90 days at the same reminder windows. No shrinking, no check-ins, no heat/Ramadan adaptation. A visible streak per behaviour resets on any miss (partials included) and knocks motivation down by `streak_sensitivity`. Not safety-audited (Task 02). |
| A0 · sensitivity | A with `streak_sensitivity = 0`. If Rebound's advantage disappears here, it came from the streak assumption, and we say so. |
| B · Rebound rules | `Engine(policy_mode="rules")`. |
| C · Rebound full | `Engine(policy_mode="bandit")`. |

### Metric definitions (where Task 02 left a choice)
| Choice | Value | Why |
|---|---|---|
| Lapse / recovery for every arm | the engine's own `compute_engagement_state` replayed on each arm's raw outcomes | Same yardstick for A, B and C. Illness days count as normal days here, in every arm. |
| Recovery rate | lapse onsets on or before day 76 (so 14 days of follow-up exist); recovered = state `active` within 14 days | Doesn't penalise late lapses that had no time to recover. |
| Time to recover (headline) | days from lapse onset to the first `active` day; median over episodes that got there | "Recovering" needs only 2 completions in 4 days, so lapse → recovering sat at 3 days in every arm and told us nothing. |
| Lapse → recovering | the same, to the first `recovering` (or `active`) day | Kept in the detailed table (Task 02's literal definition). |
| Persistence | ≥ 3 active days in the week; weeks 4, 8 and 12 separately and all three together (week 12 is the headline) | Your answer to question 8. |
| Behaviour change, movement | completed `duration_min` + half for partials, week 12 − week 1, mean over movement personas (churned = 0) | Task 02. |
| Behaviour change, sleep (headline) | tier-weighted nights: each completed night earns tier ÷ 4 (half for a partial), summed ÷ 7, week 12 − week 1 | The raw share rewards arms that ask for less: A keeps the easiest sleep action all 90 days. |
| Behaviour change, sleep (raw) | nights with the sleep action completed ÷ 7, week 12 − week 1 | Task 02's definition. Detailed table only, with a note about the bias. |
| Messages | each action prompt + each `checkin_sent`. Quiet-hour share uses the prompt hour | Your answer to question 4. |
| Intervals | mean across seeds ± t(0.975, seeds − 1) × sd ÷ √seeds; min–max also stored | A 95% interval for the mean. Arm differences use the per-seed paired difference. |
| Equity gap | best − worst segment value per seed (segments with ≥ 5 personas), then mean and interval | Very small groups (e.g. mobility aid) are too noisy to rank. |

### Differences from the PRD (Task 02 wins; flagged for review)
| Topic | PRD | What we do |
|---|---|---|
| Sleep behaviour change (§8) | Δ sleep-timing regularity vs baseline | Δ share of nights with the sleep action completed, week 1 → week 12 |
| Behaviour change baseline (§8) | vs onboarding baseline | week 1 → week 12 |
| Retention (§8) | % still interacting at day 90 | % not churned at day 90 |
| Bandit (§6.4) | arms = tier × technique × window × channel; reward also counts engagement over the next 3 days; priors shared across similar personas | arms = (action, window) at the rules tier; reward = completion only; per-user priors with warm start |
| Engagement inputs (§6.1) | completions, check-in responses and app opens | action outcomes only |
| Actions per day (§2) | one | one per goal |

## Dependencies
- Engine: Python 3.11+, Pydantic v2, PyYAML. Dev: pytest, ruff.
- Simulator: numpy, pandas, pyarrow (Parquet; falls back to CSV without it), matplotlib.

## Limitations
- The action library is a first draft: 17 actions, Arabic titles not yet reviewed (`ar_reviewed: false`),
  rationale and limits English only.
- Screening questions are paraphrased from PAR-Q+ and are not a clinical tool.
- The in-memory store loses data on restart; the API swaps in SQLite (Task 03).
- Simulated behaviour is plausible, not empirically fitted; results show relative advantage, not real-world effect sizes.
- In the calibrated simulation almost all disengagement comes from not opening the app: on open days, 82–95% of
  actions are completed in every arm. Real users also open the app and still skip; if that's common, plan quality
  matters more than this model shows.
- The engagement advantage over a streak app depends on the assumed size of the streak penalty (arm A vs A0) and of
  the success feedback δ; both are swept in Drop 2.
