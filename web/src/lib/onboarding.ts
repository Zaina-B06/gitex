import type { Condition, OnboardIn } from '../api/client'
import { AppState, OnboardingDraft, SCREENING_KEYS, ScreeningKey } from '../types'

export const emptyDraft = (): OnboardingDraft => ({
  ageYears: null,
  sex: null,
  scheduleType: null,
  usualWakeTime: '06:30',
  usualSleepTime: '22:30',
  shiftDays: [],
  shiftStart: '07:00',
  shiftEnd: '15:00',
  heightCm: null,
  weightKg: null,
  goals: [],
  conditions: [],
  smokes: false,
  consentConditions: true,
  screening: Object.fromEntries(SCREENING_KEYS.map((k) => [k, null])) as OnboardingDraft['screening'],
  pregnant: null,
  mobility: 'none',
  activeDaysPerWeek: null,
  sleepHoursTypical: null,
  sleepQualitySelf: null,
  pastHelpers: [],
  motivationReason: '',
  fastingRamadan: null,
  familyFasting: false,
  setting: 'either',
  womenOnlySpaces: false,
  household: null,
  readingLevel: 'standard',
})

/** Health-check answers suggested by the conditions picked in step 2 (the user can change them). */
export const CONDITION_HINTS: Partial<Record<Condition, ScreeningKey>> = {
  high_blood_pressure: 'heart_condition_or_high_bp',
  diabetes: 'other_long_term_condition',
  back_or_joint_pain: 'bone_joint_muscle_problem',
}

// Which baseline questions matter depends on the goals (the engine reads them only for these behaviours).
export const asksActivity = (p: OnboardingDraft) => p.goals.includes('movement')
export const asksSleep = (p: OnboardingDraft) => p.goals.includes('sleep')
export const asksBaseline = (p: OnboardingDraft) => asksActivity(p) || asksSleep(p)

// Sent for baseline questions we skipped because the goal wasn't chosen. The engine only reads
// active_days for movement and sleep_* for sleep, so these never affect a plan. See docs/ASSUMPTIONS.md.
const NEUTRAL_BASELINE = { active_days_per_week: 3, sleep_hours_typical: 7, sleep_quality_self: 3 }

export const bodyValid = (p: OnboardingDraft) =>
  (p.heightCm === null || (p.heightCm >= 100 && p.heightCm <= 250)) &&
  (p.weightKg === null || (p.weightKg >= 30 && p.weightKg <= 300))

/** Which step is still missing a required answer, or null when the draft can be sent. */
export function missingStep(p: OnboardingDraft): string | null {
  if (p.ageYears === null || p.ageYears < 18 || p.ageYears > 100 || !p.sex || !p.scheduleType || !bodyValid(p))
    return 'About you'
  if (p.scheduleType === 'shift' && p.shiftDays.length === 0) return 'About you'
  if (p.goals.length === 0) return 'Goals'
  if (SCREENING_KEYS.some((k) => p.screening[k] === null)) return 'Health check'
  if (asksActivity(p) && p.activeDaysPerWeek === null) return 'Your days'
  if (asksSleep(p) && (p.sleepHoursTypical === null || p.sleepQualitySelf === null)) return 'Your days'
  return null
}

const timezone = () => {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Dubai'
  } catch {
    return 'Asia/Dubai'
  }
}

/** Builds the POST /users body. Call only when missingStep() is null. */
export function buildOnboardPayload(state: AppState): OnboardIn {
  const p = state.profile
  const screening = Object.fromEntries(SCREENING_KEYS.map((k) => [k, p.screening[k] === true])) as Record<
    ScreeningKey,
    boolean
  >
  const hasBody = p.heightCm !== null || p.weightKg !== null
  return {
    basics: {
      language: state.language,
      age_years: p.ageYears as number,
      sex: p.sex!,
      goals: p.goals,
      schedule_type: p.scheduleType!,
      usual_wake_time: p.usualWakeTime,
      usual_sleep_time: p.usualSleepTime,
      shifts:
        p.scheduleType === 'shift' && p.shiftDays.length
          ? [{ days: p.shiftDays, start: p.shiftStart, end: p.shiftEnd }]
          : null,
    },
    body: hasBody ? { height_cm: p.heightCm, weight_kg: p.weightKg } : null,
    screening: {
      ...screening,
      pregnant: p.sex === 'female' ? (p.pregnant ?? 'prefer_not_to_say') : null,
      mobility_limitation: p.mobility,
    },
    baseline: {
      active_days_per_week: asksActivity(p) ? (p.activeDaysPerWeek as number) : NEUTRAL_BASELINE.active_days_per_week,
      sleep_hours_typical: asksSleep(p) ? (p.sleepHoursTypical as number) : NEUTRAL_BASELINE.sleep_hours_typical,
      sleep_quality_self: asksSleep(p) ? (p.sleepQualitySelf as number) : NEUTRAL_BASELINE.sleep_quality_self,
    },
    history: {
      past_helpers: p.pastHelpers,
      past_stop_reasons: [],
      smoking_status: p.smokes ? 'current' : null,
      motivation_reason: p.motivationReason.trim() || null,
    },
    conditions: { managing: p.consentConditions ? p.conditions : [] },
    // Backend defaults, except what sign-up asked; the rest can change later in Settings.
    preferences: {
      setting: p.setting,
      fasting_ramadan: p.fastingRamadan === true,
      family_fasting: p.fastingRamadan === true && p.familyFasting,
      social: 'either',
      space_preference: p.sex === 'female' && p.womenOnlySpaces ? 'women_only_spaces' : 'any',
      channel: 'app',
      accessibility: [],
      encouragement: true,
      reading_level: p.readingLevel,
      read_aloud: false,
      household: p.household,
      caregiver: p.scheduleType === 'home_caregiver',
    },
    consents: {
      screening: true,
      history: true,
      preferences: true,
      conditions: p.consentConditions,
      body: hasBody,
    },
    timezone: timezone(),
  }
}
