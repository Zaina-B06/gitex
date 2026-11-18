import React from 'react'
import { ArabicCalligraphyRing } from './BackgroundMotifs'
import { tr } from '../i18n'

interface OnboardingLayoutProps {
  step: number // 1-based
  total: number // screens this person sees (4 or 5)
  title: string
  subtitle?: string
  onBack: () => void
  onContinue: () => void
  continueLabel?: string
  continueDisabled?: boolean
  onSkip?: () => void
  skipLabel?: string
  children: React.ReactNode
}

/** Shared frame for onboarding steps: back arrow, stepper, title, scrolling body, footer CTA. */
export const OnboardingLayout: React.FC<OnboardingLayoutProps> = ({
  step,
  total,
  title,
  subtitle,
  onBack,
  onContinue,
  continueLabel = tr('common.continue'),
  continueDisabled = false,
  onSkip,
  skipLabel = tr('common.skip'),
  children,
}) => (
  <div className="relative overflow-hidden isolate w-full h-full box-border bg-[#EEF1EA] font-sans text-[#1B2A22] flex flex-col p-6">
    <ArabicCalligraphyRing width={440} height={440} style={{ right: -230, top: -160, opacity: 0.12 }} />
    <ArabicCalligraphyRing width={320} height={320} style={{ left: -200, bottom: 40, opacity: 0.08 }} />

    <div className="flex items-center justify-between">
      <button
        type="button"
        onClick={onBack}
        aria-label={tr('common.back')}
        className="min-w-[44px] min-h-[44px] flex items-center bg-transparent border-0 p-0 text-[#1B2A22] cursor-pointer"
      >
        <svg className="rtl-flip" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
          <path d="M15 18l-6-6 6-6" />
        </svg>
      </button>
      <div role="img" aria-label={tr('common.stepOf', { step, total })} className="flex gap-1.5">
        {Array.from({ length: total }, (_, i) => (
          <span key={i} className={`w-6 h-1.5 rounded-sm ${i < step ? 'bg-[#3E6B53]' : 'bg-[#C5D0C7]'}`} />
        ))}
      </div>
      <span className="w-11 text-[12px] text-[#5A6A60] text-end">
        {step} / {total}
      </span>
    </div>

    <div className="flex-1 min-h-0 overflow-y-auto overflow-x-hidden pe-0.5">
      <h1 className="mt-4 mb-1 font-display tracking-tight text-[25px] leading-tight font-semibold">{title}</h1>
      {subtitle && <p className="m-0 text-[14px] leading-relaxed text-[#3F4F45]">{subtitle}</p>}
      <div className="mt-3 flex flex-col gap-4">{children}</div>
    </div>

    <div className="mt-auto pt-2.5 flex flex-col gap-1.5">
      <button
        type="button"
        onClick={onContinue}
        disabled={continueDisabled}
        className="min-h-[52px] rounded-[14px] bg-[#3E6B53] hover:bg-[#2C5140] disabled:bg-[#9FB3A6] disabled:cursor-not-allowed text-white text-[16px] font-semibold border-0 cursor-pointer shadow-[0_8px_18px_-10px_rgba(38,70,52,0.65)]"
      >
        {continueLabel}
      </button>
      {onSkip && (
        <button
          type="button"
          onClick={onSkip}
          className="min-h-[44px] bg-transparent border-0 text-[14px] font-medium text-[#3E6B53] cursor-pointer"
        >
          {skipLabel}
        </button>
      )}
    </div>
  </div>
)

/** A labelled group of single- or multi-select chips. */
export function ChipGroup<T extends string | number>({
  label,
  hint,
  options,
  isSelected,
  onToggle,
  columns,
}: {
  label: string
  hint?: string
  options: { value: T; label: string }[]
  isSelected: (value: T) => boolean
  onToggle: (value: T) => void
  columns?: number
}) {
  return (
    <fieldset className="m-0 p-0 border-0">
      <legend className="p-0 text-[15px] font-semibold text-[#1B2A22]">{label}</legend>
      {hint && <p className="m-0 mt-0.5 text-[12px] leading-snug text-[#5A6A60]">{hint}</p>}
      <div
        className={columns ? 'mt-2 grid gap-2' : 'mt-2 flex flex-wrap gap-2'}
        style={columns ? { gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` } : undefined}
      >
        {options.map((opt) => {
          const on = isSelected(opt.value)
          return (
            <button
              key={String(opt.value)}
              type="button"
              aria-pressed={on}
              onClick={() => onToggle(opt.value)}
              className={`min-h-[44px] px-3.5 rounded-[14px] text-[14px] cursor-pointer transition-all ${
                on
                  ? 'border-2 border-[#3E6B53] bg-[#DDE9E0] font-semibold text-[#2C5140]'
                  : 'border border-[#C5D0C7] bg-white text-[#1B2A22]'
              }`}
            >
              {opt.label}
            </button>
          )
        })}
      </div>
    </fieldset>
  )
}
