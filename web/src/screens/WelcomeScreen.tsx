import React from 'react'
import { ScreenId, AppState } from '../types'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { api } from '../api/client'
import { useAsync } from '../lib/useAsync'

interface WelcomeScreenProps {
  state: AppState
  setState: React.Dispatch<React.SetStateAction<AppState>>
  onNavigate: (screen: ScreenId) => void
  showToast: (msg: string) => void
}

/** First screen on a fresh install: what Rebound is, pick a language, start sign-up. */
export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ state, setState, onNavigate }) => {
  const isArabic = state.language === 'ar'
  const setLanguage = (language: 'en' | 'ar') => setState((prev) => ({ ...prev, language }))
  // "Draft translation, pending native review" while the Arabic isn't reviewed (HANDOFF, Part D).
  const content = useAsync(() => (isArabic ? api.onboardingContent('ar') : Promise.resolve(null)), [isArabic])

  return (
    <div
      dir={isArabic ? 'rtl' : 'ltr'}
      className="relative overflow-hidden isolate w-full h-full overflow-y-auto overflow-x-hidden bg-[#54705C] font-sans text-white flex flex-col p-6"
    >
      <TatreezPattern width={230} height={230} color="#2E4837" opacity={0.35} style={{ right: -90, bottom: 160 }} />
      <ArabicCalligraphyRing width={620} height={620} color="#2E4837" opacity={0.55} style={{ left: -330, top: 220 }} />
      <ArabicCalligraphyRing width={320} height={320} color="#2E4837" opacity={0.4} style={{ right: -150, top: -120 }} />

      <span className="mt-10 text-[13px] tracking-wide text-[#DDE9E0]">{isArabic ? 'ريباوند' : 'Rebound'}</span>
      <h1 className="mt-2 mb-3 font-display tracking-tight text-[36px] leading-[1.1] font-semibold">
        {isArabic ? 'خطوة صغيرة كل يوم.' : 'One small step a day.'}
        <br />
        {isArabic ? 'لا شيء يعود إلى الصفر.' : 'Nothing resets to zero.'}
      </h1>
      <p className="m-0 text-[15px] leading-relaxed text-[#F3F7F4]">
        {isArabic
          ? 'نساعدك على الحركة والنوم بشكل أفضل، ونخفف الخطة في الأيام الصعبة.'
          : 'We help you move and sleep a little better, and make the plan lighter on tough days.'}
      </p>

      <fieldset className="mt-8 p-0 border-0">
        <legend className="p-0 text-[14px] font-semibold text-[#F3F7F4]">
          {isArabic ? 'اختر اللغة' : 'Choose your language'}
        </legend>
        <div className="mt-2 grid grid-cols-2 gap-2">
          {(
            [
              { value: 'en', label: 'English' },
              { value: 'ar', label: 'عربي' },
            ] as const
          ).map((opt) => {
            const on = state.language === opt.value
            return (
              <button
                key={opt.value}
                type="button"
                aria-pressed={on}
                onClick={() => setLanguage(opt.value)}
                className={`min-h-[52px] rounded-[14px] text-[16px] cursor-pointer transition-colors ${
                  opt.value === 'ar' ? 'font-arabic text-[19px]' : ''
                } ${
                  on
                    ? 'bg-white text-[#2C5140] font-semibold border-2 border-white'
                    : 'bg-white/10 text-white border border-white/40 hover:bg-white/20'
                }`}
              >
                {opt.label}
              </button>
            )
          })}
        </div>
      </fieldset>

      <div className="mt-auto flex flex-col gap-2">
        {content.data?.translation_note && (
          <p className="m-0 text-[12px] text-[#FFE9C7]">{content.data.translation_note}</p>
        )}
        <p className="m-0 text-[12px] leading-relaxed text-[#DDE9E0]">
          {isArabic
            ? 'يستغرق حوالي 3 دقائق. معظم الأسئلة اختيارية.'
            : 'Takes about 3 minutes. Most questions are optional.'}
        </p>
        <button
          type="button"
          onClick={() => onNavigate('onboarding-basics')}
          className="min-h-[52px] rounded-2xl bg-white hover:bg-[#F3F7F4] text-[#2C5140] text-[16px] font-bold border-0 cursor-pointer shadow-[0_10px_22px_-10px_rgba(20,40,28,0.6)]"
        >
          {isArabic ? 'لنبدأ' : 'Get started'}
        </button>
      </div>
    </div>
  )
}
