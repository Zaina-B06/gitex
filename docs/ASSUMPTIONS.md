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
| Step-up | 4 *consecutive* full completions at the current tier → +1 (`STEP_UP_SUCCESSES`) | skipped/no_response reset the count to 0; partial neither adds nor resets. Was 3 until the pre-registered step-up test (run_006, "Step-up 3 → 4" below) changed it. |
| Step-up gate | only while the state is active or recovering | After a lapse, no step-up until the user is recovering and has 4 consecutive completions since coming back. This also blocks step-up while drifting, because we've just shrunk the plan. |
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

### Where Rebound doesn't help: the no-feedback world (run_002, commit 758341a)
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

### Drop 2: scenarios, unlabelled shocks, sensitivity sweep

**Recalibrated for Drop 2.** Baseline now includes unlabelled shocks (below), which lowers engagement, so the
run_003 calibration no longer held. Arm A was recalibrated on seed 101 only (100 personas), changing `open_base`
alone; δ and everything else stayed as they were.

| Arm A on seed 101 | Target | run_003 setting (`open_base` 1.6) with shocks | **Drop 2 setting (`open_base` 1.7)** |
|---|---|---|---|
| Actions completed | ~45% | 41% | **43%** |
| Persistence, week 12 | ~40% | 38% | **41%** |
| Retention | ~60% | 62% | **61%** |

`harsh_attrition` keeps `open_base` 1.25 with novelty drop up to 3.0. With shocks, that gives arm A **24% persistence
and 40% retention** on seed 101. The retention target is hit; persistence stays below the ~30% target, because in
this model the two move together (`open_base` 1.5 with novelty drop up to 2.5 gives 30% persistence but 50%
retention).

**Outputs not to report:** a run_004 and a partial sweep_001 were produced before this recalibration. They were
deleted; the Drop 2 results are run_005 and sweep_002.

#### Scenarios (`sim/scenarios.yaml`; each changes only what it lists, which is tested)
| Scenario | Changes | Why |
|---|---|---|
| baseline | nothing | Reference. |
| ramadan_heavy | 70% fasting; Ramadan days 20–49 | Task 02. Earlier in the run, so recovery after it is fully observed. |
| hot_summer | heat days 1–60; heat penalty 1.0 → 2.0 | Task 02 ("outdoor penalty × 2"). |
| low_checkin | every persona's check-in answer rate × 0.5 | Task 02 ("halved"). Tests the PRD §15 assumption that people answer check-ins. |
| high_dropout | churn after 7 silent days (not 14); motivation mean −0.5 | Task 02. |
| shock_heavy | unlabelled shock rate × 3 (1 → 3 per 90 days) | Task 02 §4.2. |
| harsh_attrition | `open_base` 1.25; novelty drop up to 3.0 | Your harsher world (~30% persistence, ~40% retention for arm A). |

#### Unlabelled shocks (Task 02 §4.2)
| Parameter | Value | Why |
|---|---|---|
| Rate | Poisson, 1 per persona per 90 days (baseline) | One unexplained rough patch per quarter is plausible; `shock_heavy` triples it. |
| Length | uniform 2–14 days | Task 02. |
| Size | motivation −Uniform(0.5, 2.0) on the logit scale while it lasts; overlapping shocks add | Task 02 ("random amount"). From noticeable to severe. |
| What the engine learns | nothing directly: no context flag, no event field, and a check-in answer during a shock comes from the persona's usual barrier weights, never "shock" | Tested by recording every call the simulator makes into the engine. |
| Random stream | its own per persona | Adding shocks doesn't reshuffle labelled disruptions or the daily process (tested). |

#### Recovery by what preceded the lapse
A lapse is attributed to an **unlabelled shock** if one was active on the onset day or the 7 days before; otherwise
to a **labelled disruption** (illness, travel, workload, or Ramadan for fasting personas) in the same window;
otherwise **none**. Shock wins when both are present. Heat is left out of "labelled": it covers everyone for a month,
so it can't single out a lapse. Recovery within 14 days is reported for each group, and compared C vs A / A0.

#### Sensitivity sweep (`python -m sim.sweep`; arms A, A0, C; baseline scenario; 5 seeds per setting)
The tornado charts show how the **C vs A** and **C vs A0** gaps in week-12 persistence move from each parameter's
lowest to highest value. Recovery and retention gaps are recorded too. Any setting that makes a gap ≤ 0 is listed
under "Where Rebound doesn't help".

| Parameter | Values (baseline in bold) | Why this range |
|---|---|---|
| streak_sensitivity (arm A only) | [0, 0], **[0.3, 1.0]**, [0.8, 1.6] | From no abstinence-violation effect to a strong one; the assumption the C-vs-A gap depends on most. |
| motivation_volatility | [0.1, 0.4], **[0.2, 0.8]**, [0.5, 1.2] | Steadier to much moodier people. |
| check-in answer rate multiplier | 0.5, **1.0**, 1.5 (capped at 1) | Rebound's adaptation runs on check-ins. |
| bct_responsiveness_sd | 0.0, **0.5**, 1.0 | Nothing for the bandit to learn, up to large individual differences. |
| unlabelled shock rate | 0, **1**, 3 per 90 days | No shocks to shock-heavy. |
| tier_fit_penalty | 0.5, **1.5**, 3.0 | How much an over-sized task hurts. |
| success feedback δ | 0, 0.025, **0.05**, 0.1 | Pre-registered (see above). δ = 0 is the no-feedback world. |
| engine STEP_UP_SUCCESSES | 2, **3**, 4, 5 | How eagerly Rebound steps up; run_003 showed stepping up costs completions. A product question, not tuned here. |

