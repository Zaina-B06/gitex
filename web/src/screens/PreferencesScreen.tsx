import React, { useState } from 'react'
import { ScreenProps, OnboardingDraft, SettingPref, PastHelper, Household, ReadingLevel } from '../types'
import { api, errorText, FollowUp } from '../api/client'
import { OnboardingLayout, ChipGroup } from '../components/OnboardingLayout'
import { asksBaseline, buildOnboardPayload, missingStep, showFollowUp, stepOf } from '../lib/onboarding'
import { useAsync } from '../lib/useAsync'

const HELPERS: { value: PastHelper; label: string }[] = [
  { value: 'small_steps', label: 'Small steps' },
  { value: 'reminders', label: 'Reminders' },
  { value: 'buddy', label: 'A buddy' },
  { value: 'tracking', label: 'Tracking' },
  { value: 'rewards', label: 'Rewards' },
  { value: 'routine_anchor', label: 'Tying it to a routine' },
  { value: 'other', label: 'Something else' },
]

const SETTINGS: { value: SettingPref; label: string }[] = [
  { value: 'indoor', label: 'Indoors' },
  { value: 'outdoor', label: 'Outdoors' },
  { value: 'either', label: 'Either' },
]

const HOUSEHOLD: { value: Household; label: string }[] = [
  { value: 'alone', label: 'I live alone' },
  { value: 'family', label: 'With family' },
  { value: 'children', label: 'With children' },
  { value: 'older_relatives', label: 'With older relatives' },
]

const YES_NO = [
  { value: 'yes', label: 'Yes' },
  { value: 'no', label: 'No' },
]

const MAX_REASON = 200

/** Last step (all optional), with the follow-up questions that apply. "Build my plan" sends everything to POST /users. */
export const PreferencesScreen: React.FC<ScreenProps> = ({ state, setState, onNavigate, showToast }) => {
  const p = state.profile
  const [submitting, setSubmitting] = useState(false)
  const content = useAsync(() => api.onboardingContent(state.language, p.readingLevel), [state.language, p.readingLevel])
  const update = (patch: Partial<OnboardingDraft>) =>
    setState((prev) => ({ ...prev, profile: { ...prev.profile, ...patch } }))

  const toggleHelper = (h: PastHelper) =>
    update({ pastHelpers: p.pastHelpers.includes(h) ? p.pastHelpers.filter((x) => x !== h) : [...p.pastHelpers, h] })

  const submit = async () => {
    const missing = missingStep(p)
    if (missing) return showToast(`Please finish "${missing}" first.`)
    setSubmitting(true)
    try {
      const out = await api.onboard(buildOnboardPayload(state))
      setState((prev) => ({
        ...prev,
        session: { userId: out.user_id, token: out.token },
        plan: out.plan_summary,
        justSignedUp: true,
        careReason: out.red_flag ? 'red_flag' : prev.careReason,
      }))
      // Something in the free text needs care first (CLAUDE.md §6.4).
      onNavigate(out.red_flag ? 'care' : 'plan-ready')
    } catch (e) {
      showToast(errorText(e))
    } finally {
      setSubmitting(false)
    }
  }

  // Follow-ups answered on this screen (shifts and the smoking goal are asked on steps 1 and 2 by the same rules).
  const followUps = ((content.data?.follow_ups ?? []) as unknown as FollowUp[]).filter(
    (q) => ['anchor', 'iftar_time', 'family_fasting', 'caregiver', 'quiet_hours'].includes(q.id) && showFollowUp(q, p),
  )
  const examples = content.data?.reading_level_examples ?? {}
  const levels: { value: ReadingLevel; label: string }[] = [
    { value: 'standard', label: 'Standard' },
    { value: 'simple', label: 'Simpler words' },
  ]

  return (
    <OnboardingLayout
      {...stepOf(p, 'onboarding-preferences')}
      title="What helps you"
      subtitle="All optional. It helps us pick the kind of step that suits you."
      onBack={() => onNavigate(asksBaseline(p) ? 'onboarding-baseline' : 'onboarding-health')}
      onContinue={submit}
      continueLabel={submitting ? 'Building your plan…' : 'Build my plan'}
      continueDisabled={submitting}
    >
      <fieldset className="m-0 p-0 border-0">
        <legend className="p-0 text-[15px] font-semibold">How should we word your steps?</legend>
        <div className="mt-2 grid grid-cols-2 gap-2">
          {levels.map((l) => {
            const on = p.readingLevel === l.value
            return (
              <button
                key={l.value}
                type="button"
                aria-pressed={on}
                onClick={() => update({ readingLevel: l.value })}
                className={`p-3 rounded-[14px] text-start cursor-pointer flex flex-col gap-1 ${
                  on ? 'border-2 border-[#3E6B53] bg-[#DDE9E0]' : 'border border-[#C5D0C7] bg-white'
                }`}
              >
                <span className={`text-[14px] ${on ? 'font-semibold text-[#2C5140]' : ''}`}>{l.label}</span>
                {examples[l.value] && <span className="text-[12px] leading-snug text-[#3F4F45]">"{examples[l.value]}"</span>}
              </button>
            )
          })}
        </div>
      </fieldset>

      <ChipGroup<PastHelper>
        label="What helped when you tried before?"
        hint="Pick any."
        options={HELPERS}
        isSelected={(v) => p.pastHelpers.includes(v)}
        onToggle={toggleHelper}
      />

      <label className="block text-[15px] font-semibold">
        Why does this matter to you?
        <span className="block mt-0.5 text-[12px] font-normal text-[#5A6A60]">We'll remind you of this on tough days.</span>
        <textarea
          rows={2}
          maxLength={MAX_REASON}
          value={p.motivationReason}
          onChange={(e) => update({ motivationReason: e.target.value })}
          placeholder="e.g. to keep up with my kids"
          className="mt-2 w-full box-border rounded-xl border border-[#C5D0C7] bg-white p-3 text-[15px] font-normal text-[#1B2A22] resize-none font-sans"
        />
        <span className="block text-end text-[11px] font-normal text-[#5A6A60]">
          {p.motivationReason.length} / {MAX_REASON}
        </span>
      </label>

      <ChipGroup<Household>
        label="Who do you live with?"
        hint={
          p.scheduleType === 'home_caregiver'
            ? 'You care for family at home, so we can suggest steps you can do together.'
            : 'Unlocks steps you can do with family.'
        }
        options={HOUSEHOLD}
        isSelected={(v) => p.household === v}
        onToggle={(v) => update({ household: p.household === v ? null : v })}
        columns={2}
      />

      <ChipGroup<SettingPref>
        label="Where do you prefer to be active?"
        options={SETTINGS}
        isSelected={(v) => p.setting === v}
        onToggle={(v) => update({ setting: v })}
        columns={3}
      />

      {p.sex === 'female' && (
        <label className="flex gap-2.5 items-start text-[14px] leading-snug cursor-pointer">
          <input
            type="checkbox"
            checked={p.womenOnlySpaces}
            onChange={(e) => update({ womenOnlySpaces: e.target.checked })}
            className="mt-0.5 w-5 h-5 flex-none accent-[#3E6B53] cursor-pointer"
          />
          I prefer women-only spaces (for community events and outdoor steps)
        </label>
      )}

      <ChipGroup
        label="Do you fast in Ramadan?"
        hint="Steps during Ramadan will be fasting-friendly."
        options={YES_NO}
        isSelected={(v) => (v === 'yes' ? p.fastingRamadan === true : p.fastingRamadan === false)}
        onToggle={(v) => update({ fastingRamadan: v === 'yes', familyFasting: v === 'yes' ? p.familyFasting : false })}
        columns={2}
      />

      {followUps.map((q) => (
        <FollowUpField key={q.id} q={q} p={p} update={update} />
      ))}
    </OnboardingLayout>
  )
}

