import React, { useState } from 'react'
import { ScreenProps } from '../types'
import { api, ApiError, Condition, errorText, ExportOut, SettingsIn } from '../api/client'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { ScreenFrame } from '../components/ScreenFrame'
import { ProfileSection } from '../components/ProfileSection'
import { EditAnswersSection } from '../components/EditAnswersSection'
import { LoadingView, ErrorView } from '../components/StatusViews'
import { useAsync } from '../lib/useAsync'

const CONDITIONS: { value: Condition; label: string }[] = [
  { value: 'diabetes', label: 'Diabetes' },
  { value: 'high_blood_pressure', label: 'High blood pressure' },
  { value: 'back_or_joint_pain', label: 'Back or joint pain' },
  { value: 'stress', label: 'Stress' },
  { value: 'recovering_from_illness_or_injury', label: 'Recovering from illness or injury' },
]

interface SettingsScreenProps extends ScreenProps {
  /** Clears the session and returns to Welcome (after DELETE /users/{id}). */
  onSignedOut: () => void
}

const section = 'bg-white/90 rounded-[20px] flex flex-col shadow-card overflow-hidden'
const heading = 'm-0 p-3 px-4 pb-1 text-[12px] font-semibold text-[#5A6A60]'
const row =
  'min-h-[48px] px-4 flex items-center justify-between gap-3 text-[#1B2A22] border-0 border-b border-solid border-[#E6EBE4] bg-transparent hover:bg-[#DDE9E0]/40 transition-colors text-left cursor-pointer'

