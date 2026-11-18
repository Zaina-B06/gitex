import React from 'react'
import { ScreenId } from '../types'
import { useTranslation } from 'react-i18next'

interface BottomNavProps {
  currentScreen: ScreenId
  onNavigate: (screen: ScreenId) => void
}

const icon = (d: React.ReactNode) => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
    {d}
  </svg>
)

const TABS: { id: ScreenId; icon: React.ReactNode }[] = [
  { id: 'today', icon: icon(<path d="M3 11l9-7 9 7v9a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z" />) },
  {
    id: 'plan',
    icon: icon(
      <>
        <rect x="3" y="5" width="18" height="16" rx="2" />
        <path d="M3 10h18M8 3v4M16 3v4" />
      </>,
    ),
  },
  { id: 'meals', icon: icon(<path d="M4 11h16v3a6 6 0 0 1-6 6h-4a6 6 0 0 1-6-6zM2 11h20M9 7c0-1 1-1 1-2s-1-1-1-2M14 7c0-1 1-1 1-2s-1-1-1-2" />) },
  {
    id: 'community',
    icon: icon(
      <>
        <circle cx="9" cy="8" r="3" />
        <circle cx="17" cy="9" r="2.5" />
        <path d="M3 20c0-3 3-5 6-5s6 2 6 5M15 15c3 0 6 1.5 6 4.5" />
      </>,
    ),
  },
  {
    id: 'settings',
    icon: icon(
      <>
        <circle cx="12" cy="12" r="3" />
        <path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1" />
      </>,
    ),
  },
]

export const BottomNav: React.FC<BottomNavProps> = ({ currentScreen, onNavigate }) => {
  const { t } = useTranslation()
  return (
  <nav
    aria-label={t('common.mainNav')}
    className="flex justify-around items-center bg-white/95 backdrop-blur-md border-t border-[#DCE3DA] rounded-t-[22px] shadow-[0_-8px_24px_-16px_rgba(38,58,48,0.25)] py-1.5 pb-3 px-1"
  >
    {TABS.map((tab) => {
      const active = currentScreen === tab.id
      return (
        <button
          key={tab.id}
          type="button"
          aria-current={active ? 'page' : undefined}
          onClick={() => onNavigate(tab.id)}
          className={`min-w-[60px] min-h-[44px] flex flex-col items-center justify-center gap-0.5 text-[11px] rounded-2xl transition-colors border-0 cursor-pointer ${
            active ? 'font-semibold text-[#3E6B53] bg-[#E1ECE4]' : 'font-medium text-[#5A6A60] bg-transparent hover:text-[#1B2A22]'
          }`}
        >
          {tab.icon}
          {t(`common.tab.${tab.id}`)}
        </button>
      )
    })}
  </nav>
  )
}