const fieldClass =
  'mt-2 w-full min-h-[48px] box-border rounded-xl border border-[#C5D0C7] bg-white px-3 text-[15px] font-normal text-[#1B2A22]'

/** One follow-up question; its wording comes from the server (EN/AR, standard or simple). */
const FollowUpField: React.FC<{
  q: FollowUp
  p: OnboardingDraft
  update: (patch: Partial<OnboardingDraft>) => void
}> = ({ q, p, update }) => {
  const check = (checked: boolean, onChange: (v: boolean) => void) => (
    <label className="flex gap-2.5 items-start text-[14px] leading-snug cursor-pointer">
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        className="mt-0.5 w-5 h-5 flex-none accent-[#3E6B53] cursor-pointer"
      />
      {q.text}
    </label>
  )
  if (q.id === 'family_fasting') return check(p.familyFasting, (v) => update({ familyFasting: v }))
  if (q.id === 'caregiver') return check(p.caregiver, (v) => update({ caregiver: v }))
  if (q.id === 'anchor')
    return (
      <label className="block text-[15px] font-semibold">
        {q.text}
        <input
          type="text"
          maxLength={40}
          value={p.anchor}
          onChange={(e) => update({ anchor: e.target.value })}
          placeholder="e.g. after maghrib"
          className={fieldClass}
        />
      </label>
    )
  if (q.id === 'iftar_time')
    return (
      <label className="block text-[15px] font-semibold">
        {q.text}
        <input type="time" value={p.iftarTime} onChange={(e) => update({ iftarTime: e.target.value })} className={fieldClass} />
      </label>
    )
  // quiet_hours
  return (
    <fieldset className="m-0 p-0 border-0">
      <legend className="p-0 text-[15px] font-semibold">{q.text}</legend>
      <div className="grid grid-cols-2 gap-3">
        <label className="block text-[14px] font-semibold">
          From
          <input type="time" value={p.quietStart} onChange={(e) => update({ quietStart: e.target.value })} className={fieldClass} />
        </label>
        <label className="block text-[14px] font-semibold">
          Until
          <input type="time" value={p.quietEnd} onChange={(e) => update({ quietEnd: e.target.value })} className={fieldClass} />
        </label>
      </div>
    </fieldset>
  )
}
