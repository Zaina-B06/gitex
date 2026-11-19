/**
 * Typed client for the Rebound backend (github.com/Zaina-B06/gitex, api/).
 * Types come from its openapi.json: run `npm run types` after the backend changes.
 */
import type { components } from './schema'
import i18n, { tr } from '../i18n'

type S = components['schemas']
export type OnboardIn = S['OnboardIn']
export type OnboardOut = S['OnboardOut']
export type TodayOut = S['TodayOut']
export type ScheduledAction = S['ScheduledAction']
export type Action = S['Action']
export type StateOut = S['StateOut']
export type StateResponse = S['StateResponse']
export type CheckinOut = S['CheckinOut']
export type PlanOut = S['PlanOut']
export type SettingsIn = S['SettingsIn']
export type SettingsOut = S['SettingsOut']
export type ExportOut = S['ExportOut']
export type ExplainOut = S['ExplainOut']
export type RecipeOut = S['RecipeOut']
export type CommunityEvent = S['CommunityEvent']
export type OnboardingTextOut = S['OnboardingTextOut']
export type Behaviour = S['Behaviour']
export type Barrier = S['Barrier']
export type Condition = S['Condition']
export type Screening = S['Screening']
export type ContextFlag = S['ContextFlag']
export type Language = S['Language']
export type EncouragementOut = S['EncouragementOut']
export type Preferences = S['Preferences']
export type GoalOut = S['GoalOut']
export type SuggestOut = S['SuggestOut']
export type SuggestedAnswers = S['SuggestedAnswers']
export type RecapOut = S['RecapOut']
export type TokenOut = S['TokenOut']
export type SeedOut = S['SeedOut']
export type SeedPersona = S['SeedPersona']
export type AdvanceIn = S['AdvanceIn']
export type AdvanceOut = S['AdvanceOut']

/** One follow-up sign-up question (GET /content/onboarding follow_ups). Shown only when every rule matches. */
export interface FollowUpRule {
  field: string // a profile path, e.g. "basics.goals"
  op: 'contains' | 'equals' | 'not_in'
  value: unknown
}
export interface FollowUp {
  id: string
  fills: string
  show_if: FollowUpRule[]
  text: string
}

/** GET /recap facts (computed by rules on the server). */
export interface RecapFacts {
  goals: { behaviour: Behaviour; how: 'mostly_done' | 'mixed' | 'mostly_missed' | 'no_steps'; level: number }[]
  top_barrier: string | null
  comeback: boolean
}

// Dev: blank → Vite proxies /api to http://127.0.0.1:8000. Production: the deployed backend URL.
const BASE = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') || '/api'
export const REQUEST_TIMEOUT_MS = 60_000

export class ApiError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail)
  }
}

// ---------- session: only the user id and token are kept in the browser ----------

export interface Session {
  userId: string
  token: string
}

const SESSION_KEY = 'rebound.session'

export function loadSession(): Session | null {
  try {
    const raw = localStorage.getItem(SESSION_KEY)
    const s = raw ? (JSON.parse(raw) as Session) : null
    return s && s.userId && s.token ? s : null
  } catch {
    return null
  }
}

export function saveSession(s: Session | null): void {
  try {
    if (s) localStorage.setItem(SESSION_KEY, JSON.stringify(s))
    else localStorage.removeItem(SESSION_KEY)
  } catch {
    // storage blocked: the session lasts until the tab closes
  }
}

// ---------- transport ----------

let onUnauthorized: () => void = () => {}
/** App registers this so a 401 (deleted user, bad token) signs the user out. */
export function setUnauthorizedHandler(fn: () => void): void {
  onUnauthorized = fn
}

async function request<T>(
  method: 'GET' | 'POST' | 'PATCH' | 'DELETE',
  path: string,
  opts: { body?: unknown; session?: Session | null; headers?: Record<string, string> } = {},
): Promise<T> {
  const headers: Record<string, string> = { ...opts.headers }
  if (opts.body !== undefined) headers['Content-Type'] = 'application/json'
  if (opts.session) headers.Authorization = `Bearer ${opts.session.token}`

  // Free hosting sleeps when idle: give up after REQUEST_TIMEOUT_MS so no button waits for ever.
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS)
  let res: Response
  try {
    res = await fetch(BASE + path, {
      method,
      headers,
      body: opts.body === undefined ? undefined : JSON.stringify(opts.body),
      signal: controller.signal,
    })
  } catch {
    throw new ApiError(0, tr(controller.signal.aborted ? 'common.timeout' : 'common.serverDown'))
  } finally {
    clearTimeout(timer)
  }

  if (res.status === 401 && opts.session) onUnauthorized()
  if (!res.ok) {
    let detail = res.statusText || `HTTP ${res.status}`
    try {
      const data = await res.json()
      if (typeof data?.detail === 'string') detail = data.detail
      else if (Array.isArray(data?.detail)) detail = data.detail.map((d: { msg?: string }) => d.msg).join('; ')
    } catch {
      // non-JSON error body (e.g. proxy error page)
    }
    if (res.status >= 500 && res.status !== 503) detail = tr('common.serverDown')
    throw new ApiError(res.status, detail)
  }
  if (res.status === 204) return undefined as T
  return (await res.json()) as T
}

