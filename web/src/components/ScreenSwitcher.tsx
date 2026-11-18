import React, { useState } from 'react'
import { ScreenId } from '../types'
import type { AdvanceIn, SeedPersona } from '../api/client'
import { firstName, loadPersonas } from '../lib/demo'

interface ScreenSwitcherProps {
  currentScreen: ScreenId | null
  onSelectScreen: (screen: ScreenId) => void
  signedIn: boolean
  onStartOver: () => void
  /** Signed in: the current user's id, to mark who is selected. */
  userId: string | null
  onSwitchPerson: (p: SeedPersona) => void
  /** POST /demo/users/{id}/advance, then the screens re-fetch. */
  onAdvance: (body: AdvanceIn, label: string) => Promise<void>
}

const TIME_TRAVEL: { label: string; body: AdvanceIn }[] = [
  { label: 'Good day', body: { days: 1, pattern: 'good' } },
  { label: 'Mixed day', body: { days: 1, pattern: 'mixed' } },
  { label: 'Skip 4 days (lapse)', body: { days: 4, pattern: 'lapse' } },
  { label: 'Ramadan', body: { days: 1, pattern: 'good', scenario: 'ramadan' } },
  { label: 'Heat', body: { days: 1, pattern: 'good', scenario: 'heat' } },
]

// Grouped in the order a real user meets them.
const GROUPS: { title: string; screens: { id: ScreenId; label: string }[] }[] = [
  {
    title: '1 · Sign-up (first open)',
    screens: [
      { id: 'welcome', label: 'Welcome & language' },
      { id: 'onboarding-basics', label: 'About you' },
      { id: 'onboarding-goals', label: 'Goals' },
      { id: 'onboarding-health', label: 'Health check' },
      { id: 'onboarding-baseline', label: 'Your days (movement or sleep only)' },
      { id: 'onboarding-preferences', label: 'What helps' },
    ],
  },
  {
    title: '2 · Daily app',
    screens: [
      { id: 'today', label: 'Today' },
      { id: 'plan', label: 'My plan (calendar)' },
      { id: 'meals', label: 'Meals' },
      { id: 'community', label: 'Community' },
      { id: 'settings', label: 'Settings & profile' },
      { id: 'report', label: 'Progress report' },
      { id: 'checkin', label: 'Check-in' },
      { id: 'chat-nudge', label: 'Chat check-in' },
      { id: 'care', label: 'Care first / help' },
    ],
  },
  {
    title: '3 · Outside the app',
    screens: [
      { id: 'program-dashboard', label: 'Workplace dashboard' },
    ],
  },
]

const APP_GROUP: ScreenId[] = GROUPS[1].screens.map((s) => s.id).filter((id) => id !== 'care')

/** Demo-only bar (VITE_DEMO_MODE=true): switch person, time travel, jump between screens, start over. */
export const ScreenSwitcher: React.FC<ScreenSwitcherProps> = ({
  currentScreen,
  onSelectScreen,
  signedIn,
  onStartOver,
  userId,
  onSwitchPerson,
  onAdvance,
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [busy, setBusy] = useState(false)
  const personas = loadPersonas()
  const advance = async (body: AdvanceIn, label: string) => {
    setBusy(true)
    try {
      await onAdvance(body, label)
    } finally {
      setBusy(false)
    }
  }
  const active = GROUPS.flatMap((g) => g.screens).find((s) => s.id === currentScreen)

  const pick = (id: ScreenId) => {
    setIsOpen(false)
    // Daily-app screens need a signed-up user; without one the app sends you to Welcome.
    if (!signedIn && APP_GROUP.includes(id)) return onSelectScreen('welcome')
    onSelectScreen(id)
  }

  const chip =
    'flex-none min-h-[28px] px-2.5 rounded-full text-[11px] font-medium border border-[#3E6B53] cursor-pointer disabled:opacity-50'

  return (
    <div className="w-full bg-[#263A30] text-white text-xs border-b border-[#3E6B53]">
    {signedIn && (
      <div className="px-4 pt-2 flex gap-1.5 overflow-x-auto" style={{ scrollbarWidth: 'none' }} aria-label="Demo controls">
        {personas.map((p) => (
          <button
            key={p.user_id}
            type="button"
            onClick={() => onSwitchPerson(p)}
            aria-pressed={p.user_id === userId}
            className={`${chip} ${p.user_id === userId ? 'bg-[#A2C7B0] text-[#1B2A22] font-semibold' : 'bg-transparent text-white'}`}
          >
            {firstName(p)}
          </button>
        ))}
        {TIME_TRAVEL.map((t) => (
          <button key={t.label} type="button" disabled={busy} onClick={() => advance(t.body, t.label)} className={`${chip} bg-[#3E6B53] text-white`}>
            {t.label}
          </button>
        ))}
      </div>
    )}
    <div className="px-4 py-2 flex items-center justify-between">
      <div className="flex items-center gap-2 min-w-0">
        <span className="font-semibold tracking-wider text-[#A2C7B0] uppercase text-[10px]">Demo</span>
        <span className="font-medium text-white truncate max-w-[170px] sm:max-w-xs">{active?.label ?? '—'}</span>
      </div>

      <div className="relative">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="bg-[#3E6B53] hover:bg-[#2C5140] text-white font-medium px-2.5 py-1 rounded-lg flex items-center gap-1 transition-colors border-0 cursor-pointer"
        >
          <span>Demo menu</span>
          <svg className={`w-3.5 h-3.5 transition-transform ${isOpen ? 'rotate-180' : ''}`} viewBox="0 0 20 20" fill="currentColor">
            <path
              fillRule="evenodd"
              d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
              clipRule="evenodd"
            />
          </svg>
        </button>

        {isOpen && (
          <>
            <div className="fixed inset-0 z-40 bg-black/20" onClick={() => setIsOpen(false)} />
            <div className="absolute right-0 mt-2 w-72 max-h-[80vh] overflow-y-auto bg-white rounded-xl shadow-2xl border border-[#C5D0C7] py-1 z-50 text-[#1B2A22]">
              {GROUPS.map((group) => (
                <div key={group.title} className="py-1">
                  <div className="px-3 py-1.5 text-[11px] font-semibold text-[#5A6A60] uppercase">{group.title}</div>
                  {group.screens.map((screen) => (
                    <button
                      key={screen.id}
                      type="button"
                      onClick={() => pick(screen.id)}
                      className={`w-full text-left px-3 py-2 text-xs border-0 cursor-pointer hover:bg-[#DDE9E0]/50 transition-colors ${
                        currentScreen === screen.id ? 'bg-[#DDE9E0] font-semibold text-[#2C5140]' : 'bg-transparent'
                      }`}
                    >
                      {screen.label}
                    </button>
                  ))}
                </div>
              ))}
              <div className="border-t border-[#E6EBE4] mt-1 pt-1">
                <button
                  type="button"
                  onClick={() => {
                    setIsOpen(false)
                    onStartOver()
                  }}
                  className="w-full text-left px-3 py-2 text-xs font-semibold text-[#A02A1C] bg-transparent border-0 cursor-pointer hover:bg-[#FDE8E4]"
                >
                  Start over as a new user (forgets this device's account)
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
    </div>
  )
}
