import React, { useMemo, useState } from 'react'
import { ScreenProps } from '../types'
import { api, Behaviour, ExportOut, PlanOut, TodayOut } from '../api/client'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { ScreenFrame } from '../components/ScreenFrame'
import { PlanSummary } from '../components/PlanSummary'
import { LoadingView, ErrorView } from '../components/StatusViews'
import { BEHAVIOUR_STYLE } from '../lib/behaviour'
import { BARRIER_LABEL, OUTCOME_LABEL, DayRecord, addDays, buildDays, dateKey, onboardDate } from '../lib/history'
import { useAsync } from '../lib/useAsync'

const WEEKDAYS = ['S', 'M', 'T', 'W', 'T', 'F', 'S']

// Gentle lines for days without a coaching message of their own (rotated by date, no tracking involved).
const THOUGHTS = [
  'Small steps still count. Picking it up again is the skill that matters.',
  'A smaller version of a step is still a step.',
  "Rest is part of the plan, not a break from it.",
  'You don\'t have to feel motivated to start. Starting tends to bring the motivation.',
  'Missed a day? Your progress fades slowly. It never drops to zero.',
]

/** A small mark per behaviour: filled = done, half = smaller version, ring = skipped / no answer, dash = paused. */
const OutcomeMark: React.FC<{ behaviour?: Behaviour | null; outcome: string; size?: number }> = ({ behaviour, outcome, size = 7 }) => {
  const color = behaviour ? BEHAVIOUR_STYLE[behaviour].color : '#5A6A60'
  const base = { width: size, height: size, borderRadius: size }
  if (outcome === 'completed') return <span style={{ ...base, background: color }} />
  if (outcome === 'partial')
    return <span style={{ ...base, background: `linear-gradient(90deg, ${color} 50%, transparent 50%)`, border: `1px solid ${color}` }} />
  if (outcome === 'paused' || outcome === 'illness') return <span style={{ width: size, height: 2, background: '#9AA79E' }} />
  return <span style={{ ...base, border: '1.5px solid #9AA79E', boxSizing: 'border-box' }} />
}

const sameMonth = (a: Date, b: Date) => a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth()

