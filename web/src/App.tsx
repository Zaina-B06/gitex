import { useEffect, useState } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { ScreenId, AppState } from './types'
import { APP_SCREENS, SCREEN_PATHS, screenForPath } from './routes'
import { loadSession, saveSession, setUnauthorizedHandler } from './api/client'
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
import { ProgramDashboardScreen } from './screens/ProgramDashboardScreen'
import { SettingsScreen } from './screens/SettingsScreen'
import { EasierPlanScreen } from './screens/EasierPlanScreen'
import { RecipeScreen } from './screens/RecipeScreen'
import { ChatNudgeScreen } from './screens/ChatNudgeScreen'
import { OnboardingHealthScreen } from './screens/OnboardingHealthScreen'
import { CheckinScreen } from './screens/CheckinScreen'
import { GoalsScreen } from './screens/GoalsScreen'
import { CommunityScreen } from './screens/CommunityScreen'

const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

// The first name lives only in this browser (never sent to the server).
const NAME_KEY = 'rebound.name'
const loadName = () => {
  try {
    return localStorage.getItem(NAME_KEY) ?? ''
  } catch {
    return ''
  }
}
const saveName = (name: string) => {
  try {
    if (name.trim()) localStorage.setItem(NAME_KEY, name.trim())
    else localStorage.removeItem(NAME_KEY)
  } catch {
    // storage blocked: the name lasts until the tab closes
  }
}

const freshState = (): AppState => ({
  session: null,
  displayName: '',
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
  const [state, setState] = useState<AppState>(() => ({ ...freshState(), session: loadSession(), displayName: loadName() }))
  const [toast, setToast] = useState<{ message: string; id: number } | null>(null)
  const navigate = useNavigate()
  const location = useLocation()
  const currentScreen = screenForPath(location.pathname)
  const signedIn = state.session !== null

  // Only the user id + token (and the optional first name) are kept in the browser.
  useEffect(() => {
    saveSession(state.session)
  }, [state.session])
  useEffect(() => {
    saveName(state.displayName)
  }, [state.displayName])

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
      showToast('Please sign up again. Your previous session has ended.')
    })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const finishOnboarding = () => {
    setState((prev) => ({ ...prev, justSignedUp: false, profile: emptyDraft() }))
    navigateTo('today')
  }

  const props = { state, setState, onNavigate: navigateTo, showToast }

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
        return <PlanCardScreen {...props} onStart={finishOnboarding} />
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

  const isWideDashboard = currentScreen === 'program-dashboard'

  return (
    <div className="print-full min-h-screen bg-[#d9dfd6] flex flex-col items-center">
      {DEMO_MODE && (
        <div className="no-print w-full sticky top-0 z-50">
          <ScreenSwitcher
            currentScreen={currentScreen}
            onSelectScreen={navigateTo}
            signedIn={signedIn}
            onStartOver={startOver}
          />
        </div>
      )}

      <main className={`print-full w-full flex justify-center py-0 sm:py-6 px-0 sm:px-4 ${isWideDashboard ? 'max-w-6xl' : 'max-w-md'}`}>
        <div
          className={`print-full w-full shadow-2xl overflow-hidden ${
            isWideDashboard
              ? 'rounded-none sm:rounded-3xl max-w-[960px]'
              : // Phone-sized frame: screens scroll inside it instead of growing the page.
                `rounded-none sm:rounded-[36px] max-w-[390px] ${DEMO_MODE ? 'h-[calc(100dvh-41px)]' : 'h-[100dvh]'} sm:h-[min(844px,calc(100dvh-90px))]`
          }`}
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
            className="text-[#A2C7B0] hover:text-white font-bold ml-1 text-base leading-none bg-transparent border-0 cursor-pointer"
            aria-label="Dismiss notification"
          >
            ×
          </button>
        </div>
      )}
    </div>
  )
}

export default App