Five seeds per setting (not ten) keeps the full sweep (26 settings) to roughly 10–15 minutes; intervals are wider.

### Results: Drop 2 (run_005 all scenarios, sweep_002; step-up 3, superseded by run_007)
run_005: 7 scenarios × 300 personas × 90 days × seeds 1–10; arms A, A0, B, C. sweep_002: baseline, 5 seeds per
setting, arms A, A0, C. Verdicts: **helps** = whole 95% interval above zero, **worse** = whole interval below zero,
otherwise not shown.

**Headline (updated; superseded by "Reported results: shipped engine" below):** Against a streak app that penalises misses, Rebound improves recovery, persistence and
retention, in every scenario. Against a static plan without that penalty, it keeps engagement about equal while
increasing how much people do (+9 active min/week, +10 pts tier-weighted sleep in run_003). The advantage over a
streak app exists only if missing a day on a streak app lowers motivation (abstinence-violation effect); with no such
effect it disappears (C vs A persistence −1.0 pts [−3.0, +1.0]). The bandit adds no measurable benefit over rules at
90 days and this sample size.

**Pre-registered comparisons by scenario (run_005), percentage points:**

| Scenario | C vs A: recovery / persistence wk 12 / retention | C vs A0: recovery / persistence / retention | C vs B |
|---|---|---|---|
| baseline | +18.2 / +24.8 / +13.4, all helps | +1.2 / −0.6 / −0.4, none shown | ≈ 0, none shown |
| ramadan_heavy | +18.2 / +24.7 / +13.8, all helps | +1.1 / −0.8 / +0.0, none shown | persistence −0.5 [−1.0, −0.1] **worse** |
| hot_summer | +18.5 / +24.7 / +13.3, all helps | +1.1 / −0.7 [−1.2, −0.1] **worse** / −0.4 | ≈ 0 |
| low_checkin | +18.4 / +25.2 / +14.0, all helps | +1.4 / −0.1 / +0.2, none shown | ≈ 0 |
| high_dropout | +12.8 / +17.2 / +18.3, all helps | +0.0 / −0.8 [−1.4, −0.2] **worse** / −0.7 [−1.3, −0.2] **worse** | ≈ 0 |
| shock_heavy | +16.0 / +21.3 / +14.5, all helps | +0.1 / −1.5 [−2.7, −0.3] **worse** / −0.9 [−1.7, −0.1] **worse** | ≈ 0 |
| harsh_attrition | +13.5 / +17.1 / +14.1, all helps | +0.2 / −0.5 / −0.3, none shown | ≈ 0 |

All "worse" results are under 2 points, consistent with the step-up cost found in run_003 (harder actions → fewer
completions → less success feedback).

**Recovery by what preceded the lapse (run_005).** C vs A: +13 to +20 pts after both labelled disruptions and
unlabelled shocks, in every scenario. C vs A0: after labelled disruptions +0.3 to +2.8 pts, clearly positive only in
low_checkin (+2.8 [+0.8, +4.8]) and ramadan_heavy (+2.1 [+0.7, +3.4]); after unlabelled shocks never clearly
positive (−0.0 to +1.9).

**Sensitivity sweep (sweep_002), what moves the gaps:**
- **Streak penalty (arm A) dominates the C vs A gap:** none → −1.0 pts [−3.0, +1.0]; baseline → +23.0; strong →
  +33.8. No other parameter moves it by more than about ±5 pts.
- **C vs A0 is never clearly positive on engagement in any setting** (persistence −2.0 to +0.5; recovery −0.1 to +2.2).
- **Success feedback δ cuts against Rebound vs A0:** δ 0 → 0.1 moves the persistence gap from +0.5 to −2.0. Equal
  feedback for every completion rewards easy static plans (see Limitations).
- **Step-up threshold:** 3 → 4 → 5 moves the persistence gap vs A0 from −1.0 to −0.3 to −0.1 (2 gives −0.6). All
  intervals include zero with 5 seeds, so this is a direction, not a finding. Activity is in sweep_003 below.
  **The engine is not tuned to these results.**
- **Sanity checks:** the streak penalty doesn't move C vs A0 (neither arm uses it); with no streak penalty
  C vs A equals C vs A0.

### Results: step-up threshold with activity (sweep_003)
Baseline, 300 personas × 90 days × seeds 1–5, arms A, A0, C; only `STEP_UP_SUCCESSES` changed (snapshot:
`docs/results/sweep_003/summary.md`). C vs A0, mean [95% interval]:

