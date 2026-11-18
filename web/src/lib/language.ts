import { api, errorText } from '../api/client'
import type { ScreenProps } from '../types'

/** Switches the app labels at once and, for a signed-in user, the API's texts too (PATCH /settings {language}),
 *  then re-fetches every screen's data so nothing stays half-translated. */
export function useLanguageChange({ state, setState, showToast }: Pick<ScreenProps, 'state' | 'setState' | 'showToast'>) {
  return async (language: 'en' | 'ar') => {
    if (language === state.language) return
    setState((prev) => ({ ...prev, language }))
    if (!state.session) return
    try {
      await api.settings(state.session, { language })
    } catch (e) {
      showToast(errorText(e))
    }
    setState((prev) => ({ ...prev, dataVersion: prev.dataVersion + 1 }))
  }
}
