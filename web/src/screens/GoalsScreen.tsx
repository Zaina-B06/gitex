import React from 'react'
import { ScreenProps, OnboardingDraft } from '../types'
import type { Behaviour, Condition } from '../api/client'
import { OnboardingLayout, ChipGroup } from '../components/OnboardingLayout'
import { GOAL_OPTIONS } from '../lib/behaviour'
import { stepOf } from '../lib/onboarding'
import { options, tr } from '../i18n'

export const CONDITION_OPTIONS = options<Condition>('onboarding.condition', [
  'diabetes', 'high_blood_pressure', 'back_or_joint_pain', 'stress', 'recovering_from_illness_or_injury',
])

const SMOKES = 'smokes' as const

/** Step 2: goals (at least one) and anything the user is managing (optional, with consent). */
export const GoalsScreen: React.FC<ScreenProps> = ({ state, setState, onNavigate, showToast }) => {
  const p = state.profile
  const update = (patch: Partial<OnboardingDraft>) =>
    setState((prev) => ({ ...prev, profile: { ...prev.profile, ...patch } }))

  const toggle = <T,>(list: T[], v: T) => (list.includes(v) ? list.filter((x) => x !== v) : [...list, v])

  // "Smoke less" only appears for someone who smokes.
  const goalOptions = GOAL_OPTIONS.filter((g) => g.value !== 'smoking' || p.smokes)

  const toggleSmokes = () =>
    update({ smokes: !p.smokes, goals: p.smokes ? p.goals.filter((g) => g !== 'smoking') : p.goals })

  const handleContinue = () => {
    if (p.goals.length === 0) return showToast(tr('onboarding.goals.toastPick'))
    onNavigate('onboarding-health')
  }

  return (
    <OnboardingLayout
      {...stepOf(p, 'onboarding-goals')}
      title={tr('onboarding.goals.title')}
      subtitle={tr('onboarding.goals.subtitle')}
      onBack={() => onNavigate('onboarding-basics')}
      onContinue={handleContinue}
    >
      <ChipGroup<Condition | typeof SMOKES>
        label={tr('onboarding.goals.managing')}
        hint={tr('onboarding.goals.managingHint')}
        options={[...CONDITION_OPTIONS, { value: SMOKES, label: tr('onboarding.goals.smokes') }]}
        isSelected={(v) => (v === SMOKES ? p.smokes : p.conditions.includes(v))}
        onToggle={(v) => (v === SMOKES ? toggleSmokes() : update({ conditions: toggle(p.conditions, v) }))}
      />

      <label className="flex gap-2.5 items-start text-[13px] leading-snug text-[#3F4F45] cursor-pointer">
        <input
          type="checkbox"
          checked={p.consentConditions}
          onChange={(e) => update({ consentConditions: e.target.checked })}
          className="mt-0.5 w-5 h-5 flex-none accent-[#3E6B53] cursor-pointer"
        />
        {tr('onboarding.goals.consent')}
      </label>

      <ChipGroup<Behaviour>
        label={tr('onboarding.goals.goals')}
        hint={p.smokes ? undefined : tr('onboarding.goals.smokeHint')}
        options={goalOptions}
        isSelected={(v) => p.goals.includes(v)}
        onToggle={(v) => update({ goals: toggle(p.goals, v) })}
        columns={2}
      />
    </OnboardingLayout>
  )
}
