import React, { useState } from 'react'
import { ScreenProps, OnboardingDraft, ScheduleType, Sex, Weekday } from '../types'
import { OnboardingLayout, ChipGroup } from '../components/OnboardingLayout'
import { api } from '../api/client'
import { applySuggestions, bodyValid, stepOf } from '../lib/onboarding'

const SEX_OPTIONS: { value: Sex; label: string }[] = [
  { value: 'female', label: 'Female' },
  { value: 'male', label: 'Male' },
  { value: 'prefer_not_to_say', label: 'Prefer not to say' },
]

const SCHEDULE_OPTIONS: { value: ScheduleType; label: string }[] = [
  { value: 'office', label: 'Office hours' },
  { value: 'shift', label: 'Shifts' },
  { value: 'outdoor_manual', label: 'Outdoor / manual work' },
  { value: 'home_caregiver', label: 'At home / caring for family' },
  { value: 'student', label: 'Student' },
  { value: 'other', label: 'Something else' },
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

const inputClass =
  'mt-2 w-full min-h-[48px] box-border rounded-xl border border-[#C5D0C7] bg-white px-3 text-[15px] font-normal text-[#1B2A22]'
const why = 'block mt-0.5 text-[12px] font-normal text-[#5A6A60]'

const numOrNull = (v: string) => (v === '' ? null : Number(v))
const MAX_OWN_WORDS = 1000

/** Step 1: optional own-words box (suggests answers), name, the required basics (CLAUDE.md §4.1), shifts, optional body (§4.2). */
export const BasicsScreen: React.FC<ScreenProps> = ({ state, setState, onNavigate, showToast }) => {
  const p = state.profile
  const update = (patch: Partial<OnboardingDraft>) =>
    setState((prev) => ({ ...prev, profile: { ...prev.profile, ...patch } }))

  const [ownWords, setOwnWords] = useState('')
  const [suggesting, setSuggesting] = useState(false)
  const [suggestNote, setSuggestNote] = useState<string | null>(null)

  // Optional: suggested answers from a few sentences. They only pre-fill; the person checks every screen, and the
  // health check is never pre-filled. On 429 or any error we just carry on with the normal questions.
  const suggest = async () => {
    if (!ownWords.trim()) return
    setSuggesting(true)
    setSuggestNote(null)
    try {
      const out = await api.suggest(ownWords.trim(), state.language)
      if (out.red_flag) {
        setState((prev) => ({ ...prev, careReason: 'onboarding_text', careMessage: out.message ?? null }))
        return onNavigate('care')
      }
      if (out.suggestions) {
        const s = out.suggestions
        setState((prev) => ({ ...prev, profile: applySuggestions(prev.profile, s) }))
        setSuggestNote('We filled in what you mentioned. Please check each answer as you go.')
      }
    } catch {
      setSuggestNote("We couldn't fill this in right now. Just answer the questions below.")
    } finally {
      setSuggesting(false)
    }
  }

  const ageValid = p.ageYears !== null && p.ageYears >= 18 && p.ageYears <= 100
  const shiftsOk = p.scheduleType !== 'shift' || p.shiftDays.length > 0

  const handleContinue = () => {
    if (!ageValid) return showToast('Rebound is for adults aged 18 to 100.')
    if (!p.sex || !p.scheduleType) return showToast('Please answer each question to continue.')
    if (!shiftsOk) return showToast('Pick the days your shifts start on.')
    if (!bodyValid(p)) return showToast('Height should be 100–250 cm and weight 30–300 kg, or leave them empty.')
    // Pregnancy is only asked for women; drop an earlier answer if sex changed.
    if (p.sex !== 'female') update({ pregnant: null, womenOnlySpaces: false })
    onNavigate('onboarding-goals')
  }

  return (
    <OnboardingLayout
      {...stepOf(p, 'onboarding-basics')}
      title="A bit about you"
      subtitle="We use this to set a safe start and pick good times for your steps."
      onBack={() => onNavigate('welcome')}
      onContinue={handleContinue}
    >
      <div className="p-3 rounded-[16px] bg-white/70 border border-[#DCE3DA] flex flex-col gap-2">
        <label className="block text-[15px] font-semibold">
          Tell us about your week in your own words <span className="font-normal text-[#5A6A60]">(optional)</span>
          <span className={why}>
            We'll suggest answers for the next questions. You check each one. Your words aren't saved.
          </span>
          <textarea
            rows={3}
            maxLength={MAX_OWN_WORDS}
            value={ownWords}
            onChange={(e) => setOwnWords(e.target.value)}
            placeholder="e.g. I work night shifts, have two kids and want to sleep better."
            className="mt-2 w-full box-border rounded-xl border border-[#C5D0C7] bg-white p-3 text-[15px] font-normal text-[#1B2A22] resize-none font-sans"
          />
        </label>
        <div className="flex items-center justify-between gap-2">
          <span className="text-[11px] text-[#5A6A60]">
            {ownWords.length} / {MAX_OWN_WORDS}
          </span>
          <button
            type="button"
            onClick={suggest}
            disabled={suggesting || !ownWords.trim()}
            className="min-h-[40px] px-4 rounded-[12px] bg-[#3E6B53] text-white text-[14px] font-semibold border-0 cursor-pointer disabled:opacity-50"
          >
            {suggesting ? 'Reading…' : 'Fill in for me'}
          </button>
        </div>
        {suggestNote && <p className="m-0 text-[12px] text-[#3E6B53]">{suggestNote}</p>}
      </div>

      <label className="block text-[15px] font-semibold">
        What should we call you? <span className="font-normal text-[#5A6A60]">(optional)</span>
        <span className={why}>Only for greeting you. Saved with your account; never sent to the AI.</span>
        <input
          type="text"
          maxLength={40}
          autoComplete="given-name"
          value={state.displayName}
          onChange={(e) => setState((prev) => ({ ...prev, displayName: e.target.value }))}
          placeholder="First name"
          className={inputClass}
        />
      </label>

      <label className="block text-[15px] font-semibold">
        Your age
        <input
          type="number"
          inputMode="numeric"
          min={18}
          max={100}
          value={p.ageYears ?? ''}
          onChange={(e) => update({ ageYears: numOrNull(e.target.value) })}
          placeholder="e.g. 34"
          className={inputClass}
        />
      </label>
      {ageValid && p.ageYears! >= 65 && (
        <p className="m-0 -mt-2 text-[12px] text-[#3E6B53]">We'll start with balance-friendly steps.</p>
      )}

      <ChipGroup<Sex>
        label="Sex"
        hint="Decides which health questions we ask."
        options={SEX_OPTIONS}
        isSelected={(v) => p.sex === v}
        onToggle={(v) => update({ sex: v })}
      />

      <ChipGroup<ScheduleType>
        label="What do your days look like?"
        options={SCHEDULE_OPTIONS}
        isSelected={(v) => p.scheduleType === v}
        onToggle={(v) => update({ scheduleType: v, caregiver: v === 'home_caregiver' || p.caregiver })}
        columns={2}
      />

      {p.scheduleType === 'shift' && (
        <div className="p-3 rounded-[16px] bg-white/70 border border-[#DCE3DA] flex flex-col gap-3">
          <ChipGroup<Weekday>
            label="Which days do your shifts start?"
            hint="So we never nudge you at work. You can change this later."
            options={WEEKDAYS}
            isSelected={(v) => p.shiftDays.includes(v)}
            onToggle={(v) =>
              update({ shiftDays: p.shiftDays.includes(v) ? p.shiftDays.filter((d) => d !== v) : [...p.shiftDays, v] })
            }
            columns={4}
          />
          <div className="grid grid-cols-2 gap-3">
            <label className="block text-[14px] font-semibold">
              Shift starts
              <input type="time" value={p.shiftStart} onChange={(e) => update({ shiftStart: e.target.value })} className={inputClass} />
            </label>
            <label className="block text-[14px] font-semibold">
              Shift ends
              <input type="time" value={p.shiftEnd} onChange={(e) => update({ shiftEnd: e.target.value })} className={inputClass} />
            </label>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <label className="block text-[15px] font-semibold">
          Usually wake up
          <input type="time" value={p.usualWakeTime} onChange={(e) => update({ usualWakeTime: e.target.value })} className={inputClass} />
        </label>
        <label className="block text-[15px] font-semibold">
          Usually sleep
          <input type="time" value={p.usualSleepTime} onChange={(e) => update({ usualSleepTime: e.target.value })} className={inputClass} />
        </label>
      </div>

      <fieldset className="m-0 p-0 border-0">
        <legend className="p-0 text-[15px] font-semibold">
          Height and weight <span className="font-normal text-[#5A6A60]">(optional)</span>
        </legend>
        <span className={why}>
          Used only to set a safe starting level. We never show them back to you as a number or a target.
        </span>
        <div className="grid grid-cols-2 gap-3">
          <label className="block text-[14px] font-semibold">
            Height (cm)
            <input
              type="number"
              inputMode="numeric"
              min={100}
              max={250}
              value={p.heightCm ?? ''}
              onChange={(e) => update({ heightCm: numOrNull(e.target.value) })}
              className={inputClass}
            />
          </label>
          <label className="block text-[14px] font-semibold">
            Weight (kg)
            <input
              type="number"
              inputMode="decimal"
              min={30}
              max={300}
              value={p.weightKg ?? ''}
              onChange={(e) => update({ weightKg: numOrNull(e.target.value) })}
              className={inputClass}
            />
          </label>
        </div>
      </fieldset>
    </OnboardingLayout>
  )
}
