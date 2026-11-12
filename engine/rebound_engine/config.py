"""Every tunable number the engine uses. Each one is explained in docs/ASSUMPTIONS.md."""

# --- Habit strength (AGENTS.md §6.1) ---
HABIT_LAMBDA = 0.9
# a_t per outcome; paused/illness days are skipped entirely, not scored.
OUTCOME_VALUE = {"completed": 1.0, "partial": 0.5, "skipped": 0.0, "no_response": 0.0}

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
STEP_UP_SUCCESSES = 3
# Starting movement tier from active_days_per_week: first (max_days, tier) that fits.
START_TIER_BY_ACTIVE_DAYS = ((2, 1), (4, 2), (7, 3))
SENIOR_AGE = 65
SENIOR_START_TIER = 1
# Internal BMI band -> starting-tier cap. Checked in order; never shown to the user.
BMI_START_CAPS = ((40.0, 1), (30.0, 2))
SLEEP_START_TIER = 1

# --- Context ---
HEAT_START_HOUR = 11
HEAT_END_HOUR = 16  # exclusive: 16:00 is outside the heat window

# --- Prompt windows (hour of day an action is prompted) ---
MORNING_OFFSET_H = 1  # after usual wake time
MIDDAY_HOUR = 13
EVENING_OFFSET_H = -3  # before usual sleep time