| Step up after | Δ active min/week | Δ tier-weighted sleep (pts) | Persistence wk 12 (pts) | Recovery 14 d (pts) | Retention (pts) |
|---|---|---|---|---|---|
| 2 | +2.2 [−0.4, +4.8] | +4.6 [+1.9, +7.2] | −0.6 [−2.6, +1.4] | −0.1 [−2.9, +2.7] | +0.3 [−1.2, +1.9] |
| **3 (current)** | +6.6 [+3.3, +9.9] | +8.3 [+5.8, +10.8] | −1.0 [−3.0, +1.0] | +1.0 [−1.8, +3.8] | −0.5 [−2.4, +1.4] |
| 4 | +8.6 [+6.3, +10.8] | +10.4 [+7.6, +13.2] | −0.3 [−1.8, +1.2] | +1.2 [−1.4, +3.8] | +0.3 [−1.0, +1.5] |
| 5 | +8.8 [+4.9, +12.7] | +10.9 [+8.6, +13.3] | −0.1 [−1.3, +1.0] | +1.2 [−2.4, +4.7] | +0.2 [−0.6, +1.0] |

**Our prediction was wrong.** We expected slower step-ups to *cost* activity, trading engagement for less volume.
Instead, activity *rises* with a slower step-up, and engagement doesn't get worse. Our reading: an eager step-up
often pushes people past what they can sustain, so they miss, step down or slip, and end up doing less over 90 days;
a slower climb holds. The 2-vs-4 activity difference is clear; 3 vs 4 or 5 overlaps with 5 seeds. The engagement
columns match sweep_002 exactly (same seeds), a reproducibility check.

Because this comes from the same simulator we'd be tuning to, the change 3 → 4 is tested only through a
pre-registered run on fresh seeds (next section), not adopted from this table.

### Step-up 3 → 4: pre-registered before any run (committed on its own, before the code)
**The change.** Engine constant `STEP_UP_SUCCESSES` 3 → 4: step up one tier after 4 consecutive full completions at
the current tier instead of 3. Nothing else changes in the engine or the simulator.

**How it's tested.** A new arm **C4** = C (`policy_mode="bandit"`) with `STEP_UP_SUCCESSES = 4`. It uses the same
bandit random seed as C for each persona, so the threshold is the only difference between C4 and C.
- Seeds **11–20** (never used for calibration or evaluation), 300 personas, 90 days.
- Baseline **and** all six other scenarios (ramadan_heavy, hot_summer, low_checkin, high_dropout, shock_heavy,
  harsh_attrition).
- Arms A, A0, C, C4. Run once; no re-runs with other seeds.

**Comparisons.** C4 vs C (the decision), plus C4 vs A and C4 vs A0 (reported, not part of the decision).

**Measures.** Δ weekly active minutes, Δ tier-weighted sleep nights, persistence at week 12, recovery within 14 days,
retention at day 90. Verdicts as everywhere: **helps** = whole 95% interval above zero, **worse** = whole interval
below zero, otherwise not shown.

**Decision rule, applied to C4 vs C.**
- **Keep 4** only if (a) Δ weekly active minutes is **helps** in baseline, and (b) none of the three engagement
  measures (persistence wk 12, recovery, retention) is **worse** in any of the 7 scenarios.
- **Otherwise revert to 3.**
- Δ tier-weighted sleep and the C4 vs A / A0 comparisons are reported but don't decide.

**Known property of the rule.** Condition (b) checks 21 intervals (3 measures × 7 scenarios), so even with no real
effect there's a fair chance one shows "worse" by chance. The rule is deliberately conservative: it favours keeping
the current, already-documented behaviour. We apply it as written and report the result either way.

**If kept:** `engine/rebound_engine/config.py` changes to 4, with a line here citing this test, and run_005-style
results are re-run on seeds 1–10 so the reported numbers match the shipped engine. **If reverted:** nothing changes;
the result is recorded here and the threshold stays a pilot question.

#### Result (run_006: seeds 11–20, all 7 scenarios, arms A, A0, C, C4; commits cac4f73 → a657d17 → run)
**Decision by the pre-registered rule: keep 4.** (a) Baseline Δ weekly active minutes, C4 vs C: +2.1 min
[+1.4, +2.9], helps. (b) No engagement measure for C4 vs C is worse in any of the 7 scenarios (21 checks).

