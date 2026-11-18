import React, { useState } from 'react'
import { Trans } from 'react-i18next'
import { ScreenProps } from '../types'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { BARRIER_LABEL } from '../lib/history'
import { tr } from '../i18n'

type Range = 'thisWeek' | 'lastWeek' | 'last30'
const RANGES: Range[] = ['thisWeek', 'lastWeek', 'last30']
const D = (key: string, vars?: Record<string, unknown>) => tr(`extra.d.${key}`, vars)
const card =
  'bg-white/90 rounded-[20px] p-4.5 flex flex-col gap-1.5 shadow-[0_1px_2px_rgba(38,58,48,0.06),0_10px_28px_-14px_rgba(38,58,48,0.22)]'

// Illustrative pilot numbers (no real organisation data); the live view is GET /dashboard/employer.
const METRICS: Record<Range, { enrolled: number; active: string; slipping: string; returned: number }> = {
  thisWeek: { enrolled: 312, active: '61%', slipping: '14%', returned: 47 },
  lastWeek: { enrolled: 308, active: '59%', slipping: '16%', returned: 42 },
  last30: { enrolled: 312, active: '64%', slipping: '12%', returned: 118 },
}
const GROUPS: { key: string; people: number; top: [string, number]; second: [string, number]; hot?: boolean }[] = [
  { key: 'shift', people: 84, top: ['energy_fatigue', 38], second: ['schedule_change', 22] },
  { key: 'outdoor', people: 61, top: ['environment', 41], second: ['energy_fatigue', 24], hot: true },
  { key: 'office', people: 139, top: ['time', 35], second: ['forgot', 19] },
  { key: 'carers', people: 28, top: ['social_family', 44], second: ['time', 30] },
]
const LANGS: [string, number][] = [['arabic', 63], ['english', 60], ['southAsian', 58]]

const reason = ([barrier, n]: [string, number]) =>
  D('reason', { reason: BARRIER_LABEL[barrier as keyof typeof BARRIER_LABEL] ?? barrier, n })

