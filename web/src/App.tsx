import { CSSProperties, useEffect, useRef, useState } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { ScreenId, AppState } from './types'
import { APP_SCREENS, SCREEN_PATHS, screenForPath } from './routes'
import { AdvanceIn, api, errorText, loadSession, saveSession, SeedPersona, setUnauthorizedHandler } from './api/client'
import { emptyDraft } from './lib/onboarding'
import { ScreenSwitcher } from './components/ScreenSwitcher'
import { WelcomeScreen } from './screens/WelcomeScreen'
import { BasicsScreen } from './screens/BasicsScreen'
import { BaselineScreen } from './screens/BaselineScreen'
import { PreferencesScreen } from './screens/PreferencesScreen'
import { TodayScreen } from './screens/TodayScreen'
import { MyPlanScreen } from './screens/MyPlanScreen'
import { MealsScreen } from './screens/MealsScreen'
import { ReportScreen } from './screens/ReportScreen'
import { CareScreen } from './screens/CareScreen'
import { PlanCardScreen } from './screens/PlanCardScreen'
import { SaveProgressScreen } from './screens/SaveProgressScreen'
import { ProgramDashboardScreen } from './screens/ProgramDashboardScreen'
import { SettingsScreen } from './screens/SettingsScreen'
import { EasierPlanScreen } from './screens/EasierPlanScreen'
import { RecipeScreen } from './screens/RecipeScreen'
import { ChatNudgeScreen } from './screens/ChatNudgeScreen'
import { OnboardingHealthScreen } from './screens/OnboardingHealthScreen'
import { CheckinScreen } from './screens/CheckinScreen'
import { GoalsScreen } from './screens/GoalsScreen'
import { CommunityScreen } from './screens/CommunityScreen'
import { ResultsScreen } from './screens/ResultsScreen'

import { DEMO_MODE } from './lib/demo'
import i18n, { tr } from './i18n'

const freshState = (): AppState => ({
  session: null,
  displayName: '',
  careMessage: null,
  language: 'en',
  profile: emptyDraft(),
  plan: null,
  justSignedUp: false,
  lastCheckin: null,
  careReason: null,
  recipeTarget: null,
  bannerDismissed: false,
  dataVersion: 0,
})

