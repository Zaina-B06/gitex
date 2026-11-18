import type { Dispatch, SetStateAction } from 'react'
import type { Behaviour, CheckinOut, Condition, PlanOut, Session } from './api/client'
import type { components } from './api/schema'

export type ScreenId =
  // first-run onboarding, in order
  | 'welcome'
  | 'onboarding-basics'
  | 'onboarding-goals'
  | 'onboarding-health'
  | 'onboarding-baseline'
  | 'onboarding-preferences'
  | 'plan-ready' // "Your plan, built for you"
  | 'save-progress' // optional username + password, last sign-up screen
  // the app (needs a signed-in user); the first five are the bottom tabs
  | 'today'
  | 'plan' // "My plan" tab: calendar, daily thought, plan reasons
  | 'meals'
  | 'community'
  | 'settings'
  | 'checkin'
  | 'easier-plan'
  | 'recipe'
  | 'report'
  | 'care'
  // outside the user app
  | 'program-dashboard'
  | 'chat-nudge' // chat check-in (WhatsApp-style), at /chat

type S = components['schemas']
export type Sex = S['Sex']
export type ScheduleType = S['ScheduleType']
export type SettingPref = S['PlaceSetting']
export type PastHelper = S['PastHelper']
export type MobilityLimitation = S['MobilityLimitation']
export type PregnancyAnswer = S['PregnancyAnswer']
export type Household = S['Household']
export type Weekday = S['Weekday']
export type ReadingLevel = S['ReadingLevel']

/** The seven yes/no health-check fields of `Screening` (CLAUDE.md §4.3). */
export const SCREENING_KEYS = [
  'heart_condition_or_high_bp',
  'chest_pain',
  'dizziness_or_fainting',
  'other_long_term_condition',
  'prescribed_medication',
  'bone_joint_muscle_problem',
  'supervised_exercise_only',
] as const
export type ScreeningKey = (typeof SCREENING_KEYS)[number]

/** What onboarding collects (CLAUDE.md §4). Turned into POST /users by lib/onboarding.ts. */
export interface OnboardingDraft {
  // step 1: about you
  ageYears: number | null
  sex: Sex | null
  scheduleType: ScheduleType | null
  usualWakeTime: string // HH:MM
  usualSleepTime: string // HH:MM
  shiftDays: Weekday[] // shift workers only
  shiftStart: string
  shiftEnd: string
  heightCm: number | null // optional, internal intensity cap only, never shown as BMI or a goal
  weightKg: number | null
  // step 2: goals
  goals: Behaviour[]
  conditions: Condition[]
  smokes: boolean
  consentConditions: boolean
  // step 3: health check
  screening: Record<ScreeningKey, boolean | null>
  pregnant: PregnancyAnswer | null // asked only if sex = female
  mobility: MobilityLimitation
  // step 4: baseline (questions depend on goals)
  activeDaysPerWeek: number | null
  sleepHoursTypical: number | null
  sleepQualitySelf: number | null // 1–5
  // step 5: what helps
  pastHelpers: PastHelper[]
  motivationReason: string
  fastingRamadan: boolean | null
  familyFasting: boolean
  setting: SettingPref
  womenOnlySpaces: boolean
  household: Household | null
  readingLevel: ReadingLevel
  // follow-up questions (shown only when their show_if rules match)
  caregiver: boolean
  anchor: string // "after maghrib": replaces "something you do daily" in step titles
  iftarTime: string // HH:MM, empty = local sunset
  quietStart: string // HH:MM, empty = no quiet hours
  quietEnd: string
}

/** Why the Care screen is showing. */
export type CareReason = 'onboarding_screening' | 'onboarding_text' | 'red_flag' | 'help'

export interface AppState {
  session: Session | null
  /** First name for the greeting: preferences.display_name on the server (not stored in the browser). */
  displayName: string
  /** The care text returned by the server for a red flag before sign-up (POST /content/onboarding/suggest). */
  careMessage: string | null
  language: 'en' | 'ar'
  profile: OnboardingDraft
  /** Plan summary from POST /users, shown on the plan-ready screen right after sign-up. */
  plan: PlanOut | null
  /** true from POST /users until "Start today". */
  justSignedUp: boolean
  /** Result of the last check-in, shown on the Easier plan screen. */
  lastCheckin: CheckinOut | null
  careReason: CareReason | null
  /** Recipe opened from a meal card on Today. */
  recipeTarget: { recipeId: string; actionId: string } | null
  bannerDismissed: boolean
  /** Bumped when server data changed behind the screen's back (demo fast-forward): screens refetch. */
  dataVersion: number
}

export interface ScreenProps {
  state: AppState
  setState: Dispatch<SetStateAction<AppState>>
  onNavigate: (screen: ScreenId) => void
  showToast: (msg: string) => void
}
