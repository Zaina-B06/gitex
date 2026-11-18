import React, { useState } from 'react'
import { ScreenProps } from '../types'
import { api, errorText, StateOut, TodayOut } from '../api/client'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { ScreenFrame } from '../components/ScreenFrame'
import { HabitRings } from '../components/HabitRings'
import { ActionCard, Outcome } from '../components/ActionCard'
import { ExplainSheet } from '../components/ExplainSheet'
import { LoadingView, ErrorView } from '../components/StatusViews'
import { WINDOW_LABEL, formatHour } from '../lib/behaviour'
import { useAsync } from '../lib/useAsync'
import { tr } from '../i18n'

const greeting = () => {
  const h = new Date().getHours()
  return tr(h < 12 ? 'app.today.morning' : h < 18 ? 'app.today.afternoon' : 'app.today.evening')
}

const CONTEXT_BANNER: Partial<Record<string, { bg: string; fg: string }>> = {
  ramadan: { bg: '#EAE6F7', fg: '#2E2563' },
  eid: { bg: '#EAE6F7', fg: '#2E2563' },
  heat: { bg: '#F6E9DC', fg: '#8A4B0F' },
  paused: { bg: '#E6EBE4', fg: '#3F4F45' },
  illness: { bg: '#E6EBE4', fg: '#3F4F45' },
}

