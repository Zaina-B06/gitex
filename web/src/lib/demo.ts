import type { SeedPersona } from '../api/client'

export const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

const KEY_STORE = 'rebound.demoKey'
const PERSONAS_STORE = 'rebound.demoPersonas'

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
