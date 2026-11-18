import React, { useEffect } from 'react'
import type { Action, RecipeOut } from '../api/client'
import { BEHAVIOUR_STYLE } from '../lib/behaviour'
import { ACTION_ICON } from '../lib/icons'
import { useTranslation } from 'react-i18next'
import { labels } from '../i18n'

export type Outcome = 'completed' | 'partial' | 'skipped'

const OUTCOME_TEXT: Record<string, string> = labels('common.card', [
  'completed', 'partial', 'skipped', 'no_response', 'paused', 'illness',
])

interface ActionCardProps {
  action: Action
  lang: 'en' | 'ar'
  when?: string
  /** Set once the step was answered today. */
  outcome?: string | null
  busy?: boolean
  onAnswer?: (type: Outcome) => void
  onWhy: () => void
  recipe?: RecipeOut | null
  onRecipe?: () => void
  /** Smaller variant offered by the engine ("lighter"). */
  lighterTitle?: string | null
  /** Settings "Read steps aloud" (preferences.read_aloud): adds a speaker button using the browser's speech. */
  readAloud?: boolean
}

const canSpeak = () => typeof window !== 'undefined' && 'speechSynthesis' in window

function speak(text: string, lang: 'en' | 'ar') {
  if (!canSpeak()) return
  window.speechSynthesis.cancel()
  const u = new SpeechSynthesisUtterance(text)
  u.lang = lang === 'ar' ? 'ar-AE' : 'en-US'
  window.speechSynthesis.speak(u)
}

export const ActionCard: React.FC<ActionCardProps> = ({
  action,
  lang,
  when,
  outcome,
  busy,
  onAnswer,
  onWhy,
  recipe,
  onRecipe,
  lighterTitle,
  readAloud,
}) => {
  const { t } = useTranslation()
  const st = BEHAVIOUR_STYLE[action.behaviour]
  // Stop reading when the card leaves the screen (e.g. navigating away).
  useEffect(() => () => {
    if (readAloud && canSpeak()) window.speechSynthesis.cancel()
  }, [readAloud])
  return (
    <article className="bg-white/90 rounded-[20px] p-3.5 flex flex-col gap-2 shadow-card">
      <div className="flex justify-between items-center gap-2">
        <span className="flex items-center gap-1.5 text-[12px] font-semibold" style={{ color: st.color }}>
          {(action.icon && ACTION_ICON[action.icon]) || st.icon}
          {st.label} · {t('common.level', { n: action.tier })}
        </span>
        <div className="flex items-center gap-3">
          {when && <span className="text-[12px] text-[#5A6A60]">{when}</span>}
          <button
            type="button"
            onClick={onWhy}
            className="text-[12px] font-medium text-[#3E6B53] hover:underline bg-transparent border-0 p-0 cursor-pointer"
          >
            {t('common.whyThis')}
          </button>
        </div>
      </div>

      <div className="flex items-start gap-2">
        <p className="m-0 flex-1 text-[17px] font-semibold leading-tight text-[#1B2A22]" dir={lang === 'ar' ? 'rtl' : 'ltr'}>
          {action.title[lang]}
        </p>
        {readAloud && canSpeak() && (
          <button
            type="button"
            onClick={() => speak(action.title[lang], lang)}
            aria-label={t('common.readAloud')}
            className="flex-none w-9 h-9 rounded-full bg-[#EEF1EA] text-[#2C5140] flex items-center justify-center border-0 cursor-pointer"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d="M11 5L6 9H2v6h4l5 4zM15.5 8.5a5 5 0 0 1 0 7M19 5a10 10 0 0 1 0 14" />
            </svg>
          </button>
        )}
      </div>
      <span className="text-[12px] text-[#5A6A60]">{t('common.aboutMin', { n: action.duration_min })}</span>

      {recipe && onRecipe && (
        <button
          type="button"
          onClick={onRecipe}
          className="min-h-[44px] px-3 rounded-[14px] bg-[#F6E9DC] hover:bg-[#ECCFB8] text-[#6B3A0B] text-[14px] font-semibold flex items-center justify-between transition-colors border-0 cursor-pointer"
        >
          <span>{t('common.tryRecipe', { title: recipe.title[lang], n: recipe.minutes })}</span>
          <svg className="rtl-flip" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <path d="M9 6l6 6-6 6" />
          </svg>
        </button>
      )}

      {outcome ? (
        <div
          className="p-2 rounded-xl text-xs font-semibold"
          style={{ background: st.tint, color: st.color }}
          role="status"
        >
          {OUTCOME_TEXT[outcome] ?? outcome}
        </div>
      ) : (
        onAnswer && (
          <>
            {lighterTitle && <span className="text-[12px] text-[#5A6A60]">{t('common.smallerVersion', { title: lighterTitle })}</span>}
            <div className="flex gap-2">
              <button
                type="button"
                disabled={busy}
                onClick={() => onAnswer('completed')}
                className="flex-1 min-h-[44px] rounded-[14px] text-white text-[14px] font-semibold shadow-button border-0 cursor-pointer disabled:opacity-60"
                style={{ background: st.color }}
              >
                {t('common.done')}
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => onAnswer('partial')}
                className="flex-1 min-h-[44px] rounded-[14px] border border-[#C5D0C7] bg-white hover:bg-[#F3F7F4] text-[#1B2A22] text-[14px] font-medium cursor-pointer disabled:opacity-60"
              >
                {t('common.didLess')}
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => onAnswer('skipped')}
                className="min-h-[44px] px-3.5 rounded-[14px] bg-[#E6EBE4] hover:bg-[#DDE3DB] text-[#3F4F45] text-[14px] font-medium border-0 cursor-pointer disabled:opacity-60"
              >
                {t('common.skipStep')}
              </button>
            </div>
          </>
        )
      )}
    </article>
  )
}