/** Settings: reads the profile via GET /export, saves with PATCH /settings, deletes with DELETE /users/{id}. */
export const SettingsScreen: React.FC<SettingsScreenProps> = ({ state, setState, onNavigate, showToast, onSignedOut }) => {
  const session = state.session!
  const data = useAsync<ExportOut>(() => api.exportData(session), [session, state.dataVersion])
  const arNote = useAsync(
    () => (state.language === 'ar' ? api.onboardingContent('ar').then((c) => c.translation_note) : Promise.resolve(null)),
    [state.language],
  )
  const [editingConditions, setEditingConditions] = useState(false)
  const [draftConditions, setDraftConditions] = useState<Condition[]>([])
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [saving, setSaving] = useState(false)

  const profile = data.data?.profile
  const prefs = profile?.preferences
  const flags = data.data?.state.context_flags ?? []

  const save = async (body: SettingsIn, done: string) => {
    if (!data.data) return
    setSaving(true)
    try {
      const out = await api.settings(session, body)
      data.setData({
        ...data.data,
        profile: {
          ...data.data.profile,
          preferences: out.preferences,
          consents: out.consents,
          conditions: body.conditions ?? data.data.profile.conditions,
          basics: body.shifts !== undefined ? { ...data.data.profile.basics, shifts: body.shifts } : data.data.profile.basics,
        },
        state: { ...data.data.state, context_flags: out.state.context_flags },
      })
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

  const download = () => {
    if (!data.data) return
    const blob = new Blob([JSON.stringify(data.data, null, 2)], { type: 'application/json' })
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

  const deleteAccount = async () => {
    setSaving(true)
    try {
      await api.deleteUser(session)
      setConfirmDelete(false)
      showToast('Your account and all your data were deleted.')
      onSignedOut()
    } catch (e) {
      showToast(errorText(e))
      setSaving(false)
    }
  }

  const managing = profile?.conditions?.managing ?? []

  // Ramadan and Eid turn on by themselves from the calendar; this only corrects the start by a day.
  const ramadanStarted = () => save({ ramadan: 'started_today' }, 'Ramadan Mubarak. Your steps are now fasting-friendly.')

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

      {data.loading && !data.data && <LoadingView />}
      {data.error && <ErrorView message={data.error} onRetry={data.reload} />}

      {prefs && (
        <div className="p-6 pt-3 flex flex-col gap-3">
          <ProfileSection
            exp={data.data!}
            name={state.displayName}
            onNameChange={(displayName) => setState((prev) => ({ ...prev, displayName }))}
          />

          <EditAnswersSection exp={data.data!} saving={saving} save={save} />

          <section aria-labelledby="s-plan" className={section}>
            <h2 id="s-plan" className={heading}>
              My plan
            </h2>
            <button
              type="button"
              className={row}
              onClick={() => {
                setDraftConditions(managing)
                setEditingConditions(!editingConditions)
              }}
            >
              <span className="text-[15px]">Anything you're managing</span>
              <span className="text-[13px] text-[#5A6A60]">{managing.length} chosen</span>
            </button>
            {editingConditions && (
              <div className="p-4 pt-2 flex flex-col gap-2 border-b border-[#E6EBE4]">
                <div className="flex flex-wrap gap-2">
                  {CONDITIONS.map((c) => {
                    const on = draftConditions.includes(c.value)
                    return (
                      <button
                        key={c.value}
                        type="button"
                        aria-pressed={on}
                        onClick={() =>
                          setDraftConditions((d) => (on ? d.filter((x) => x !== c.value) : [...d, c.value]))
                        }
                        className={`min-h-[40px] px-3 rounded-[20px] text-[13px] cursor-pointer ${
                          on ? 'border-2 border-[#3E6B53] bg-[#DDE9E0] font-semibold text-[#2C5140]' : 'border border-[#C5D0C7] bg-white'
                        }`}
                      >
                        {c.label}
                      </button>
                    )
                  })}
                </div>
                <button
                  type="button"
                  disabled={saving}
                  onClick={async () => {
                    await save(
                      { conditions: { managing: draftConditions }, consents: { conditions: true } },
                      'Saved. Your plan was rebuilt.',
                    )
                    setEditingConditions(false)
                  }}
                  className="self-start min-h-[40px] px-4 rounded-[12px] bg-[#3E6B53] text-white text-[14px] font-semibold border-0 cursor-pointer disabled:opacity-60"
                >
                  Save
                </button>
              </div>
            )}
            {prefs.fasting_ramadan && !flags.includes('ramadan') && (
              <button type="button" className={row} disabled={saving} onClick={ramadanStarted}>
                <span className="flex flex-col gap-0.5">
                  <span className="text-[15px]">Moon sighted: Ramadan started today</span>
                  <span className="text-[12px] text-[#5A6A60]">Ramadan turns on by itself; use this if it started a day early where you are</span>
                </span>
              </button>
            )}
            <label className={row + ' border-b-0'}>
              <span className="flex flex-col gap-0.5">
                <span className="text-[15px]">Simpler wording</span>
                <span className="text-[12px] text-[#5A6A60]">Shorter sentences and everyday words</span>
              </span>
              <input
                type="checkbox"
                checked={prefs.reading_level === 'simple'}
                disabled={saving}
                onChange={(e) =>
                  save({ preferences: { reading_level: e.target.checked ? 'simple' : 'standard' } }, 'Saved.')
                }
                className="w-[22px] h-[22px] accent-[#3E6B53] cursor-pointer"
              />
            </label>
          </section>

          <section aria-labelledby="s-msg" className={section}>
            <h2 id="s-msg" className={heading}>
              Messages
            </h2>
            <label className={row}>
              <span className="text-[15px]">Kind words after good moments</span>
              <input
                type="checkbox"
                checked={prefs.encouragement !== false}
                disabled={saving}
                onChange={(e) => save({ preferences: { encouragement: e.target.checked } }, 'Saved.')}
                className="w-[22px] h-[22px] accent-[#3E6B53] cursor-pointer"
              />
            </label>
            <button
              type="button"
              className={row + ' border-b-0'}
              onClick={() => setState((prev) => ({ ...prev, language: prev.language === 'en' ? 'ar' : 'en' }))}
            >
              <span className="flex flex-col gap-0.5">
                <span className="text-[15px]">App language</span>
                <span className="text-[12px] text-[#5A6A60]">Coaching messages use the language you signed up with</span>
              </span>
              <span className="text-[13px] text-[#5A6A60]">{state.language === 'en' ? 'English' : 'عربي'}</span>
            </button>
            {arNote.data && <p className="m-0 px-4 pb-3 text-[12px] text-[#8A4B0F]">{arNote.data}</p>}
          </section>

          <section aria-labelledby="s-data" className={section}>
            <h2 id="s-data" className={heading}>
              My data
            </h2>
            <p className="m-0 px-4 pb-2 text-[12px] leading-snug text-[#5A6A60]">
              Your health check keeps your plan safe, so it can't be switched off. To remove it, delete your account.
            </p>
            <button type="button" className={row} onClick={() => onNavigate('report')}>
              <span className="flex flex-col gap-0.5">
                <span className="text-[15px] font-semibold text-[#2C5140]">My progress report</span>
                <span className="text-[12px] text-[#5A6A60]">Save as PDF or download a spreadsheet</span>
              </span>
              <span aria-hidden="true">›</span>
            </button>
            <button type="button" className={row} onClick={download}>
              <span className="text-[15px]">Download all my data (JSON)</span>
            </button>
            <button
              type="button"
              className={row + ' border-b-0 text-[#A02A1C] hover:bg-[#FDE8E4]'}
              onClick={() => setConfirmDelete(true)}
            >
              <span className="text-[15px] font-medium text-[#A02A1C]">Delete my account</span>
            </button>
          </section>

          <p className="m-0 text-[12px] leading-relaxed text-[#5A6A60]">
            Your employer only ever sees totals for groups of 10 or more people. Never your answers.
          </p>
        </div>
      )}

      {confirmDelete && (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4" role="dialog" aria-modal="true">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full flex flex-col gap-3 shadow-2xl">
            <h3 className="m-0 text-lg font-bold text-[#A02A1C]">Delete your account?</h3>
            <p className="m-0 text-sm text-[#3F4F45]">
              This permanently deletes your plan, health check answers and progress. It can't be undone.
            </p>
            <div className="flex gap-2 justify-end mt-2">
              <button
                type="button"
                onClick={() => setConfirmDelete(false)}
                className="px-4 py-2 text-sm font-medium rounded-xl border border-[#C5D0C7] bg-white cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={saving}
                onClick={deleteAccount}
                className="px-4 py-2 text-sm font-semibold rounded-xl bg-[#A02A1C] text-white border-0 cursor-pointer disabled:opacity-60"
              >
                Yes, delete
              </button>
            </div>
          </div>
        </div>
      )}

    </ScreenFrame>
  )
}
