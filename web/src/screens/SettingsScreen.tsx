import React, { useEffect, useState } from 'react'
import { ScreenProps, Household, SettingPref, Weekday } from '../types'
import { api, ApiError, Condition, errorText, ExportOut, SettingsIn } from '../api/client'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { ScreenFrame } from '../components/ScreenFrame'
import { ProfileSection } from '../components/ProfileSection'
import { ChipGroup } from '../components/OnboardingLayout'
import { LoadingView, ErrorView } from '../components/StatusViews'
import { useAsync } from '../lib/useAsync'

const CONDITIONS: { value: Condition; label: string }[] = [
  { value: 'diabetes', label: 'Diabetes' },
  { value: 'high_blood_pressure', label: 'High blood pressure' },
  { value: 'back_or_joint_pain', label: 'Back or joint pain' },
  { value: 'stress', label: 'Stress' },
  { value: 'recovering_from_illness_or_injury', label: 'Recovering from illness or injury' },
]
const HOUSEHOLD: { value: Household; label: string }[] = [
  { value: 'alone', label: 'Alone' },
  { value: 'family', label: 'With family' },
  { value: 'children', label: 'With children' },
  { value: 'older_relatives', label: 'With older relatives' },
]
const PLACES: { value: SettingPref; label: string }[] = [
  { value: 'indoor', label: 'Indoors' },
  { value: 'outdoor', label: 'Outdoors' },
  { value: 'either', label: 'Either' },
]
const WEEKDAYS: { value: Weekday; label: string }[] = [
  { value: 'sun', label: 'Sun' },
  { value: 'mon', label: 'Mon' },
  { value: 'tue', label: 'Tue' },
  { value: 'wed', label: 'Wed' },
  { value: 'thu', label: 'Thu' },
  { value: 'fri', label: 'Fri' },
  { value: 'sat', label: 'Sat' },
]
// Withdrawing one of these deletes those answers (the health check can't be withdrawn: it keeps the plan safe).
const CONSENTS: { group: string; label: string; note: string }[] = [
  { group: 'body', label: 'Height and weight', note: 'Used only for a safe starting level' },
  { group: 'conditions', label: "Anything you're managing", note: 'Shapes the order of your steps' },
  { group: 'history', label: 'What helped before, and why it matters', note: 'Shown back on tough days' },
  { group: 'preferences', label: 'Preferences', note: 'Turning this off resets them, including your name' },
]

type GroupId = 'profile' | 'health' | 'routine' | 'family' | 'messages' | 'privacy' | 'help'
const GROUPS: { id: GroupId; title: string; hint: string }[] = [
  { id: 'profile', title: 'Profile', hint: 'Name, language, wording, read aloud, daily anchor' },
  { id: 'health', title: 'Health', hint: "Anything you're managing, health check, I'm OK now" },
  { id: 'routine', title: 'Routine', hint: 'Shifts, Ramadan and iftar, quiet hours' },
  { id: 'family', title: 'Family', hint: 'Who you live with, caring, family fasting' },
  { id: 'messages', title: 'Messages', hint: 'Kind words after good moments' },
  { id: 'privacy', title: 'Privacy & data', hint: 'What you share, download, delete' },
  { id: 'help', title: 'Help', hint: '998 and 800 SAKINA' },
]

interface SettingsScreenProps extends ScreenProps {
  /** Clears the session and returns to Welcome (after logout or DELETE /users/{id}). */
  onSignedOut: () => void
}

const row = 'min-h-[48px] px-4 py-2 flex items-center justify-between gap-3 border-b border-[#E6EBE4] text-[#1B2A22]'
const check = 'w-[22px] h-[22px] flex-none accent-[#3E6B53] cursor-pointer'
const field = 'min-h-[40px] rounded-lg border border-[#C5D0C7] px-2 text-[14px] bg-white'
const smallBtn =
  'self-start min-h-[40px] px-4 rounded-[12px] bg-[#3E6B53] text-white text-[14px] font-semibold border-0 cursor-pointer disabled:opacity-60'
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

