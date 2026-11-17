/**
 * Typed client for the Rebound backend (github.com/Zaina-B06/gitex, api/).
 * Types come from its openapi.json: run `npm run types` after the backend changes.
 */
import type { components } from './schema'

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

// Dev: blank → Vite proxies /api to http://127.0.0.1:8000. Production: the deployed backend URL.
const BASE = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, '') || '/api'

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

  let res: Response
  try {
    res = await fetch(BASE + path, {
      method,
      headers,
      body: opts.body === undefined ? undefined : JSON.stringify(opts.body),
    })
  } catch {
    throw new ApiError(0, 'Cannot reach the Rebound server. Is the backend running?')
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
    if (res.status >= 500 && res.status !== 503) detail = 'Cannot reach the Rebound server. Is the backend running?'
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
}

/** Friendly text for an error shown in a toast or inline. */
export function errorText(e: unknown): string {
  return e instanceof ApiError ? e.detail : 'Something went wrong. Please try again.'
}
