import React, { useState } from 'react'
import { ScreenProps } from '../types'
import { api, ApiError, errorText } from '../api/client'
import { ScreenFrame } from '../components/ScreenFrame'
import { ArabicCalligraphyRing } from '../components/BackgroundMotifs'

const USERNAME = /^[A-Za-z0-9._-]{3,30}$/
const MIN_PASSWORD = 8
const input =
  'mt-2 w-full min-h-[48px] box-border rounded-xl border border-[#C5D0C7] bg-white px-3 text-[15px] font-normal text-[#1B2A22]'

/** Last sign-up step (optional): a username + password, so the account can be opened on another device.
 *  Saved with PATCH /settings {login}. No email is asked for, so there's no password reset. */
export const SaveProgressScreen: React.FC<ScreenProps & { onDone: () => void }> = ({ state, showToast, onDone }) => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [saving, setSaving] = useState(false)
  const valid = USERNAME.test(username) && password.length >= MIN_PASSWORD

  const save = async () => {
    if (!valid) return
    setSaving(true)
    try {
      await api.settings(state.session!, { login: { username, password } })
      showToast('Saved. You can now sign in on another device.')
      onDone()
    } catch (e) {
      showToast(e instanceof ApiError && e.status === 409 ? 'That username is taken. Try another one.' : errorText(e))
    } finally {
      setSaving(false)
    }
  }

  return (
    <ScreenFrame
      dir={state.language === 'ar' ? 'rtl' : 'ltr'}
      background={<ArabicCalligraphyRing width={440} height={440} style={{ right: -230, top: -160, opacity: 0.12 }} />}
      footer={
        <div className="flex flex-col gap-1.5">
          <button
            type="button"
            onClick={save}
            disabled={!valid || saving}
            className="min-h-[52px] rounded-[14px] bg-[#3E6B53] hover:bg-[#2C5140] disabled:bg-[#9FB3A6] disabled:cursor-not-allowed text-white text-[16px] font-semibold border-0 cursor-pointer"
          >
            {saving ? 'Saving…' : 'Save and start'}
          </button>
          <button
            type="button"
            onClick={onDone}
            className="min-h-[44px] bg-transparent border-0 text-[14px] font-medium text-[#3E6B53] cursor-pointer"
          >
            Continue without an account
          </button>
          <p className="m-0 text-center text-[12px] leading-snug text-[#5A6A60]">
            Without one, your progress lives only in this browser and may be lost if you clear it or change phones.
          </p>
        </div>
      }
    >
      <div className="p-6 flex flex-col gap-4">
        <h1 className="m-0 mt-4 font-display tracking-tight text-[26px] leading-tight font-semibold">Save your progress</h1>
        <p className="m-0 text-[14px] leading-relaxed text-[#3F4F45]">
          Pick a username and password to sign in on another phone or laptop. We don't ask for an email, so we can't
          reset a forgotten password.
        </p>
        <label className="block text-[15px] font-semibold">
          Username
          <span className="block mt-0.5 text-[12px] font-normal text-[#5A6A60]">3–30 letters, numbers, . _ or -</span>
          <input
            type="text"
            autoComplete="username"
            autoCapitalize="none"
            maxLength={30}
            value={username}
            onChange={(e) => setUsername(e.target.value.trim())}
            className={input}
          />
        </label>
        <label className="block text-[15px] font-semibold">
          Password
          <span className="block mt-0.5 text-[12px] font-normal text-[#5A6A60]">At least {MIN_PASSWORD} characters</span>
          <input
            type="password"
            autoComplete="new-password"
            maxLength={128}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className={input}
          />
        </label>
      </div>
    </ScreenFrame>
  )
}
