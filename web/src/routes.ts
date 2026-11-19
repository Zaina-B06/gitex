import { ScreenId } from './types'

/** One URL per screen. */
export const SCREEN_PATHS: Record<ScreenId, string> = {
  welcome: '/welcome',
  'onboarding-basics': '/onboarding/about-you',
  'onboarding-goals': '/onboarding/goals',
  'onboarding-health': '/onboarding/health',
  'onboarding-baseline': '/onboarding/your-days',
  'onboarding-preferences': '/onboarding/what-helps',
  'plan-ready': '/onboarding/your-plan',
  'save-progress': '/onboarding/save-progress',
  today: '/today',
  plan: '/plan',
  meals: '/meals',
  community: '/community',
  settings: '/settings',
  checkin: '/checkin',
  'easier-plan': '/checkin/easier',
  recipe: '/recipe',
  report: '/settings/report',
  care: '/care',
  'program-dashboard': '/employer',
  'chat-nudge': '/chat',
  results: '/results',
}

/** Screens that need a signed-in user; others are always reachable. */
export const APP_SCREENS: ScreenId[] = [
  'plan-ready',
  'save-progress',
  'today',
  'plan',
  'meals',
  'community',
  'settings',
  'checkin',
  'easier-plan',
  'recipe',
  'report',
  'chat-nudge',
]

export function screenForPath(pathname: string): ScreenId | null {
  const hit = Object.entries(SCREEN_PATHS).find(([, p]) => p === pathname)
  return hit ? (hit[0] as ScreenId) : null
}