| Scenario | Δ active min/week | Δ tier-weighted sleep (pts) | Persistence wk 12 (pts) | Recovery 14 d (pts) | Retention (pts) |
|---|---|---|---|---|---|
| baseline | +2.1 [+1.4, +2.9] helps | +1.8 [+1.5, +2.1] helps | +0.1 [−0.5, +0.7] | +0.5 [−0.2, +1.1] | +0.4 [−0.1, +0.9] |
| ramadan_heavy | +1.4 [+0.8, +1.9] helps | +1.5 [+1.1, +2.0] helps | +0.1 [−0.5, +0.7] | +0.1 [−0.5, +0.8] | +0.3 [−0.1, +0.7] |
| hot_summer | +2.1 [+1.3, +2.8] helps | +1.5 [+1.1, +1.9] helps | +0.0 [−0.5, +0.6] | +0.3 [−0.6, +1.1] | +0.3 [−0.3, +0.8] |
| low_checkin | +2.1 [+1.7, +2.5] helps | +2.0 [+1.5, +2.4] helps | +0.5 [+0.1, +0.9] helps | −0.0 [−1.0, +0.9] | +0.4 [−0.1, +0.8] |
| high_dropout | +1.7 [+1.0, +2.4] helps | +1.4 [+1.1, +1.6] helps | +0.1 [−0.3, +0.6] | +0.4 [−0.0, +0.8] | +0.0 [−0.4, +0.5] |
| shock_heavy | +1.8 [+1.2, +2.5] helps | +1.7 [+1.3, +2.1] helps | +0.6 [−0.2, +1.4] | +0.1 [−0.7, +0.9] | +0.1 [−0.4, +0.6] |
| harsh_attrition | +1.8 [+1.2, +2.4] helps | +1.9 [+1.7, +2.1] helps | +0.5 [+0.1, +0.8] helps | +0.4 [−0.3, +1.1] | +0.3 [−0.3, +0.9] |

C4 vs C, mean [95% interval]; blank = not shown. The gain is consistent but modest: about +2 active minutes per
week and +1.5 to +2 pts of tier-weighted sleep in every scenario, with engagement unchanged or slightly better.

**Reported, not deciding.** C4 vs A: helps on every measure in every scenario. C4 vs A0: activity helps everywhere
(+3.5 to +8.6 min/week), recovery helps in **7 of 7** scenarios (+0.9 to +1.8 pts), persistence worse in
high_dropout (−0.9 [−1.6, −0.1]), everything else not shown. Also on these fresh seeds, C (step-up 3) vs A0 recovery
is "helps" in 5 of 7 scenarios (+0.8 to +1.7 pts), where on seeds 1–10 (run_005) it wasn't in any. (An earlier
version of this note said "6 of 7" for C4; the run_006 table shows 7 of 7.)

**Decision applied:** tests made threshold-agnostic (`f13f9dd`), engine `STEP_UP_SUCCESSES` 3 → 4 (`b402774`),
AGENTS.md / CLAUDE.md §6.3 updated (`ead1934`). The reported results were then re-run on seeds 1–10 with the shipped
engine (run_007, next section). Snapshot of this run: `docs/results/run_006/scenarios.md`.

### Reported results: shipped engine, step-up 4 (run_007)
**These are the numbers to report.** run_007 = 7 scenarios × 300 personas × 90 days × seeds 1–10 (the evaluation
seeds), arms A, A0, B, C, engine as shipped (`STEP_UP_SUCCESSES` = 4). It supersedes run_005 (step-up 3) as the
headline; run_005 and the Drop 2 sections above stay as history. Safety audit: 0 unsafe actions and 0 quiet-hour
messages in B and C, every scenario. Snapshot: `docs/results/run_007/`.

**Provenance of the shipped step-up threshold (no seed set both chose and reported it):**
- seeds **1–5** *informed* the choice (sweep_003, a sensitivity sweep);
- seeds **11–20** *confirmed* it (run_006, pre-registered rule, decision "keep 4");
- seeds **1–10** *re-report* the shipped engine (run_007, below). These seeds include the sweep's 1–5, which is why
  run_006, not run_007, is the evidence for the change; run_007 only brings the reported numbers in line with the
  engine as shipped.

**Headline (shipped engine, run_007):** Against a streak app that penalises misses, Rebound improves recovery (+13
to +19 pts), week-12 persistence (+17 to +25 pts) and retention (+13 to +19 pts) in every scenario, and people do
more: +16.9 active min/week [+15.6, +18.1] and +13.9 pts tier-weighted sleep [+12.5, +15.3] in baseline (+8.5 to
+18.1 min across scenarios). Against a static plan without that penalty, engagement is about equal, recovery after a
lapse is small (~1–2 pts) but consistent, and people still do more: +8.7 active min/week [+7.5, +9.9] and +10.4 pts
tier-weighted sleep [+9.0, +11.8] in baseline (+4.4 to +9.8 min across scenarios). The engagement advantage over a
streak app exists only if missing a day on a streak app lowers motivation (abstinence-violation effect); with no
such effect it disappears (sweep_002). The bandit adds no measurable benefit over rules at 90 days and this sample
size.

**Pre-registered comparisons (run_007), percentage points, mean [95% interval]; blank = not shown:**

