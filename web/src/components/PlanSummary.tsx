import React, { useState } from 'react'
import type { PlanOut } from '../api/client'
import { BEHAVIOUR_STYLE } from '../lib/behaviour'
import { useTranslation } from 'react-i18next'

/** The plan's behaviours in order (optional; My plan shows goal cards instead), plus "why it looks like this". */
export const PlanSummary: React.FC<{ plan: PlanOut; showList?: boolean }> = ({ plan, showList = true }) => {
  const { t } = useTranslation()
  const [showAll, setShowAll] = useState(false)
  return (
    <div className="flex flex-col gap-3 text-[#1B2A22]">
      {showList && <ol aria-label={t('common.goalsInOrder')} className="m-0 p-0 list-none bg-white/95 rounded-[20px] shadow-card flex flex-col">
        {plan.behaviours.map((b, i) => {
          const st = BEHAVIOUR_STYLE[b]
          return (
            <li
              key={b}
              className={`p-2.5 px-3.5 flex items-center gap-3 ${i < plan.behaviours.length - 1 ? 'border-b border-[#E6EBE4]' : ''}`}
            >
              <span className="w-9 h-9 rounded-full flex items-center justify-center flex-none" style={{ background: st.tint, color: st.color }}>
                {st.icon}
              </span>
              <span className="flex-1 text-[15px] font-semibold">{st.label}</span>
            </li>
          )
        })}
      </ol>}

      <section aria-label={t('common.whyLooks')} className="bg-white/95 rounded-[20px] shadow-card p-3.5 px-4 flex flex-col gap-2">
        <h2 className="m-0 font-display tracking-tight text-[16px] font-semibold">{t('common.whyLooks')}</h2>
        <ul className="m-0 ps-5 flex flex-col gap-1.5 text-[14px] leading-relaxed text-[#3F4F45] list-disc">
          {(showAll ? plan.all_reasons : plan.reasons).map((r) => (
            <li key={r}>{r}</li>
          ))}
        </ul>
        {plan.all_reasons.length > plan.reasons.length && (
          <button
            type="button"
            onClick={() => setShowAll(!showAll)}
            className="self-start min-h-[40px] flex items-center text-[14px] font-semibold text-[#2C5140] hover:underline bg-transparent border-0 p-0 cursor-pointer"
          >
            {showAll ? t('common.fewerReasons') : t('common.seeAllReasons')}
          </button>
        )}
        {plan.rotation_note && <p className="m-0 text-[12px] leading-relaxed text-[#5A6A60]">{plan.rotation_note}</p>}
      </section>
    </div>
  )
}
