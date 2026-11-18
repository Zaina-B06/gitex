import React from 'react'
import { ScreenProps } from '../types'
import { api, ApiError, errorText } from '../api/client'
import { ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { asksBaseline } from '../lib/onboarding'
import { tr } from '../i18n'


/**
 * Care first. Four ways in:
 * - health check (chest pain / dizziness) during sign-up → continue sign-up gently
 * - red flag in the sign-up "why it matters" text → continue to the plan
 * - red flag in a check-in → coaching paused until a person has checked in
 * - the "Need help?" link → just the numbers, nothing is paused
 */
export const CareScreen: React.FC<ScreenProps> = ({ state, setState, onNavigate, showToast }) => {
  const fromHelp = state.careReason === 'help'
  const fromScreening = state.careReason === 'onboarding_screening' && !state.session
  // Red-flag words in the optional "own words" box at sign-up: the server's care text; nothing was saved.
  const fromSignupText = state.careReason === 'onboarding_text' && !state.session
  const fromSignup = state.justSignedUp
  const message = fromHelp
    ? tr('onboarding.care.help')
    : fromSignupText
      ? (state.careMessage ?? tr('onboarding.care.default'))
      : fromScreening
      ? tr('onboarding.care.screening')
      : state.lastCheckin?.red_flag
        ? state.lastCheckin.message
        : tr('onboarding.care.default')
  const doneLabel = fromHelp
    ? tr('common.back')
    : fromSignupText
      ? tr('onboarding.care.backToSignup')
      : fromScreening || fromSignup
        ? tr('onboarding.care.continueSetup')
        : tr('onboarding.care.beenSeen')

  const handleBeenSeen = async () => {
    setState((prev) => ({ ...prev, careReason: null, careMessage: null }))
    if (fromHelp) return onNavigate('today')
    if (fromSignupText) return onNavigate('onboarding-basics')
    if (fromScreening) return onNavigate(asksBaseline(state.profile) ? 'onboarding-baseline' : 'onboarding-preferences')
    if (fromSignup) return onNavigate('plan-ready')
    try {
      await api.settings(state.session!, { context: { paused: false } })
      showToast(tr('onboarding.care.glad'))
    } catch (e) {
      // The backend keeps coaching paused after a safety concern until a person has checked in.
      showToast(
        e instanceof ApiError && e.status === 409
          ? tr('onboarding.care.staysPaused')
          : errorText(e),
      )
    }
    onNavigate('today')
  }

  return (
    <div className="relative isolate w-full h-full overflow-y-auto overflow-x-hidden overscroll-contain bg-[#F7F9F4] font-sans text-[#1B2A22] flex flex-col p-6">
      {/* Background Motif */}
      <ArabicCalligraphyRing
        width={380}
        height={380}
        style={{ right: '-200px', top: '-140px', opacity: 0.08 }}
      />

      {/* Heart Icon Badge */}
      <span className="mt-5 w-14 h-14 rounded-full bg-[#FDE8E4] text-[#A02A1C] flex items-center justify-center">
        <svg
          width="28"
          height="28"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          aria-hidden="true"
        >
          <path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8z" />
        </svg>
      </span>

      {/* Title */}
      <h1 className="mt-[18px] mb-2 font-display tracking-tight text-[28px] leading-tight font-semibold text-[#1B2A22]">
        {tr('onboarding.care.title')}
      </h1>

      <p className="m-0 text-[15px] leading-relaxed text-[#3F4F45]">
        {message}
      </p>

      {/* Emergency Call Buttons */}
      <div className="mt-[22px] flex flex-col gap-2.5">
        <a
          href="tel:998"
          onClick={() => showToast(tr('onboarding.care.opening998'))}
          className="min-h-[64px] px-4 rounded-[14px] bg-[#A02A1C] hover:bg-[#852317] text-white flex items-center justify-between no-underline shadow-[0_8px_18px_-10px_rgba(38,70,52,0.65)] transition-colors"
        >
          <span className="flex flex-col gap-0.5">
            <span className="text-[16px] font-semibold">{tr('onboarding.care.call998')}</span>
            <span className="text-[13px] text-[#FBE3DF]">{tr('onboarding.care.call998Sub')}</span>
          </span>
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            aria-hidden="true"
          >
            <path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z" />
          </svg>
        </a>

        <a
          href="tel:800725462"
          onClick={() => showToast(tr('onboarding.care.openingSakina'))}
          className="min-h-[64px] px-4 rounded-[14px] border-2 border-[#1B2A22] bg-transparent hover:bg-black/5 text-[#1B2A22] flex items-center justify-between no-underline transition-colors"
        >
          <span className="flex flex-col gap-0.5">
            <span className="text-[16px] font-semibold">{tr('onboarding.care.callSakina')}</span>
            <span className="text-[13px] text-[#3F4F45]">{tr('onboarding.care.callSakinaSub')}</span>
          </span>
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            aria-hidden="true"
          >
            <path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z" />
          </svg>
        </a>
      </div>

      <p className="mt-[18px] mb-0 text-[14px] leading-relaxed text-[#3F4F45]">
        {tr('onboarding.care.harm')}
      </p>

      {/* Footer */}
      <div className="mt-auto flex flex-col gap-2">
        <button
          type="button"
          onClick={handleBeenSeen}
          className="min-h-[48px] rounded-[14px] border border-[#C5D0C7] bg-white hover:bg-[#DDE9E0] text-[#1B2A22] text-[15px] font-medium flex items-center justify-center transition-colors shadow-sm"
        >
          {doneLabel}
        </button>
      </div>
    </div>
  )
}
