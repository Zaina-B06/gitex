import React from 'react'
import { ScreenProps } from '../types'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { ScreenFrame } from '../components/ScreenFrame'
import { PlanSummary } from '../components/PlanSummary'

interface PlanCardScreenProps extends ScreenProps {
  onStart: () => void
}

/** Last sign-up screen: "Your plan, built for you", from the plan_summary returned by POST /users. */
export const PlanCardScreen: React.FC<PlanCardScreenProps> = ({ state, onStart }) => (
  <ScreenFrame
    className="bg-[#54705C] text-white"
    background={
      <>
        <TatreezPattern width={230} height={230} color="#2E4837" opacity={0.35} style={{ right: '-90px', bottom: '120px' }} />
        <ArabicCalligraphyRing width={660} height={660} color="#2E4837" opacity={0.6} style={{ left: '-350px', top: '240px' }} />
        <ArabicCalligraphyRing width={320} height={320} color="#2E4837" opacity={0.4} style={{ right: '-150px', top: '-120px' }} />
      </>
    }
    footer={
      <button
        type="button"
        onClick={onStart}
        className="w-full min-h-[52px] rounded-2xl bg-white hover:bg-[#F3F7F4] text-[#2C5140] text-[16px] font-bold shadow-[0_10px_22px_-10px_rgba(20,40,28,0.6)] border-0 cursor-pointer"
      >
        Continue
      </button>
    }
  >
    <div className="p-6 pb-2">
      <span className="text-[13px] text-[#F3F7F4]">Sign-up done{state.displayName ? `, ${state.displayName}` : ''}</span>
      <h1 className="mt-2 mb-1.5 font-display tracking-tight text-[32px] leading-[1.12] font-semibold">
        Your plan,
        <br />
        built for you
      </h1>
      <p className="m-0 mb-4 text-[14px] leading-relaxed text-[#F3F7F4]">
        Small steps every day. Each one grows only when you're ready. You'll find this any time under My plan.
      </p>
      {state.plan && <PlanSummary plan={state.plan} />}
    </div>
  </ScreenFrame>
)