| Scenario | C vs A: recovery / persistence wk 12 / retention | C vs A0: recovery / persistence / retention | C vs B |
|---|---|---|---|
| baseline | +18.5 / +25.2 / +13.8, all helps | +1.5 [+0.4, +2.6] helps / −0.2 / −0.0 | ≈ 0 |
| ramadan_heavy | +18.3 / +25.0 / +14.0, all helps | +1.2 [+0.0, +2.4] helps / −0.5 / +0.2 | ≈ 0 |
| hot_summer | +19.2 / +25.1 / +13.4, all helps | +1.8 [+0.5, +3.1] helps / −0.2 / −0.3 | ≈ 0 |
| low_checkin | +18.5 / +25.2 / +14.1, all helps | +1.5 [+0.0, +3.0] helps / −0.1 / +0.3 | ≈ 0 |
| high_dropout | +13.3 / +17.3 / +18.7, all helps | +0.6 / −0.7 [−1.3, −0.2] **worse** / −0.3 | ≈ 0 |
| shock_heavy | +16.7 / +21.6 / +15.1, all helps | +0.8 [+0.2, +1.5] helps / −1.1 [−2.0, −0.3] **worse** / −0.4 | ≈ 0 |
| harsh_attrition | +13.9 / +17.5 / +14.4, all helps | +0.6 / −0.1 / −0.1 | retention −0.5 [−0.9, −0.0] **worse** |

**Activity (secondary), run_007, mean [95% interval]; all intervals above zero:**

| Scenario | C vs A: Δ active min/week | C vs A: Δ tier-weighted sleep (pts) | C vs A0: Δ active min/week | C vs A0: Δ tier-weighted sleep (pts) |
|---|---|---|---|---|
| baseline | +16.9 [+15.6, +18.1] | +13.9 [+12.5, +15.3] | +8.7 [+7.5, +9.9] | +10.4 [+9.0, +11.8] |
| ramadan_heavy | +16.8 [+15.5, +18.2] | +13.9 [+12.4, +15.3] | +8.7 [+7.2, +10.2] | +10.4 [+8.9, +11.9] |
| hot_summer | +18.1 [+16.7, +19.5] | +14.0 [+12.6, +15.3] | +9.8 [+8.3, +11.3] | +10.5 [+9.2, +11.9] |
| low_checkin | +16.8 [+15.4, +18.2] | +13.9 [+12.6, +15.2] | +8.6 [+7.2, +10.1] | +10.4 [+9.2, +11.7] |
| high_dropout | +9.8 [+8.1, +11.4] | +5.7 [+4.7, +6.7] | +5.5 [+4.0, +7.0] | +3.8 [+2.9, +4.6] |
| shock_heavy | +12.5 [+10.7, +14.3] | +10.6 [+9.3, +11.9] | +6.0 [+4.5, +7.4] | +7.7 [+6.5, +8.8] |
| harsh_attrition | +8.5 [+7.1, +10.0] | +6.6 [+5.7, +7.6] | +4.4 [+3.2, +5.6] | +4.8 [+4.0, +5.7] |

**C vs A0 recovery: small (~1–2 pts) but consistent.** Clear ("helps") in 5 of 7 worlds in run_007 (+0.8 to +1.8
pts; not shown in high_dropout and harsh_attrition, +0.6 each), and in 7 of 7 for C4 in run_006 on fresh seeds. This
replaces the earlier "weak evidence" label, which was based on run_003 and run_005 with step-up 3.

**The 3 "worse" results in run_007** (whole interval below zero, out of 63 pre-registered intervals):
1. C vs A0, persistence wk 12, high_dropout: −0.7 [−1.3, −0.2].
2. C vs A0, persistence wk 12, shock_heavy: −1.1 [−2.0, −0.3].
3. C vs B, retention, harsh_attrition: −0.5 [−0.9, −0.0].

The first two match the known step-up cost vs a static easy plan, in the two harshest engagement worlds. The C vs B
one is likely chance: with 63 intervals, a few will exclude zero with no real effect; C vs B is ≈ 0 everywhere else,
and that interval only just excludes zero.

**Compared with run_005 (step-up 3, same seeds):** C vs A0 recovery is now "helps" in 5 of 7 scenarios (it was in
none), and the "worse" results shrink (shock_heavy persistence −1.5 → −1.1; retention worse in high_dropout and
shock_heavy → no longer). Arm A's week-12 persistence is 33% here vs 41% on calibration seed 101: a seed-set
difference, not retuned.

### Lapse-risk model (Task 02b, Drop A)
Details and limitations: `docs/MODEL_CARD.md`. Choices made here:

| Choice | Value | Why |
|---|---|---|
| Training data | arm C, baseline scenario, 300 personas × 90 days, seeds 21–30 | Fresh seeds: 1–10 evaluation, 11–20 step-up test, 101 calibration are never used. Arm C because that's the shipped engine's behaviour. |
| Split | by seed: train 21–26, validation 27–28, test 29–30 | Splitting by seed splits by persona, so a person's days never leak across splits (Task 02b honesty rule). |
| Label | engine state becomes `lapsed` within the next 7 days | What the engine would act on (the engine's state, not the simulator's replay). Already-lapsed rows, rows after churn and the last 7 days (no full window) are excluded. |
| Features | 41, from `compute_features(profile, state, events, day)` only | Same code in training and in the app. Travel left out (the engine never gets a travel flag). Weekend gap kept for real data but uninformative here (no weekly rhythm in the sim). |
| Habit-strength slope | from `UserState.h_daily`: H at the start of each of the last 15 days | The only engine change in Drop A: an observation-only field, needed because H can't be recovered from the event log. No engine behaviour changes. |
| Models | logistic regression and gradient boosting (`random_state=0`); pick by validation AUROC | Task 02b. Both reported. |
| Alert threshold | score flagging 15% of validation days (`RISK_ALERT_RATE`) | Task 02b's example alert rate, frozen into the model file. |
| Baselines | drifting rule (state is `drifting`); completion heuristic (last-7-day completion rate below a threshold set on validation at the same 15% alert rate) | Your additions (a). The model must beat both to be worth having. |
| Lapses caught / warning time | caught = an alert in the 7 days before the engine entered `lapsed`; warning = days from the first such alert to the lapse, median over caught lapses | Your addition (b). |
| Intervals | 95% persona-bootstrap (200 resamples) for AUROC, recall, and model-minus-heuristic AUROC | Test has only 2 seeds, so a t-interval across seeds would be meaningless. |

