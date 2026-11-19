import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { ScreenProps } from '../types'
import { api, DashboardOutcomesData, MeasureStat, ComparisonStat } from '../api/client'
import { useAsync } from '../lib/useAsync'
import { LanguageSwitch } from '../components/LanguageSwitch'
import { useLanguageChange } from '../lib/language'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'

const MEASURES_TO_SHOW = ['recovery_rate', 'persistence_w12', 'retention', 'delta_minutes'] as const

const SCENARIO_LABELS: Record<string, string> = {
  baseline: 'res.scenario.baseline',
  ramadan_heavy: 'res.scenario.ramadan_heavy',
  hot_summer: 'res.scenario.hot_summer',
  low_checkin: 'res.scenario.low_checkin',
  high_dropout: 'res.scenario.high_dropout',
  shock_heavy: 'res.scenario.shock_heavy',
  harsh_attrition: 'res.scenario.harsh_attrition',
}

function formatArmValue(val: number, unit: string): string {
  if (unit === 'pct') return `${(val * 100).toFixed(1)}%`
  if (unit === 'min') return `${val.toFixed(1)} min`
  return `${val.toFixed(1)}`
}

function formatComparisonMean(val: number, unit: string): string {
  const sign = val >= 0 ? '+' : ''
  if (unit === 'pct') return `${sign}${(val * 100).toFixed(1)} pts`
  if (unit === 'min') return `${sign}${val.toFixed(1)} min`
  return `${sign}${val.toFixed(1)}`
}

function formatComparisonRange(low: number, high: number, unit: string): string {
  const sLow = low >= 0 ? `+${(low * (unit === 'pct' ? 100 : 1)).toFixed(1)}` : (low * (unit === 'pct' ? 100 : 1)).toFixed(1)
  const sHigh = high >= 0 ? `+${(high * (unit === 'pct' ? 100 : 1)).toFixed(1)}` : (high * (unit === 'pct' ? 100 : 1)).toFixed(1)
  const suffix = unit === 'pct' ? ' pts' : unit === 'min' ? ' min' : ''
  return `${sLow} to ${sHigh}${suffix}`
}