/** "My plan" tab: calendar of past days, a thought for today, tomorrow's focus, and the plan's reasons. */
export const MyPlanScreen: React.FC<ScreenProps> = ({ state, setState, onNavigate }) => {
  const session = state.session!
  const data = useAsync(
    () => Promise.all([api.exportData(session), api.plan(session), api.today(session)]) as Promise<[ExportOut, PlanOut, TodayOut]>,
    [session, state.dataVersion],
  )
  const [exp, plan, today] = data.data ?? [null, null, null]

  const days = useMemo(() => (exp ? buildDays(exp) : new Map<string, DayRecord>()), [exp])
  const now = new Date()
  const start = exp ? onboardDate(exp) : now
  const todayDate = exp ? addDays(start, exp.state.day - 1) : now

  const [month, setMonth] = useState<Date | null>(null)
  const shownMonth = month ?? new Date(todayDate.getFullYear(), todayDate.getMonth(), 1)
  const [selected, setSelected] = useState<string | null>(null)
  const selectedKey = selected ?? dateKey(todayDate)
  const selectedDay = days.get(selectedKey)

  // Technique names for the selected day's steps (one small call per step, from /actions/{id}/explain).
  const actionIds = (selectedDay?.logs ?? []).map((l) => l.action_id).filter(Boolean) as string[]
  const techniques = useAsync(
    async () =>
      Object.fromEntries(
        await Promise.all(actionIds.map(async (id) => [id, (await api.explain(id, state.language)).bct_name] as const)),
      ) as Record<string, string>,
    [actionIds.join(','), state.language],
  )

  const firstCell = new Date(shownMonth.getFullYear(), shownMonth.getMonth(), 1 - shownMonth.getDay())
  const cells = Array.from({ length: 42 }, (_, i) => addDays(firstCell, i))
  const canPrev = shownMonth > new Date(start.getFullYear(), start.getMonth(), 1)
  const canNext = shownMonth < new Date(todayDate.getFullYear(), todayDate.getMonth(), 1)

  const reason = exp?.profile.history?.motivation_reason
  const thought = today?.messages?.[0] ?? THOUGHTS[(todayDate.getDate() + todayDate.getMonth()) % THOUGHTS.length]
  const flags = exp?.state.context_flags ?? []

  return (
    <ScreenFrame
      tab="plan"
      onNavigate={onNavigate}
      onHelp={() => {
        setState((prev) => ({ ...prev, careReason: 'help' }))
        onNavigate('care')
      }}
      background={
        <>
          <TatreezPattern width={230} height={230} style={{ right: -110, bottom: 60, opacity: 0.07 }} />
          <ArabicCalligraphyRing width={440} height={440} style={{ left: -250, top: -150, opacity: 0.1 }} />
        </>
      }
    >
      <header className="p-6 pt-10 pb-2">
        <h1 className="m-0 font-display tracking-tight text-[28px] font-semibold">My plan</h1>
        <p className="m-0 text-[14px] text-[#3F4F45]">Your days so far, and what's next.</p>
      </header>

      {data.loading && !data.data && <LoadingView />}
      {data.error && <ErrorView message={data.error} onRetry={data.reload} />}

      {exp && plan && (
        <div className="px-6 pb-6 flex flex-col gap-3">
          {/* Thought for today */}
          <section className="rounded-[20px] p-4 bg-[#263A30] text-white flex flex-col gap-2">
            <span className="text-[12px] font-semibold text-[#A2C7B0]">Thought for today</span>
            <p className="m-0 text-[15px] leading-relaxed">{thought}</p>
            {reason && (
              <p className="m-0 text-[13px] leading-relaxed text-[#DDE9E0]">
                You told us why this matters: <em>"{reason}"</em>
              </p>
            )}
          </section>

          {/* Calendar */}
          <section aria-label="Calendar" className="bg-white/90 rounded-[20px] p-3.5 shadow-card">
            <div className="flex items-center justify-between mb-2">
              <button
                type="button"
                disabled={!canPrev}
                onClick={() => setMonth(new Date(shownMonth.getFullYear(), shownMonth.getMonth() - 1, 1))}
                aria-label="Previous month"
                className="w-9 h-9 rounded-full bg-transparent border-0 cursor-pointer disabled:opacity-30 text-[#1B2A22]"
              >
                ‹
              </button>
              <span className="text-[15px] font-semibold">
                {shownMonth.toLocaleDateString(state.language === 'ar' ? 'ar-AE' : 'en-GB', { month: 'long', year: 'numeric' })}
              </span>
              <button
                type="button"
                disabled={!canNext}
                onClick={() => setMonth(new Date(shownMonth.getFullYear(), shownMonth.getMonth() + 1, 1))}
                aria-label="Next month"
                className="w-9 h-9 rounded-full bg-transparent border-0 cursor-pointer disabled:opacity-30 text-[#1B2A22]"
              >
                ›
              </button>
            </div>
            <div className="grid grid-cols-7 gap-1 text-center">
              {WEEKDAYS.map((w, i) => (
                <span key={i} className="text-[11px] text-[#5A6A60] pb-1">
                  {w}
                </span>
              ))}
              {cells.map((d) => {
                const key = dateKey(d)
                const rec = days.get(key)
                const inMonth = sameMonth(d, shownMonth)
                const isToday = key === dateKey(todayDate)
                const isSel = key === selectedKey
                return (
                  <button
                    key={key}
                    type="button"
                    disabled={!rec}
                    onClick={() => setSelected(key)}
                    aria-label={d.toDateString()}
                    aria-pressed={isSel}
                    className={`min-h-[44px] rounded-[10px] flex flex-col items-center justify-start pt-1 gap-1 border-0 ${
                      rec ? 'cursor-pointer' : 'cursor-default'
                    } ${isSel ? 'bg-[#DDE9E0]' : 'bg-transparent'} ${isToday ? 'ring-2 ring-[#3E6B53]' : ''} ${
                      inMonth ? '' : 'opacity-30'
                    }`}
                  >
                    <span className={`text-[12px] ${rec ? 'text-[#1B2A22] font-medium' : 'text-[#9AA79E]'}`}>{d.getDate()}</span>
                    <span className="flex gap-[2px] flex-wrap justify-center max-w-[34px]">
                      {rec?.logs.map((l, i) => (
                        <OutcomeMark key={i} behaviour={l.behaviour} outcome={l.outcome} />
                      ))}
                    </span>
                  </button>
                )
              })}
            </div>
            <div className="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-[#5A6A60]">
              <span className="flex items-center gap-1">
                <OutcomeMark behaviour="movement" outcome="completed" /> Done
              </span>
              <span className="flex items-center gap-1">
                <OutcomeMark behaviour="movement" outcome="partial" /> Smaller version
              </span>
              <span className="flex items-center gap-1">
                <OutcomeMark outcome="skipped" /> Skipped
              </span>
              <span className="flex items-center gap-1">
                <OutcomeMark outcome="paused" /> Paused
              </span>
              <span>Colour = habit</span>
            </div>
          </section>

          {/* Selected day */}
          {selectedDay && (
            <section className="bg-white/90 rounded-[20px] p-4 shadow-card flex flex-col gap-2">
              <h2 className="m-0 text-[15px] font-semibold">
                {selectedDay.date.toLocaleDateString(state.language === 'ar' ? 'ar-AE' : 'en-GB', {
                  weekday: 'long',
                  day: 'numeric',
                  month: 'long',
                })}
                {selectedKey === dateKey(todayDate) && <span className="font-normal text-[#5A6A60]"> · today</span>}
              </h2>
              {selectedDay.logs.length === 0 && (
                <p className="m-0 text-[14px] text-[#3F4F45]">
                  {selectedKey === dateKey(todayDate) ? 'Nothing answered yet today.' : 'No steps recorded this day.'}
                </p>
              )}
              {selectedDay.logs.map((l, i) => {
                const st = l.behaviour ? BEHAVIOUR_STYLE[l.behaviour] : null
                return (
                  <div key={i} className="flex items-center gap-2.5">
                    <OutcomeMark behaviour={l.behaviour} outcome={l.outcome} size={10} />
                    <span className="flex-1 text-[14px]">
                      <strong style={{ color: st?.color }}>{st?.label ?? 'Step'}</strong> · {OUTCOME_LABEL[l.outcome] ?? l.outcome}
                      {l.action_id && techniques.data?.[l.action_id] && (
                        <span className="block text-[12px] text-[#5A6A60]">Technique: {techniques.data[l.action_id]}</span>
                      )}
                    </span>
                  </div>
                )
              })}
              {selectedDay.checkins.map((b, i) => (
                <p key={i} className="m-0 text-[13px] text-[#3F4F45]">
                  Check-in: {b.length ? b.map((x) => BARRIER_LABEL[x] ?? x).join(', ') : 'in your own words'}
                </p>
              ))}
            </section>
          )}

          {/* Tomorrow */}
          <section className="bg-white/90 rounded-[20px] p-4 shadow-card flex flex-col gap-2">
            <h2 className="m-0 text-[15px] font-semibold">Tomorrow</h2>
            <div className="flex flex-wrap gap-1.5">
              {plan.behaviours.map((b) => (
                <span
                  key={b}
                  className="px-2.5 py-1 rounded-full text-[12px] font-semibold"
                  style={{ background: BEHAVIOUR_STYLE[b].tint, color: BEHAVIOUR_STYLE[b].color }}
                >
                  {BEHAVIOUR_STYLE[b].label}
                </span>
              ))}
            </div>
            {flags.includes('ramadan') && <p className="m-0 text-[13px] text-[#2E2563]">Ramadan: steps stay fasting-friendly.</p>}
            {flags.includes('heat') && <p className="m-0 text-[13px] text-[#8A4B0F]">Hot weather: outdoor steps move indoors or to cooler hours.</p>}
            <p className="m-0 text-[12px] leading-relaxed text-[#5A6A60]">
              Your exact steps are picked each morning, based on how today goes. That's how the plan adapts to you.
            </p>
          </section>

          {/* The plan itself */}
          <h2 className="m-0 mt-1 text-[15px] font-semibold">Your plan</h2>
          <PlanSummary plan={plan} />
        </div>
      )}
    </ScreenFrame>
  )
}
