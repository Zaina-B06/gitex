import React, { useState } from 'react'
import { ScreenProps } from '../types'
import { ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { ActionCard } from '../components/ActionCard'
import { ExplainSheet } from '../components/ExplainSheet'
import { tr } from '../i18n'

/** After a check-in: the engine's message and the adjusted (lighter) steps from CheckinOut. */
export const EasierPlanScreen: React.FC<ScreenProps> = ({ state, onNavigate }) => {
  const result = state.lastCheckin
  const [whyId, setWhyId] = useState<string | null>(null)

  return (
    <div className="relative isolate w-full h-full overflow-y-auto overflow-x-hidden overscroll-contain box-border bg-[#EEF1EA] font-sans text-[#1B2A22] flex flex-col p-6">
      <ArabicCalligraphyRing width={440} height={440} style={{ right: -230, top: -160, opacity: 0.12 }} />

      <span className="text-[13px] text-[#5A6A60]">{tr('app.easier.after')}</span>
      <h1 className="mt-2.5 mb-1.5 font-display tracking-tight text-[27px] leading-tight font-semibold">
        {tr('app.easier.title')}
      </h1>

      {!result ? (
        <p className="m-0 text-[14px] text-[#3F4F45]">{tr('app.easier.first')}</p>
      ) : (
        <>
          <p className="m-0 text-[15px] leading-relaxed text-[#3F4F45]">{result.message}</p>
          <div className="mt-4 flex flex-col gap-2.5">
            {result.adjusted_actions.map((a) => (
              <ActionCard key={a.id} action={a} lang={state.language} onWhy={() => setWhyId(a.id)} />
            ))}
          </div>
          <p className="mt-3 mb-0 text-[12px] leading-relaxed text-[#5A6A60]">
            {tr('app.easier.replaces')}
          </p>
        </>
      )}

      <button
        type="button"
        onClick={() => onNavigate('today')}
        className="mt-auto min-h-[52px] rounded-[14px] bg-[#3E6B53] hover:bg-[#2C5140] text-white text-[16px] font-semibold border-0 cursor-pointer shadow-button"
      >
        {tr('app.easier.goToday')}
      </button>

      {whyId && <ExplainSheet actionId={whyId} lang={state.language} onClose={() => setWhyId(null)} />}
    </div>
  )
}