export const ResultsScreen: React.FC<ScreenProps> = (props) => {
  const { state, onNavigate } = props
  const { t } = useTranslation()
  const changeLanguage = useLanguageChange(props)
  const [selectedScenario, setSelectedScenario] = useState<string>('baseline')

  const { data, error, loading, reload } = useAsync<DashboardOutcomesData>(
    () => api.dashboardOutcomes(),
    [],
  )

  const isRtl = state.language === 'ar'

  // If loading or error, do not render partial or hard-coded numbers
  if (loading) {
    return (
      <div className="min-h-screen w-full bg-[#EEF1EA] text-[#1B2A22] p-6 sm:p-10 flex flex-col items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <span className="spinner" aria-hidden="true" />
          <p className="text-[15px] font-medium text-[#3F4F45]">{t('res.loading')}</p>
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="min-h-screen w-full bg-[#EEF1EA] text-[#1B2A22] p-6 sm:p-10 flex flex-col items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-2xl p-6 shadow-sm border border-[#DCE3DA] flex flex-col items-center text-center gap-4">
          <div className="w-12 h-12 rounded-full bg-[#FCE8E6] text-[#A02A1C] flex items-center justify-center text-xl font-bold">
            !
          </div>
          <h2 className="m-0 text-[18px] font-semibold text-[#1B2A22]">{t('res.error')}</h2>
          <p className="m-0 text-[14px] text-[#5A6A60]">{error || t('common.serverDown')}</p>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={reload}
              className="min-h-[44px] px-5 rounded-xl bg-[#2C5140] hover:bg-[#1E382B] text-white text-[14px] font-semibold border-0 cursor-pointer transition-colors"
            >
              {t('common.tryAgain')}
            </button>
            <button
              type="button"
              onClick={() => onNavigate('welcome')}
              className="min-h-[44px] px-4 rounded-xl bg-[#E6EBE4] hover:bg-[#DCE3DA] text-[#1B2A22] text-[14px] font-medium border-0 cursor-pointer transition-colors"
            >
              {t('common.back')}
            </button>
          </div>
        </div>
      </div>
    )
  }

  const scenarioNames = Object.keys(data.scenarios || {})
  const activeScenarioKey = scenarioNames.includes(selectedScenario) ? selectedScenario : (scenarioNames[0] || 'baseline')
  const scenario = data.scenarios?.[activeScenarioKey]

  const safetyInfo = scenario?.safety?.C
  const isSafetyZero = safetyInfo && safetyInfo.violations === 0 && safetyInfo.quiet_messages === 0

  // "Where Rebound doesn't help" items
  const noHelpItems: { label: string; text: string }[] = []
  if (scenario?.comparisons?.C_vs_A0) {
    for (const [mKey, comp] of Object.entries(scenario.comparisons.C_vs_A0)) {
      const measureLabel = data.measures?.[mKey]?.label || mKey
      if (comp.verdict === 'not shown') {
        noHelpItems.push({
          label: measureLabel,
          text: t('res.noHelp.notShown', { label: measureLabel }),
        })
      } else if (comp.verdict === 'worse') {
        const meanPts = (comp.mean * (data.measures?.[mKey]?.unit === 'pct' ? 100 : 1)).toFixed(1)
        noHelpItems.push({
          label: measureLabel,
          text: t('res.noHelp.worse', { label: measureLabel, mean: meanPts }),
        })
      }
    }
  }

  return (
    <div className="relative overflow-hidden box-border min-h-screen w-full bg-[#EEF1EA] font-sans text-[#1B2A22] p-4 sm:p-8">
      <TatreezPattern width={340} height={340} style={{ right: '-50px', top: '150px', opacity: 0.06 }} />
      <ArabicCalligraphyRing width={640} height={640} style={{ right: '-220px', top: '-240px', opacity: 0.1 }} />
      <ArabicCalligraphyRing width={480} height={480} style={{ left: '-200px', bottom: '-180px', opacity: 0.08 }} />

      <div className="max-w-[1120px] mx-auto flex flex-col gap-6">
        {/* Navigation & Header */}
        <header className="flex flex-col gap-3">
          <div className="flex items-center justify-between gap-4">
            <button
              type="button"
              onClick={() => onNavigate('welcome')}
              className="min-h-[44px] px-2 flex items-center gap-2 text-[14px] text-[#2C5140] hover:text-[#1B2A22] font-semibold bg-transparent border-0 cursor-pointer"
            >
              <span className="text-base rtl:rotate-180 transition-transform">←</span>
              <span>{t('res.back')}</span>
            </button>
            <LanguageSwitch value={state.language} onChange={changeLanguage} tone="light" />
          </div>

          <div className="flex flex-col gap-1">
            <span className="text-[13px] font-semibold text-[#5A6A60] tracking-wide uppercase">{t('res.kicker')}</span>
            <h1 className="m-0 font-display tracking-tight text-[28px] sm:text-[36px] font-bold text-[#1B2A22]">
              {t('res.title')}
            </h1>
            <p className="m-0 text-[14px] text-[#5A6A60] font-medium leading-relaxed">
              {t('res.note')}
            </p>
          </div>

          {/* Intro line */}
          <div className="p-3.5 px-4 rounded-xl bg-white/80 border border-[#DCE3DA] shadow-xs">
            <p className="m-0 text-[14px] sm:text-[15px] font-semibold text-[#2C5140]">
              {t('res.intro', {
                personas: data.personas,
                days: data.days,
                runs: data.seeds?.length ?? 0,
              })}
            </p>
          </div>
        </header>

        {/* Scenarios Chips */}
        <section aria-label={t('res.scenarios')} className="flex flex-col gap-2">
          <span className="text-[13px] font-semibold text-[#5A6A60] uppercase tracking-wider">
            {t('res.scenarios')}
          </span>
          <div className="flex flex-wrap gap-2">
            {scenarioNames.map((sName) => {
              const active = sName === activeScenarioKey
              const labelKey = SCENARIO_LABELS[sName]
              const labelText = labelKey ? t(labelKey, { defaultValue: sName }) : sName
              return (
                <button
                  key={sName}
                  type="button"
                  onClick={() => setSelectedScenario(sName)}
                  className={`min-h-[44px] px-4 py-2 rounded-full text-[13px] sm:text-[14px] font-semibold transition-all border cursor-pointer ${
                    active
                      ? 'bg-[#2C5140] text-white border-[#2C5140] shadow-sm'
                      : 'bg-white/90 text-[#3F4F45] border-[#C5D0C7] hover:bg-white hover:border-[#2C5140]'
                  }`}
                >
                  {labelText}
                </button>
              )
            })}
          </div>
        </section>

        {/* Legend */}
        <section aria-label={t('res.legend.title')} className="p-4 rounded-2xl bg-white/90 border border-[#DCE3DA] shadow-xs flex flex-wrap items-center gap-x-6 gap-y-2 text-[13px]">
          <span className="font-bold text-[#5A6A60]">{t('res.legend.title')}:</span>
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-3.5 rounded-sm bg-[#6E7D74] border border-[#525E57] flex-shrink-0" />
            <span className="text-[#2A362F] font-medium">{t('res.legend.a')}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-3.5 rounded-sm bg-[#2563EB] border border-[#1D4ED8] flex-shrink-0" />
            <span className="text-[#1E3A8A] font-medium">{t('res.legend.a0')}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3.5 h-3.5 rounded-sm bg-[#0F766E] border border-[#115E59] flex-shrink-0" />
            <span className="text-[#134E4A] font-bold">{t('res.legend.c')}</span>
          </div>
        </section>

        {/* 4 Measure Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {MEASURES_TO_SHOW.map((mKey) => {
            const meta = data.measures?.[mKey]
            const label = meta?.label || mKey
            const unit = meta?.unit || 'pct'

            const armA: MeasureStat | undefined = scenario?.arms?.A?.[mKey]
            const armA0: MeasureStat | undefined = scenario?.arms?.A0?.[mKey]
            const armC: MeasureStat | undefined = scenario?.arms?.C?.[mKey]

            const compA: ComparisonStat | undefined = scenario?.comparisons?.C_vs_A?.[mKey]
            const compA0: ComparisonStat | undefined = scenario?.comparisons?.C_vs_A0?.[mKey]

            // Compute dynamic range for the 3 arms
            const allCis: number[] = []
            if (armA) allCis.push(armA.ci_low, armA.ci_high)
            if (armA0) allCis.push(armA0.ci_low, armA0.ci_high)
            if (armC) allCis.push(armC.ci_low, armC.ci_high)

            const minVal = allCis.length > 0 ? Math.min(...allCis) : 0
            const maxVal = allCis.length > 0 ? Math.max(...allCis) : 1
            const span = maxVal - minVal > 0 ? maxVal - minVal : 1

            const getPct = (val: number) => Math.max(0, Math.min(100, ((val - minVal) / span) * 100))

            const verdictColor = (verdict?: string) => {
              if (verdict === 'helps') return 'text-[#0F766E] bg-[#E6F4F1] border-[#99D5C9]'
              if (verdict === 'worse') return 'text-[#9A4A00] bg-[#FFF2E6] border-[#F5C299]'
              return 'text-[#475569] bg-[#F1F5F9] border-[#CBD5E1]'
            }

            const verdictText = (verdict?: string) => {
              if (verdict === 'helps') return t('res.verdict.helps')
              if (verdict === 'worse') return t('res.verdict.worse')
              return t('res.verdict.not_shown')
            }

            return (
              <div
                key={mKey}
                className="bg-white/95 rounded-2xl p-5 border border-[#DCE3DA] shadow-sm flex flex-col gap-4"
              >
                <div className="flex flex-col gap-1">
                  <h3 className="m-0 text-[16px] sm:text-[17px] font-bold text-[#1B2A22] leading-snug">
                    {label}
                  </h3>
                </div>

                {/* Bars for Arms A, A0, C */}
                <div className="flex flex-col gap-3 py-1">
                  {/* Arm C (Rebound) */}
                  {armC && (
                    <div className="flex flex-col gap-1">
                      <div className="flex justify-between text-[13px]">
                        <span className="font-bold text-[#0F766E]">{t('res.legend.c')}</span>
                        <span className="font-bold text-[#0F766E]">{formatArmValue(armC.mean, unit)}</span>
                      </div>
                      <div className="relative h-4 rounded-full bg-[#E5E9E4] overflow-hidden">
                        {/* Shaded CI range */}
                        <div
                          className="absolute h-full bg-[#0F766E]/30"
                          style={{
                            [isRtl ? 'right' : 'left']: `${getPct(armC.ci_low)}%`,
                            width: `${Math.max(2, getPct(armC.ci_high) - getPct(armC.ci_low))}%`,
                          }}
                        />
                        {/* Mean tick */}
                        <div
                          className="absolute top-0 bottom-0 w-1.5 bg-[#0F766E] rounded-full"
                          style={{
                            [isRtl ? 'right' : 'left']: `calc(${getPct(armC.mean)}% - 3px)`,
                          }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Arm A0 (Kind fixed plan) */}
                  {armA0 && (
                    <div className="flex flex-col gap-1">
                      <div className="flex justify-between text-[13px]">
                        <span className="font-medium text-[#1E3A8A]">{t('res.legend.a0')}</span>
                        <span className="font-semibold text-[#1E3A8A]">{formatArmValue(armA0.mean, unit)}</span>
                      </div>
                      <div className="relative h-4 rounded-full bg-[#E5E9E4] overflow-hidden">
                        {/* Shaded CI range */}
                        <div
                          className="absolute h-full bg-[#2563EB]/25"
                          style={{
                            [isRtl ? 'right' : 'left']: `${getPct(armA0.ci_low)}%`,
                            width: `${Math.max(2, getPct(armA0.ci_high) - getPct(armA0.ci_low))}%`,
                          }}
                        />
                        {/* Mean tick */}
                        <div
                          className="absolute top-0 bottom-0 w-1.5 bg-[#2563EB] rounded-full"
                          style={{
                            [isRtl ? 'right' : 'left']: `calc(${getPct(armA0.mean)}% - 3px)`,
                          }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Arm A (Typical streak app) */}
                  {armA && (
                    <div className="flex flex-col gap-1">
                      <div className="flex justify-between text-[13px]">
                        <span className="font-medium text-[#4B5550]">{t('res.legend.a')}</span>
                        <span className="font-semibold text-[#4B5550]">{formatArmValue(armA.mean, unit)}</span>
                      </div>
                      <div className="relative h-4 rounded-full bg-[#E5E9E4] overflow-hidden">
                        {/* Shaded CI range */}
                        <div
                          className="absolute h-full bg-[#6E7D74]/25"
                          style={{
                            [isRtl ? 'right' : 'left']: `${getPct(armA.ci_low)}%`,
                            width: `${Math.max(2, getPct(armA.ci_high) - getPct(armA.ci_low))}%`,
                          }}
                        />
                        {/* Mean tick */}
                        <div
                          className="absolute top-0 bottom-0 w-1.5 bg-[#6E7D74] rounded-full"
                          style={{
                            [isRtl ? 'right' : 'left']: `calc(${getPct(armA.mean)}% - 3px)`,
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Verdict lines */}
                <div className="mt-auto pt-3 border-t border-[#E8ECE6] flex flex-col gap-2 text-[12px] sm:text-[13px]">
                  {/* vs Typical streak app */}
                  {compA && (
                    <div className="flex flex-wrap items-center justify-between gap-1">
                      <span className="text-[#5A6A60]">{t('res.vsStreak')}:</span>
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className={`px-2 py-0.5 rounded-md text-[11px] font-bold border ${verdictColor(compA.verdict)}`}>
                          {verdictText(compA.verdict)}
                        </span>
                        <span className="font-semibold text-[#1B2A22]">
                          {formatComparisonMean(compA.mean, unit)}
                        </span>
                        <span className="text-[#718077] text-[11px]">
                          ({t('res.range95', { low: formatComparisonRange(compA.ci_low, compA.ci_high, unit).split(' to ')[0], high: formatComparisonRange(compA.ci_low, compA.ci_high, unit).split(' to ')[1] })})
                        </span>
                      </div>
                    </div>
                  )}

                  {/* vs Kind fixed plan */}
                  {compA0 && (
                    <div className="flex flex-wrap items-center justify-between gap-1">
                      <span className="text-[#5A6A60]">{t('res.vsKind')}:</span>
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className={`px-2 py-0.5 rounded-md text-[11px] font-bold border ${verdictColor(compA0.verdict)}`}>
                          {verdictText(compA0.verdict)}
                        </span>
                        <span className="font-semibold text-[#1B2A22]">
                          {formatComparisonMean(compA0.mean, unit)}
                        </span>
                        <span className="text-[#718077] text-[11px]">
                          ({t('res.range95', { low: formatComparisonRange(compA0.ci_low, compA0.ci_high, unit).split(' to ')[0], high: formatComparisonRange(compA0.ci_low, compA0.ci_high, unit).split(' to ')[1] })})
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )
          })}
        </div>

        {/* Safety Section */}
        <section aria-labelledby="safety-title" className="p-4 sm:p-5 rounded-2xl bg-white/95 border border-[#DCE3DA] shadow-xs flex flex-col gap-2">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#0F766E]" />
            <h2 id="safety-title" className="m-0 text-[16px] font-bold text-[#1B2A22]">{t('res.safety.audit')}</h2>
          </div>
          <p className="m-0 text-[14px] text-[#2C5140] font-semibold leading-relaxed">
            {isSafetyZero
              ? t('res.safety.zero')
              : t('res.safety.detail', {
                  violations: safetyInfo?.violations ?? 0,
                  quiet: safetyInfo?.quiet_messages ?? 0,
                })}
          </p>
        </section>

        {/* Where Rebound doesn't help */}
        <section aria-labelledby="no-help-title" className="p-5 sm:p-6 rounded-2xl bg-[#F6F8F5] border border-[#D5DDD2] shadow-xs flex flex-col gap-3">
          <h2 id="no-help-title" className="m-0 text-[17px] font-bold text-[#1B2A22]">
            {t('res.noHelp.title')}
          </h2>

          {noHelpItems.length > 0 && (
            <ul className="m-0 ps-5 text-[14px] leading-relaxed text-[#2C3830] list-disc space-y-1.5 font-medium">
              {noHelpItems.map((item, idx) => (
                <li key={idx}>{item.text}</li>
              ))}
            </ul>
          )}

          <div className="flex flex-col gap-1.5 pt-2 border-t border-[#D5DDD2]/70 text-[14px] text-[#425046] leading-relaxed">
            <p className="m-0 font-medium">{t('res.noHelp.stepPicker')}</p>
            <p className="m-0 font-medium">{t('res.noHelp.streakAssumption')}</p>
          </div>
        </section>

        {/* Footnote */}
        {data.verdict_rule && (
          <footer className="pt-2 pb-6 text-[12px] text-[#6E7D74] leading-relaxed">
            <p className="m-0">
              <strong className="font-semibold">{t('res.footnote')}:</strong> {data.verdict_rule}
            </p>
          </footer>
        )}
      </div>
    </div>
  )
}

export default ResultsScreen
