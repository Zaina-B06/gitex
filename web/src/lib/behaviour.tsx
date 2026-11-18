import React from 'react'
import type { Behaviour } from '../api/client'
import { labels, tr } from '../i18n'

export interface BehaviourStyle {
  label: string
  color: string
  tint: string
  icon: React.ReactNode
}

const svg = (d: React.ReactNode) => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
    {d}
  </svg>
)

/** Colour, label and icon per behaviour, from the design tokens in index.css. */
export const BEHAVIOUR_STYLE: Record<Behaviour, BehaviourStyle> = {
  movement: {
    get label() {
      return tr('common.behaviour.movement')
    },
    color: '#3E6B53',
    tint: '#DDE9E0',
    icon: svg(
      <>
        <circle cx="13" cy="4" r="2" />
        <path d="M9 20l2-6 3 3v4M7 11l3-3 4 1 2 4" />
      </>,
    ),
  },
  sleep: {
    get label() {
      return tr('common.behaviour.sleep')
    },
    color: '#3F4FA8',
    tint: '#E2E5F5',
    icon: svg(<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />),
  },
  nutrition: {
    get label() {
      return tr('common.behaviour.nutrition')
    },
    color: '#8A4B0F',
    tint: '#F6E9DC',
    icon: svg(<path d="M4 11h16v3a6 6 0 0 1-6 6h-4a6 6 0 0 1-6-6zM2 11h20" />),
  },
  recovery: {
    get label() {
      return tr('common.behaviour.recovery')
    },
    color: '#6E4A8E',
    tint: '#EDE6F3',
    icon: svg(<path d="M3 8h11a3 3 0 1 0-3-3M3 12h15a3 3 0 1 1-3 3M3 16h7" />),
  },
  smoking: {
    get label() {
      return tr('common.behaviour.smoking')
    },
    color: '#5A6A60',
    tint: '#E6EBE4',
    icon: svg(<path d="M2 16h15v3H2zM18 16h1.5v3H18zM21 16h1v3h-1M18 8c0-2.5-2-2.5-2-5M21 8c0-2.5-2-2.5-2-5" />),
  },
}

/** UI goal labels ↔ backend behaviours. */
const GOALS: Behaviour[] = ['movement', 'sleep', 'nutrition', 'recovery', 'smoking']
export const GOAL_OPTIONS: { value: Behaviour; label: string }[] = GOALS.map((value) => ({
  value,
  get label() {
    return tr(`common.goal.${value}`)
  },
}))

export const WINDOW_LABEL: Record<string, string> = labels('common.window', ['morning', 'afternoon', 'evening'])

export function formatHour(hour: number): string {
  const h = ((hour % 24) + 24) % 24
  const suffix = tr(h < 12 ? 'common.am' : 'common.pm')
  const h12 = h % 12 === 0 ? 12 : h % 12
  return `${h12} ${suffix}`
}

/** Habit strength comes as 0–1; the rings show 0–100. */
export const pct = (h: number | undefined) => Math.round((h ?? 0) * 100)
