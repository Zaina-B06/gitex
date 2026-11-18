import React, { useState } from 'react'
import { ScreenProps } from '../types'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { api, ApiError, errorText, SeedPersona } from '../api/client'
import { useAsync } from '../lib/useAsync'
import { PERSONA_LINES, demoKey, firstName, forgetDemoKey, savePersonas } from '../lib/demo'

type Mode = 'home' | 'signin' | 'demo'

const light =
  'min-h-[52px] rounded-2xl bg-white hover:bg-[#F3F7F4] text-[#2C5140] text-[16px] font-bold border-0 cursor-pointer shadow-[0_10px_22px_-10px_rgba(20,40,28,0.6)] disabled:opacity-60'
const ghost =
  'min-h-[48px] rounded-2xl bg-white/10 hover:bg-white/20 text-white text-[15px] font-semibold border border-white/40 cursor-pointer'
const input =
  'mt-1.5 w-full min-h-[48px] box-border rounded-xl border-0 bg-white px-3 text-[15px] text-[#1B2A22]'

/** First screen: what Rebound is, the language, then start sign-up, sign in, or try a demo person. */
export const WelcomeScreen: React.FC<ScreenProps> = ({ state, setState, onNavigate, showToast }) => {
  const isArabic = state.language === 'ar'
  const [mode, setMode] = useState<Mode>('home')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [personas, setPersonas] = useState<SeedPersona[] | null>(null)
  const setLanguage = (language: 'en' | 'ar') => setState((prev) => ({ ...prev, language }))
  // "Draft translation, pending native review" while the Arabic isn't reviewed (HANDOFF, Part D).
  const content = useAsync(() => (isArabic ? api.onboardingContent('ar') : Promise.resolve(null)), [isArabic])

  const open = (userId: string, token: string) => {
    setState((prev) => ({ ...prev, session: { userId, token }, justSignedUp: false }))
    onNavigate('today')
  }

  const signIn = async () => {
    setBusy(true)
    try {
      const out = await api.login(username.trim(), password)
      open(out.user_id, out.token)
    } catch (e) {
      showToast(
        e instanceof ApiError && e.status === 401
          ? 'Wrong username or password.'
          : e instanceof ApiError && e.status === 429
            ? 'Too many tries. Please wait 15 minutes.'
            : errorText(e),
      )
    } finally {
      setBusy(false)
    }
  }

  const tryDemo = async () => {
    const key = demoKey()
    if (!key) return
    setBusy(true)
    try {
      const out = await api.demoSeed(key)
      savePersonas(out.personas)
      setPersonas(out.personas)
      setMode('demo')
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) forgetDemoKey()
      showToast(
        e instanceof ApiError && e.status === 401
          ? 'That demo key is wrong. Try again.'
          : e instanceof ApiError && e.status === 404
            ? "The demo isn't switched on for this server."
            : errorText(e),
      )
    } finally {
      setBusy(false)
    }
  }

  return (
    <div
      dir={isArabic ? 'rtl' : 'ltr'}
      className="relative overflow-hidden isolate w-full h-full overflow-y-auto overflow-x-hidden bg-[#54705C] font-sans text-white flex flex-col p-6"
    >
      <TatreezPattern width={230} height={230} color="#2E4837" opacity={0.35} style={{ right: -90, bottom: 160 }} />
      <ArabicCalligraphyRing width={620} height={620} color="#2E4837" opacity={0.55} style={{ left: -330, top: 220 }} />
      <ArabicCalligraphyRing width={320} height={320} color="#2E4837" opacity={0.4} style={{ right: -150, top: -120 }} />

      <span className="mt-8 text-[13px] tracking-wide text-[#DDE9E0]">{isArabic ? 'ريباوند' : 'Rebound'}</span>
      <h1 className="mt-2 mb-3 font-display tracking-tight text-[34px] leading-[1.1] font-semibold">
        {isArabic ? 'خطوة صغيرة كل يوم.' : 'One small step a day.'}
        <br />
        {isArabic ? 'لا شيء يعود إلى الصفر.' : 'Nothing resets to zero.'}
      </h1>
      <p className="m-0 text-[15px] leading-relaxed text-[#F3F7F4]">
        {isArabic
          ? 'نساعدك على الحركة والنوم بشكل أفضل، ونخفف الخطة في الأيام الصعبة.'
          : 'We help you move and sleep a little better, and make the plan lighter on tough days.'}
      </p>

      <fieldset className="mt-6 p-0 border-0">
        <legend className="p-0 text-[14px] font-semibold text-[#F3F7F4]">
          {isArabic ? 'اختر اللغة' : 'Choose your language'}
        </legend>
        <div className="mt-2 grid grid-cols-2 gap-2">
          {(
            [
              { value: 'en', label: 'English' },
              { value: 'ar', label: 'العربية' },
            ] as const
          ).map((opt) => {
            const on = state.language === opt.value
            return (
              <button
                key={opt.value}
                type="button"
                aria-pressed={on}
                onClick={() => setLanguage(opt.value)}
                className={`min-h-[52px] rounded-[14px] text-[16px] cursor-pointer transition-colors ${
                  opt.value === 'ar' ? 'font-arabic text-[19px]' : ''
                } ${
                  on
                    ? 'bg-white text-[#2C5140] font-semibold border-2 border-white'
                    : 'bg-white/10 text-white border border-white/40 hover:bg-white/20'
                }`}
              >
                {opt.label}
              </button>
            )
          })}
        </div>
      </fieldset>

      <div className="mt-auto pt-6 flex flex-col gap-2">
        {content.data?.translation_note && <p className="m-0 text-[12px] text-[#FFE9C7]">{content.data.translation_note}</p>}

        {mode === 'home' && (
          <>
            <p className="m-0 text-[12px] leading-relaxed text-[#DDE9E0]">
              {isArabic ? 'يستغرق حوالي 3 دقائق. معظم الأسئلة اختيارية.' : 'Takes about 3 minutes. Most questions are optional.'}
            </p>
            <button type="button" className={light} onClick={() => onNavigate('onboarding-basics')}>
              {isArabic ? 'ابدأ خطتي' : 'Start my plan'}
            </button>
            <button type="button" className={ghost} onClick={() => setMode('signin')}>
              {isArabic ? 'تسجيل الدخول' : 'Sign in'}
            </button>
            <button type="button" className={ghost} disabled={busy} onClick={tryDemo}>
              {busy ? '…' : isArabic ? 'جرّب شخصاً تجريبياً' : 'Try a demo person'}
            </button>
          </>
        )}

        {mode === 'signin' && (
          <form
            className="flex flex-col gap-2"
            onSubmit={(e) => {
              e.preventDefault()
              signIn()
            }}
          >
            <label className="text-[14px] font-semibold">
              {isArabic ? 'اسم المستخدم' : 'Username'}
              <input className={input} autoComplete="username" autoCapitalize="none" value={username}
                onChange={(e) => setUsername(e.target.value)} />
            </label>
            <label className="text-[14px] font-semibold">
              {isArabic ? 'كلمة المرور' : 'Password'}
              <input className={input} type="password" autoComplete="current-password" value={password}
                onChange={(e) => setPassword(e.target.value)} />
            </label>
            <button type="submit" className={light} disabled={busy || !username.trim() || !password}>
              {busy ? '…' : isArabic ? 'دخول' : 'Sign in'}
            </button>
            <button type="button" className="min-h-[44px] bg-transparent border-0 text-white text-[14px] cursor-pointer" onClick={() => setMode('home')}>
              {isArabic ? 'رجوع' : 'Back'}
            </button>
          </form>
        )}

        {mode === 'demo' && personas && (
          <>
            <p className="m-0 text-[13px] text-[#F3F7F4]">Pick someone to try. Their first week is already filled in.</p>
            {personas.map((p) => (
              <button
                key={p.user_id}
                type="button"
                onClick={() => open(p.user_id, p.token)}
                className="min-h-[60px] px-4 py-2 rounded-2xl bg-white text-start text-[#1B2A22] border-0 cursor-pointer flex flex-col gap-0.5"
              >
                <span className="text-[15px] font-semibold">{firstName(p)}</span>
                <span className="text-[12px] text-[#3F4F45]">{PERSONA_LINES[firstName(p)] ?? p.name}</span>
              </button>
            ))}
            <button type="button" className="min-h-[44px] bg-transparent border-0 text-white text-[14px] cursor-pointer" onClick={() => setMode('home')}>
              Back
            </button>
          </>
        )}
      </div>
    </div>
  )
}
