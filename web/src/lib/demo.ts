import type { SeedPersona } from '../api/client'

export const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

const KEY_STORE = 'rebound.demoKey'
const PERSONAS_STORE = 'rebound.demoPersonas'

/** One line per seeded person (api/demo.py DEMO_PERSONAS), shown when picking who to try. */
export const PERSONA_LINES: Record<string, string> = {
  Ahmed: 'Night-shift worker, fasts in Ramadan, lives with his children',
  Sara: 'Office worker with no conditions: the plain plan, for comparison',
  Mariam: 'Uses a wheelchair, recovering, cares for family at home',
}
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
export function demoKey(): string | null {
  const built = import.meta.env.VITE_DEMO_KEY as string | undefined
  if (built) return built
  const stored = session.get(KEY_STORE)
  if (stored) return stored
  const typed = window.prompt('Demo key (ask the Rebound team):')?.trim() || null
  session.set(KEY_STORE, typed)
  return typed
}
export const forgetDemoKey = () => session.set(KEY_STORE, null)

/** The people from the last POST /demo/seed in this tab, for "switch person". */
export function loadPersonas(): SeedPersona[] {
  try {
    return JSON.parse(session.get(PERSONAS_STORE) ?? '[]') as SeedPersona[]
  } catch {
    return []
  }
}
export const savePersonas = (p: SeedPersona[]) => session.set(PERSONAS_STORE, JSON.stringify(p))
