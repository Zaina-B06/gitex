"""Every tunable number the engine uses. Each one is explained in docs/ASSUMPTIONS.md."""

# --- Habit strength (AGENTS.md §6.1) ---
HABIT_LAMBDA = 0.9
# a_t per outcome; paused/illness days are skipped entirely, not scored.
OUTCOME_VALUE = {"completed": 1.0, "partial": 0.5, "skipped": 0.0, "no_response": 0.0}
# H_0 = scale x baseline fraction (active days / 7, or (sleep quality - 1) / 4).
HABIT_START_SCALE = 0.5

# --- Engagement state (AGENTS.md §6.1) ---
ENGAGEMENT_WINDOW_DAYS = 7
ACTIVE_MIN_RATE = 4 / 7  # >= 4 of 7 days
LAPSED_MAX_RATE = 1 / 7  # <= 1 of 7 days
LAPSE_CONSECUTIVE_NO_RESPONSE = 3
RECOVERY_WINDOW_DAYS = 4
RECOVERY_MIN_COMPLETIONS = 2
MIN_DAYS_FOR_STATE = 3  # fewer counted days than this -> keep the previous state

# --- Tiers ---
MIN_TIER = 1
MAX_TIER = 4
SCREENING_TIER_CAP = 2  # any "yes" on screening Q1-Q7
GENTLE_TIER_CAP = 1  # chest pain or dizziness/fainting: gentle movement only
# Consecutive full completions at the current tier before stepping up. Was 3; changed to 4 by the pre-registered
# test in docs/ASSUMPTIONS.md ("Step-up 3 → 4", commit cac4f73): run_006, fresh seeds 11-20, all 7 scenarios.
STEP_UP_SUCCESSES = 4
STEP_DOWN_FAILURES = 2  # consecutive skipped/no_response at the current tier, while active
DRIFT_TIER_DROP = 1  # entering drifting; entering lapsed resets to MIN_TIER
# Starting movement tier from active_days_per_week: first (max_days, tier) that fits.
START_TIER_BY_ACTIVE_DAYS = ((2, 1), (4, 2), (7, 3))
SENIOR_AGE = 65
SENIOR_START_TIER = 1
# Internal BMI band -> starting-tier cap. Checked in order; never shown to the user.
BMI_START_CAPS = ((40.0, 1), (30.0, 2))
SLEEP_START_TIER = 1

# --- Encouragement moments (Task 05 Part C) ---
ENCOURAGE_HABIT_STRENGTH = 0.5  # habit_strength_50: H reaches half, once per behaviour
ENCOURAGE_FIRST_WEEK_DAY = 7  # first_week_done: a completion on or after this day
ENCOURAGE_GOOD_DAYS = 3  # three_good_days: a completion on each of the last 3 days

# --- Plan builder (Task 05) ---
MAX_ACTIVE_BEHAVIOURS = 3  # at most this many actions a day; with more goals the last slot rotates (burden cap)
NEW_BEHAVIOUR_START_TIER = 1  # nutrition, smoking, recovery start at their smallest step
NEW_BEHAVIOUR_H0 = 0.0  # no baseline question for these, so habit strength starts empty and builds from there

# --- Context ---
ILLNESS_MAX_TIER = 1  # nutrition and recovery while ill (safety.ILLNESS_TIER1_ONLY); movement is removed entirely
HEAT_START_HOUR = 11
HEAT_END_HOUR = 16  # exclusive: 16:00 is outside the heat window

# --- Calendar context (Task 05 A2; only when the engine is given a calendar) ---
HEAT_MONTHS = (5, 6, 7, 8, 9)  # May-September: heat mode on automatically
EID_REST_DAYS = 3  # first days of Shawwal (Eid al-Fitr) are rest-friendly for fasting users
RAMADAN_MOVE_AFTER_IFTAR_H = 1  # movement prompt this many hours after iftar
SHIFT_HOME_H = 1  # sleep starts this long after a night shift ends
SHIFT_SLEEP_H = 7  # sleep length after a night shift
NIGHT_SHIFT_ENDS_BEFORE_H = 12  # an overnight shift ending before noon is a night shift

# --- Prompt windows (hour of day an action is prompted) ---
MORNING_OFFSET_H = 1  # after usual wake time
AFTERNOON_HOUR = 13
EVENING_OFFSET_H = -3  # before usual sleep time

# --- History kept in UserState (engagement needs <= 7 counted days; the event log keeps everything) ---
HISTORY_KEEP_DAYS = 21
H_DAILY_KEEP = 15  # daily H values kept for the lapse-risk 7-day slope (Task 02b)

# --- Lapse-risk model (Task 02b) ---
RISK_ALERT_RATE = 0.15  # the alert threshold flags this share of validation days (frozen into the model file)
RISK_CHECKIN_EVERY_DAYS = 7  # a risk-triggered check-in at most once per this many days

# --- Bandit (Task 02) ---
BANDIT_PRIOR = (1.0, 1.0)  # Beta(alpha, beta) for every arm
WARM_START_BONUS = 1.0  # +alpha for arms whose BCT matches one of the user's past_helpers
HELPER_BCTS = {
    "small_steps": ["8.7"],  # Graded tasks
    "reminders": ["7.1"],  # Prompts/cues
    "tracking": ["2.3"],  # Self-monitoring of behaviour
    "routine_anchor": ["8.3", "1.4"],  # Habit formation, Action planning
    "buddy": [],  # no social-support actions in the library yet
    "rewards": [],  # no reward actions in the library yet
    "other": [],
}
