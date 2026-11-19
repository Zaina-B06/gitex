import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { ScreenProps } from '../types'
import { api, ApiError, EmployerData, errorText } from '../api/client'
import { demoKey, loadOrgId, loadOrgKey, saveOrgId, saveOrgKey, savePersonas } from '../lib/demo'
import { BARRIER_LABEL } from '../lib/history'
import { LanguageSwitch } from '../components/LanguageSwitch'
import { useLanguageChange } from '../lib/language'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'

function getBarrierLabel(code: string): string {
  const friendly = BARRIER_LABEL[code as keyof typeof BARRIER_LABEL]
  return friendly || code
}

export const ProgramDashboardScreen: React.FC<ScreenProps> = (props) => {
  const { state, onNavigate } = props
  const { t } = useTranslation()
  const changeLanguage = useLanguageChange(props)

  const [orgId, setOrgId] = useState<string | null>(() => loadOrgId())
  const [orgKey, setOrgKey] = useState<string | null>(() => loadOrgKey())
  const [data, setData] = useState<EmployerData | null>(null)
  const [loading, setLoading] = useState(false)
  const [seeding, setSeeding] = useState(false)
  const [keyInput, setKeyInput] = useState('')
  const [error, setError] = useState<{ status?: number; message: string } | null>(null)

  const fetchEmployerData = async (targetOrgId: string, targetKey: string | null) => {
    setLoading(true)
    setError(null)
    try {
      const out = await api.dashboardEmployer(targetOrgId, targetKey || '')
      setData(out)
    } catch (e) {
      setData(null)
      if (e instanceof ApiError) {
        if (e.status === 401) {
          setError({ status: 401, message: t('d.keyWrong') })
        } else if (e.status === 403) {
          setError({ status: 403, message: t('d.groupTooSmall') })
        } else {
          setError({ status: e.status, message: errorText(e) })
        }
      } else {
        setError({ status: 0, message: t('d.error') })
      }
    } finally {
      setLoading(false)
    }
  }

  // Initial load
  useEffect(() => {
    if (orgId) {
      void fetchEmployerData(orgId, orgKey)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orgId])

  // Seed demo org if requested or if none exists
  const runSeed = async () => {
    const key = demoKey(t('onboarding.welcome.demoKeyPrompt'))
    if (!key) return
    setSeeding(true)
    setError(null)
    try {
      const out = await api.demoSeed(key)
      savePersonas(out.personas)
      if (out.org_id) {
        saveOrgId(out.org_id)
        setOrgId(out.org_id)
        await fetchEmployerData(out.org_id, orgKey)
      }
    } catch (e) {
      setError({ status: e instanceof ApiError ? e.status : 0, message: errorText(e) })
    } finally {
      setSeeding(false)
    }
  }

  const handleKeySubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = keyInput.trim()
    if (!trimmed) return
    saveOrgKey(trimmed)
    setOrgKey(trimmed)
    if (orgId) {
      void fetchEmployerData(orgId, trimmed)
    }
  }

  // 1. Loading state (no hard-coded numbers)
  if (loading || seeding) {
    return (
      <div className="min-h-screen w-full bg-[#EEF1EA] text-[#1B2A22] p-6 sm:p-10 flex flex-col items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <span className="spinner" aria-hidden="true" />
          <p className="text-[15px] font-medium text-[#3F4F45]">
            {seeding ? t('d.seeding') : t('d.loading')}
          </p>
        </div>
      </div>
    )
  }

  // 2. Error: 401 Key required or wrong key
  if (error?.status === 401) {
    return (
      <div className="min-h-screen w-full bg-[#EEF1EA] text-[#1B2A22] p-4 sm:p-8 flex flex-col items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-2xl p-6 sm:p-7 shadow-sm border border-[#DCE3DA] flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <span className="text-[12px] font-bold text-[#5A6A60] uppercase tracking-wide">
              {t('d.kicker')}
            </span>
            <LanguageSwitch value={state.language} onChange={changeLanguage} tone="light" />
          </div>

          <h2 className="m-0 text-[20px] font-bold text-[#1B2A22]">
            {t('d.keyRequiredTitle')}
          </h2>

          <div className="p-3 rounded-xl bg-[#FFF2E6] border border-[#F5C299] text-[#9A4A00] text-[13px] font-semibold">
            {t('d.keyWrong')}
          </div>

          <form onSubmit={handleKeySubmit} className="flex flex-col gap-3">
            <label className="text-[14px] text-[#3F4F45] font-medium flex flex-col gap-1.5">
              <span>{t('d.keyPrompt')}</span>
              <input
                type="password"
                value={keyInput}
                onChange={(e) => setKeyInput(e.target.value)}
                placeholder={t('d.keyPlaceholder')}
                className="min-h-[44px] px-3.5 rounded-xl border border-[#C5D0C7] text-[14px] focus:outline-none focus:border-[#2C5140] transition-colors"
                autoFocus
              />
            </label>
            <div className="flex gap-2 pt-1">
              <button
                type="submit"
                disabled={!keyInput.trim()}
                className="flex-1 min-h-[44px] px-4 rounded-xl bg-[#2C5140] hover:bg-[#1E382B] disabled:opacity-50 text-white text-[14px] font-semibold border-0 cursor-pointer transition-colors"
              >
                {t('d.keySubmit')}
              </button>
              <button
                type="button"
                onClick={() => onNavigate('welcome')}
                className="min-h-[44px] px-4 rounded-xl bg-[#E6EBE4] hover:bg-[#DCE3DA] text-[#1B2A22] text-[14px] font-medium border-0 cursor-pointer transition-colors"
              >
                {t('common.back')}
              </button>
            </div>
          </form>
        </div>
      </div>
    )
  }

  // 3. Error: 403 Group too small or other network error
  if (error && error.status !== 401) {
    return (
      <div className="min-h-screen w-full bg-[#EEF1EA] text-[#1B2A22] p-4 sm:p-8 flex flex-col items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-2xl p-6 sm:p-7 shadow-sm border border-[#DCE3DA] flex flex-col items-center text-center gap-4">
          <div className="w-12 h-12 rounded-full bg-[#FCE8E6] text-[#A02A1C] flex items-center justify-center text-xl font-bold">
            !
          </div>
          <h2 className="m-0 text-[18px] font-bold text-[#1B2A22]">
            {error.status === 403 ? t('d.groupTooSmall') : t('d.error')}
          </h2>
          <p className="m-0 text-[14px] text-[#5A6A60] leading-relaxed">
            {error.message}
          </p>
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={() => (orgId ? fetchEmployerData(orgId, orgKey) : runSeed())}
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

  // 4. Missing orgId state
  if (!orgId || !data) {
    return (
      <div className="min-h-screen w-full bg-[#EEF1EA] text-[#1B2A22] p-4 sm:p-8 flex flex-col items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-2xl p-6 sm:p-7 shadow-sm border border-[#DCE3DA] flex flex-col items-center text-center gap-4">
          <span className="text-[12px] font-bold text-[#5A6A60] uppercase tracking-wide">
            {t('d.kicker')}
          </span>
          <h2 className="m-0 text-[19px] font-bold text-[#1B2A22]">
            {t('d.noOrgId')}
          </h2>
          <p className="m-0 text-[14px] text-[#5A6A60] leading-relaxed">
            {t('d.seedPrompt')}
          </p>
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={runSeed}
              className="min-h-[44px] px-5 rounded-xl bg-[#2C5140] hover:bg-[#1E382B] text-white text-[14px] font-semibold border-0 cursor-pointer transition-colors"
            >
              {t('d.seedButton')}
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

  // 5. Successful Data Display (100% data-driven, NO hardcoded numbers)
  const habitEntries = Object.entries(data.average_habit_strength || {})

  return (
    <div className="relative overflow-hidden box-border min-h-screen w-full bg-[#EEF1EA] font-sans text-[#1B2A22] p-4 sm:p-8">
      <TatreezPattern width={340} height={340} style={{ right: '-50px', top: '150px', opacity: 0.06 }} />
      <ArabicCalligraphyRing width={640} height={640} style={{ right: '-220px', top: '-240px', opacity: 0.1 }} />
      <ArabicCalligraphyRing width={480} height={480} style={{ left: '-200px', bottom: '-180px', opacity: 0.08 }} />

      <div className="max-w-[1120px] mx-auto flex flex-col gap-6">
        {/* Header */}
        <header className="flex flex-col gap-3">
          <div className="flex items-center justify-between gap-4">
            <button
              type="button"
              onClick={() => onNavigate('welcome')}
              className="min-h-[44px] px-2 flex items-center gap-2 text-[14px] text-[#2C5140] hover:text-[#1B2A22] font-semibold bg-transparent border-0 cursor-pointer"
            >
              <span className="text-base rtl:rotate-180 transition-transform">←</span>
              <span>{t('d.back')}</span>
            </button>
            <LanguageSwitch value={state.language} onChange={changeLanguage} tone="light" />
          </div>

          <div className="flex flex-col gap-1">
            <span className="text-[13px] font-semibold text-[#5A6A60] tracking-wide uppercase">
              {t('d.kicker')}
            </span>
            <h1 className="m-0 font-display tracking-tight text-[28px] sm:text-[36px] font-bold text-[#1B2A22]">
              {t('d.title')}
            </h1>
            <div className="flex flex-wrap items-center gap-2 pt-1 text-[13px] sm:text-[14px]">
              <span className="px-2.5 py-1 rounded-md bg-[#2C5140] text-white font-medium">
                {t('d.demoOrgLabel')}
              </span>
              <span className="text-[#5A6A60] font-medium">
                {t('d.privacyLine')}
              </span>
            </div>
          </div>
        </header>

        {/* 3 Tiles: group_size, active_share, first top barrier */}
        <section aria-label={t('d.keyNumbers')} className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Tile 1: Group size */}
          <div className="bg-white/95 rounded-2xl p-5 border border-[#DCE3DA] shadow-xs flex flex-col gap-1">
            <span className="text-[13px] font-semibold text-[#5A6A60]">{t('d.groupSize')}</span>
            <span className="font-display tracking-tight text-[32px] sm:text-[36px] font-bold text-[#1B2A22]">
              {t('d.people', { n: data.group_size })}
            </span>
          </div>

          {/* Tile 2: Active share as % */}
          <div className="bg-white/95 rounded-2xl p-5 border border-[#DCE3DA] shadow-xs flex flex-col gap-1">
            <span className="text-[13px] font-semibold text-[#5A6A60]">{t('d.activeShare')}</span>
            <span className="font-display tracking-tight text-[32px] sm:text-[36px] font-bold text-[#2C5140]">
              {(data.active_share * 100).toFixed(0)}%
            </span>
          </div>

          {/* Tile 3: Top barrier */}
          <div className="bg-white/95 rounded-2xl p-5 border border-[#DCE3DA] shadow-xs flex flex-col gap-1">
            <span className="text-[13px] font-semibold text-[#5A6A60]">{t('d.topBarrierTile')}</span>
            <span className="font-display tracking-tight text-[24px] sm:text-[28px] font-bold text-[#9A4A00] truncate">
              {data.top_barriers && data.top_barriers[0]
                ? getBarrierLabel(data.top_barriers[0].barrier)
                : t('d.noneReported')}
            </span>
          </div>
        </section>

        {/* Dynamic Habit Strengths & Top Barriers */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          {/* Habit Strengths: one bar per behaviour present in average_habit_strength */}
          <section
            aria-labelledby="habit-strengths-title"
            className="lg:col-span-7 bg-white/95 rounded-2xl p-5 sm:p-6 border border-[#DCE3DA] shadow-xs flex flex-col gap-4"
          >
            <h2 id="habit-strengths-title" className="m-0 text-[17px] font-bold text-[#1B2A22]">
              {t('d.habitStrengths')}
            </h2>

            {habitEntries.length > 0 ? (
              <div className="flex flex-col gap-3.5">
                {habitEntries.map(([bKey, val]) => {
                  const bLabel = t(`common.behaviour.${bKey}`, { defaultValue: bKey })
                  const score = Math.round(val <= 1 ? val * 100 : val)
                  return (
                    <div key={bKey} className="flex flex-col gap-1.5">
                      <div className="flex justify-between items-center text-[13px] sm:text-[14px]">
                        <span className="font-semibold text-[#1B2A22]">{bLabel}</span>
                        <span className="font-bold text-[#2C5140]">{score}%</span>
                      </div>
                      <div className="h-3 rounded-full bg-[#E5E9E4] overflow-hidden">
                        <div
                          className="h-full rounded-full bg-[#2C5140] transition-all duration-300"
                          style={{
                            width: `${Math.max(0, Math.min(100, score))}%`,
                          }}
                        />
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <p className="m-0 text-[14px] text-[#5A6A60]">{t('d.noneReported')}</p>
            )}
          </section>

          {/* Top Barriers List */}
          <section
            aria-labelledby="top-barriers-title"
            className="lg:col-span-5 bg-white/95 rounded-2xl p-5 sm:p-6 border border-[#DCE3DA] shadow-xs flex flex-col gap-4"
          >
            <h2 id="top-barriers-title" className="m-0 text-[17px] font-bold text-[#1B2A22]">
              {t('d.topBarriers')}
            </h2>

            {data.top_barriers && data.top_barriers.length > 0 ? (
              <ul className="m-0 p-0 list-none divide-y divide-[#E8ECE6] flex flex-col">
                {data.top_barriers.map((tb, idx) => (
                  <li key={idx} className="py-3 flex items-center justify-between text-[14px]">
                    <span className="font-medium text-[#2C3830]">
                      {getBarrierLabel(tb.barrier)}
                    </span>
                    <span className="font-bold text-[#9A4A00] px-2.5 py-0.5 rounded-full bg-[#FFF2E6] border border-[#F5C299] text-[12px]">
                      {t('d.barrierCount', { count: tb.count })}
                    </span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="m-0 text-[14px] text-[#5A6A60]">{t('d.noneReported')}</p>
            )}
          </section>
        </div>

        {/* Privacy by Design */}
        <section aria-labelledby="privacy-title" className="p-5 sm:p-6 rounded-2xl bg-white/95 border border-[#DCE3DA] shadow-xs flex flex-col gap-3">
          <h2 id="privacy-title" className="m-0 text-[17px] font-bold text-[#1B2A22]">
            {t('d.privacy')}
          </h2>
          <ul className="m-0 ps-5 text-[14px] leading-relaxed text-[#3F4F45] list-disc space-y-1.5 font-medium">
            <li>{t('d.privacy1')}</li>
            <li>{t('d.privacy2')}</li>
            <li>{t('d.privacy3')}</li>
          </ul>
        </section>
      </div>
    </div>
  )
}

export default ProgramDashboardScreen
