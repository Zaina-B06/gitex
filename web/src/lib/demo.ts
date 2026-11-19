import type { SeedPersona } from '../api/client'

export const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

const KEY_STORE = 'rebound.demoKey'
const PERSONAS_STORE = 'rebound.demoPersonas'
const ORG_ID_STORE = 'rebound.demoOrgId'
const ORG_KEY_STORE = 'rebound.orgKey'

export const firstName = (p: SeedPersona) => p.name.split(',')[0]

const session = {
  get: (k: string) => {
    try {
      return sessionStorage.getItem(k)
    } catch {
      return null
    }
  },
  set: (k: string, v: string | null) => {
    try {
      if (v === null) sessionStorage.removeItem(k)
      else sessionStorage.setItem(k, v)
    } catch {
      // storage blocked: asked again next time
    }
  },
}

/** The demo key: VITE_DEMO_KEY if the build has one, else asked once per tab (kept in sessionStorage only). */
export function demoKey(promptText: string): string | null {
  const built = import.meta.env.VITE_DEMO_KEY as string | undefined
  if (built) return built
  const stored = session.get(KEY_STORE)
  if (stored) return stored
  const typed = window.prompt(promptText)?.trim() || null
  session.set(KEY_STORE, typed)
  return typed
}
export const forgetDemoKey = () => session.set(KEY_STORE, null)

/** One line per seeded person lives in i18n/onboarding.ts (welcome.persona.*). */

/** The people from the last POST /demo/seed in this tab, for "switch person". */
export function loadPersonas(): SeedPersona[] {
  try {
    return JSON.parse(session.get(PERSONAS_STORE) ?? '[]') as SeedPersona[]
  } catch {
    return []
  }
}
export const savePersonas = (p: SeedPersona[]) => session.set(PERSONAS_STORE, JSON.stringify(p))

/** The org ID from the last POST /demo/seed, kept in sessionStorage for the employer dashboard. */
export function loadOrgId(): string | null {
  return session.get(ORG_ID_STORE)
}
export function saveOrgId(orgId: string | null): void {
  session.set(ORG_ID_STORE, orgId)
}

/** The org key: VITE_ORG_KEY if configured, else stored in sessionStorage. */
export function loadOrgKey(): string | null {
  const built = import.meta.env.VITE_ORG_KEY as string | undefined
  if (built) return built
  return session.get(ORG_KEY_STORE)
}
export function saveOrgKey(key: string | null): void {
  session.set(ORG_KEY_STORE, key)
}
