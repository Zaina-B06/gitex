import React from 'react'
import type { Behaviour } from '../api/client'
import { BEHAVIOUR_STYLE, pct } from '../lib/behaviour'

const R = 16
const CIRC = 2 * Math.PI * R

/** One ring per behaviour from `habit_strength` (0–1). Strength fades slowly and never resets. */
export const HabitRings: React.FC<{ strength: Record<string, number> }> = ({ strength }) => {
  const entries = Object.entries(strength).filter(([b]) => b in BEHAVIOUR_STYLE) as [Behaviour, number][]
  if (entries.length === 0) return null
  return (
    <section
      aria-label="Habit strength"
      className="mx-6 mt-2.5 p-2.5 px-3 bg-white/90 rounded-[20px] flex justify-between items-center gap-2 shadow-card"
    >
      <div className="flex gap-3 flex-wrap">
        {entries.map(([b, h]) => {
          const st = BEHAVIOUR_STYLE[b]
          const value = pct(h)
          return (
            <div key={b} className="flex flex-col items-center gap-0.5">
              <svg width="40" height="40" viewBox="0 0 40 40" role="img" aria-label={`${st.label} habit strength ${value} percent`}>
                <circle cx="20" cy="20" r={R} fill="none" stroke={st.tint} strokeWidth="5" />
                <circle
                  cx="20"
                  cy="20"
                  r={R}
                  fill="none"
                  stroke={st.color}
                  strokeWidth="5"
                  strokeLinecap="round"
                  strokeDasharray={`${(value / 100) * CIRC} ${CIRC}`}
                  transform="rotate(-90 20 20)"
                />
                <text x="20" y="24" textAnchor="middle" fontSize="10" fontWeight="600" fill="#1B2A22">
                  {value}
                </text>
              </svg>
              <span className="text-[11px] text-[#5A6A60]">{st.label}</span>
            </div>
          )
        })}
      </div>
      <p className="m-0 w-[92px] text-[11px] leading-[1.35] text-[#3F4F45]">
        Fades slowly, <strong className="text-[#1B2A22]">never resets to zero</strong>.
      </p>
    </section>
  )
}
