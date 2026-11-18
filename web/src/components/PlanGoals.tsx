import React from 'react'
import { api, ApiError, GoalOut, RecapFacts, Session } from '../api/client'
import { BEHAVIOUR_STYLE } from '../lib/behaviour'
import { useAsync } from '../lib/useAsync'

/** One card per goal (plan.goals): level, good days to the next level, the last change and today's note.
 *  All texts come from the API in the user's language and reading level. It counts forward, never a streak. */
export const GoalCards: React.FC<{ goals: GoalOut[] }> = ({ goals }) => (
  <div className="flex flex-col gap-2.5">
    {goals.map((g) => {
      const st = BEHAVIOUR_STYLE[g.behaviour]
      const toNext = g.good_days_to_next ?? null
      return (
        <section key={g.behaviour} aria-label={st.label} className="bg-white/95 rounded-[20px] shadow-card p-3.5 px-4 flex flex-col gap-1.5">
          <div className="flex items-center gap-3">
            <span className="w-9 h-9 rounded-full flex items-center justify-center flex-none" style={{ background: st.tint, color: st.color }}>
              {st.icon}
            </span>
            <span className="flex-1 text-[15px] font-semibold">{st.label}</span>
            <span className="text-[13px] font-semibold" style={{ color: st.color }}>
              Level {g.tier}
            </span>
          </div>
          {toNext !== null && (
            <p className="m-0 text-[13px] text-[#3F4F45]">
              {toNext <= 1 ? 'One more good day' : `${toNext} more good days`} to level {g.tier + 1}
            </p>
          )}
          {g.today_note && <p className="m-0 text-[13px] font-medium text-[#2E2563]">{g.today_note}</p>}
          {g.last_change && <p className="m-0 text-[13px] text-[#3F4F45]">{g.last_change.reason}</p>}
          <p className="m-0 text-[12px] text-[#5A6A60]">{g.start_reason}</p>
        </section>
      )
    })}
  </div>
)

const HOW: Record<RecapFacts['goals'][number]['how'], string> = {
  mostly_done: 'mostly done',
  mixed: 'mixed',
  mostly_missed: 'mostly missed',
  no_steps: 'no steps yet',
}

/** Weekly recap (GET /recap): the server's 2–3 sentences and one word per goal. Hidden while coaching is paused
 *  after a safety concern (409) or if the recap can't be loaded. No numbers, no streaks. */
export const RecapCard: React.FC<{ session: Session; version: number }> = ({ session, version }) => {
  const recap = useAsync(
    () => api.recap(session).catch((e) => (e instanceof ApiError ? null : Promise.reject(e))),
    [session, version],
  )
  if (!recap.data) return null
  const facts = recap.data.facts as unknown as RecapFacts
  return (
    <section aria-label="Your week" className="rounded-[20px] p-4 bg-white/95 shadow-card flex flex-col gap-2">
      <h2 className="m-0 text-[15px] font-semibold">Your week</h2>
      <p className="m-0 text-[14px] leading-relaxed text-[#3F4F45]">{recap.data.summary}</p>
      <ul className="m-0 p-0 list-none flex flex-wrap gap-1.5">
        {facts.goals.map((g) => {
          const st = BEHAVIOUR_STYLE[g.behaviour]
          return (
            <li key={g.behaviour} className="px-2.5 py-1 rounded-full text-[12px] font-semibold" style={{ background: st.tint, color: st.color }}>
              {st.label}: {HOW[g.how]}
            </li>
          )
        })}
      </ul>
    </section>
  )
}
