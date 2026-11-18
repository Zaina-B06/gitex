import React from 'react'
import { ScreenProps, OnboardingDraft } from '../types'
import { OnboardingLayout, ChipGroup } from '../components/OnboardingLayout'
import { asksActivity, asksSleep } from '../lib/onboarding'

const DAYS = [0, 1, 2, 3, 4, 5, 6, 7].map((d) => ({ value: d, label: String(d) }))
const SLEEP_HOURS = [4, 5, 6, 7, 8, 9].map((h) => ({ value: h, label: h === 4 ? '≤4' : h === 9 ? '9+' : String(h) }))
const QUALITY = [
  { value: 1, label: 'Very poor' },
  { value: 2, label: 'Poor' },
  { value: 3, label: 'OK' },
  { value: 4, label: 'Good' },
  { value: 5, label: 'Very good' },
]

/** Step 4 of 5: activity and/or sleep baseline (CLAUDE.md §4.4), only for the goals picked. */
export const BaselineScreen: React.FC<ScreenProps> = ({ state, setState, onNavigate, showToast }) => {
  const p = state.profile
  const update = (patch: Partial<OnboardingDraft>) =>
    setState((prev) => ({ ...prev, profile: { ...prev.profile, ...patch } }))
  const activity = asksActivity(p)
  const sleep = asksSleep(p)

  const handleContinue = () => {
    if ((activity && p.activeDaysPerWeek === null) || (sleep && (p.sleepHoursTypical === null || p.sleepQualitySelf === null)))
      return showToast('Please answer each question. A rough guess is fine.')
    onNavigate('onboarding-preferences')
  }

  return (
    <OnboardingLayout
      step={4}
      title="Your days right now"
      subtitle="A rough guess is fine. This is where we start, not a target."
      onBack={() => onNavigate('onboarding-health')}
      onContinue={handleContinue}
    >
      {activity && (
        <ChipGroup
          label="On how many days a week are you active for 20+ minutes?"
          options={DAYS}
          isSelected={(v) => p.activeDaysPerWeek === v}
          onToggle={(v) => update({ activeDaysPerWeek: v })}
          columns={4}
        />
      )}
      {sleep && (
        <>
          <ChipGroup
            label="How many hours do you usually sleep?"
            options={SLEEP_HOURS}
            isSelected={(v) => p.sleepHoursTypical === v}
            onToggle={(v) => update({ sleepHoursTypical: v })}
            columns={3}
          />
          <ChipGroup
            label="How well do you usually sleep?"
            options={QUALITY}
            isSelected={(v) => p.sleepQualitySelf === v}
            onToggle={(v) => update({ sleepQualitySelf: v })}
          />
        </>
      )}
    </OnboardingLayout>
  )
}
