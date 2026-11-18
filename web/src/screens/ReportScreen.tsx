import React, { useMemo, useState } from 'react'
import { CartesianGrid, Legend, Line, LineChart, XAxis, YAxis } from 'recharts'
import { ScreenProps } from '../types'
import { api, Behaviour, ExportOut, PlanOut } from '../api/client'
import { ScreenFrame } from '../components/ScreenFrame'
import { LoadingView, ErrorView } from '../components/StatusViews'
import { BEHAVIOUR_STYLE, pct } from '../lib/behaviour'
import { BARRIER_LABEL, DayRecord, OUTCOME_LABEL, addDays, buildDays, dateKey, onboardDate } from '../lib/history'
import { useAsync } from '../lib/useAsync'

type Period = 7 | 30 | 'all'

const fmt = (d: Date) => d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })

/** Plain words for how often a habit was done in a week (no counters, CLAUDE.md §2.1). */
function howOften(logs: DayRecord['logs'][]): string {
  const total = logs.length
  if (!total) return 'no steps yet'
  const score = logs.reduce((s, ls) => s + (ls.some((l) => l.outcome === 'completed') ? 1 : ls.some((l) => l.outcome === 'partial') ? 0.5 : 0), 0)
  const share = score / total
  if (share >= 0.7) return 'most days'
  if (share >= 0.4) return 'about half the days'
  if (share > 0) return 'some days'
  return 'a quieter week'
}

function csvCell(v: string | number): string {
  const s = String(v)
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s
}

