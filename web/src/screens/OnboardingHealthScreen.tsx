import React from 'react'
import { ScreenProps, SCREENING_KEYS, ScreeningKey, MobilityLimitation, PregnancyAnswer } from '../types'
import { api } from '../api/client'
import { OnboardingLayout, ChipGroup } from '../components/OnboardingLayout'
import { LoadingView, ErrorView } from '../components/StatusViews'
import { useAsync } from '../lib/useAsync'
import { asksBaseline, stepOf } from '../lib/onboarding'
import { options, tr } from '../i18n'

const MOBILITY = options<MobilityLimitation>('onboarding.mobility', ['none', 'some', 'mobility_aid'])
const PREGNANCY = options<PregnancyAnswer>('onboarding.pregnancy', ['yes', 'no', 'prefer_not_to_say'])

/** Step 3: health check, always asked in full and never pre-filled. Wording from GET /content/onboarding. */
export const OnboardingHealthScreen: React.FC<ScreenProps> = ({ state, setState, onNavigate, showToast }) => {
  const p = state.profile
  const content = useAsync(() => api.onboardingContent(state.language, p.readingLevel), [state.language, p.readingLevel])

  const answer = (key: ScreeningKey, value: boolean) =>
    setState((prev) => ({
      ...prev,
      profile: { ...prev.profile, screening: { ...prev.profile.screening, [key]: value } },
    }))

  const handleContinue = () => {
    if (SCREENING_KEYS.some((k) => p.screening[k] === null))
      return showToast(tr('onboarding.health.toastAnswer'))
    // Chest pain or dizziness/fainting: see a doctor first, then gentle steps only (CLAUDE.md §4.3).
    if (p.screening.chest_pain || p.screening.dizziness_or_fainting) {
      setState((prev) => ({ ...prev, careReason: 'onboarding_screening' }))
      return onNavigate('care')
    }
    onNavigate(asksBaseline(p) ? 'onboarding-baseline' : 'onboarding-preferences')
  }

  const questions = content.data?.questions ?? {}
  const why = content.data?.why_we_ask?.screening

  return (
    <OnboardingLayout
      {...stepOf(p, 'onboarding-health')}
      title={tr('onboarding.health.title')}
      subtitle={why ?? tr('onboarding.health.subtitle')}
      onBack={() => onNavigate('onboarding-goals')}
      onContinue={handleContinue}
      continueDisabled={!content.data}
    >
      {content.loading && <LoadingView label={tr('onboarding.health.loading')} />}
      {content.error && <ErrorView message={content.error} onRetry={content.reload} />}
      {content.data && (
        <>
          <ol className="m-0 p-0 list-none flex flex-col gap-2">
            {SCREENING_KEYS.map((key, i) => (
              <li key={key} className="bg-white/90 rounded-[16px] p-3 flex flex-col gap-2 shadow-sm">
                <span className="text-[14px] leading-snug">
                  <span className="text-[#5A6A60] me-1">{i + 1}.</span>
                  {questions[key] ?? key}
                </span>
                <div className="flex gap-2" role="group" aria-label={tr('onboarding.health.question', { n: i + 1 })}>
                  {([true, false] as const).map((v) => {
                    const on = p.screening[key] === v
                    return (
                      <button
                        key={String(v)}
                        type="button"
                        aria-pressed={on}
                        onClick={() => answer(key, v)}
                        className={`flex-1 min-h-[40px] rounded-[12px] text-[14px] cursor-pointer ${
                          on
                            ? 'border-2 border-[#3E6B53] bg-[#DDE9E0] font-semibold text-[#2C5140]'
                            : 'border border-[#C5D0C7] bg-white text-[#1B2A22]'
                        }`}
                      >
                        {v ? tr('common.yes') : tr('common.no')}
                      </button>
                    )
                  })}
                </div>
              </li>
            ))}
          </ol>

          {p.sex === 'female' && (
            <ChipGroup<PregnancyAnswer>
              label={tr('onboarding.health.pregnant')}
              hint={tr('onboarding.health.pregnantHint')}
              options={PREGNANCY}
              isSelected={(v) => p.pregnant === v}
              onToggle={(v) => setState((prev) => ({ ...prev, profile: { ...prev.profile, pregnant: v } }))}
            />
          )}

          <ChipGroup<MobilityLimitation>
            label={tr('onboarding.health.mobility')}
            hint={tr('onboarding.health.mobilityHint')}
            options={MOBILITY}
            isSelected={(v) => p.mobility === v}
            onToggle={(v) => setState((prev) => ({ ...prev, profile: { ...prev.profile, mobility: v } }))}
          />

          {content.data.translation_note && <p className="m-0 text-[12px] text-[#5A6A60]">{content.data.translation_note}</p>}
        </>
      )}
    </OnboardingLayout>
  )
}
