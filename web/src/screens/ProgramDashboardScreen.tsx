import React, { useState } from 'react'
import { ScreenId, AppState } from '../types'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'

interface ProgramDashboardScreenProps {
  state: AppState
  setState: React.Dispatch<React.SetStateAction<AppState>>
  onNavigate: (screen: ScreenId) => void
  showToast: (msg: string) => void
}

export const ProgramDashboardScreen: React.FC<ProgramDashboardScreenProps> = ({
  onNavigate,
  showToast,
}) => {
  const [timeRange, setTimeRange] = useState<'This week' | 'Last week' | 'Last 30 days'>('This week')
  const [dropdownOpen, setDropdownOpen] = useState(false)

  // Dynamic metrics based on timeframe
  const metrics = {
    'This week': { enrolled: 312, active: '61%', slipping: '14%', returned: '47 people' },
    'Last week': { enrolled: 308, active: '59%', slipping: '16%', returned: '42 people' },
    'Last 30 days': { enrolled: 312, active: '64%', slipping: '12%', returned: '118 people' },
  }[timeRange]

  return (
    <div className="relative overflow-hidden isolation-auto box-border min-h-[900px] w-full max-w-[1240px] mx-auto bg-[#EEF1EA] font-sans text-[#1B2A22] p-6 sm:p-7 shadow-2xl rounded-3xl">
      {/* Background SVG motifs */}
      <TatreezPattern
        width={360}
        height={360}
        style={{ right: '-50px', top: '170px', opacity: 0.07 }}
      />
      <ArabicCalligraphyRing
        width={680}
        height={680}
        style={{ right: '-200px', top: '-220px', opacity: 0.12 }}
      />
      <ArabicCalligraphyRing
        width={520}
        height={520}
        style={{ left: '-230px', bottom: '-200px', opacity: 0.09 }}
      />

      <div className="max-w-[1220px] mx-auto flex flex-col gap-5">
        {/* Header */}
        <header className="flex flex-wrap justify-between items-end gap-3">
          <div className="flex flex-col gap-1">
            <div className="flex items-center gap-3">
              <span className="text-[13px] text-[#5A6A60]">Rebound · Program view</span>
              <button
                type="button"
                onClick={() => onNavigate('today')}
                className="text-xs text-[#3E6B53] underline font-medium hover:text-[#2C5140]"
              >
                ← Back to Mobile App
              </button>
            </div>
            <h1 className="m-0 font-display tracking-tight text-[32px] font-semibold text-[#1B2A22]">
              Workplace wellbeing pilot
            </h1>
          </div>

          <div className="flex flex-wrap gap-2 items-center relative">
            <div className="relative">
              <button
                type="button"
                onClick={() => setDropdownOpen(!dropdownOpen)}
                className="min-h-[44px] px-4 rounded-[14px] border border-[#C5D0C7] bg-white text-[14px] text-[#1B2A22] hover:bg-[#F3F7F4] flex items-center gap-1.5 transition-colors shadow-sm"
              >
                <span>{timeRange}</span>
                <span className="text-xs">▾</span>
              </button>

              {dropdownOpen && (
                <>
                  <div className="fixed inset-0 z-30" onClick={() => setDropdownOpen(false)} />
                  <div className="absolute right-0 mt-1 w-36 bg-white rounded-xl shadow-xl border border-[#C5D0C7] py-1 z-40">
                    {(['This week', 'Last week', 'Last 30 days'] as const).map((opt) => (
                      <button
                        key={opt}
                        type="button"
                        onClick={() => {
                          setTimeRange(opt)
                          setDropdownOpen(false)
                          showToast(`Loaded data for ${opt}`)
                        }}
                        className={`w-full text-left px-3 py-2 text-xs hover:bg-[#DDE9E0] transition-colors ${
                          timeRange === opt ? 'font-bold text-[#2C5140] bg-[#DDE9E0]/40' : ''
                        }`}
                      >
                        {opt}
                      </button>
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        </header>

        {/* 4 Metric Cards */}
        <section
          aria-label="Key numbers"
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3"
        >
          <div className="bg-white/90 rounded-[20px] p-4.5 flex flex-col gap-1.5 shadow-[0_1px_2px_rgba(38,58,48,0.06),0_10px_28px_-14px_rgba(38,58,48,0.22)]">
            <span className="text-[13px] text-[#5A6A60]">Enrolled</span>
            <span className="font-display tracking-tight text-[32px] font-semibold text-[#1B2A22]">
              {metrics.enrolled}
            </span>
          </div>

          <div className="bg-white/90 rounded-[20px] p-4.5 flex flex-col gap-1.5 shadow-[0_1px_2px_rgba(38,58,48,0.06),0_10px_28px_-14px_rgba(38,58,48,0.22)]">
            <span className="text-[13px] text-[#5A6A60]">Active this week</span>
            <span className="font-display tracking-tight text-[32px] font-semibold text-[#1B2A22]">
              {metrics.active}
            </span>
          </div>

          <div className="bg-white/90 rounded-[20px] p-4.5 flex flex-col gap-1.5 shadow-[0_1px_2px_rgba(38,58,48,0.06),0_10px_28px_-14px_rgba(38,58,48,0.22)]">
            <span className="text-[13px] text-[#5A6A60]">Slipping right now</span>
            <span className="font-display tracking-tight text-[32px] font-semibold text-[#9A4A00]">
              {metrics.slipping}
            </span>
            <span className="text-[12px] text-[#5A6A60]">offered an easier plan automatically</span>
          </div>

          <div className="bg-white/90 rounded-[20px] p-4.5 flex flex-col gap-1.5 shadow-[0_1px_2px_rgba(38,58,48,0.06),0_10px_28px_-14px_rgba(38,58,48,0.22)]">
            <span className="text-[13px] text-[#5A6A60]">Came back after a slip (30 days)</span>
            <span className="font-display tracking-tight text-[32px] font-semibold text-[#3E6B53]">
              {metrics.returned}
            </span>
          </div>
        </section>

        {/* Middle Two-Column Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Group breakdown table */}
          <section
            aria-labelledby="barriers-title"
            className="lg:col-span-8 bg-white/90 rounded-[20px] p-5 flex flex-col gap-3.5 shadow-[0_1px_2px_rgba(38,58,48,0.06),0_10px_28px_-14px_rgba(38,58,48,0.22)]"
          >
            <h2 id="barriers-title" className="m-0 text-[16px] font-semibold text-[#1B2A22]">
              What's getting in the way, by group
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-[14px]">
                <thead>
                  <tr className="text-left text-[#5A6A60]">
                    <th scope="col" className="py-2 pr-2 font-medium">Group</th>
                    <th scope="col" className="p-2 font-medium">People</th>
                    <th scope="col" className="p-2 font-medium">Top reason</th>
                    <th scope="col" className="p-2 font-medium">Second reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#DCE3DA]">
                  <tr>
                    <td className="py-2.5 pr-2 font-medium text-[#1B2A22]">Shift workers</td>
                    <td className="p-2.5">84</td>
                    <td className="p-2.5">Tired (38%)</td>
                    <td className="p-2.5">Schedule changed (22%)</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 pr-2 font-medium text-[#1B2A22]">Outdoor and site workers</td>
                    <td className="p-2.5">61</td>
                    <td className="p-2.5 text-[#9A4A00] font-medium">Too hot (41%)</td>
                    <td className="p-2.5">Tired (24%)</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 pr-2 font-medium text-[#1B2A22]">Office staff</td>
                    <td className="p-2.5">139</td>
                    <td className="p-2.5">No time (35%)</td>
                    <td className="p-2.5">Forgot (19%)</td>
                  </tr>
                  <tr>
                    <td className="py-2.5 pr-2 font-medium text-[#1B2A22]">Caregivers</td>
                    <td className="p-2.5">28</td>
                    <td className="p-2.5">Family things (44%)</td>
                    <td className="p-2.5">No time (30%)</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <p className="m-0 p-3 px-3.5 rounded-xl bg-[#DDE9E0] text-[#2C5140] text-[14px] leading-relaxed">
              <strong>Suggested action:</strong> outdoor workers report heat most. Consider an
              indoor activity space or cooler shift-change times.
            </p>
          </section>

          {/* Equity Chart */}
          <section
            aria-labelledby="fair-title"
            className="lg:col-span-4 bg-white/90 rounded-[20px] p-5 flex flex-col gap-3.5 shadow-[0_1px_2px_rgba(38,58,48,0.06),0_10px_28px_-14px_rgba(38,58,48,0.22)]"
          >
            <h2 id="fair-title" className="m-0 text-[16px] font-semibold text-[#1B2A22]">
              Is everyone benefiting?
            </h2>
            <p className="m-0 text-[13px] text-[#5A6A60]">Active this week, by language</p>

            <div className="flex flex-col gap-2.5">
              <div className="flex flex-col gap-1">
                <div className="flex justify-between text-[13px]">
                  <span>Arabic</span>
                  <span className="font-semibold">63%</span>
                </div>
                <div className="h-2.5 rounded-full bg-[#E6EBE4] overflow-hidden">
                  <div className="w-[63%] h-full rounded-full bg-[#3E6B53]" />
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <div className="flex justify-between text-[13px]">
                  <span>English</span>
                  <span className="font-semibold">60%</span>
                </div>
                <div className="h-2.5 rounded-full bg-[#E6EBE4] overflow-hidden">
                  <div className="w-[60%] h-full rounded-full bg-[#3E6B53]" />
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <div className="flex justify-between text-[13px]">
                  <span>South Asian languages</span>
                  <span className="font-semibold">58%</span>
                </div>
                <div className="h-2.5 rounded-full bg-[#E6EBE4] overflow-hidden">
                  <div className="w-[58%] h-full rounded-full bg-[#3E6B53]" />
                </div>
              </div>
            </div>

            <p className="m-0 text-[13px] leading-relaxed text-[#3F4F45]">
              Gap between best and worst group: <strong>5 pts</strong>. We flag any gap over 10 pts.
            </p>
          </section>
        </div>

        {/* Bottom Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Why We Expect This To Work */}
          <section
            aria-labelledby="evidence-title"
            className="relative overflow-hidden isolation-auto bg-[#263A30] text-white rounded-2xl p-5 flex flex-col gap-2.5 shadow-sm"
          >
            <TatreezPattern
              width={220}
              height={220}
              color="#9DBBA5"
              opacity={0.16}
              style={{ right: '-60px', bottom: '-70px' }}
            />
            <h2 id="evidence-title" className="m-0 text-[16px] font-semibold text-white">
              Why we expect this to work
            </h2>
            <p className="m-0 text-[14px] leading-relaxed text-[#DCE7E0]">
              In simulation (300 people × 90 days × 7 situations), compared with a typical streak
              app, Rebound brought back <strong className="text-white">18 points more people within 14 days</strong> of
              a lapse, with <strong className="text-white">0 unsafe suggestions</strong>. That gap
              depends on our assumption that streak resets make people give up.
            </p>
            <p className="m-0 text-[14px] leading-relaxed text-[#DCE7E0]">
              <strong className="text-white">Where it doesn't help:</strong> against a kind, fixed
              plan, Rebound is about equal on engagement, with no reliable recovery edge (it does
              lead to more activity). The smart step-picker adds nothing measurable. Simulated, not
              real users; a pilot would measure it for real.
            </p>
          </section>

          {/* Privacy By Design */}
          <section
            aria-labelledby="privacy-title"
            className="bg-white/90 rounded-[20px] p-5 flex flex-col gap-2.5 shadow-[0_1px_2px_rgba(38,58,48,0.06),0_10px_28px_-14px_rgba(38,58,48,0.22)]"
          >
            <h2 id="privacy-title" className="m-0 text-[16px] font-semibold text-[#1B2A22]">
              Privacy by design
            </h2>
            <ul className="m-0 pl-4.5 text-[14px] leading-relaxed text-[#3F4F45] list-disc space-y-1">
              <li>Only group totals. No names, no individual data, ever.</li>
              <li>Groups under 10 people are hidden.</li>
              <li>Health answers are never shown to the organisation.</li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  )
}