export function App() {
  const [state, setState] = useState<AppState>(() => ({ ...freshState(), session: loadSession() }))
  const [toast, setToast] = useState<{ message: string; id: number } | null>(null)
  const navigate = useNavigate()
  const location = useLocation()
  const currentScreen = screenForPath(location.pathname)
  const signedIn = state.session !== null

  // Only the user id + token are kept in the browser. The name comes from the account (preferences.display_name).
  useEffect(() => {
    saveSession(state.session)
    if (!state.session) return
    let live = true
    api
      .exportData(state.session)
      // The app follows the person's saved language (Ahmed opens in Arabic) and their name for the greeting.
      .then(
        (e) =>
          live &&
          setState((prev) => ({
            ...prev,
            displayName: e.profile.preferences?.display_name ?? '',
            language: e.profile.basics.language === 'ar' ? 'ar' : 'en',
          })),
      )
      .catch(() => {}) // a 401 is handled below; the greeting just goes without a name
    return () => {
      live = false
    }
  }, [state.session])

  // Demo bar height, so the phone frame fits below it (one or two rows).
  const barRef = useRef<HTMLDivElement>(null)
  const [barHeight, setBarHeight] = useState(0)
  useEffect(() => {
    const el = barRef.current
    if (!el) return
    const observer = new ResizeObserver(() => setBarHeight(el.offsetHeight))
    observer.observe(el)
    return () => observer.disconnect()
  }, [])

  const showToast = (message: string) => {
    const id = Date.now()
    setToast({ message, id })
    setTimeout(() => {
      setToast((prev) => (prev?.id === id ? null : prev))
    }, 3200)
  }

  const navigateTo = (screen: ScreenId) => {
    navigate(SCREEN_PATHS[screen])
  }

  const startOver = () => {
    setState(freshState())
    navigate(SCREEN_PATHS.welcome)
  }

  // A 401 means the account is gone or the token is wrong: start again at Welcome.
  useEffect(() => {
    setUnauthorizedHandler(() => {
      startOver()
      showToast(tr('common.sessionEnded'))
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const finishOnboarding = () => {
    setState((prev) => ({ ...prev, justSignedUp: false, profile: emptyDraft() }))
    showToast(tr('common.planReady'))
    navigateTo('today')
  }

  // Labels switch in the same render as the language (resources are in memory, so this is immediate).
  if (i18n.language !== state.language) void i18n.changeLanguage(state.language)

  const props = { state, setState, onNavigate: navigateTo, showToast }

  // Demo bar: switch to another seeded person, or move time on for the current one.
  const switchPerson = (p: SeedPersona) => {
    setState((prev) => ({ ...freshState(), language: prev.language, session: { userId: p.user_id, token: p.token } }))
    navigateTo('today')
  }
  const advance = async (body: AdvanceIn, label: string) => {
    if (!state.session) return
    try {
      await api.demoAdvance(state.session, body)
      setState((prev) => ({ ...prev, dataVersion: prev.dataVersion + 1, bannerDismissed: false }))
      showToast(tr('common.advanced', { label }))
    } catch (e) {
      showToast(errorText(e))
    }
  }

  const renderScreen = (screen: ScreenId) => {
    switch (screen) {
      case 'welcome':
        return <WelcomeScreen {...props} />
      case 'onboarding-basics':
        return <BasicsScreen {...props} />
      case 'onboarding-goals':
        return <GoalsScreen {...props} />
      case 'onboarding-health':
        return <OnboardingHealthScreen {...props} />
      case 'onboarding-baseline':
        return <BaselineScreen {...props} />
      case 'onboarding-preferences':
        return <PreferencesScreen {...props} />
      case 'plan-ready':
        return <PlanCardScreen {...props} onStart={() => navigateTo('save-progress')} />
      case 'save-progress':
        return <SaveProgressScreen {...props} onDone={finishOnboarding} />
      case 'today':
        return <TodayScreen {...props} />
      case 'plan':
        return <MyPlanScreen {...props} />
      case 'meals':
        return <MealsScreen {...props} />
      case 'community':
        return <CommunityScreen {...props} />
      case 'settings':
        return <SettingsScreen {...props} onSignedOut={startOver} />
      case 'report':
        return <ReportScreen {...props} />
      case 'care':
        return <CareScreen {...props} />
      case 'checkin':
        return <CheckinScreen {...props} />
      case 'easier-plan':
        return <EasierPlanScreen {...props} />
      case 'recipe':
        return <RecipeScreen {...props} />
      case 'program-dashboard':
        return <ProgramDashboardScreen {...props} />
      case 'results':
        return <ResultsScreen {...props} />
      case 'chat-nudge':
        return <ChatNudgeScreen {...props} />
    }
  }

  const routeElement = (screen: ScreenId) => {
    if (APP_SCREENS.includes(screen) && !signedIn) return <Navigate to={SCREEN_PATHS.welcome} replace />
    // A signed-in user doesn't go through sign-up again (delete the account in Settings to restart).
    if (signedIn && !state.justSignedUp && (screen === 'welcome' || screen.startsWith('onboarding-')))
      return <Navigate to={SCREEN_PATHS.today} replace />
    return renderScreen(screen)
  }

  const isWidePage = currentScreen === 'program-dashboard' || currentScreen === 'results'

  return (
    <div className="print-full min-h-screen bg-[#d9dfd6] flex flex-col items-center">
      {DEMO_MODE && (
        <div ref={barRef} className="no-print w-full sticky top-0 z-50">
          <ScreenSwitcher
            currentScreen={currentScreen}
            onSelectScreen={navigateTo}
            signedIn={signedIn}
            onStartOver={startOver}
            userId={state.session?.userId ?? null}
            onSwitchPerson={switchPerson}
            onAdvance={advance}
          />
        </div>
      )}

      <main className={`print-full w-full flex justify-center ${isWidePage ? 'max-w-7xl py-0 sm:py-6 px-0 sm:px-4' : ''}`}>
        <div
          className={
            isWidePage
              ? 'print-full w-full shadow-2xl overflow-hidden rounded-none sm:rounded-3xl max-w-[1160px]'
              : // Phone frame (index.css): 390 x min(844, screen - 32), full screen under 500px wide.
                'print-full phone-frame'
          }
          style={{ '--demo-bar': `${barHeight}px` } as CSSProperties}
          dir={state.language === 'ar' ? 'rtl' : 'ltr'}
          lang={state.language}
        >
          <Routes>
            <Route path="/" element={<Navigate to={signedIn ? SCREEN_PATHS.today : SCREEN_PATHS.welcome} replace />} />
            {(Object.keys(SCREEN_PATHS) as ScreenId[]).map((screen) => (
              <Route key={screen} path={SCREEN_PATHS[screen]} element={routeElement(screen)} />
            ))}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </main>

      {toast && (
        <div
          role="status"
          aria-live="polite"
          className="no-print fixed bottom-24 left-1/2 -translate-x-1/2 z-50 bg-[#1B2A22] text-[#F3F7F4] px-4 py-2.5 rounded-full shadow-2xl flex items-center gap-3 text-xs sm:text-sm font-medium border border-[#3E6B53]"
          style={{ maxWidth: '90vw' }}
        >
          <span className="w-2 h-2 rounded-full bg-[#6DA483] animate-pulse flex-shrink-0" />
          <span className="truncate">{toast.message}</span>
          <button
            onClick={() => setToast(null)}
            className="text-[#A2C7B0] hover:text-white font-bold ms-1 text-base leading-none bg-transparent border-0 cursor-pointer"
            aria-label={tr('common.dismiss')}
          >
            ×
          </button>
        </div>
      )}
    </div>
  )
}

export default App