/** Progress report built on this device from GET /export: save as PDF (print) or download a CSV. */
export const ReportScreen: React.FC<ScreenProps> = ({ state, onNavigate, showToast }) => {
  const session = state.session!
  const data = useAsync(
    () => Promise.all([api.exportData(session), api.plan(session)]) as Promise<[ExportOut, PlanOut]>,
    [session, state.dataVersion],
  )
  const [period, setPeriod] = useState<Period>(30)
  const [exp, plan] = data.data ?? [null, null]

  const report = useMemo(() => {
    if (!exp) return null
    const all = [...buildDays(exp).values()].sort((a, b) => a.day - b.day)
    const days = period === 'all' ? all : all.slice(-period)
    const behaviours = exp.profile.basics.goals as Behaviour[]
    // Weeks of 7 days, oldest first.
    const weeks: DayRecord[][] = []
    for (let i = 0; i < days.length; i += 7) weeks.push(days.slice(i, i + 7))
    // Habit-strength trend: the engine keeps the last 15 daily values per behaviour.
    const h = (exp.state.h_daily ?? {}) as Record<string, number[]>
    const len = Math.max(0, ...Object.values(h).map((v) => v.length))
    const lastDate = addDays(onboardDate(exp), exp.state.day - 1)
    const trend = Array.from({ length: len }, (_, i) => {
      const row: Record<string, string | number> = {
        date: addDays(lastDate, i - len + 1).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' }),
      }
      for (const b of behaviours) {
        const v = h[b]
        if (v && v.length >= len - i) row[b] = pct(v[v.length - (len - i)])
      }
      return row
    })
    const checkins = days.flatMap((d) => d.checkins.map((b) => ({ date: d.date, barriers: b })))
    return { days, behaviours, weeks, trend, checkins }
  }, [exp, period])

  const downloadCsv = () => {
    if (!report) return
    const rows: (string | number)[][] = [['date', 'day', 'habit', 'outcome', 'details']]
    for (const d of report.days) {
      for (const l of d.logs)
        rows.push([dateKey(d.date), d.day, l.behaviour ? BEHAVIOUR_STYLE[l.behaviour].label : '', OUTCOME_LABEL[l.outcome] ?? l.outcome, ''])
      for (const b of d.checkins)
        rows.push([dateKey(d.date), d.day, 'check-in', '', b.map((x) => BARRIER_LABEL[x] ?? x).join('; ')])
    }
    const blob = new Blob([rows.map((r) => r.map(csvCell).join(',')).join('\n')], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `rebound-history-${dateKey(new Date())}.csv`
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
    showToast('Spreadsheet downloaded.')
  }

  const periods: { value: Period; label: string }[] = [
    { value: 7, label: 'Last 7 days' },
    { value: 30, label: 'Last 30 days' },
    { value: 'all', label: 'Everything' },
  ]

  return (
    <ScreenFrame className="bg-white text-[#1B2A22]">
      <div className="no-print sticky top-0 z-10 bg-[#EEF1EA] p-4 flex flex-col gap-2 border-b border-[#DCE3DA]">
        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => onNavigate('settings')}
            className="min-h-[40px] flex items-center gap-1 bg-transparent border-0 p-0 cursor-pointer text-[14px] font-medium text-[#3E6B53]"
          >
            ‹ Settings
          </button>
          <span className="text-[13px] font-semibold">Progress report</span>
        </div>
        <div className="flex gap-1.5" role="group" aria-label="Period">
          {periods.map((p) => (
            <button
              key={p.label}
              type="button"
              aria-pressed={period === p.value}
              onClick={() => setPeriod(p.value)}
              className={`flex-1 min-h-[34px] rounded-full text-[12px] cursor-pointer ${
                period === p.value ? 'bg-[#3E6B53] text-white font-semibold border-0' : 'bg-white border border-[#C5D0C7]'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={!report}
            onClick={() => window.print()}
            className="flex-1 min-h-[42px] rounded-[12px] bg-[#3E6B53] text-white text-[14px] font-semibold border-0 cursor-pointer disabled:opacity-60"
          >
            Save as PDF
          </button>
          <button
            type="button"
            disabled={!report}
            onClick={downloadCsv}
            className="flex-1 min-h-[42px] rounded-[12px] bg-white border border-[#C5D0C7] text-[14px] font-semibold cursor-pointer disabled:opacity-60"
          >
            Spreadsheet (CSV)
          </button>
        </div>
        <p className="m-0 text-[11px] text-[#5A6A60]">"Save as PDF": choose "Save as PDF" as the printer in the window that opens.</p>
      </div>

      {data.loading && !data.data && <LoadingView label="Building your report…" />}
      {data.error && <ErrorView message={data.error} onRetry={data.reload} />}

      {exp && plan && report && (
        <article className="p-5 flex flex-col gap-5 text-[14px] leading-relaxed">
          <header className="border-b-2 border-[#3E6B53] pb-3">
            <h1 className="m-0 font-display tracking-tight text-[24px] font-semibold text-[#2C5140]">Rebound progress report</h1>
            <p className="m-0 text-[13px] text-[#3F4F45]">
              {state.displayName ? `${state.displayName} · ` : ''}
              {report.days.length ? `${fmt(report.days[0].date)} – ${fmt(report.days[report.days.length - 1].date)}` : ''}
            </p>
            <p className="m-0 text-[12px] text-[#5A6A60]">Made on {fmt(new Date())}</p>
          </header>

          <section className="flex flex-col gap-2">
            <h2 className="m-0 text-[16px] font-semibold">Habit strength now</h2>
            <p className="m-0 text-[12px] text-[#5A6A60]">0–100. It grows with each step and fades slowly on missed days. It never resets to zero.</p>
            <table className="w-full border-collapse text-[13px]">
              <tbody>
                {report.behaviours.map((b) => {
                  const v = (exp.state.h_daily as Record<string, number[]>)?.[b] ?? []
                  const nowH = pct(exp.state.habit_strength[b])
                  const first = v.length ? pct(v[0]) : nowH
                  const change = nowH - first
                  return (
                    <tr key={b} className="border-b border-[#E6EBE4]">
                      <td className="py-1.5 font-semibold" style={{ color: BEHAVIOUR_STYLE[b].color }}>
                        {BEHAVIOUR_STYLE[b].label}
                      </td>
                      <td className="py-1.5 text-end">{nowH}</td>
                      <td className="py-1.5 text-end text-[#5A6A60]">
                        {change === 0 ? 'steady' : change > 0 ? `up ${change} recently` : `down ${-change} recently`}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
            {report.trend.length > 1 && (
              <LineChart width={340} height={190} data={report.trend} margin={{ top: 8, right: 8, bottom: 0, left: -24 }}>
                <CartesianGrid stroke="#E6EBE4" vertical={false} />
                <XAxis dataKey="date" tick={{ fontSize: 10, fill: '#5A6A60' }} interval="preserveStartEnd" />
                <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#5A6A60' }} />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                {report.behaviours.map((b) => (
                  <Line
                    key={b}
                    type="monotone"
                    dataKey={b}
                    name={BEHAVIOUR_STYLE[b].label}
                    stroke={BEHAVIOUR_STYLE[b].color}
                    strokeWidth={2}
                    dot={false}
                    isAnimationActive={false}
                  />
                ))}
              </LineChart>
            )}
          </section>

          <section className="flex flex-col gap-2">
            <h2 className="m-0 text-[16px] font-semibold">Week by week</h2>
            {report.weeks.map((w, i) => (
              <div key={i} className="break-inside-avoid">
                <h3 className="m-0 text-[13px] font-semibold text-[#3F4F45]">
                  {fmt(w[0].date)} – {fmt(w[w.length - 1].date)}
                </h3>
                <ul className="m-0 ps-5 list-disc">
                  {report.behaviours.map((b) => (
                    <li key={b}>
                      {BEHAVIOUR_STYLE[b].label}: {howOften(w.map((d) => d.logs.filter((l) => l.behaviour === b)).filter((ls) => ls.length))}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </section>

          <section className="flex flex-col gap-2">
            <h2 className="m-0 text-[16px] font-semibold">Check-ins</h2>
            {report.checkins.length === 0 ? (
              <p className="m-0 text-[#3F4F45]">No check-ins in this period.</p>
            ) : (
              <ul className="m-0 ps-5 list-disc">
                {report.checkins.map((c, i) => (
                  <li key={i}>
                    {fmt(c.date)}: {c.barriers.length ? c.barriers.map((b) => BARRIER_LABEL[b] ?? b).join(', ') : 'in your own words'}
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="flex flex-col gap-2 break-inside-avoid">
            <h2 className="m-0 text-[16px] font-semibold">Day by day</h2>
            <table className="w-full border-collapse text-[12px]">
              <thead>
                <tr className="text-start border-b border-[#C5D0C7]">
                  <th className="py-1 text-start font-semibold">Date</th>
                  <th className="py-1 text-start font-semibold">Habit</th>
                  <th className="py-1 text-start font-semibold">What happened</th>
                </tr>
              </thead>
              <tbody>
                {report.days.flatMap((d) =>
                  d.logs.map((l, i) => (
                    <tr key={`${d.day}-${i}`} className="border-b border-[#EEF1EA]">
                      <td className="py-1">{i === 0 ? fmt(d.date) : ''}</td>
                      <td className="py-1">{l.behaviour ? BEHAVIOUR_STYLE[l.behaviour].label : ''}</td>
                      <td className="py-1">{OUTCOME_LABEL[l.outcome] ?? l.outcome}</td>
                    </tr>
                  )),
                )}
              </tbody>
            </table>
          </section>

          <section className="flex flex-col gap-1 break-inside-avoid">
            <h2 className="m-0 text-[16px] font-semibold">Why your plan looks like this</h2>
            <ul className="m-0 ps-5 list-disc">
              {plan.all_reasons.map((r) => (
                <li key={r}>{r}</li>
              ))}
            </ul>
          </section>

          <footer className="pt-3 border-t border-[#DCE3DA] text-[11px] leading-snug text-[#5A6A60]">
            Made on your device from your Rebound data. It contains health information, so share it only with people you trust.
            This is not a medical document.
          </footer>
        </article>
      )}
    </ScreenFrame>
  )
}