### Arm D (lapse-risk hook): pre-registered before any Task 02b run (committed on its own, before the code)
**What's tested.** Arm **D** = C plus the lapse-risk model (`Engine(risk_model=...)`, Task 02b). When predicted risk is
above the frozen threshold and the state is still `active`, the engine offers the next action one tier smaller as an
option, and sends a gentle check-in at most once per 7 days. The model, its features and its threshold are frozen
from the training seeds (21–30) before D is run; nothing about them is changed after seeing D's results.

**How the simulated person responds to the lighter option.**
- **Main assumption (arm D):** the persona takes whichever option it's more likely to complete, under its own hidden
  model.
- **Sensitivity (arm D50):** the persona picks either option with probability 0.5.

Both are reported. Only D decides.

**Runs.** Seeds 1–10 (the evaluation seeds; never used for training or threshold-setting), 300 personas, 90 days,
all 7 scenarios, arms A, A0, C, D, D50. Run once.

**Comparisons.** D vs C (the decision); D50 vs C (sensitivity); D vs A and D vs A0 (reported).

**Measures.**
- persistence at week 12, recovery within 14 days, retention at day 90;
- **lapse rate:** % of personas with at least one lapse onset in 90 days (lower is better);
- messages per persona-week (burden).

**Verdicts.** helps / worse = whole 95% interval of the difference above / below zero, except where lower is better:
for lapse rate, "helps" means the whole interval of D − C is below zero and "worse" means it is entirely above.

**Ship rule (D vs C).** The hook goes into the app only if all three hold:
1. lapse rate is **helps** in baseline;
2. none of persistence wk 12, recovery or retention is **worse** in any of the 7 scenarios;
3. burden: in every scenario the mean difference in messages per persona-week is at most **+0.5**. "Worse" on burden
   means exceeding +0.5, not any increase.

Otherwise the hook stays out of the app, and the model is shown only as a prediction result (PLAN.md cut list).

**How the hook was built (Drop B, decided before running D):**
| Choice | Value | Why |
|---|---|---|
| When risk is computed | at the start of each day, from everything up to the end of yesterday | The lighter option has to be there when today's actions are shown. |
| Lighter option | same behaviour, the highest allowed tier below the shown one, at the same hour, through the same safety filter | Never a different or riskier kind of action; quiet hours unaffected. None if the shown action is already the smallest allowed. |
| What the hook doesn't change | the shown action, the tier, the bandit's choice | It's an *option*; the plan itself is unchanged (tested). |
| Taking the lighter option | answers the shown action for the day; no bandit reward (the bandit didn't choose it) and no step-up credit (it's below the current tier) | Same rule as other lower-tier fallbacks. |
| Gentle check-in | only if none is already due, at most once per 7 days, and never two check-in messages on one day (any kind) | Your burden answer (6). Answering it applies the usual barrier rules. |
| Explanations | `RiskModel.reasons`: plain phrases, intuitive direction only | Shown in the app as "We noticed …". |
| Model used by D / D50 | `models/lapse_risk.joblib` from risk_001, frozen | Pre-registered. |

#### Result (run_008: seeds 1–10, all 7 scenarios, arms A, A0, C, D, D50)
**Decision by the pre-registered rule: keep the hook out of the app.** Condition (1) fails: baseline lapse rate, D vs C,
is +0.2 pts [−0.1, +0.5], not "helps". Conditions (2) and (3) hold: no engagement measure is worse for D vs C in any
scenario, and burden is +0.1 messages per persona-week everywhere (cap +0.5). D vs C is ≈ 0 on every measure in
every scenario (one "helps": hot_summer retention +0.5 [+0.1, +0.9]). D50 is the same picture.

**So the shipped default is no hook:** `Engine()` without a risk model, exactly as before Task 02b. The model stays in
the repo as a tested component (features, training, evaluation, explanations, the hook code and its tests), with its
prediction results in `docs/MODEL_CARD.md`.

**Likely reason (read-only check on run_008 baseline, arm D):**
- On alert days with a lighter option offered, **46% were days the persona didn't open the app** (35% on other days),
  so the option was never seen. When the app *was* opened, the option was taken on 89% of those days.
