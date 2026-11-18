/**
 * App labels in English and Arabic (react-i18next). Arabic is a draft translation, pending native review, like
 * the API's Arabic. Each area has its own file with `en` and `ar` objects; `ar` is typed against `en`, so a
 * missing Arabic label fails the build. Texts that come from the API (steps, reasons, messages) are already in the
 * user's language and are not repeated here.
 */
import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import common from './common'
import onboarding from './onboarding'
import app from './app'
import settings from './settings'
import extra from './extra'

type Section = { en: Record<string, string>; ar: Record<string, string> }
const SECTIONS: Record<string, Section> = { common, onboarding, app, settings, extra }
// Flat keys, "section.key" (keys may contain dots themselves, e.g. "common.behaviour.movement").
const pick = (lang: 'en' | 'ar') =>
  Object.fromEntries(
    Object.entries(SECTIONS).flatMap(([s, v]) => Object.entries(v[lang]).map(([k, text]) => [`${s}.${k}`, text])),
  )

void i18n.use(initReactI18next).init({
  resources: { en: { translation: pick('en') }, ar: { translation: pick('ar') } },
  lng: 'en',
  fallbackLng: 'en',
  keySeparator: false,
  nsSeparator: false,
  interpolation: { escapeValue: false }, // React already escapes
})

export default i18n

/** For labels used outside components (maps with getters, error texts): read at render time. */
export const tr = (key: string, vars?: Record<string, unknown>): string =>
  (i18n as unknown as { t: (k: string, o?: Record<string, unknown>) => string }).t(key, vars)

/** A map whose values are looked up on every read, so they follow the current language. */
export function labels<K extends string>(prefix: string, keys: readonly K[]): Record<K, string> {
  const map = {} as Record<K, string>
  for (const k of keys) Object.defineProperty(map, k, { get: () => tr(`${prefix}.${k}`), enumerable: true })
  return map
}

/** Chip options whose labels follow the current language: `${prefix}.${value}`. */
export function options<V extends string | number>(prefix: string, values: readonly V[]): { value: V; label: string }[] {
  return values.map((value) => ({
    value,
    get label() {
      return tr(`${prefix}.${value}`)
    },
  }))
}
