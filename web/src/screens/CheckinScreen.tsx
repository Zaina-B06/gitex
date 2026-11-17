import React, { useState } from 'react'
import { ScreenProps } from '../types'
import { api, ApiError, Barrier, errorText, PlanOut, StateOut } from '../api/client'
import { ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { HabitRings } from '../components/HabitRings'
import { useAsync } from '../lib/useAsync'

// Labels for the backend's Barrier enum (CLAUDE.md §6.2 plus the smoking/food extensions).
const BARRIERS: { value: Barrier; label: string; smokersOnly?: boolean }[] = [
  { value: 'time', label: 'No time' },
  { value: 'energy_fatigue', label: 'Tired' },
  { value: 'illness_pain', label: 'Sick or in pain' },
  { value: 'stress', label: 'Stressed' },
  { value: 'schedule_change', label: 'Schedule changed' },
  { value: 'environment', label: 'Too hot / no space' },
  { value: 'no_healthy_food_nearby', label: 'No healthy food nearby' },
  { value: 'craving', label: 'Craving a cigarette', smokersOnly: true },
  { value: 'others_smoking', label: 'People smoking around me', smokersOnly: true },
  { value: 'social_family', label: 'Family things' },
  { value: 'forgot', label: 'Forgot' },
  { value: 'low_motivation', label: 'Not feeling it' },
  { value: 'other', label: 'Something else' },
]

/** Blame-free check-in: POST /users/{id}/checkin. Red flag → Care; otherwise → Easier plan. */
export const CheckinScreen: React.FC<ScreenProps> = ({ state, setState, onNavigate, showToast }) => {
  const session = state.session!
  const [selected, setSelected] = useState<Barrier[]>([])
  const [note, setNote] = useState('')
  const [sending, setSending] = useState(false)
  const ctx = useAsync(
    () => Promise.all([api.state(session), api.plan(session)]) as Promise<[StateOut, PlanOut]>,
    [session],
  )

  const smokes = state.profile.smokes || !!ctx.data?.[1].behaviours.includes('smoking')
  const options = BARRIERS.filter((b) => !b.smokersOnly || smokes)

  const toggle = (b: Barrier) => setSelected((s) => (s.includes(b) ? s.filter((x) => x !== b) : [...s, b]))

  const submit = async () => {
    if (selected.length === 0 && !note.trim()) {
      showToast('Pick what got in the way, or write a few words.')
      return
    }
    setSending(true)
    try {
      const out = await api.checkin(session, selected, note)
      if (out.red_flag) {
        setState((prev) => ({ ...prev, careReason: 'red_flag', lastCheckin: out }))
        onNavigate('care')
      } else {
        setState((prev) => ({ ...prev, lastCheckin: out }))
        onNavigate('easier-plan')
      }
    } catch (e) {
      showToast(
        e instanceof ApiError && e.status === 409
          ? "You've already checked in today. We'll ask again tomorrow."
          : errorText(e),
      )
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="relative isolate w-full h-full overflow-y-auto overflow-x-hidden overscroll-contain box-border bg-[#EEF1EA] font-sans text-[#1B2A22] flex flex-col p-6">
      <ArabicCalligraphyRing width={460} height={460} style={{ right: -250, top: -170, opacity: 0.12 }} />
      <ArabicCalligraphyRing width={300} height={300} style={{ left: -190, bottom: 120, opacity: 0.08 }} />

      <div className="flex justify-end">
        <button
          type="button"
          onClick={() => onNavigate('today')}
          aria-label="Close"
          className="min-w-[44px] min-h-[44px] flex items-center justify-end bg-transparent border-0 p-0 cursor-pointer text-[#1B2A22]"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <path d="M6 6l12 12M18 6L6 18" />
          </svg>
        </button>
      </div>

      <h1 className="mt-1 mb-1.5 font-display tracking-tight text-[27px] leading-tight font-semibold">
        Rough few days?
        <br />
        What got in the way?
      </h1>
      <p className="m-0 text-[14px] leading-relaxed text-[#3F4F45]">
        Weeks like this happen to everyone. Tell us and we'll make things easier.
      </p>

      {ctx.data && (
        <div className="-mx-6">
          <HabitRings strength={ctx.data[0].habit_strength} />
        </div>
      )}

      <div role="group" aria-label="What got in the way" className="mt-3 grid grid-cols-2 gap-2">
        {options.map((b) => {
          const on = selected.includes(b.value)
          return (
            <button
              key={b.value}
              type="button"
              aria-pressed={on}
              onClick={() => toggle(b.value)}
              className={`min-h-[44px] rounded-[14px] px-2 text-[14px] cursor-pointer transition-all ${
                on ? 'border-2 border-[#3E6B53] bg-[#DDE9E0] font-semibold text-[#2C5140]' : 'border border-[#C5D0C7] bg-white'
              }`}
            >
              {b.label}
            </button>
          )
        })}
      </div>

      <label htmlFor="checkin-text" className="mt-3 text-[14px] font-medium">
        Or tell us in your own words (optional)
      </label>
      <textarea
        id="checkin-text"
        rows={2}
        maxLength={500}
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="e.g. night shifts this week"
        className="mt-1.5 box-border rounded-xl border border-[#C5D0C7] p-3 text-[14px] resize-none bg-white font-sans"
      />

      <div className="mt-auto pt-3 flex flex-col gap-1">
        <button
          type="button"
          onClick={submit}
          disabled={sending}
          className="min-h-[52px] rounded-[14px] bg-[#3E6B53] hover:bg-[#2C5140] disabled:opacity-60 text-white text-[16px] font-semibold border-0 cursor-pointer shadow-button"
        >
          {sending ? 'Making it easier…' : 'Make it easier'}
        </button>
        <button
          type="button"
          onClick={() => onNavigate('today')}
          className="min-h-[44px] bg-transparent border-0 text-[14px] font-medium text-[#3E6B53] cursor-pointer"
        >
          Not now
        </button>
      </div>
    </div>
  )
}