/** Settings in groups that fold open. Reads GET /export, saves with PATCH /settings. */
export const SettingsScreen: React.FC<SettingsScreenProps> = ({ state, setState, onNavigate, showToast, onSignedOut }) => {
  const session = state.session!
  const data = useAsync<ExportOut>(() => api.exportData(session), [session, state.dataVersion])
  const arNote = useAsync(
    () => (state.language === 'ar' ? api.onboardingContent('ar').then((c) => c.translation_note) : Promise.resolve(null)),
    [state.language],
  )
  const [open, setOpen] = useState<GroupId | null>('profile')
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
      showToast(
        e instanceof ApiError && e.status === 409 && body.ramadan
          ? "Ramadan isn't close yet by the calendar, so nothing changed."
          : errorText(e),
      )
    } finally {
      setSaving(false)
    }
  }
  const pref = (p: Record<string, unknown>, done = 'Saved.') => save({ preferences: p }, done)

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
    showToast('Your Rebound data has been downloaded.')
  }

  const finish = async (kind: 'delete' | 'signout') => {
    setSaving(true)
    try {
      if (kind === 'delete') await api.deleteUser(session)
      else await api.logout(session)
      setConfirm(null)
      showToast(kind === 'delete' ? 'Your account and all your data were deleted.' : 'Signed out.')
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
              <span className="text-[15px]">Name</span>
              <input
                type="text"
                maxLength={40}
                value={name}
                onChange={(e) => setName(e.target.value)}
                onBlur={() => name.trim() !== (prefs.display_name ?? '') && pref({ display_name: name.trim() || null })}
                placeholder="Add a name (optional)"
                className={field + ' w-40 text-end'}
              />
            </label>
            <button
              type="button"
              className={row + ' w-full bg-transparent border-x-0 border-t-0 text-left cursor-pointer'}
              onClick={() => setState((prev) => ({ ...prev, language: prev.language === 'en' ? 'ar' : 'en' }))}
            >
              <span className="flex flex-col gap-0.5">
                <span className="text-[15px]">App language</span>
                <span className="text-[12px] text-[#5A6A60]">Coaching messages use the language you signed up with</span>
              </span>
              <span className="text-[13px] text-[#5A6A60]">{state.language === 'en' ? 'English' : 'العربية'}</span>
            </button>
            {arNote.data && <p className="m-0 px-4 py-2 text-[12px] text-[#8A4B0F]">{arNote.data}</p>}
            <Toggle
              label="Simpler wording"
              hint="Shorter sentences and everyday words"
              checked={prefs.reading_level === 'simple'}
              disabled={saving}
              onChange={(v) => pref({ reading_level: v ? 'simple' : 'standard' })}
            />
            <Toggle
              label="Read steps aloud"
              hint="Adds a speaker button to each step"
              checked={!!prefs.read_aloud}
              disabled={saving}
              onChange={(v) => pref({ read_aloud: v })}
            />
            <label className={row}>
              <span className="flex flex-col gap-0.5">
                <span className="text-[15px]">Daily anchor</span>
                <span className="text-[12px] text-[#5A6A60]">Something you do every day, e.g. after maghrib</span>
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
              <p className="m-0 mb-2 text-[12px] font-semibold text-[#5A6A60]">What you told us at sign-up</p>
              <ProfileSection exp={exp} />
            </div>
            <button
              type="button"
              className={row + ' w-full bg-transparent border-x-0 border-t-0 border-b-0 text-left cursor-pointer'}
              onClick={() => setConfirm('signout')}
            >
              <span className="text-[15px] font-medium text-[#2C5140]">Sign out{username ? ` (${username})` : ''}</span>
            </button>
          </>
        )
      case 'health':
        return (
          <>
            <div className="px-4 py-3 flex flex-col gap-2 border-b border-[#E6EBE4]">
              <ChipGroup<Condition>
                label="Anything you're managing"
                hint="Optional. It changes the order of your steps, never the medical care you get."
                options={CONDITIONS}
                isSelected={(v) => conditions.includes(v)}
                onToggle={(v) => setConditions((c) => (c.includes(v) ? c.filter((x) => x !== v) : [...c, v]))}
              />
              <button
                type="button"
                disabled={saving}
                className={smallBtn}
                onClick={() =>
                  save({ conditions: { managing: conditions }, consents: { conditions: true } }, 'Saved. Your plan was rebuilt.')
                }
              >
                Save
              </button>
            </div>
            <div className={row}>
              <span className="flex flex-col gap-0.5">
                <span className="text-[15px]">Health check</span>
                <span className="text-[12px] text-[#5A6A60]">It keeps your plan safe, so it can't be switched off</span>
              </span>
            </div>
            {flags.includes('illness') ? (
              <button
                type="button"
                disabled={saving}
                className={row + ' w-full bg-transparent border-x-0 border-t-0 border-b-0 text-left cursor-pointer'}
                onClick={() => save({ context: { illness: false } }, "Glad you're feeling better. Movement steps are back.")}
              >
                <span className="text-[15px] font-medium text-[#2C5140]">I'm OK now</span>
              </button>
            ) : (
              <p className="m-0 px-4 py-3 text-[12px] text-[#5A6A60]">
                "I'm OK now" appears here after you tell us you're unwell in a check-in.
              </p>
            )}
          </>
        )
      case 'routine':
        return (
          <>
            {basics.schedule_type === 'shift' && (
              <div className="px-4 py-3 flex flex-col gap-2 border-b border-[#E6EBE4]">
                <ChipGroup<Weekday>
                  label="Shift days"
                  hint="The days your shifts start. Steps move the day after you save."
                  options={WEEKDAYS}
                  isSelected={(v) => shiftDays.includes(v)}
                  onToggle={(v) => setShiftDays((d) => (d.includes(v) ? d.filter((x) => x !== v) : [...d, v]))}
                  columns={4}
                />
                <div className="flex items-center gap-2 text-[14px]">
                  <input type="time" className={field} value={shiftTimes.start} aria-label="Shift starts"
                    onChange={(e) => setShiftTimes((s) => ({ ...s, start: e.target.value }))} />
                  <span>to</span>
                  <input type="time" className={field} value={shiftTimes.end} aria-label="Shift ends"
                    onChange={(e) => setShiftTimes((s) => ({ ...s, end: e.target.value }))} />
                </div>
                <button
                  type="button"
                  disabled={saving}
                  className={smallBtn}
                  onClick={() => save({ shifts: shiftDays.length ? [{ days: shiftDays, ...shiftTimes }] : [] }, 'Shifts saved.')}
                >
                  Save shifts
                </button>
              </div>
            )}
            <div className="px-4 py-3 border-b border-[#E6EBE4]">
              <ChipGroup<SettingPref>
                label="Where do you prefer to be active?"
                options={PLACES}
                isSelected={(v) => prefs.setting === v}
                onToggle={(v) => !saving && pref({ setting: v })}
                columns={3}
              />
            </div>
            <Toggle
              label="I fast in Ramadan"
              checked={!!prefs.fasting_ramadan}
              disabled={saving}
              onChange={(v) => pref({ fasting_ramadan: v, ...(v ? {} : { family_fasting: false }) })}
            />
            {prefs.fasting_ramadan && (
              <div className={row}>
                <span className="flex flex-col gap-0.5">
                  <span className="text-[15px]">Iftar time</span>
                  <span className="text-[12px] text-[#5A6A60]">Leave empty to use sunset in Abu Dhabi</span>
                </span>
                <input
                  type="time"
                  className={field}
                  value={iftar}
                  disabled={saving}
                  onChange={(e) => setIftar(e.target.value)}
                  onBlur={() => iftar !== hm(prefs.iftar_time) && pref({ iftar_time: iftar || null }, 'Iftar time saved.')}
                />
              </div>
            )}
            {prefs.fasting_ramadan && !flags.includes('ramadan') && (
              <button
                type="button"
                disabled={saving}
                className={row + ' w-full bg-transparent border-x-0 border-t-0 text-left cursor-pointer'}
                onClick={() => save({ ramadan: 'started_today' }, 'Ramadan Mubarak. Your steps are now fasting-friendly.')}
              >
                <span className="flex flex-col gap-0.5">
                  <span className="text-[15px]">Moon sighted: Ramadan started today</span>
                  <span className="text-[12px] text-[#5A6A60]">Ramadan turns on by itself; use this if it started a day early</span>
                </span>
              </button>
            )}
            <div className="px-4 py-3 flex flex-col gap-2">
              <span className="flex flex-col gap-0.5">
                <span className="text-[15px]">Quiet hours</span>
                <span className="text-[12px] text-[#5A6A60]">We never send messages in this time</span>
              </span>
              <div className="flex items-center gap-2 text-[14px]">
                <input type="time" className={field} value={quiet.start} aria-label="Quiet from"
                  onChange={(e) => setQuiet((q) => ({ ...q, start: e.target.value }))} />
                <span>to</span>
                <input type="time" className={field} value={quiet.end} aria-label="Quiet until"
                  onChange={(e) => setQuiet((q) => ({ ...q, end: e.target.value }))} />
              </div>
              <button
                type="button"
                disabled={saving || (!!quiet.start !== !!quiet.end)}
                className={smallBtn}
                onClick={() => pref({ quiet_hours: quiet.start && quiet.end ? quiet : null }, 'Quiet hours saved.')}
              >
                Save quiet hours
              </button>
            </div>
          </>
        )
      case 'family':
        return (
          <>
            <div className="px-4 py-3 border-b border-[#E6EBE4]">
              <ChipGroup<Household>
                label="Who do you live with?"
                options={HOUSEHOLD}
                isSelected={(v) => prefs.household === v}
                onToggle={(v) => !saving && pref({ household: prefs.household === v ? null : v })}
                columns={2}
              />
            </div>
            <Toggle label="I care for someone at home" checked={!!prefs.caregiver} disabled={saving}
              onChange={(v) => pref({ caregiver: v })} />
            {basics.sex === 'female' && (
              <Toggle
                label="I prefer women-only spaces"
                checked={prefs.space_preference === 'women_only_spaces'}
                disabled={saving}
                onChange={(v) => pref({ space_preference: v ? 'women_only_spaces' : 'any' })}
              />
            )}
            {prefs.fasting_ramadan && (
              <Toggle label="My family fasts together" checked={!!prefs.family_fasting} disabled={saving}
                onChange={(v) => pref({ family_fasting: v })} />
            )}
          </>
        )
      case 'messages':
        return (
          <Toggle
            label="Kind words after good moments"
            checked={prefs.encouragement !== false}
            disabled={saving}
            onChange={(v) => pref({ encouragement: v })}
          />
        )
      case 'privacy':
        return (
          <>
            {CONSENTS.map((c) => (
              <Toggle
                key={c.group}
                label={c.label}
                hint={c.note}
                checked={(exp.profile.consents as Record<string, boolean> | undefined)?.[c.group] !== false}
                disabled={saving}
                onChange={(v) =>
                  save({ consents: { [c.group]: v } as SettingsIn['consents'] }, v ? 'Saved.' : 'Those answers were deleted.')
                }
              />
            ))}
            <p className="m-0 px-4 py-2 text-[12px] leading-snug text-[#5A6A60]">
              Turning one off deletes those answers. The health check keeps your plan safe, so it can't be switched
              off: to remove it, delete your account. Your employer only ever sees totals for groups of 10 or more.
            </p>
            <button type="button" className={row + ' w-full bg-transparent border-x-0 text-left cursor-pointer'} onClick={() => onNavigate('report')}>
              <span className="flex flex-col gap-0.5">
                <span className="text-[15px] font-semibold text-[#2C5140]">My progress report</span>
                <span className="text-[12px] text-[#5A6A60]">Save as PDF or download a spreadsheet</span>
              </span>
              <span aria-hidden="true">›</span>
            </button>
            <button type="button" className={row + ' w-full bg-transparent border-x-0 border-t-0 text-left cursor-pointer'} onClick={download}>
              <span className="text-[15px]">Download all my data (JSON)</span>
            </button>
            <button
              type="button"
              className={row + ' w-full bg-transparent border-0 text-left cursor-pointer hover:bg-[#FDE8E4]'}
              onClick={() => setConfirm('delete')}
            >
              <span className="text-[15px] font-medium text-[#A02A1C]">Delete my account</span>
            </button>
          </>
        )
      case 'help':
        return (
          <div className="p-4 flex flex-col gap-2">
            <a href="tel:998" className="min-h-[52px] px-4 rounded-[14px] bg-[#A02A1C] text-white flex items-center no-underline font-semibold">
              Call 998 · ambulance, UAE emergency
            </a>
            <a
              href="tel:800725462"
              className="min-h-[52px] px-4 rounded-[14px] border-2 border-[#1B2A22] text-[#1B2A22] flex items-center no-underline font-semibold"
            >
              Call 800 SAKINA (800 725462) · 24/7 mental health support
            </a>
            <button
              type="button"
              onClick={() => {
                setState((prev) => ({ ...prev, careReason: 'help' }))
                onNavigate('care')
              }}
              className="self-start min-h-[40px] bg-transparent border-0 p-0 text-[14px] font-semibold text-[#2C5140] cursor-pointer"
            >
              Open the help screen
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
      <h1 className="m-0 p-6 pb-0 font-display tracking-tight text-[28px] font-semibold">Settings</h1>

      {data.loading && !exp && <LoadingView />}
      {data.error && <ErrorView message={data.error} onRetry={data.reload} />}

      {prefs && (
        <div className="p-6 pt-3 flex flex-col gap-2.5">
          {GROUPS.map((g) => {
            const isOpen = open === g.id
            return (
              <section key={g.id} className="bg-white/90 rounded-[20px] shadow-card overflow-hidden">
                <button
                  type="button"
                  aria-expanded={isOpen}
                  aria-controls={`settings-${g.id}`}
                  onClick={() => setOpen(isOpen ? null : g.id)}
                  className="w-full min-h-[56px] px-4 py-2 flex items-center justify-between gap-3 bg-transparent border-0 text-left cursor-pointer"
                >
                  <span className="flex flex-col gap-0.5">
                    <span className="text-[16px] font-semibold text-[#1B2A22]">{g.title}</span>
                    <span className="text-[12px] text-[#5A6A60]">{g.hint}</span>
                  </span>
                  <span aria-hidden="true" className={`text-[#5A6A60] transition-transform ${isOpen ? 'rotate-90' : ''}`}>
                    ›
                  </span>
                </button>
                {isOpen && (
                  <div id={`settings-${g.id}`} className="border-t border-[#E6EBE4]">
                    {body(g.id)}
                  </div>
                )}
              </section>
            )
          })}
        </div>
      )}

      {confirm && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full flex flex-col gap-3 shadow-2xl">
            <h3 className={`m-0 text-lg font-bold ${confirm === 'delete' ? 'text-[#A02A1C]' : 'text-[#1B2A22]'}`}>
              {confirm === 'delete' ? 'Delete your account?' : 'Sign out?'}
            </h3>
            <p className="m-0 text-sm text-[#3F4F45]">
              {confirm === 'delete'
                ? "This permanently deletes your plan, health check answers and progress. It can't be undone."
                : username
                  ? `You can sign in again with your username "${username}" and password.`
                  : "You haven't saved a username and password, so you won't be able to come back to this account."}
            </p>
            <div className="flex gap-2 justify-end mt-2">
              <button
                type="button"
                onClick={() => setConfirm(null)}
                className="px-4 py-2 text-sm font-medium rounded-xl border border-[#C5D0C7] bg-white cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={saving}
                onClick={() => finish(confirm)}
                className={`px-4 py-2 text-sm font-semibold rounded-xl text-white border-0 cursor-pointer disabled:opacity-60 ${
                  confirm === 'delete' ? 'bg-[#A02A1C]' : 'bg-[#3E6B53]'
                }`}
              >
                {confirm === 'delete' ? 'Yes, delete' : 'Sign out'}
              </button>
            </div>
          </div>
        </div>
      )}
    </ScreenFrame>
  )
}