/** Workplace view (outside the user app): group totals only, never individual data. */
export const ProgramDashboardScreen: React.FC<ScreenProps> = ({ onNavigate, showToast }) => {
  const [range, setRange] = useState<Range>('thisWeek')
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const metrics = METRICS[range]

  return (
    <div className="relative overflow-hidden isolation-auto box-border min-h-[900px] w-full max-w-[1240px] mx-auto bg-[#EEF1EA] font-sans text-[#1B2A22] p-6 sm:p-7 shadow-2xl rounded-3xl">
      <TatreezPattern width={360} height={360} style={{ right: '-50px', top: '170px', opacity: 0.07 }} />
      <ArabicCalligraphyRing width={680} height={680} style={{ right: '-200px', top: '-220px', opacity: 0.12 }} />
      <ArabicCalligraphyRing width={520} height={520} style={{ left: '-230px', bottom: '-200px', opacity: 0.09 }} />

      <div className="max-w-[1220px] mx-auto flex flex-col gap-5">
        <header className="flex flex-wrap justify-between items-end gap-3">
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-3">
              <span className="text-[13px] text-[#5A6A60]">{D('kicker')}</span>
              <button type="button" onClick={() => onNavigate('today')}
                className="text-xs text-[#3E6B53] underline font-medium hover:text-[#2C5140] bg-transparent border-0 cursor-pointer">
                {D('back')}
              </button>
            </div>
            <h1 className="m-0 font-display tracking-tight text-[32px] font-semibold text-[#1B2A22]">{D('title')}</h1>
          </div>

          <div className="relative">
            <button
              type="button"
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="min-h-[44px] px-4 rounded-[14px] border border-[#C5D0C7] bg-white text-[14px] text-[#1B2A22] hover:bg-[#F3F7F4] flex items-center gap-1.5 transition-colors shadow-sm cursor-pointer"
            >
              <span>{D(range)}</span>
              <span className="text-xs">▾</span>
            </button>
            {dropdownOpen && (
              <>
                <div className="fixed inset-0 z-30" onClick={() => setDropdownOpen(false)} />
                <div className="absolute end-0 mt-1 w-40 bg-white rounded-xl shadow-xl border border-[#C5D0C7] py-1 z-40">
                  {RANGES.map((opt) => (
                    <button
                      key={opt}
                      type="button"
                      onClick={() => {
                        setRange(opt)
                        setDropdownOpen(false)
                        showToast(D('loaded', { range: D(opt) }))
                      }}
                      className={`w-full text-start px-3 py-2 text-xs hover:bg-[#DDE9E0] transition-colors bg-transparent border-0 cursor-pointer ${
                        range === opt ? 'font-bold text-[#2C5140] bg-[#DDE9E0]/40' : ''
                      }`}
                    >
                      {D(opt)}
                    </button>
                  ))}
                </div>
              </>
            )}
          </div>
        </header>

        <section aria-label={D('keyNumbers')} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <div className={card}>
            <span className="text-[13px] text-[#5A6A60]">{D('enrolled')}</span>
            <span className="font-display tracking-tight text-[32px] font-semibold">{metrics.enrolled}</span>
          </div>
          <div className={card}>
            <span className="text-[13px] text-[#5A6A60]">{D('active')}</span>
            <span className="font-display tracking-tight text-[32px] font-semibold">{metrics.active}</span>
          </div>
          <div className={card}>
            <span className="text-[13px] text-[#5A6A60]">{D('slipping')}</span>
            <span className="font-display tracking-tight text-[32px] font-semibold text-[#9A4A00]">{metrics.slipping}</span>
            <span className="text-[12px] text-[#5A6A60]">{D('slippingNote')}</span>
          </div>
          <div className={card}>
            <span className="text-[13px] text-[#5A6A60]">{D('returned')}</span>
            <span className="font-display tracking-tight text-[32px] font-semibold text-[#3E6B53]">
              {D('people', { n: metrics.returned })}
            </span>
          </div>
        </section>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <section aria-labelledby="barriers-title" className={'lg:col-span-8 p-5 gap-3.5 ' + card}>
            <h2 id="barriers-title" className="m-0 text-[16px] font-semibold">{D('barriers')}</h2>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-[14px]">
                <thead>
                  <tr className="text-start text-[#5A6A60]">
                    <th scope="col" className="py-2 pe-2 font-medium text-start">{D('group')}</th>
                    <th scope="col" className="p-2 font-medium text-start">{D('peopleCol')}</th>
                    <th scope="col" className="p-2 font-medium text-start">{D('top')}</th>
                    <th scope="col" className="p-2 font-medium text-start">{D('second')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#DCE3DA]">
                  {GROUPS.map((g) => (
                    <tr key={g.key}>
                      <td className="py-2.5 pe-2 font-medium">{D(g.key)}</td>
                      <td className="p-2.5">{g.people}</td>
                      <td className={`p-2.5 ${g.hot ? 'text-[#9A4A00] font-medium' : ''}`}>{reason(g.top)}</td>
                      <td className="p-2.5">{reason(g.second)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="m-0 p-3 px-3.5 rounded-xl bg-[#DDE9E0] text-[#2C5140] text-[14px] leading-relaxed">
              <strong>{D('suggested')}</strong> {D('suggestedText')}
            </p>
          </section>

          <section aria-labelledby="fair-title" className={'lg:col-span-4 p-5 gap-3.5 ' + card}>
            <h2 id="fair-title" className="m-0 text-[16px] font-semibold">{D('fair')}</h2>
            <p className="m-0 text-[13px] text-[#5A6A60]">{D('byLang')}</p>
            <div className="flex flex-col gap-2.5">
              {LANGS.map(([key, pctValue]) => (
                <div key={key} className="flex flex-col gap-1">
                  <div className="flex justify-between text-[13px]">
                    <span>{D(key)}</span>
                    <span className="font-semibold">{pctValue}%</span>
                  </div>
                  <div className="h-2.5 rounded-full bg-[#E6EBE4] overflow-hidden">
                    <div className="h-full rounded-full bg-[#3E6B53]" style={{ width: `${pctValue}%` }} />
                  </div>
                </div>
              ))}
            </div>
            <p className="m-0 text-[13px] leading-relaxed text-[#3F4F45]">
              <Trans i18nKey="extra.d.gap" components={{ 1: <strong /> }} />
            </p>
          </section>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <section aria-labelledby="evidence-title"
            className="relative overflow-hidden isolation-auto bg-[#263A30] text-white rounded-2xl p-5 flex flex-col gap-2.5 shadow-sm">
            <TatreezPattern width={220} height={220} color="#9DBBA5" opacity={0.16} style={{ right: '-60px', bottom: '-70px' }} />
            <h2 id="evidence-title" className="m-0 text-[16px] font-semibold text-white">{D('evidence')}</h2>
            <p className="m-0 text-[14px] leading-relaxed text-[#DCE7E0]">
              <Trans i18nKey="extra.d.evidence1"
                components={{ 1: <strong className="text-white" />, 3: <strong className="text-white" /> }} />
            </p>
            <p className="m-0 text-[14px] leading-relaxed text-[#DCE7E0]">
              <Trans i18nKey="extra.d.evidence2" components={{ 1: <strong className="text-white" /> }} />
            </p>
          </section>

          <section aria-labelledby="privacy-title" className={'p-5 gap-2.5 ' + card}>
            <h2 id="privacy-title" className="m-0 text-[16px] font-semibold">{D('privacy')}</h2>
            <ul className="m-0 ps-4.5 text-[14px] leading-relaxed text-[#3F4F45] list-disc space-y-1">
              <li>{D('privacy1')}</li>
              <li>{D('privacy2')}</li>
              <li>{D('privacy3')}</li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  )
}
