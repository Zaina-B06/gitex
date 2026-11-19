import React, { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { ScreenProps } from '../types'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { LanguageSwitch } from '../components/LanguageSwitch'
import { api, ApiError, errorText, SeedPersona } from '../api/client'
import { useAsync } from '../lib/useAsync'
import { useLanguageChange } from '../lib/language'
import { demoKey, firstName, forgetDemoKey, saveOrgId, savePersonas } from '../lib/demo'

type Mode = 'home' | 'signin' | 'demo'
const SLOW_MS = 60_000 // after this, offer "Try again"

const light =
  'min-h-[52px] rounded-2xl bg-white hover:bg-[#F3F7F4] text-[#2C5140] text-[16px] font-bold border-0 cursor-pointer shadow-[0_10px_22px_-10px_rgba(20,40,28,0.6)] disabled:opacity-60 flex items-center justify-center gap-2'
const ghost =
  'min-h-[48px] rounded-2xl bg-white/10 hover:bg-white/20 text-white text-[15px] font-semibold border border-white/40 cursor-pointer disabled:opacity-60 flex items-center justify-center gap-2'
const input = 'mt-1.5 w-full min-h-[48px] box-border rounded-xl border-0 bg-white px-3 text-[15px] text-[#1B2A22]'

/** First screen: what Rebound is, the language, then start sign-up, sign in, or try a demo person.
 *  It pings GET /health straight away: free hosting sleeps when idle and can take up to a minute to wake. */
export const WelcomeScreen: React.FC<ScreenProps> = (props) => {
  const { state, setState, onNavigate, showToast } = props
  const { t } = useTranslation()
  const changeLanguage = useLanguageChange(props)
  const [mode, setMode] = useState<Mode>('home')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState<null | 'signin' | 'demo'>(null)
  const [awake, setAwake] = useState(false)
  const [waking, setWaking] = useState(true)
  const [slow, setSlow] = useState(false)
  const [personas, setPersonas] = useState<SeedPersona[] | null>(null)
  const content = useAsync(
    () => (state.language === 'ar' ? api.onboardingContent('ar') : Promise.resolve(null)),
    [state.language],
  )

  const wake = () => {
    setWaking(true)
    setSlow(false)
    api
      .health()
      .then(() => setAwake(true))
      .catch(() => setSlow(true)) // timed out or unreachable: offer "Try again"
      .finally(() => setWaking(false))
  }
  useEffect(wake, [])

  // Anything still waiting after a minute gets a "Try again".
  const waiting = waking || busy !== null
  useEffect(() => {
    if (!waiting) return
    const timer = setTimeout(() => setSlow(true), SLOW_MS)
    return () => clearTimeout(timer)
  }, [waiting])

  const open = (userId: string, token: string) => {
    // The app language follows the person's saved language once their data loads (App).
    setState((prev) => ({ ...prev, session: { userId, token }, justSignedUp: false }))
    onNavigate('today')
  }

  const signIn = async () => {
    setBusy('signin')
    try {
      const out = await api.login(username.trim(), password)
      open(out.user_id, out.token)
    } catch (e) {
      showToast(
        e instanceof ApiError && e.status === 401
          ? t('onboarding.welcome.wrongLogin')
          : e instanceof ApiError && e.status === 429
            ? t('onboarding.welcome.tooMany')
            : errorText(e),
      )
    } finally {
      setBusy(null)
    }
  }

  const tryDemo = async () => {
    const key = demoKey(t('onboarding.welcome.demoKeyPrompt'))
    if (!key) return
    setBusy('demo')
    try {
      const out = await api.demoSeed(key)
      savePersonas(out.personas)
      if (out.org_id) saveOrgId(out.org_id)
      setPersonas(out.personas)
      setMode('demo')
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) forgetDemoKey()
      showToast(
        e instanceof ApiError && e.status === 401
          ? t('onboarding.welcome.demoWrongKey')
          : e instanceof ApiError && e.status === 404
            ? t('onboarding.welcome.demoOff')
            : errorText(e),
      )
    } finally {
      setBusy(null)
    }
  }

  const spinner = <span className="spinner" aria-hidden="true" />

  return (
    <div className="relative overflow-hidden isolate w-full h-full overflow-y-auto overflow-x-hidden bg-[#54705C] font-sans text-white flex flex-col p-6">
      <TatreezPattern width={230} height={230} color="#2E4837" opacity={0.35} style={{ right: -90, bottom: 160 }} />
      <ArabicCalligraphyRing width={620} height={620} color="#2E4837" opacity={0.55} style={{ left: -330, top: 220 }} />
      <ArabicCalligraphyRing width={320} height={320} color="#2E4837" opacity={0.4} style={{ right: -150, top: -120 }} />

      <span className="mt-8 text-[13px] tracking-wide text-[#DDE9E0]">{t('onboarding.welcome.brand')}</span>
      <h1 className="mt-2 mb-3 font-display tracking-tight text-[34px] leading-[1.1] font-semibold">
        {t('onboarding.welcome.title1')}
        <br />
        {t('onboarding.welcome.title2')}
      </h1>
      <p className="m-0 text-[15px] leading-relaxed text-[#F3F7F4]">{t('onboarding.welcome.intro')}</p>

      <div className="mt-6 flex flex-col gap-2">
        <span className="text-[14px] font-semibold text-[#F3F7F4]">{t('onboarding.welcome.chooseLang')}</span>
        <LanguageSwitch value={state.language} onChange={changeLanguage} tone="dark" />
      </div>

      <div className="mt-auto pt-6 flex flex-col gap-2">
        {content.data?.translation_note && <p className="m-0 text-[12px] text-[#FFE9C7]">{content.data.translation_note}</p>}

        {(waiting || slow) && (
          <div role="status" aria-live="polite" className="flex items-center gap-2 text-[13px] text-[#F3F7F4]">
            {waiting && spinner}
            <span>{slow ? t('onboarding.welcome.slow') : t('common.waking')}</span>
            {slow && (
              <button type="button" onClick={wake} className="ms-auto min-h-[36px] px-3 rounded-full bg-white text-[#2C5140] text-[13px] font-semibold border-0 cursor-pointer">
                {t('common.tryAgain')}
              </button>
            )}
          </div>
        )}

        {mode === 'home' && (
          <>
            <p className="m-0 text-[12px] leading-relaxed text-[#DDE9E0]">{t('onboarding.welcome.takes3')}</p>
            <button type="button" className={light} onClick={() => onNavigate('onboarding-basics')}>
              {t('onboarding.welcome.start')}
            </button>
            <button type="button" className={ghost} onClick={() => setMode('signin')}>
              {t('onboarding.welcome.signIn')}
            </button>
            <button type="button" className={ghost} disabled={busy !== null || (!awake && waking)} onClick={tryDemo}>
              {busy === 'demo' && spinner}
              {busy === 'demo' ? t('onboarding.welcome.loadingDemo') : t('onboarding.welcome.tryDemo')}
            </button>
            <div className="mt-2 pt-2 flex flex-col items-center gap-1 border-t border-white/20">
              <button
                type="button"
                onClick={() => onNavigate('results')}
                className="min-h-[44px] px-3 py-1 bg-transparent border-0 text-[#DDE9E0] hover:text-white text-[13px] underline cursor-pointer flex items-center justify-center transition-colors"
              >
                {t('onboarding.welcome.howItWorks')}
              </button>
              <button
                type="button"
                onClick={() => onNavigate('program-dashboard')}
                className="min-h-[44px] px-3 py-1 bg-transparent border-0 text-[#DDE9E0] hover:text-white text-[13px] underline cursor-pointer flex items-center justify-center transition-colors"
              >
                {t('onboarding.welcome.forEmployers')}
              </button>
            </div>
          </>
        )}

        {mode === 'signin' && (
          <form
            className="flex flex-col gap-2"
            onSubmit={(e) => {
              e.preventDefault()
              void signIn()
            }}
          >
            <label className="text-[14px] font-semibold">
              {t('onboarding.welcome.username')}
              <input className={input} autoComplete="username" autoCapitalize="none" dir="ltr" value={username}
                onChange={(e) => setUsername(e.target.value)} />
            </label>
            <label className="text-[14px] font-semibold">
              {t('onboarding.welcome.password')}
              <input className={input} type="password" autoComplete="current-password" dir="ltr" value={password}
                onChange={(e) => setPassword(e.target.value)} />
            </label>
            <button type="submit" className={light} disabled={busy !== null || !username.trim() || !password}>
              {busy === 'signin' && spinner}
              {busy === 'signin' ? t('onboarding.welcome.signingIn') : t('onboarding.welcome.signIn')}
            </button>
            <button type="button" className="min-h-[44px] bg-transparent border-0 text-white text-[14px] cursor-pointer" onClick={() => setMode('home')}>
              {t('common.back')}
            </button>
          </form>
        )}

        {mode === 'demo' && personas && (
          <>
            <p className="m-0 text-[13px] text-[#F3F7F4]">{t('onboarding.welcome.pickPerson')}</p>
            {personas.map((p) => (
              <button
                key={p.user_id}
                type="button"
                onClick={() => open(p.user_id, p.token)}
                className="min-h-[60px] px-4 py-2 rounded-2xl bg-white text-start text-[#1B2A22] border-0 cursor-pointer flex flex-col gap-0.5"
              >
                <span className="text-[15px] font-semibold">{firstName(p)}</span>
                <span className="text-[12px] text-[#3F4F45]">{t(`onboarding.welcome.persona.${firstName(p)}`, { defaultValue: p.name })}</span>
              </button>
            ))}
            <button type="button" className="min-h-[44px] bg-transparent border-0 text-white text-[14px] cursor-pointer" onClick={() => setMode('home')}>
              {t('common.back')}
            </button>
          </>
        )}
      </div>
    </div>
  )
}
