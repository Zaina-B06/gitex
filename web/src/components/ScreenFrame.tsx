import React from 'react'
import { ScreenId } from '../types'
import { BottomNav } from './BottomNav'

interface ScreenFrameProps {
  children: React.ReactNode
  /** Active tab; when set, the bottom bar is shown pinned below the scrolling content. */
  tab?: ScreenId
  onNavigate?: (screen: ScreenId) => void
  /** Shows "Need help?" in the header row (it never overlaps other buttons); opens the Care screen. */
  onHelp?: () => void
  /** Pinned above the scroll area (e.g. a title and filter chips that scroll sideways). */
  top?: React.ReactNode
  /** Decorative motifs, drawn behind the content. */
  background?: React.ReactNode
  className?: string
  dir?: 'ltr' | 'rtl'
  /** Pinned below the scroll area, above the tab bar (e.g. a main button). */
  footer?: React.ReactNode
}

/**
 * Every screen sits in a fixed phone-sized frame with ONE vertical scroll area: the header row, `top`, the footer
 * and the tab bar stay put. Scrollbars are hidden inside the frame (index.css, .phone-frame).
 */
export const ScreenFrame: React.FC<ScreenFrameProps> = ({
  children,
  tab,
  onNavigate,
  onHelp,
  top,
  background,
  className = 'bg-[#EEF1EA] text-[#1B2A22]',
  dir,
  footer,
}) => (
  <div dir={dir} className={`print-full relative isolate overflow-hidden h-full w-full flex flex-col font-sans ${className}`}>
    {background}
    {onHelp && (
      <div className="no-print flex-none flex justify-end px-4 pt-3">
        <button
          type="button"
          onClick={onHelp}
          className="min-h-[32px] px-2.5 rounded-full bg-white/85 border border-[#E8B4AC] text-[12px] font-semibold text-[#A02A1C] cursor-pointer"
        >
          Need help?
        </button>
      </div>
    )}
    {top && <div className="flex-none">{top}</div>}
    <div className="print-full flex-1 min-h-0 overflow-y-auto overflow-x-hidden overscroll-contain">{children}</div>
    {footer && <div className="no-print flex-none px-6 pb-5 pt-2">{footer}</div>}
    {tab && onNavigate && (
      <div className="no-print flex-none">
        <BottomNav currentScreen={tab} onNavigate={onNavigate} />
      </div>
    )}
  </div>
)
