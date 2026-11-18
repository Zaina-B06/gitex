import React, { useMemo, useState } from 'react'
import { ScreenProps } from '../types'
import { api, Behaviour, ExportOut, PlanOut, TodayOut } from '../api/client'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { ScreenFrame } from '../components/ScreenFrame'
import { PlanSummary } from '../components/PlanSummary'
import { GoalCards, RecapCard } from '../components/PlanGoals'
import { LoadingView, ErrorView } from '../components/StatusViews'
import { BEHAVIOUR_STYLE } from '../lib/behaviour'
import { BARRIER_LABEL, OUTCOME_LABEL, DayRecord, addDays, buildDays, dateKey, onboardDate } from '../lib/history'
import { useAsync } from '../lib/useAsync'
import { tr } from '../i18n'

const WEEKDAYS = [0, 1, 2, 3, 4, 5, 6]
const THOUGHTS = 5 // app.plan.thought0..4: gentle lines for days without a coaching message of their own

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

/** "My plan" tab, in this order: the calendar, one card per goal, "Your week", "Why it looks like this", then a
 *  thought for today and tomorrow's focus. */
export const MyPlanScreen: React.FC<ScreenProps> = ({ state, setState, onNavigate }) => {
  const session = state.session!
  const locale = state.language === 'ar' ? 'ar-AE' : 'en-GB'
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
  const thought =
    today?.messages?.[0] ?? tr(`app.plan.thought${(todayDate.getDate() + todayDate.getMonth()) % THOUGHTS}`)
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
      <header className="p-6 pt-1 pb-2">
        <h1 className="m-0 font-display tracking-tight text-[28px] font-semibold">{tr('app.plan.title')}</h1>
        <p className="m-0 text-[14px] text-[#3F4F45]">{tr('app.plan.subtitle')}</p>
      </header>

      {data.loading && !data.data && <LoadingView />}
      {data.error && <ErrorView message={data.error} onRetry={data.reload} />}

      {exp && plan && (
        <div className="px-6 pb-6 flex flex-col gap-3">
          {/* 1. Calendar */}
          <section aria-label={tr('app.plan.calendar')} className="bg-white/90 rounded-[20px] p-3.5 shadow-card">
            <div className="flex items-center justify-between mb-2">
              <button
                type="button"
                disabled={!canPrev}
                onClick={() => setMonth(new Date(shownMonth.getFullYear(), shownMonth.getMonth() - 1, 1))}
                aria-label={tr('app.plan.prevMonth')}
                className="w-9 h-9 rounded-full bg-transparent border-0 cursor-pointer disabled:opacity-30 text-[#1B2A22]"
              >
                <span className="inline-block rtl-flip">‹</span>
              </button>
              <span className="text-[15px] font-semibold">
                {shownMonth.toLocaleDateString(locale, { month: 'long', year: 'numeric' })}
              </span>
              <button
                type="button"
                disabled={!canNext}
                onClick={() => setMonth(new Date(shownMonth.getFullYear(), shownMonth.getMonth() + 1, 1))}
                aria-label={tr('app.plan.nextMonth')}
                className="w-9 h-9 rounded-full bg-transparent border-0 cursor-pointer disabled:opacity-30 text-[#1B2A22]"
              >
                <span className="inline-block rtl-flip">›</span>
              </button>
            </div>
            <div className="grid grid-cols-7 gap-1 text-center">
              {WEEKDAYS.map((w) => (
                <span key={w} className="text-[11px] text-[#5A6A60] pb-1">
                  {tr(`app.plan.wk${w}`)}
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
                    aria-label={d.toLocaleDateString(locale, { weekday: 'long', day: 'numeric', month: 'long' })}
                    aria-pressed={isSel}
                    className={`min-h-[44px] rounded-[10px] flex flex-col items-center justify-start pt-1 gap-1 border-0 ${
                      rec ? 'cursor-pointer' : 'cursor-default'
                    } ${isSel ? 'bg-[#DDE9E0]' : 'bg-transparent'} ${isToday ? 'ring-2 ring-[#3E6B53]' : ''} ${
                      inMonth ? '' : 'opacity-30'
                    }`}
                  >
                    <span className={`text-[12px] ${rec ? 'text-[#1B2A22] font-medium' : 'text-[#9AA79E]'}`}>
                      {d.toLocaleDateString(locale, { day: 'numeric' })}
                    </span>
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
                <OutcomeMark behaviour="movement" outcome="completed" /> {tr('app.plan.legendDone')}
              </span>
              <span className="flex items-center gap-1">
                <OutcomeMark behaviour="movement" outcome="partial" /> {tr('app.plan.legendSmaller')}
              </span>
              <span className="flex items-center gap-1">
                <OutcomeMark outcome="skipped" /> {tr('app.plan.legendSkipped')}
              </span>
              <span className="flex items-center gap-1">
                <OutcomeMark outcome="paused" /> {tr('app.plan.legendPaused')}
              </span>
              <span>{tr('app.plan.legendColour')}</span>
            </div>
          </section>

          {/* The day picked on the calendar */}
          {selectedDay && (
            <section className="bg-white/90 rounded-[20px] p-4 shadow-card flex flex-col gap-2">
              <h2 className="m-0 text-[15px] font-semibold">
                {selectedDay.date.toLocaleDateString(locale, { weekday: 'long', day: 'numeric', month: 'long' })}
                {selectedKey === dateKey(todayDate) && <span className="font-normal text-[#5A6A60]">{tr('app.plan.today')}</span>}
              </h2>
              {selectedDay.logs.length === 0 && (
                <p className="m-0 text-[14px] text-[#3F4F45]">
                  {selectedKey === dateKey(todayDate) ? tr('app.plan.nothingToday') : tr('app.plan.nothingDay')}
                </p>
              )}
              {selectedDay.logs.map((l, i) => {
                const st = l.behaviour ? BEHAVIOUR_STYLE[l.behaviour] : null
                return (
                  <div key={i} className="flex items-center gap-2.5">
                    <OutcomeMark behaviour={l.behaviour} outcome={l.outcome} size={10} />
                    <span className="flex-1 text-[14px]">
                      <strong style={{ color: st?.color }}>{st?.label ?? tr('app.plan.step')}</strong> ·{' '}
                      {OUTCOME_LABEL[l.outcome] ?? l.outcome}
                      {l.action_id && techniques.data?.[l.action_id] && (
                        <span className="block text-[12px] text-[#5A6A60]">
                          {tr('app.plan.technique', { name: techniques.data[l.action_id] })}
                        </span>
                      )}
                    </span>
                  </div>
                )
              })}
              {selectedDay.checkins.map((b, i) => (
                <p key={i} className="m-0 text-[13px] text-[#3F4F45]">
                  {tr('app.plan.checkin', {
                    list: b.length
                      ? b.map((x) => BARRIER_LABEL[x] ?? x).join(state.language === 'ar' ? '، ' : ', ')
                      : tr('app.plan.ownWords'),
                  })}
                </p>
              ))}
            </section>
          )}

          {/* 2. Your goals: level, good days to the next level, what changed and why */}
          {plan.goals && plan.goals.length > 0 && <GoalCards goals={plan.goals} />}

          {/* 3. Your week (hidden while coaching is paused) */}
          <RecapCard session={session} version={state.dataVersion} />

          {/* 4. Why it looks like this */}
          <PlanSummary plan={plan} showList={false} />

          {/* Thought for today */}
          <section className="rounded-[20px] p-4 bg-[#263A30] text-white flex flex-col gap-2">
            <span className="text-[12px] font-semibold text-[#A2C7B0]">{tr('app.plan.thought')}</span>
            <p className="m-0 text-[15px] leading-relaxed">{thought}</p>
            {reason && (
              <p className="m-0 text-[13px] leading-relaxed text-[#DDE9E0]">
                {tr('app.plan.whyMatters')} <em>"{reason}"</em>
              </p>
            )}
          </section>

          {/* Tomorrow */}
          <section className="bg-white/90 rounded-[20px] p-4 shadow-card flex flex-col gap-2">
            <h2 className="m-0 text-[15px] font-semibold">{tr('app.plan.tomorrow')}</h2>
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
            {flags.includes('ramadan') && <p className="m-0 text-[13px] text-[#2E2563]">{tr('app.plan.ramadanNote')}</p>}
            {flags.includes('heat') && <p className="m-0 text-[13px] text-[#8A4B0F]">{tr('app.plan.heatNote')}</p>}
            <p className="m-0 text-[12px] leading-relaxed text-[#5A6A60]">{tr('app.plan.adaptNote')}</p>
          </section>
        </div>
      )}
    </ScreenFrame>
  )
}
