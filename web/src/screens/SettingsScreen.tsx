import React, { useEffect, useState } from 'react'
import { ScreenProps, Household, SettingPref, Weekday } from '../types'
import { api, ApiError, Condition, errorText, ExportOut, SettingsIn } from '../api/client'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { ScreenFrame } from '../components/ScreenFrame'
import { ProfileSection } from '../components/ProfileSection'
import { ChipGroup } from '../components/OnboardingLayout'
import { LanguageSwitch } from '../components/LanguageSwitch'
import { LoadingView, ErrorView } from '../components/StatusViews'
import { useAsync } from '../lib/useAsync'
import { useLanguageChange } from '../lib/language'
import { options, tr } from '../i18n'

const CONDITIONS = options<Condition>('onboarding.condition', [
  'diabetes', 'high_blood_pressure', 'back_or_joint_pain', 'stress', 'recovering_from_illness_or_injury',
])
const HOUSEHOLD = options<Household>('onboarding.household', ['alone', 'family', 'children', 'older_relatives'])
const PLACES = options<SettingPref>('onboarding.place', ['indoor', 'outdoor', 'either'])
const WEEKDAYS = options<Weekday>('onboarding.day', ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'])
// Withdrawing one of these deletes those answers (the health check can't be withdrawn: it keeps the plan safe).
const CONSENTS = ['body', 'conditions', 'history', 'preferences'] as const

type GroupId = 'profile' | 'health' | 'routine' | 'family' | 'messages' | 'privacy' | 'help'
const GROUPS: GroupId[] = ['profile', 'health', 'routine', 'family', 'messages', 'privacy', 'help']

interface SettingsScreenProps extends ScreenProps {
  /** Clears the session and returns to Welcome (after logout or DELETE /users/{id}). */
  onSignedOut: () => void
}

const S = (key: string, vars?: Record<string, unknown>) => tr(`settings.${key}`, vars)
const row = 'min-h-[48px] px-4 py-2 flex items-center justify-between gap-3 border-b border-[#E6EBE4] text-[#1B2A22]'
const check = 'w-[22px] h-[22px] flex-none accent-[#3E6B53] cursor-pointer'
const field = 'min-h-[40px] rounded-lg border border-[#C5D0C7] px-2 text-[14px] bg-white'
const smallBtn =
  'self-start min-h-[40px] px-4 rounded-[12px] bg-[#3E6B53] text-white text-[14px] font-semibold border-0 cursor-pointer disabled:opacity-60'
const linkRow = row + ' w-full bg-transparent border-x-0 border-t-0 text-start cursor-pointer'
const hm = (t: unknown) => (t ? String(t).slice(0, 5) : '')

const Toggle: React.FC<{ label: string; hint?: string; checked: boolean; disabled: boolean; onChange: (v: boolean) => void }> = ({
  label,
  hint,
  checked,
  disabled,
  onChange,
}) => (
  <label className={row + ' cursor-pointer'}>
    <span className="flex flex-col gap-0.5">
      <span className="text-[15px]">{label}</span>
      {hint && <span className="text-[12px] text-[#5A6A60]">{hint}</span>}
    </span>
    <input type="checkbox" className={check} checked={checked} disabled={disabled} onChange={(e) => onChange(e.target.checked)} />
  </label>
)

/** Settings in groups that fold open (all closed at first), and Sign out on its own at the bottom.
 *  Reads GET /export, saves with PATCH /settings. */
export const SettingsScreen: React.FC<SettingsScreenProps> = (props) => {
  const { state, setState, onNavigate, showToast, onSignedOut } = props
  const session = state.session!
  const changeLanguage = useLanguageChange(props)
  const data = useAsync<ExportOut>(() => api.exportData(session), [session, state.dataVersion])
  const arNote = useAsync(
    () => (state.language === 'ar' ? api.onboardingContent('ar').then((c) => c.translation_note) : Promise.resolve(null)),
    [state.language],
  )
  const [open, setOpen] = useState<GroupId | null>(null)
  const [saving, setSaving] = useState(false)
  const [confirm, setConfirm] = useState<'delete' | 'signout' | null>(null)

  const exp = data.data
  const prefs = exp?.profile.preferences
  const basics = exp?.profile.basics
  const flags = exp?.state.context_flags ?? []
  const username = (exp?.account as { username?: string | null } | undefined)?.username ?? null

  // Local drafts for typed fields; saved on blur or with a button.
  const [name, setName] = useState('')
  const [anchor, setAnchor] = useState('')
  const [iftar, setIftar] = useState('')
  const [quiet, setQuiet] = useState({ start: '', end: '' })
  const [shiftDays, setShiftDays] = useState<Weekday[]>([])
  const [shiftTimes, setShiftTimes] = useState({ start: '07:00', end: '15:00' })
  const [conditions, setConditions] = useState<Condition[]>([])
  useEffect(() => {
    if (!exp || !prefs) return
    setName(prefs.display_name ?? '')
    setAnchor(prefs.anchor ?? '')
    setIftar(hm(prefs.iftar_time))
    setQuiet({ start: hm(prefs.quiet_hours?.start), end: hm(prefs.quiet_hours?.end) })
    const shift = exp.profile.basics.shifts?.[0]
    setShiftDays((shift?.days as Weekday[]) ?? [])
    setShiftTimes({ start: hm(shift?.start) || '07:00', end: hm(shift?.end) || '15:00' })
    setConditions(exp.profile.conditions?.managing ?? [])
  }, [exp, prefs])

  const save = async (body: SettingsIn, done: string) => {
    if (!exp) return
    setSaving(true)
    try {
      const out = await api.settings(session, body)
      data.setData({
        ...exp,
        profile: {
          ...exp.profile,
          preferences: out.preferences,
          consents: out.consents,
          conditions: body.conditions ?? exp.profile.conditions,
          basics: body.shifts !== undefined ? { ...exp.profile.basics, shifts: body.shifts } : exp.profile.basics,
        },
        state: { ...exp.state, context_flags: out.state.context_flags },
      })
      setState((prev) => ({ ...prev, displayName: out.preferences.display_name ?? '', dataVersion: prev.dataVersion + 1 }))
      showToast(done)
    } catch (e) {
      showToast(e instanceof ApiError && e.status === 409 && body.ramadan ? S('ramadanNotClose') : errorText(e))
    } finally {
      setSaving(false)
    }
  }
  const pref = (p: Record<string, unknown>, done = tr('common.saved')) => save({ preferences: p }, done)

  const download = () => {
    if (!exp) return
    const blob = new Blob([JSON.stringify(exp, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'rebound-my-data.json'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
    showToast(S('downloaded'))
  }

  const finish = async (kind: 'delete' | 'signout') => {
    setSaving(true)
    try {
      if (kind === 'delete') await api.deleteUser(session)
      else await api.logout(session)
      setConfirm(null)
      showToast(kind === 'delete' ? S('deleted') : S('signedOut'))
      onSignedOut()
    } catch (e) {
      showToast(errorText(e))
      setSaving(false)
    }
  }

  const body = (id: GroupId): React.ReactNode => {
    if (!exp || !prefs || !basics) return null
    switch (id) {
      case 'profile':
        return (
          <>
            <label className={row}>
              <span className="text-[15px]">{S('name')}</span>
              <input
                type="text"
                maxLength={40}
                value={name}
                onChange={(e) => setName(e.target.value)}
                onBlur={() => name.trim() !== (prefs.display_name ?? '') && pref({ display_name: name.trim() || null })}
                placeholder={S('namePlaceholder')}
                className={field + ' w-40 text-end'}
              />
            </label>
            <div className="px-4 py-3 flex flex-col gap-2 border-b border-[#E6EBE4]">
              <span className="flex flex-col gap-0.5">
                <span className="text-[15px]">{S('language')}</span>
                <span className="text-[12px] text-[#5A6A60]">{S('languageHint')}</span>
              </span>
              <LanguageSwitch value={state.language} onChange={changeLanguage} disabled={saving} />
              {arNote.data && <p className="m-0 text-[12px] text-[#8A4B0F]">{arNote.data}</p>}
            </div>
            <Toggle
              label={S('simpler')}
              hint={S('simplerHint')}
              checked={prefs.reading_level === 'simple'}
              disabled={saving}
              onChange={(v) => pref({ reading_level: v ? 'simple' : 'standard' })}
            />
            <Toggle label={S('readAloud')} hint={S('readAloudHint')} checked={!!prefs.read_aloud} disabled={saving}
              onChange={(v) => pref({ read_aloud: v })} />
            <label className={row}>
              <span className="flex flex-col gap-0.5">
                <span className="text-[15px]">{S('anchor')}</span>
                <span className="text-[12px] text-[#5A6A60]">{S('anchorHint')}</span>
              </span>
              <input
                type="text"
                maxLength={40}
                value={anchor}
                onChange={(e) => setAnchor(e.target.value)}
                onBlur={() => anchor.trim() !== (prefs.anchor ?? '') && pref({ anchor: anchor.trim() || null })}
                className={field + ' w-36 text-end'}
              />
            </label>
            <div className="px-4 py-3">
              <p className="m-0 mb-2 text-[12px] font-semibold text-[#5A6A60]">{S('toldUs')}</p>
              <ProfileSection exp={exp} />
            </div>
          </>
        )
      case 'health':
        return (
          <>
            <div className="px-4 py-3 flex flex-col gap-2 border-b border-[#E6EBE4]">
              <ChipGroup<Condition>
                label={tr('onboarding.goals.managing')}
                hint={S('managingHint')}
                options={CONDITIONS}
                isSelected={(v) => conditions.includes(v)}
                onToggle={(v) => setConditions((c) => (c.includes(v) ? c.filter((x) => x !== v) : [...c, v]))}
              />
              <button
                type="button"
                disabled={saving}
                className={smallBtn}
                onClick={() => save({ conditions: { managing: conditions }, consents: { conditions: true } }, S('rebuilt'))}
              >
                {tr('common.save')}
              </button>
            </div>
            <div className={row}>
              <span className="flex flex-col gap-0.5">
                <span className="text-[15px]">{S('healthCheck')}</span>
                <span className="text-[12px] text-[#5A6A60]">{S('healthCheckHint')}</span>
              </span>
            </div>
            {flags.includes('illness') ? (
              <button type="button" disabled={saving} className={linkRow + ' border-b-0'}
                onClick={() => save({ context: { illness: false } }, S('okToast'))}>
                <span className="text-[15px] font-medium text-[#2C5140]">{S('okNow')}</span>
              </button>
            ) : (
              <p className="m-0 px-4 py-3 text-[12px] text-[#5A6A60]">{S('okNowHint')}</p>
            )}
          </>
        )
      case 'routine':
        return (
          <>
            {basics.schedule_type === 'shift' && (
              <div className="px-4 py-3 flex flex-col gap-2 border-b border-[#E6EBE4]">
                <ChipGroup<Weekday>
                  label={S('shiftDays')}
                  hint={S('shiftDaysHint')}
                  options={WEEKDAYS}
                  isSelected={(v) => shiftDays.includes(v)}
                  onToggle={(v) => setShiftDays((d) => (d.includes(v) ? d.filter((x) => x !== v) : [...d, v]))}
                  columns={4}
                />
                <div className="flex items-center gap-2 text-[14px]">
                  <input type="time" className={field} value={shiftTimes.start} aria-label={tr('onboarding.basics.shiftStart')}
                    onChange={(e) => setShiftTimes((s) => ({ ...s, start: e.target.value }))} />
                  <span>{S('to')}</span>
                  <input type="time" className={field} value={shiftTimes.end} aria-label={tr('onboarding.basics.shiftEnd')}
                    onChange={(e) => setShiftTimes((s) => ({ ...s, end: e.target.value }))} />
                </div>
                <button type="button" disabled={saving} className={smallBtn}
                  onClick={() => save({ shifts: shiftDays.length ? [{ days: shiftDays, ...shiftTimes }] : [] }, S('shiftsSaved'))}>
                  {S('saveShifts')}
                </button>
              </div>
            )}
            <div className="px-4 py-3 border-b border-[#E6EBE4]">
              <ChipGroup<SettingPref>
                label={S('where')}
                options={PLACES}
                isSelected={(v) => prefs.setting === v}
                onToggle={(v) => !saving && pref({ setting: v })}
                columns={3}
              />
            </div>
            <Toggle
              label={S('fast')}
              checked={!!prefs.fasting_ramadan}
              disabled={saving}
              onChange={(v) => pref({ fasting_ramadan: v, ...(v ? {} : { family_fasting: false }) })}
            />
            {prefs.fasting_ramadan && (
              <div className={row}>
                <span className="flex flex-col gap-0.5">
                  <span className="text-[15px]">{S('iftar')}</span>
                  <span className="text-[12px] text-[#5A6A60]">{S('iftarHint')}</span>
                </span>
                <input
                  type="time"
                  className={field}
                  value={iftar}
                  disabled={saving}
                  onChange={(e) => setIftar(e.target.value)}
                  onBlur={() => iftar !== hm(prefs.iftar_time) && pref({ iftar_time: iftar || null }, S('iftarSaved'))}
                />
              </div>
            )}
            {prefs.fasting_ramadan && !flags.includes('ramadan') && (
              <button type="button" disabled={saving} className={linkRow}
                onClick={() => save({ ramadan: 'started_today' }, S('ramadanToast'))}>
                <span className="flex flex-col gap-0.5">
                  <span className="text-[15px]">{S('moonStarted')}</span>
                  <span className="text-[12px] text-[#5A6A60]">{S('moonStartedHint')}</span>
                </span>
              </button>
            )}
            <div className="px-4 py-3 flex flex-col gap-2">
              <span className="flex flex-col gap-0.5">
                <span className="text-[15px]">{S('quiet')}</span>
                <span className="text-[12px] text-[#5A6A60]">{S('quietHint')}</span>
              </span>
              <div className="flex items-center gap-2 text-[14px]">
                <input type="time" className={field} value={quiet.start} aria-label={S('quietFrom')}
                  onChange={(e) => setQuiet((q) => ({ ...q, start: e.target.value }))} />
                <span>{S('to')}</span>
                <input type="time" className={field} value={quiet.end} aria-label={S('quietUntil')}
                  onChange={(e) => setQuiet((q) => ({ ...q, end: e.target.value }))} />
              </div>
              <button type="button" disabled={saving || !!quiet.start !== !!quiet.end} className={smallBtn}
                onClick={() => pref({ quiet_hours: quiet.start && quiet.end ? quiet : null }, S('quietSaved'))}>
                {S('saveQuiet')}
              </button>
            </div>
          </>
        )
      case 'family':
        return (
          <>
            <div className="px-4 py-3 border-b border-[#E6EBE4]">
              <ChipGroup<Household>
                label={tr('onboarding.prefs.household')}
                options={HOUSEHOLD}
                isSelected={(v) => prefs.household === v}
                onToggle={(v) => !saving && pref({ household: prefs.household === v ? null : v })}
                columns={2}
              />
            </div>
            <Toggle label={S('caregiver')} checked={!!prefs.caregiver} disabled={saving} onChange={(v) => pref({ caregiver: v })} />
            {basics.sex === 'female' && (
              <Toggle
                label={S('womenOnly')}
                checked={prefs.space_preference === 'women_only_spaces'}
                disabled={saving}
                onChange={(v) => pref({ space_preference: v ? 'women_only_spaces' : 'any' })}
              />
            )}
            {prefs.fasting_ramadan && (
              <Toggle label={S('familyFasting')} checked={!!prefs.family_fasting} disabled={saving}
                onChange={(v) => pref({ family_fasting: v })} />
            )}
          </>
        )
      case 'messages':
        return (
          <Toggle label={S('kindWords')} checked={prefs.encouragement !== false} disabled={saving}
            onChange={(v) => pref({ encouragement: v })} />
        )
      case 'privacy':
        return (
          <>
            {CONSENTS.map((g) => (
              <Toggle
                key={g}
                label={S(`consent.${g}`)}
                hint={S(`consent.${g}Note`)}
                checked={(exp.profile.consents as Record<string, boolean> | undefined)?.[g] !== false}
                disabled={saving}
                onChange={(v) => save({ consents: { [g]: v } as SettingsIn['consents'] }, v ? tr('common.saved') : S('deletedAnswers'))}
              />
            ))}
            <p className="m-0 px-4 py-2 text-[12px] leading-snug text-[#5A6A60]">{S('consentNote')}</p>
            <button type="button" className={linkRow + ' border-t'} onClick={() => onNavigate('report')}>
              <span className="flex flex-col gap-0.5">
                <span className="text-[15px] font-semibold text-[#2C5140]">{S('report')}</span>
                <span className="text-[12px] text-[#5A6A60]">{S('reportHint')}</span>
              </span>
              <span aria-hidden="true" className="rtl-flip">›</span>
            </button>
            <button type="button" className={linkRow} onClick={download}>
              <span className="text-[15px]">{S('download')}</span>
            </button>
            <button type="button" className={linkRow + ' border-b-0 hover:bg-[#FDE8E4]'} onClick={() => setConfirm('delete')}>
              <span className="text-[15px] font-medium text-[#A02A1C]">{S('delete')}</span>
            </button>
          </>
        )
      case 'help':
        return (
          <div className="p-4 flex flex-col gap-2">
            <a href="tel:998" className="min-h-[52px] px-4 rounded-[14px] bg-[#A02A1C] text-white flex items-center no-underline font-semibold">
              {S('call998')}
            </a>
            <a href="tel:800725462"
              className="min-h-[52px] px-4 rounded-[14px] border-2 border-[#1B2A22] text-[#1B2A22] flex items-center no-underline font-semibold">
              {S('callSakina')}
            </a>
            <button
              type="button"
              onClick={() => {
                setState((prev) => ({ ...prev, careReason: 'help' }))
                onNavigate('care')
              }}
              className="self-start min-h-[40px] bg-transparent border-0 p-0 text-[14px] font-semibold text-[#2C5140] cursor-pointer"
            >
              {S('openHelp')}
            </button>
          </div>
        )
    }
  }

  return (
    <ScreenFrame
      tab="settings"
      onNavigate={onNavigate}
      background={
        <>
          <TatreezPattern width={210} height={210} style={{ right: '-110px', bottom: '90px', opacity: 0.07 }} />
          <ArabicCalligraphyRing width={460} height={460} style={{ left: '-250px', top: '-140px', opacity: 0.12 }} />
        </>
      }
    >
      <h1 className="m-0 p-6 pb-0 font-display tracking-tight text-[28px] font-semibold">{S('title')}</h1>

      {data.loading && !exp && <LoadingView />}
      {data.error && <ErrorView message={data.error} onRetry={data.reload} />}

      {prefs && (
        <div className="p-6 pt-3 flex flex-col gap-2.5">
          {GROUPS.map((g) => {
            const isOpen = open === g
            return (
              <section key={g} className="bg-white/90 rounded-[20px] shadow-card overflow-hidden">
                <button
                  type="button"
                  aria-expanded={isOpen}
                  aria-controls={`settings-${g}`}
                  onClick={() => setOpen(isOpen ? null : g)}
                  className="w-full min-h-[56px] px-4 py-2 flex items-center justify-between gap-3 bg-transparent border-0 text-start cursor-pointer"
                >
                  <span className="flex flex-col gap-0.5">
                    <span className="text-[16px] font-semibold text-[#1B2A22]">{S(`g.${g}`)}</span>
                    <span className="text-[12px] text-[#5A6A60]">{S(`g.${g}Hint`)}</span>
                  </span>
                  <span aria-hidden="true" className={`text-[#5A6A60] transition-transform ${isOpen ? 'rotate-90' : 'rtl-flip'}`}>
                    ›
                  </span>
                </button>
                {isOpen && (
                  <div id={`settings-${g}`} className="border-t border-[#E6EBE4]">
                    {body(g)}
                  </div>
                )}
              </section>
            )
          })}

          {/* Sign out: its own clear button, outside the groups */}
          <button
            type="button"
            onClick={() => setConfirm('signout')}
            className="mt-3 min-h-[52px] rounded-[16px] border-2 border-[#A02A1C] bg-white text-[#A02A1C] text-[16px] font-semibold cursor-pointer flex flex-col items-center justify-center"
          >
            {S('signOut')}
            {username && <span className="text-[12px] font-normal text-[#5A6A60]">{S('signOutAs', { name: username })}</span>}
          </button>
        </div>
      )}

      {confirm && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full flex flex-col gap-3 shadow-2xl">
            <h3 className={`m-0 text-lg font-bold ${confirm === 'delete' ? 'text-[#A02A1C]' : 'text-[#1B2A22]'}`}>
              {confirm === 'delete' ? S('deleteTitle') : S('signOutTitle')}
            </h3>
            <p className="m-0 text-sm text-[#3F4F45]">
              {confirm === 'delete'
                ? S('deleteBody')
                : username
                  ? S('signOutWith', { name: username })
                  : S('signOutNoUser')}
            </p>
            <div className="flex gap-2 justify-end mt-2">
              <button type="button" onClick={() => setConfirm(null)}
                className="px-4 py-2 text-sm font-medium rounded-xl border border-[#C5D0C7] bg-white cursor-pointer">
                {tr('common.cancel')}
              </button>
              <button
                type="button"
                disabled={saving}
                onClick={() => finish(confirm)}
                className="px-4 py-2 text-sm font-semibold rounded-xl bg-[#A02A1C] text-white border-0 cursor-pointer disabled:opacity-60"
              >
                {confirm === 'delete' ? S('yesDelete') : S('signOut')}
              </button>
            </div>
          </div>
        </div>
      )}
    </ScreenFrame>
  )
}
