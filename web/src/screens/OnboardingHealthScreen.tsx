import React from 'react'
import { ScreenProps, SCREENING_KEYS, ScreeningKey, MobilityLimitation, PregnancyAnswer } from '../types'
import { api } from '../api/client'
import { OnboardingLayout, ChipGroup } from '../components/OnboardingLayout'
import { LoadingView, ErrorView } from '../components/StatusViews'
import { useAsync } from '../lib/useAsync'
import { asksBaseline, stepOf } from '../lib/onboarding'

const MOBILITY: { value: MobilityLimitation; label: string }[] = [
  { value: 'none', label: 'No' },
  { value: 'some', label: 'Some' },
  { value: 'mobility_aid', label: 'I use a mobility aid or wheelchair' },
]

const PREGNANCY: { value: PregnancyAnswer; label: string }[] = [
  { value: 'yes', label: 'Yes' },
  { value: 'no', label: 'No' },
  { value: 'prefer_not_to_say', label: 'Prefer not to say' },
]

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
      return showToast('Please answer yes or no to each question. They keep your plan safe.')
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
      title="A quick health check"
      subtitle={why ?? 'So every step we suggest is safe for you.'}
      onBack={() => onNavigate('onboarding-goals')}
      onContinue={handleContinue}
      continueDisabled={!content.data}
    >
      {content.loading && <LoadingView label="Loading questions…" />}
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
                <div className="flex gap-2" role="group" aria-label={`Question ${i + 1}`}>
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
                        {v ? 'Yes' : 'No'}
                      </button>
                    )
                  })}
                </div>
              </li>
            ))}
          </ol>

          {p.sex === 'female' && (
            <ChipGroup<PregnancyAnswer>
              label="Are you pregnant?"
              hint="If yes, we only suggest pregnancy-safe steps."
              options={PREGNANCY}
              isSelected={(v) => p.pregnant === v}
              onToggle={(v) => setState((prev) => ({ ...prev, profile: { ...prev.profile, pregnant: v } }))}
            />
          )}

          <ChipGroup<MobilityLimitation>
            label="Does anything limit how you move?"
            hint="We'll suggest seated or adapted steps where needed."
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