/** Today: GET /today (steps, messages) + GET /state (what was already answered). */
export const TodayScreen: React.FC<ScreenProps> = ({ state, setState, onNavigate, showToast }) => {
  const lang = state.language
  const session = state.session!
  const data = useAsync(
    () => Promise.all([api.today(session), api.state(session)]) as Promise<[TodayOut, StateOut]>,
    [session, state.dataVersion],
  )
  // Only for the read-aloud preference (preferences aren't part of /today).
  const prefs = useAsync(() => api.exportData(session).then((e) => e.profile.preferences), [session, state.dataVersion])
  const onHelp = () => {
    setState((prev) => ({ ...prev, careReason: 'help' }))
    onNavigate('care')
  }
  const [busy, setBusy] = useState<string | null>(null)
  const [whyId, setWhyId] = useState<string | null>(null)

  const answer = async (actionId: string, type: Outcome) => {
    if (!data.data) return
    setBusy(actionId)
    try {
      const res = await api.recordEvent(session, actionId, type)
      data.setData([data.data[0], res.state])
      showToast(
        res.encouragement?.message ??
          tr(type === 'completed' ? 'app.today.doneToast' : type === 'partial' ? 'app.today.partialToast' : 'app.today.skippedToast'),
      )
    } catch (e) {
      showToast(errorText(e))
      data.reload()
    } finally {
      setBusy(null)
    }
  }

  const endRamadan = async () => {
    try {
      await api.settings(session, { ramadan: 'ended_today' })
      showToast(tr('app.today.eidToast'))
      data.reload()
    } catch (e) {
      showToast(errorText(e))
    }
  }

  const [today, st] = data.data ?? [null, null]
  // Outcomes already recorded for today's steps.
  const answered = new Map(
    (st?.history ?? []).filter((d) => today && d.day === today.day && d.action_id).map((d) => [d.action_id!, d.outcome]),
  )
  const flags = st?.context_flags ?? []

  return (
    <ScreenFrame
      dir={lang === 'ar' ? 'rtl' : 'ltr'}
      tab="today"
      onNavigate={onNavigate}
      onHelp={onHelp}
      background={
        <>
          <TatreezPattern width={250} height={250} style={{ right: '-100px', bottom: '50px', opacity: 0.1 }} />
          <ArabicCalligraphyRing width={460} height={460} style={{ right: '-230px', top: '-150px', opacity: 0.14 }} />
          <ArabicCalligraphyRing width={340} height={340} style={{ left: '-190px', bottom: '90px', opacity: 0.09 }} />
        </>
      }
    >
      {/* The language is chosen on Welcome and changed in Settings → Profile. */}
      <header className="p-6 pt-1 pb-1.5 flex flex-col gap-0.5">
        <span className="text-[13px] text-[#5A6A60]">
          {new Date().toLocaleDateString(lang === 'ar' ? 'ar-AE' : 'en-GB', { weekday: 'long', day: 'numeric', month: 'long' })}
        </span>
        <h1 className="m-0 font-display tracking-tight text-[27px] font-semibold">
          {state.displayName ? tr('app.today.greetName', { greeting: greeting(), name: state.displayName }) : greeting()}
        </h1>
      </header>

      {data.loading && !data.data && <LoadingView label={tr('app.today.loading')} />}
      {data.error && <ErrorView message={data.error} onRetry={data.reload} />}

      {today && st && (
        <>
          {flags.map((f) => {
            const b = CONTEXT_BANNER[f]
            if (!b) return null
            return (
              <div
                key={f}
                role="status"
                className="mx-6 mt-2 p-3 px-3.5 rounded-[14px] text-[14px] leading-snug flex flex-col gap-2"
                style={{ background: b.bg, color: b.fg }}
              >
                <span>{tr(`app.today.banner.${f}`)}</span>
                {f === 'ramadan' && (
                  <button
                    type="button"
                    onClick={endRamadan}
                    className="self-start min-h-[36px] px-3 rounded-full bg-white/80 border-0 text-[13px] font-semibold cursor-pointer"
                    style={{ color: b.fg }}
                  >
                    {tr('app.today.moonEnded')}
                  </button>
                )}
              </div>
            )
          })}

          {!state.bannerDismissed && today.messages.length > 0 && (
            <div role="status" className="mx-6 mt-2 p-2.5 ps-3.5 pe-2 rounded-[14px] bg-[#263A30] text-white flex items-center gap-2.5 shadow-sm">
              <p className="m-0 flex-1 text-[14px] leading-snug">{today.messages.join(' ')}</p>
              <button
                type="button"
                onClick={() => setState((prev) => ({ ...prev, bannerDismissed: true }))}
                aria-label={tr('common.dismiss')}
                className="flex-none w-11 h-11 border-0 bg-transparent text-white flex items-center justify-center hover:opacity-75 cursor-pointer"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                  <path d="M6 6l12 12M18 6L6 18" />
                </svg>
              </button>
            </div>
          )}

          <HabitRings strength={st.habit_strength} />

          {today.checkin_due ? (
            <button
              type="button"
              onClick={() => onNavigate('checkin')}
              className="mx-6 mt-2.5 p-3 px-3.5 rounded-[16px] bg-white border-2 border-[#3E6B53] text-start cursor-pointer flex flex-col gap-0.5"
            >
              <span className="text-[15px] font-semibold text-[#2C5140]">{tr('app.today.rough')}</span>
              <span className="text-[13px] text-[#3F4F45]">{tr('app.today.roughSub')}</span>
            </button>
          ) : (
            <div className="px-6 pt-2">
              <button
                type="button"
                onClick={() => onNavigate('checkin')}
                className="text-xs bg-white/80 border border-[#C5D0C7] text-[#3F4F45] px-2.5 py-1 rounded-full font-medium hover:bg-white transition-colors cursor-pointer"
              >
                {tr('app.today.inTheWay')}
              </button>
            </div>
          )}
          <div className="px-6 pt-2">
            <button
              type="button"
              onClick={() => onNavigate('chat-nudge')}
              className="text-xs bg-[#263A30] text-white px-3 py-1.5 rounded-full font-medium border-0 cursor-pointer inline-flex items-center gap-1.5"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                <path d="M21 12a8 8 0 0 1-11.6 7.1L4 20l1-4.6A8 8 0 1 1 21 12z" />
              </svg>
              {tr('app.today.chat')}
            </button>
          </div>

          <div className="mx-6 mt-4 mb-2 flex justify-between items-baseline">
            <h2 className="m-0 text-[15px] font-semibold">
              {tr(today.actions.length === 1 ? 'app.today.oneStep' : 'app.today.steps')}
            </h2>
          </div>

          <div className="flex flex-col gap-2.5 px-6 pb-4">
            {today.actions.length === 0 && (
              <p className="m-0 p-4 rounded-[20px] bg-white/90 text-[14px] text-[#3F4F45]">
                {tr('app.today.noSteps')}
              </p>
            )}
            {today.actions.map((s) => {
              const recipe = today.recipes?.[s.action.id] ?? null
              return (
                <ActionCard
                  key={s.action.id}
                  action={s.action}
                  lang={lang}
                  when={`${WINDOW_LABEL[s.time_window] ?? s.time_window} · ${formatHour(s.hour)}`}
                  outcome={answered.get(s.action.id) ?? null}
                  busy={busy === s.action.id}
                  onAnswer={(type) => answer(s.action.id, type)}
                  onWhy={() => setWhyId(s.explanation_id || s.action.id)}
                  lighterTitle={s.lighter?.title[lang] ?? null}
                  readAloud={!!prefs.data?.read_aloud}
                  recipe={recipe}
                  onRecipe={() => {
                    if (!recipe) return
                    setState((prev) => ({ ...prev, recipeTarget: { recipeId: recipe.id, actionId: s.action.id } }))
                    onNavigate('recipe')
                  }}
                />
              )
            })}
          </div>
        </>
      )}

      {whyId && <ExplainSheet actionId={whyId} lang={lang} onClose={() => setWhyId(null)} />}
    </ScreenFrame>
  )
}
