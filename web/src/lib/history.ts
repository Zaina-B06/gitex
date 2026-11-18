import type { Barrier, ExportOut } from '../api/client'
import type { components } from '../api/schema'

type DayLog = components['schemas']['DayLog']

export const BARRIER_LABEL: Record<Barrier, string> = {
  time: 'No time',
  energy_fatigue: 'Tired',
  illness_pain: 'Sick or in pain',
  stress: 'Stressed',
  schedule_change: 'Schedule changed',
  environment: 'Too hot / no space',
  no_healthy_food_nearby: 'No healthy food nearby',
  craving: 'Craving a cigarette',
  others_smoking: 'People smoking around me',
  social_family: 'Family things',
  forgot: 'Forgot',
  low_motivation: 'Not feeling it',
  other: 'Something else',
}

export const OUTCOME_LABEL: Record<string, string> = {
  completed: 'Done',
  partial: 'Did a smaller version',
  skipped: 'Skipped',
  no_response: 'No answer',
  paused: 'Paused',
  illness: 'Resting (unwell)',
}

export interface DayRecord {
  day: number
  date: Date
  logs: DayLog[]
  checkins: Barrier[][]
}

/** "YYYY-MM-DD" → local Date at midnight (no time-zone shift). */
export function parseDate(iso: string): Date {
  const [y, m, d] = iso.slice(0, 10).split('-').map(Number)
  return new Date(y, m - 1, d)
}

export const dateKey = (d: Date) =>
  `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`

export const addDays = (d: Date, n: number) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + n)

/** Engine day N is the user's sign-up date + (N − 1) days (same rule as the API's local_date_of). */
export function onboardDate(exp: ExportOut): Date {
  return parseDate(String(exp.account.onboard_date ?? dateKey(new Date())))
}

/** Every engine day so far, keyed by local date, with its outcomes and check-ins. */
export function buildDays(exp: ExportOut): Map<string, DayRecord> {
  const start = onboardDate(exp)
  const days = new Map<string, DayRecord>()
  const get = (day: number) => {
    const date = addDays(start, day - 1)
    const key = dateKey(date)
    if (!days.has(key)) days.set(key, { day, date, logs: [], checkins: [] })
    return days.get(key)!
  }
  for (let d = 1; d <= exp.state.day; d++) get(d)
  for (const log of exp.state.history ?? []) if (log.day >= 1) get(log.day).logs.push(log)
  for (const ev of exp.events) {
    if (ev.type === 'checkin' && ev.day >= 1) {
      const barriers = (ev.payload?.barriers as Barrier[] | undefined) ?? []
      get(ev.day).checkins.push(barriers)
    }
  }
  return days
}