- On risk-check-in days (6,248; each is an alert day), **77% had every action already at tier 1**, so there was
  nothing lighter to offer, and 48% were closed-app days. **Only 26% of these alert days put a lighter option in
  front of the user.**

People at risk have mostly stopped opening the app, and the plan has usually already shrunk to the smallest step. An
in-app lighter option can't reach them. (The simulator doesn't log every alert, only offers and check-ins, so
risk-check-in days are a sample: the first alert in each 7-day window.)

**Pilot recommendation:** keep the risk score, and test *out-of-app* interventions triggered by it, which reach people
who aren't opening the app. For example a WhatsApp-style nudge (`channel: whatsapp_style`), a buddy prompt, or a
voice note, within the same message cap and quiet hours. Pre-register it like arm D, with a micro-randomised design
(PRD §14).

**Also from run_008: C and D vs A0, lapse rate slightly *higher* while recovery is better.** Lapse rate vs A0 is
+0.4 to +1.4 pts for both C (baseline +1.1 [+0.7, +1.6]) and D (baseline +1.4 [+1.0, +1.7]), whole interval above zero
in every scenario. Recovery within 14 days is better (D vs A0 +0.6 to +1.7 pts, "helps" in 5 of 7; C vs A0 the same
picture, see run_007).
Consistent with Rebound asking for more than a static easy plan: a few more people slip at some point, and more of them
come back.

### Check-ins answered only on open days: pre-registered before any run (committed on its own, before the code)
**The change (simulator behaviour model only; the engine is unchanged).** Today a persona with a check-in due answers
it with probability `answer_rate` on any day, including days it doesn't open the app. A real user can only answer
inside the app. New rule: **a check-in can be answered only on a day the persona opens the app** (`app_open`); on
those days the answer probability is unchanged. Config flag `traits.checkin_needs_open_app`, default `false` until
this test has run, so run_007 still reproduces exactly from the same commit.

**Why.** It's more realistic, and it was found in code review, not in results. It matters because people open the app
on ~40% of days, so the current model lets engine arms (B, C) adapt from check-ins that no real user could have
answered. Expected direction, written down now: fewer answered check-ins in B and C, so their recovery edge over A0
probably shrinks. A and A0 send no check-ins, so they can't be affected.

**Adoption, decided now, whatever the result.** The stricter rule becomes the reported world: after the test the
default flips to `true` and the reported results are re-run on the evaluation seeds 1–10 (as for step-up 3 → 4).
run_007 stays documented as the earlier world ("answered on any day"), like run_002. Calibration is unaffected (arm A
only, and A answers no check-ins), so `open_base` stays.

**How it's tested.**
- Seeds **31–40**: never used before (1–10 evaluation, 11–20 step-up test, 21–30 risk-model training and test,
  101 calibration). 300 personas, 90 days, all 7 scenarios, arms A, A0, B, C.
- Two runs on those seeds, identical except for the flag: **run_009** (`false`, any day) and **run_010** (`true`,
  open days only), so the check-in rule is the only difference. Each is run once.
- **Validity check:** A and A0 must give identical metrics in run_009 and run_010. If they differ, the change touched
  something it shouldn't have; both runs are invalid, deleted and recorded here.
- Safety audit must be 0 for B and C in both runs (§9.8).

**Comparisons and measures.** The pre-registered headline: C vs A, C vs A0, C vs B on recovery within 14 days,
persistence at week 12 and retention at day 90, plus Δ weekly active minutes and Δ tier-weighted sleep, in every
scenario and in both runs. Verdicts as everywhere: **helps** = whole 95% interval above zero, **worse** = whole
interval below zero, otherwise **not shown**. Also reported: the share of check-ins answered in B and C in each run.

**How it's reported.**
- Every headline verdict for run_009 and run_010 side by side, whatever the direction.
- A verdict that is **helps** in run_009 but not in run_010 is reported as **depending on the assumption that
  check-ins can be answered on closed-app days** (§9.5), in this file, `docs/HANDOFF.md` and the submission.
- Any verdict that changes the other way (not shown → helps) with only one or two such changes among the 105 is
  labelled weak evidence, not a finding.
- The lapse-risk model (risk_001) was trained in the earlier world and is not retrained; its model card says so.

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

## API (Task 03)

