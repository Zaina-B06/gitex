import React from 'react'
import { useTranslation } from 'react-i18next'

/** The one language switch (Welcome and Settings → Profile): "English" and "العربية", the active one highlighted. */
export const LanguageSwitch: React.FC<{
  value: 'en' | 'ar'
  onChange: (lang: 'en' | 'ar') => void
  /** "dark" on the green Welcome screen, "light" on cards. */
  tone?: 'dark' | 'light'
  disabled?: boolean
}> = ({ value, onChange, tone = 'light', disabled }) => {
  const { t } = useTranslation()
  const options = [
    { value: 'en', label: t('common.langEnglish') },
    { value: 'ar', label: t('common.langArabic') },
  ] as const
  return (
    <div role="group" aria-label={t('common.languageLabel')} className="grid grid-cols-2 gap-2">
      {options.map((opt) => {
        const on = value === opt.value
        const look =
          tone === 'dark'
            ? on
              ? 'bg-white text-[#2C5140] font-semibold border-2 border-white'
              : 'bg-white/10 text-white border border-white/40 hover:bg-white/20'
            : on
              ? 'bg-[#DDE9E0] text-[#2C5140] font-semibold border-2 border-[#3E6B53]'
              : 'bg-white text-[#1B2A22] border border-[#C5D0C7]'
        return (
          <button
            key={opt.value}
            type="button"
            lang={opt.value}
            aria-pressed={on}
            disabled={disabled}
            onClick={() => !on && onChange(opt.value)}
            className={`min-h-[48px] rounded-[14px] text-[16px] cursor-pointer transition-colors disabled:opacity-60 ${
              opt.value === 'ar' ? 'font-arabic text-[18px]' : ''
            } ${look}`}
          >
            {opt.label}
          </button>
        )
      })}
    </div>
  )
}
