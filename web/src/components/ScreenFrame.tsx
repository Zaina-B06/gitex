import React from 'react'
import { ScreenId } from '../types'
import { BottomNav } from './BottomNav'

interface ScreenFrameProps {
  children: React.ReactNode
  /** Active tab; when set, the bottom bar is shown pinned below the scrolling content. */
  tab?: ScreenId
  onNavigate?: (screen: ScreenId) => void
  /** Shows the "Need help?" link (top corner) that opens the Care screen. */
  onHelp?: () => void
  /** Decorative motifs, drawn behind the content. */
  background?: React.ReactNode
  className?: string
  dir?: 'ltr' | 'rtl'
  /** Pinned below the scroll area, above the tab bar (e.g. a main button). */
  footer?: React.ReactNode
}

/**
 * Every screen sits in a fixed phone-sized frame: the content scrolls inside it,
 * the footer and tab bar stay put. Long lists (Community, Meals…) scroll instead of growing the page.
 */
export const ScreenFrame: React.FC<ScreenFrameProps> = ({
  children,
  tab,
  onNavigate,
  onHelp,
  background,
  className = 'bg-[#EEF1EA] text-[#1B2A22]',
  dir,
  footer,
}) => (
  <div dir={dir} className={`print-full relative isolate overflow-hidden h-full w-full flex flex-col font-sans ${className}`}>
    {background}
    {onHelp && (
      <button
        type="button"
        onClick={onHelp}
        className="no-print absolute top-2 end-3 z-20 min-h-[32px] px-2.5 rounded-full bg-white/85 border border-[#E8B4AC] text-[12px] font-semibold text-[#A02A1C] cursor-pointer"
      >
        Need help?
      </button>
    )}
    <div className="print-full flex-1 min-h-0 overflow-y-auto overscroll-contain">{children}</div>
    {footer && <div className="no-print px-6 pb-5 pt-2">{footer}</div>}
    {tab && onNavigate && (
      <div className="no-print">
        <BottomNav currentScreen={tab} onNavigate={onNavigate} />
      </div>
    )}
  </div>
)
