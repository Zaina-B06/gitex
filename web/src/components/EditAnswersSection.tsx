import React, { useState } from 'react'
import type { ExportOut, SettingsIn } from '../api/client'
import type { Household, SettingPref, Weekday } from '../types'
import { ChipGroup } from './OnboardingLayout'

const HOUSEHOLD: { value: Household; label: string }[] = [
  { value: 'alone', label: 'Alone' },
  { value: 'family', label: 'With family' },
  { value: 'children', label: 'With children' },
  { value: 'older_relatives', label: 'With older relatives' },
]
const SETTINGS: { value: SettingPref; label: string }[] = [
  { value: 'indoor', label: 'Indoors' },
  { value: 'outdoor', label: 'Outdoors' },
  { value: 'either', label: 'Either' },
]
const WEEKDAYS: { value: Weekday; label: string }[] = [
  { value: 'sun', label: 'Sun' },
  { value: 'mon', label: 'Mon' },
  { value: 'tue', label: 'Tue' },
  { value: 'wed', label: 'Wed' },
  { value: 'thu', label: 'Thu' },
  { value: 'fri', label: 'Fri' },
  { value: 'sat', label: 'Sat' },
]

const toggleRow =
  'px-4 py-3 flex items-center justify-between gap-3 border-b border-[#E6EBE4] cursor-pointer hover:bg-[#DDE9E0]/40'
const check = 'w-[22px] h-[22px] flex-none accent-[#3E6B53] cursor-pointer'
const time = 'min-h-[40px] rounded-lg border border-[#C5D0C7] px-2 text-[14px] bg-white'

/**
 * "Edit my answers": the sign-up answers the API lets you change later (PATCH /settings: preferences, shifts).
 * Each change saves straight away. Age, sex and the health check are fixed at sign-up.
 */
export const EditAnswersSection: React.FC<{
  exp: ExportOut
  saving: boolean
  save: (body: SettingsIn, done: string) => Promise<void>
}> = ({ exp, saving, save }) => {
  const prefs = exp.profile.preferences!
  const basics = exp.profile.basics
  const shift = basics.shifts?.[0]
  const [days, setDays] = useState<Weekday[]>((shift?.days as Weekday[]) ?? [])
  const [start, setStart] = useState(String(shift?.start ?? '07:00').slice(0, 5))
  const [end, setEnd] = useState(String(shift?.end ?? '15:00').slice(0, 5))
  const [iftar, setIftar] = useState(prefs.iftar_time ? String(prefs.iftar_time).slice(0, 5) : '')

  const pref = (p: Record<string, unknown>, done = 'Saved.') => save({ preferences: p }, done)

  return (
    <section aria-labelledby="s-answers" className="bg-white/90 rounded-[20px] flex flex-col shadow-card overflow-hidden">
      <h2 id="s-answers" className="m-0 p-3 px-4 pb-1 text-[12px] font-semibold text-[#5A6A60]">
        Edit my answers
      </h2>
      <p className="m-0 px-4 pb-2 text-[12px] leading-snug text-[#5A6A60]">Changes save straight away and update your plan.</p>

      <div className="px-4 py-3 border-b border-[#E6EBE4]">
        <ChipGroup<SettingPref>
          label="Where do you prefer to be active?"
          options={SETTINGS}
          isSelected={(v) => prefs.setting === v}
          onToggle={(v) => !saving && pref({ setting: v })}
          columns={3}
        />
      </div>

      <div className="px-4 py-3 border-b border-[#E6EBE4]">
        <ChipGroup<Household>
          label="Who do you live with?"
          options={HOUSEHOLD}
          isSelected={(v) => prefs.household === v}
          onToggle={(v) => !saving && pref({ household: prefs.household === v ? null : v })}
          columns={2}
        />
      </div>

      <label className={toggleRow}>
        <span className="text-[15px]">I care for someone at home</span>
        <input type="checkbox" className={check} checked={prefs.caregiver} disabled={saving} onChange={(e) => pref({ caregiver: e.target.checked })} />
      </label>

      {basics.sex === 'female' && (
        <label className={toggleRow}>
          <span className="text-[15px]">I prefer women-only spaces</span>
          <input
            type="checkbox"
            className={check}
            checked={prefs.space_preference === 'women_only_spaces'}
            disabled={saving}
            onChange={(e) => pref({ space_preference: e.target.checked ? 'women_only_spaces' : 'any' })}
          />
        </label>
      )}

      <label className={toggleRow}>
        <span className="text-[15px]">I fast in Ramadan</span>
        <input
          type="checkbox"
          className={check}
          checked={prefs.fasting_ramadan}
          disabled={saving}
          onChange={(e) => pref({ fasting_ramadan: e.target.checked, ...(e.target.checked ? {} : { family_fasting: false }) })}
        />
      </label>
      {prefs.fasting_ramadan && (
        <>
          <label className={toggleRow}>
            <span className="text-[15px]">My family fasts together</span>
            <input type="checkbox" className={check} checked={prefs.family_fasting} disabled={saving} onChange={(e) => pref({ family_fasting: e.target.checked })} />
          </label>
          <div className="px-4 py-3 flex items-center justify-between gap-3 border-b border-[#E6EBE4]">
            <span className="flex flex-col">
              <span className="text-[15px]">Iftar time</span>
              <span className="text-[12px] text-[#5A6A60]">Leave empty to use the local time automatically</span>
            </span>
            <input
              type="time"
              className={time}
              value={iftar}
              disabled={saving}
              onChange={(e) => setIftar(e.target.value)}
              onBlur={() => pref({ iftar_time: iftar || null }, iftar ? 'Iftar time saved.' : 'Using the local iftar time.')}
            />
          </div>
        </>
      )}

      {basics.schedule_type === 'shift' && (
        <div className="px-4 py-3 flex flex-col gap-2 border-b border-[#E6EBE4]">
          <ChipGroup<Weekday>
            label="Shift days"
            hint="The days your shifts start. Steps move the day after you save."
            options={WEEKDAYS}
            isSelected={(v) => days.includes(v)}
            onToggle={(v) => setDays((d) => (d.includes(v) ? d.filter((x) => x !== v) : [...d, v]))}
            columns={4}
          />
          <div className="flex items-center gap-2 text-[14px]">
            <input type="time" className={time} value={start} onChange={(e) => setStart(e.target.value)} aria-label="Shift starts" />
            <span>to</span>
            <input type="time" className={time} value={end} onChange={(e) => setEnd(e.target.value)} aria-label="Shift ends" />
          </div>
          <button
            type="button"
            disabled={saving}
            onClick={() => save({ shifts: days.length ? [{ days, start, end }] : [] }, 'Shifts saved.')}
            className="self-start min-h-[40px] px-4 rounded-[12px] bg-[#3E6B53] text-white text-[14px] font-semibold border-0 cursor-pointer disabled:opacity-60"
          >
            Save shifts
          </button>
        </div>
      )}

      <label className={toggleRow + ' border-b-0'}>
        <span className="flex flex-col gap-0.5">
          <span className="text-[15px]">Read steps aloud</span>
          <span className="text-[12px] text-[#5A6A60]">Adds a speaker button to each step</span>
        </span>
        <input type="checkbox" className={check} checked={prefs.read_aloud} disabled={saving} onChange={(e) => pref({ read_aloud: e.target.checked })} />
      </label>
    </section>
  )
}
