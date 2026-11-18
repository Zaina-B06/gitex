import React from 'react'
import { useTranslation } from 'react-i18next'
import { api } from '../api/client'
import { useAsync } from '../lib/useAsync'
import { LoadingView, ErrorView } from './StatusViews'

/** "Why this step?" bottom sheet: GET /actions/{id}/explain (BCT name, rationale, limits, how to turn off). */
export const ExplainSheet: React.FC<{ actionId: string; lang: 'en' | 'ar'; onClose: () => void }> = ({
  actionId,
  lang,
  onClose,
}) => {
  const { t } = useTranslation()
  const ex = useAsync(() => api.explain(actionId, lang), [actionId, lang])

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center" role="dialog" aria-modal="true" aria-labelledby="why-title">
      <div className="absolute inset-0 bg-black/40" onClick={onClose} />
      <div className="relative w-full max-w-[390px] max-h-[80vh] overflow-y-auto bg-white rounded-t-[24px] p-5 pb-7 flex flex-col gap-3 shadow-2xl">
        <div className="flex justify-between items-start gap-3">
          <div className="flex flex-col gap-0.5">
            <h2 id="why-title" className="m-0 font-display tracking-tight text-[20px] font-semibold">
              {t('common.whyTitle')}
            </h2>
            {ex.data && (
              <span className="text-[13px] font-semibold text-[#3E6B53]">
                {ex.data.bct_name} · BCT {ex.data.bct_code}
              </span>
            )}
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label={t('common.close')}
            className="min-w-[44px] min-h-[44px] flex items-center justify-center bg-transparent border-0 cursor-pointer text-[#1B2A22]"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d="M6 6l12 12M18 6L6 18" />
            </svg>
          </button>
        </div>

        {ex.loading && <LoadingView />}
        {ex.error && <ErrorView message={ex.error} onRetry={ex.reload} />}
        {ex.data && (
          <>
            <p className="m-0 text-[14px] leading-relaxed text-[#3F4F45]">{ex.data.rationale}</p>
            <div className="flex flex-col gap-1">
              <h3 className="m-0 text-[14px] font-semibold">{t('common.whenLess')}</h3>
              <p className="m-0 text-[14px] leading-relaxed text-[#3F4F45]">{ex.data.limits}</p>
            </div>
            <div className="flex flex-col gap-1">
              <h3 className="m-0 text-[14px] font-semibold">{t('common.turnOff')}</h3>
              <p className="m-0 text-[14px] leading-relaxed text-[#3F4F45]">{ex.data.how_to_turn_off}</p>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