| Choice | Value | Why |
|---|---|---|
| Engine day | calendar days in the user's time zone; the onboarding day is day 1 (+ `day_offset`, demo only) | Engine day 0 is the onboarding state with nothing shown yet. Time zone defaults to `Asia/Dubai`. |
| Days the app wasn't opened | the API brings the engine forward one day at a time; each skipped day's actions are shown and closed as `no_response`; every user route (today, events, check-in, state, settings, export) does this first | Same as a closed-app day in the simulator; without it a silent user would never become drifting/lapsed, and a check-in on a stale day would be followed by a second ask. |
| Catch-up cap | at most 60 unopened days are filled in; older ones are not logged | Bounds the work on one request. 60 > every engagement window (7–14 days) and the 21-day history, so the engagement state is the same as without the cap; H after 60 silent days is already below 0.2% of where it started (0.9^60). |
| Check-ins | at most one per day (409); a red-flag free text is always accepted | One blame-free question a day; a safety signal must never be rate-limited. |
| Adjusted actions | the API calls `Engine.checkin(replace_pending=True)`: today's open action is swapped for the smaller one, logged as `action_shown` with `payload.replaces` | Otherwise the user is told "here's a smaller step" but can't record it until tomorrow. The simulator keeps the default (`False`), so reported results are unchanged. |
| CORS | `FRONTEND_URL` always; `http://localhost:5173` only with `DEMO_MODE` or `DEV_MODE` | No local origin in production. |
| Screening consent | onboarding with `consents.screening = false` → 422 | The health check is required for a safe plan (§4.3). |
| Prompt hour | chosen by the engine (wake/sleep times, quiet hours); the API doesn't pass an hour | Keeps quiet hours in one place. |
| Events | only for today's still-open actions; repeats and unknown ids → 409 | A double tap must not count a completion twice. |
| Check-in free text | used only when no barrier button was pressed; skipped if the engine's red-flag keywords match | Buttons decide (Task 03 §6); red-flag text is never sent to a classifier. |
| Unpausing after a red flag | refused (409) through settings | §6.4: coaching stays stopped until a person has checked in. |
| Messages | `api/messages.py`, EN + AR; Arabic unreviewed (`AR_REVIEWED = False`); 998 (UAE ambulance, u.ae) and 800 SAKINA / 800 725462 (Abu Dhabi DoH 24/7 mental health line, announced Mar 2026) in the red-flag message | Placeholder until TASK_01_C's templates. Abu Dhabi line chosen because the pilot is in Abu Dhabi; other emirates may need their own. |
| Consents | a group sent with consent `false` is never stored (onboarding) and is deleted when withdrawn (settings); screening can't be withdrawn | §2.4 data minimisation, §4.7 data controls. |
| Red-flag text | apostrophes (`'`, `’`) are deleted before matching, so "can't", "can’t" and "cant" match the same phrase; added "end it all", "ending my life", "no reason to live", "can't go on", "don't want to be here" | Typed messages often drop apostrophes. Substring matching means more false positives (e.g. "I can't go on the trip"); for a safety check that's the right side to err on. |
| Export | `GET /users/{id}/export`: profile, state, full event log, account fields; never the token hash | §4.7 "view … export". |
| Policy mode | rules (`Engine()` default), no risk model | Bandit adds nothing at 90 days (run_007); hook failed its test (run_008). |

## Dependencies
- Engine: Python 3.11+, Pydantic v2, PyYAML. Dev: pytest, ruff.
- Simulator: numpy, pandas, pyarrow (Parquet; falls back to CSV without it), matplotlib.
- API: FastAPI, uvicorn, python-dotenv, tzdata (time zones on Windows), stdlib sqlite3. Dev: httpx (TestClient).

## Limitations
- The action library is a first draft: 17 actions, Arabic titles not yet reviewed (`ar_reviewed: false`),
  rationale and limits English only.
- Screening questions are paraphrased from PAR-Q+ and are not a clinical tool.
- The in-memory store loses data on restart; the API uses `SQLiteStore` (Task 03).
- `SQLiteStore` serialises single reads and writes, but an engine call (load state → change → save) is not one
  transaction: two requests for the same user at the same moment can overwrite each other's state. Fine for a
  one-person demo; production needs a per-user lock or optimistic versioning, and a server database.
- **Prototype auth, not production auth.** One random bearer token per user, returned once at onboarding and stored
  as a sha256 hash; no expiry, rotation, recovery or rate limiting, and a lost token means a lost account. Demo
  routes exist only with `DEMO_MODE=true`; the employer view uses one shared org key from `.env`.
- Changing `preferences.channel` in settings is saved but doesn't change the engine's channel (set at onboarding,
  then only by the `forgot` rule); the engine has no call for it yet.
- Withdrawing consent for body, history or preferences deletes those answers (preferences go back to defaults,
  which also drops custom quiet hours). The health check can't be withdrawn on its own because the plan's safety
  depends on it; the user deletes the account instead. Engine state already derived from withdrawn answers (e.g.
  a starting tier capped by the body group) is kept.
- Simulated behaviour is plausible, not empirically fitted; results show relative advantage, not real-world effect sizes.
- In the calibrated simulation almost all disengagement comes from not opening the app: on open days, 82–95% of
  actions are completed in every arm. Real users also open the app and still skip; if that's common, plan quality
  matters more than this model shows.
- The engagement advantage over a streak app depends on the assumed size of the streak penalty (arm A vs A0) and of
  the success feedback δ; both are swept in Drop 2. With no streak penalty the advantage disappears.
- Success feedback is the same for every completion regardless of difficulty, which favours easy static plans; a
  difficulty-weighted version (mastery experiences) is an untested alternative.
- The step-up threshold (now 4 consecutive completions) was chosen by a pre-registered simulator test, not by real
  users. It has to be confirmed in the pilot.
