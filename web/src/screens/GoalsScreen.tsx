import React from 'react'
import { ScreenProps, OnboardingDraft } from '../types'
import type { Behaviour, Condition } from '../api/client'
import { OnboardingLayout, ChipGroup } from '../components/OnboardingLayout'
import { GOAL_OPTIONS } from '../lib/behaviour'

const CONDITION_OPTIONS: { value: Condition; label: string }[] = [
  { value: 'diabetes', label: 'Diabetes' },
  { value: 'high_blood_pressure', label: 'High blood pressure' },
  { value: 'back_or_joint_pain', label: 'Back or joint pain' },
  { value: 'stress', label: 'Stress' },
  { value: 'recovering_from_illness_or_injury', label: 'Recovering from illness or injury' },
]

const SMOKES = 'smokes' as const

/** Step 2 of 5: goals (at least one) and anything the user is managing (optional, with consent). */
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
    if (p.goals.length === 0) return showToast('Pick at least one thing to work on.')
    onNavigate('onboarding-health')
  }

  return (
    <OnboardingLayout
      step={2}
      title="What do you want to work on?"
      subtitle="Pick any. We'll start with one or two."
      onBack={() => onNavigate('onboarding-basics')}
      onContinue={handleContinue}
    >
      <ChipGroup<Condition | typeof SMOKES>
        label="Anything you're managing?"
        hint="Optional. It changes the order of your steps, never the medical care you get. You can remove it any time."
        options={[...CONDITION_OPTIONS, { value: SMOKES, label: 'I smoke' }]}
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
        I agree Rebound can use the conditions I picked to shape my plan.
      </label>

      <ChipGroup<Behaviour>
        label="Your goals"
        hint={p.smokes ? undefined : '"Smoke less" appears if you tell us you smoke.'}
        options={goalOptions}
        isSelected={(v) => p.goals.includes(v)}
        onToggle={(v) => update({ goals: toggle(p.goals, v) })}
        columns={2}
      />
    </OnboardingLayout>
  )
}
