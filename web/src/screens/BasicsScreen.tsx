import React, { useState } from 'react'
import { ScreenProps, OnboardingDraft, ScheduleType, Sex, Weekday } from '../types'
import { OnboardingLayout, ChipGroup } from '../components/OnboardingLayout'
import { api } from '../api/client'
import { applySuggestions, bodyValid, stepOf } from '../lib/onboarding'
import { options, tr } from '../i18n'

const SEX_OPTIONS = options<Sex>('onboarding.sex', ['female', 'male', 'prefer_not_to_say'])
const SCHEDULE_OPTIONS = options<ScheduleType>('onboarding.schedule', [
  'office', 'shift', 'outdoor_manual', 'home_caregiver', 'student', 'other',
])
export const WEEKDAYS = options<Weekday>('onboarding.day', ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'])

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
        setSuggestNote(tr('onboarding.basics.filled'))
      }
    } catch {
      setSuggestNote(tr('onboarding.basics.couldNotFill'))
    } finally {
      setSuggesting(false)
    }
  }

  const ageValid = p.ageYears !== null && p.ageYears >= 18 && p.ageYears <= 100
  const shiftsOk = p.scheduleType !== 'shift' || p.shiftDays.length > 0

  const handleContinue = () => {
    if (!ageValid) return showToast(tr('onboarding.basics.toastAge'))
    if (!p.sex || !p.scheduleType) return showToast(tr('onboarding.basics.toastAnswer'))
    if (!shiftsOk) return showToast(tr('onboarding.basics.toastShifts'))
    if (!bodyValid(p)) return showToast(tr('onboarding.basics.toastBody'))
    // Pregnancy is only asked for women; drop an earlier answer if sex changed.
    if (p.sex !== 'female') update({ pregnant: null, womenOnlySpaces: false })
    onNavigate('onboarding-goals')
  }

  return (
    <OnboardingLayout
      {...stepOf(p, 'onboarding-basics')}
      title={tr('onboarding.basics.title')}
      subtitle={tr('onboarding.basics.subtitle')}
      onBack={() => onNavigate('welcome')}
      onContinue={handleContinue}
    >
      <div className="p-3 rounded-[16px] bg-white/70 border border-[#DCE3DA] flex flex-col gap-2">
        <label className="block text-[15px] font-semibold">
          {tr('onboarding.basics.ownWords')} <span className="font-normal text-[#5A6A60]">{tr('common.optional')}</span>
          <span className={why}>{tr('onboarding.basics.ownWordsWhy')}</span>
          <textarea
            rows={3}
            maxLength={MAX_OWN_WORDS}
            value={ownWords}
            onChange={(e) => setOwnWords(e.target.value)}
            placeholder={tr('onboarding.basics.ownWordsPlaceholder')}
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
            {suggesting ? tr('onboarding.basics.reading') : tr('onboarding.basics.fillIn')}
          </button>
        </div>
        {suggestNote && <p className="m-0 text-[12px] text-[#3E6B53]">{suggestNote}</p>}
      </div>

      <label className="block text-[15px] font-semibold">
        {tr('onboarding.basics.name')} <span className="font-normal text-[#5A6A60]">{tr('common.optional')}</span>
        <span className={why}>{tr('onboarding.basics.nameWhy')}</span>
        <input
          type="text"
          maxLength={40}
          autoComplete="given-name"
          value={state.displayName}
          onChange={(e) => setState((prev) => ({ ...prev, displayName: e.target.value }))}
          placeholder={tr('onboarding.basics.namePlaceholder')}
          className={inputClass}
        />
      </label>

      <label className="block text-[15px] font-semibold">
        {tr('onboarding.basics.age')}
        <input
          type="number"
          inputMode="numeric"
          min={18}
          max={100}
          value={p.ageYears ?? ''}
          onChange={(e) => update({ ageYears: numOrNull(e.target.value) })}
          placeholder={tr('onboarding.basics.agePlaceholder')}
          className={inputClass}
        />
      </label>
      {ageValid && p.ageYears! >= 65 && (
        <p className="m-0 -mt-2 text-[12px] text-[#3E6B53]">{tr('onboarding.basics.senior')}</p>
      )}

      <ChipGroup<Sex>
        label={tr('onboarding.basics.sex')}
        hint={tr('onboarding.basics.sexHint')}
        options={SEX_OPTIONS}
        isSelected={(v) => p.sex === v}
        onToggle={(v) => update({ sex: v })}
      />

      <ChipGroup<ScheduleType>
        label={tr('onboarding.basics.days')}
        options={SCHEDULE_OPTIONS}
        isSelected={(v) => p.scheduleType === v}
        onToggle={(v) => update({ scheduleType: v, caregiver: v === 'home_caregiver' || p.caregiver })}
        columns={2}
      />

      {p.scheduleType === 'shift' && (
        <div className="p-3 rounded-[16px] bg-white/70 border border-[#DCE3DA] flex flex-col gap-3">
          <ChipGroup<Weekday>
            label={tr('onboarding.basics.shiftDays')}
            hint={tr('onboarding.basics.shiftDaysHint')}
            options={WEEKDAYS}
            isSelected={(v) => p.shiftDays.includes(v)}
            onToggle={(v) =>
              update({ shiftDays: p.shiftDays.includes(v) ? p.shiftDays.filter((d) => d !== v) : [...p.shiftDays, v] })
            }
            columns={4}
          />
          <div className="grid grid-cols-2 gap-3">
            <label className="block text-[14px] font-semibold">
              {tr('onboarding.basics.shiftStart')}
              <input type="time" value={p.shiftStart} onChange={(e) => update({ shiftStart: e.target.value })} className={inputClass} />
            </label>
            <label className="block text-[14px] font-semibold">
              {tr('onboarding.basics.shiftEnd')}
              <input type="time" value={p.shiftEnd} onChange={(e) => update({ shiftEnd: e.target.value })} className={inputClass} />
            </label>
          </div>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3">
        <label className="block text-[15px] font-semibold">
          {tr('onboarding.basics.wake')}
          <input type="time" value={p.usualWakeTime} onChange={(e) => update({ usualWakeTime: e.target.value })} className={inputClass} />
        </label>
        <label className="block text-[15px] font-semibold">
          {tr('onboarding.basics.sleep')}
          <input type="time" value={p.usualSleepTime} onChange={(e) => update({ usualSleepTime: e.target.value })} className={inputClass} />
        </label>
      </div>

      <fieldset className="m-0 p-0 border-0">
        <legend className="p-0 text-[15px] font-semibold">
          {tr('onboarding.basics.body')} <span className="font-normal text-[#5A6A60]">{tr('common.optional')}</span>
        </legend>
        <span className={why}>{tr('onboarding.basics.bodyWhy')}</span>
        <div className="grid grid-cols-2 gap-3">
          <label className="block text-[14px] font-semibold">
            {tr('onboarding.basics.height')}
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
            {tr('onboarding.basics.weight')}
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
