import React from 'react'
import { ScreenProps, OnboardingDraft } from '../types'
import { OnboardingLayout, ChipGroup } from '../components/OnboardingLayout'
import { asksActivity, asksSleep, stepOf } from '../lib/onboarding'
import { options, tr } from '../i18n'

const DAYS = [0, 1, 2, 3, 4, 5, 6, 7].map((d) => ({ value: d, label: String(d) }))
const SLEEP_HOURS = [4, 5, 6, 7, 8, 9].map((h) => ({ value: h, label: h === 4 ? '≤4' : h === 9 ? '9+' : String(h) }))
const QUALITY = options<number>('onboarding.quality', [1, 2, 3, 4, 5])

/** Step 4 (only with a movement or sleep goal): activity and/or sleep baseline (CLAUDE.md §4.4), only for the goals picked. */
export const BaselineScreen: React.FC<ScreenProps> = ({ state, setState, onNavigate, showToast }) => {
  const p = state.profile
  const update = (patch: Partial<OnboardingDraft>) =>
    setState((prev) => ({ ...prev, profile: { ...prev.profile, ...patch } }))
  const activity = asksActivity(p)
  const sleep = asksSleep(p)

  const handleContinue = () => {
    if ((activity && p.activeDaysPerWeek === null) || (sleep && (p.sleepHoursTypical === null || p.sleepQualitySelf === null)))
      return showToast(tr('onboarding.baseline.toast'))
    onNavigate('onboarding-preferences')
  }

  return (
    <OnboardingLayout
      {...stepOf(p, 'onboarding-baseline')}
      title={tr('onboarding.baseline.title')}
      subtitle={tr('onboarding.baseline.subtitle')}
      onBack={() => onNavigate('onboarding-health')}
      onContinue={handleContinue}
    >
      {activity && (
        <ChipGroup
          label={tr('onboarding.baseline.active')}
          options={DAYS}
          isSelected={(v) => p.activeDaysPerWeek === v}
          onToggle={(v) => update({ activeDaysPerWeek: v })}
          columns={4}
        />
      )}
      {sleep && (
        <>
          <ChipGroup
            label={tr('onboarding.baseline.sleepHours')}
            options={SLEEP_HOURS}
            isSelected={(v) => p.sleepHoursTypical === v}
            onToggle={(v) => update({ sleepHoursTypical: v })}
            columns={3}
          />
          <ChipGroup
            label={tr('onboarding.baseline.sleepQuality')}
            options={QUALITY}
            isSelected={(v) => p.sleepQualitySelf === v}
            onToggle={(v) => update({ sleepQualitySelf: v })}
          />
        </>
      )}
    </OnboardingLayout>
  )
}