const q = (params: Record<string, string | undefined | null>) => {
  const s = new URLSearchParams()
  for (const [k, v] of Object.entries(params)) if (v) s.set(k, v)
  const str = s.toString()
  return str ? `?${str}` : ''
}

const u = (s: Session) => `/users/${encodeURIComponent(s.userId)}`

// ---------- endpoints ----------

export const api = {
  /** Wake-up check: no auth, no database work (free hosting sleeps when idle). */
  health: () => request<{ ok: boolean }>('GET', '/health'),

  onboardingContent: (lang: Language, readingLevel = 'standard') =>
    request<OnboardingTextOut>('GET', `/content/onboarding${q({ lang, reading_level: readingLevel })}`),

  onboard: (body: OnboardIn) => request<OnboardOut>('POST', '/users', { body }),

  today: (s: Session) => request<TodayOut>('GET', `${u(s)}/today`, { session: s }),
  plan: (s: Session) => request<PlanOut>('GET', `${u(s)}/plan`, { session: s }),
  state: (s: Session) => request<StateOut>('GET', `${u(s)}/state`, { session: s }),

  recordEvent: (s: Session, actionId: string, type: 'completed' | 'partial' | 'skipped') =>
    request<StateResponse>('POST', `${u(s)}/events`, { session: s, body: { action_id: actionId, type } }),

  checkin: (s: Session, barriers: Barrier[], freeText?: string) =>
    request<CheckinOut>('POST', `${u(s)}/checkin`, {
      session: s,
      body: { barriers, free_text: freeText?.trim() || null },
    }),

  settings: (s: Session, body: SettingsIn) => request<SettingsOut>('PATCH', `${u(s)}/settings`, { session: s, body }),
  exportData: (s: Session) => request<ExportOut>('GET', `${u(s)}/export`, { session: s }),
  deleteUser: (s: Session) => request<void>('DELETE', u(s), { session: s }),

  explain: (actionId: string, lang: Language) =>
    request<ExplainOut>('GET', `/actions/${encodeURIComponent(actionId)}/explain${q({ lang })}`),

  recipes: (tag?: string) => request<RecipeOut[]>('GET', `/recipes${q({ tag })}`),
  recipe: (id: string) => request<RecipeOut>('GET', `/recipes/${encodeURIComponent(id)}`),

  communityEvents: (s: Session, city?: string) =>
    request<CommunityEvent[]>('GET', `${u(s)}/community/events${q({ city })}`, { session: s }),

  // Sign-in (optional): a new token per device; logout revokes only this one.
  login: (username: string, password: string) =>
    request<TokenOut>('POST', '/auth/login', { body: { username, password } }),
  logout: (s: Session) => request<void>('POST', '/auth/logout', { session: s }),

  // Optional "tell us in your own words" at sign-up: suggestions only, never the health check.
  suggest: (text: string, lang: Language) =>
    request<SuggestOut>('POST', '/content/onboarding/suggest', { body: { text, lang } }),

  recap: (s: Session, days = 7) => request<RecapOut>('GET', `${u(s)}/recap${q({ days: String(days) })}`, { session: s }),

  // Dashboard pages (no auth).
  dashboardOutcomes: () => request<DashboardOutcomesData>('GET', '/dashboard/outcomes'),
  dashboardEmployer: (orgId: string, orgKey: string) =>
    request<EmployerData>('GET', `/dashboard/employer?org_id=${encodeURIComponent(orgId)}`, {
      headers: { 'X-Org-Key': orgKey },
    }),

  // Demo only (backend DEMO_MODE=true): seeded personas and time travel.
  demoSeed: (demoKey: string) => request<SeedOut>('POST', '/demo/seed', { headers: { 'X-Demo-Key': demoKey } }),
  demoAdvance: (s: Session, body: AdvanceIn) =>
    request<AdvanceOut>('POST', `/demo${u(s)}/advance`, { session: s, body }),
}

// ---------- dashboard types ----------

export interface MeasureStat { mean: number; ci_low: number; ci_high: number }
export interface ComparisonStat extends MeasureStat { verdict: 'helps' | 'not shown' | 'worse' }
export interface MeasureMeta { label: string; unit: string }
export interface ScenarioData {
  arms: Record<string, Record<string, MeasureStat>>
  comparisons: Record<string, Record<string, ComparisonStat>>
  safety: Record<string, { violations: number; quiet_messages: number }>
}
export interface DashboardOutcomesData {
  personas: number
  days: number
  seeds: number[]
  measures: Record<string, MeasureMeta>
  scenarios: Record<string, ScenarioData>
  verdict_rule: string
  [key: string]: unknown
}
export interface EmployerData {
  org_id: string
  group_size: number
  active_share: number
  average_habit_strength: Record<string, number>
  top_barriers: { barrier: string; count: number }[]
}

/** Friendly text for an error shown in a toast or inline. Server details are English, so Arabic gets our own. */
export function errorText(e: unknown): string {
  if (e instanceof ApiError && (e.status === 0 || i18n.language !== 'ar')) return e.detail
  return tr('common.genericError')
}
