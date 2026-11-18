import React, { useState } from 'react'
import { ScreenProps } from '../types'
import { api, ApiError, errorText, RecipeOut } from '../api/client'
import { ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { ScreenFrame } from '../components/ScreenFrame'
import { RecipeDetail } from '../components/RecipeDetail'
import { LoadingView, ErrorView } from '../components/StatusViews'
import { useAsync } from '../lib/useAsync'
import { tr } from '../i18n'

/** Recipe opened from today's meal step. "I cooked it" marks that step done (POST /events). */
export const RecipeScreen: React.FC<ScreenProps> = ({ state, onNavigate, showToast }) => {
  const target = state.recipeTarget
  const list = useAsync<RecipeOut[]>(async () => {
    const all = await api.recipes()
    // The recipe suggested for today's step goes first.
    const i = target ? all.findIndex((r) => r.id === target.recipeId) : -1
    return i > 0 ? [all[i], ...all.slice(0, i), ...all.slice(i + 1)] : all
  }, [target?.recipeId])
  const [index, setIndex] = useState(0)
  const [saving, setSaving] = useState(false)

  const recipes = list.data ?? []
  const recipe = recipes.length ? recipes[index % recipes.length] : null

  const cooked = async () => {
    if (!target || !state.session) return onNavigate('today')
    setSaving(true)
    try {
      await api.recordEvent(state.session, target.actionId, 'completed')
      showToast(tr('app.recipe.doneToast'))
    } catch (e) {
      showToast(e instanceof ApiError && e.status === 409 ? tr('app.recipe.already') : errorText(e))
    } finally {
      setSaving(false)
    }
    onNavigate('today')
  }

  return (
    <ScreenFrame
      background={<ArabicCalligraphyRing width={440} height={440} style={{ left: -250, top: -120, opacity: 0.12 }} />}
      footer={
        recipe && (
          <div className="flex flex-col gap-1">
            <button
              type="button"
              disabled={saving}
              onClick={cooked}
              className="w-full min-h-[52px] rounded-[14px] bg-[#8A4B0F] hover:bg-[#6B3A0B] disabled:opacity-60 text-white text-[16px] font-semibold border-0 cursor-pointer shadow-button"
            >
              {tr('app.recipe.cooked')}
            </button>
            {recipes.length > 1 && (
              <button
                type="button"
                onClick={() => setIndex((i) => i + 1)}
                className="min-h-[40px] bg-transparent border-0 text-[14px] font-medium text-[#8A4B0F] cursor-pointer"
              >
                {tr('app.recipe.another', { i: (index % recipes.length) + 1, n: recipes.length })}
              </button>
            )}
          </div>
        )
      }
    >
      <div className="p-6 pb-2">
        <button
          type="button"
          onClick={() => onNavigate('today')}
          aria-label={tr('common.back')}
          className="min-w-[44px] min-h-[44px] flex items-center bg-transparent border-0 p-0 cursor-pointer text-[#1B2A22]"
        >
          <svg className="rtl-flip" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
        {list.loading && <LoadingView label={tr('app.recipe.loading')} />}
        {list.error && <ErrorView message={list.error} onRetry={list.reload} />}
        {recipe && (
          <>
            <span className="block mt-1.5 mb-1.5 text-[12px] font-semibold text-[#8A4B0F]">{tr('app.recipe.forToday')}</span>
            <RecipeDetail recipe={recipe} lang={state.language} />
          </>
        )}
      </div>
    </ScreenFrame>
  )
}
