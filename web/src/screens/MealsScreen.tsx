import React, { useMemo, useState } from 'react'
import { ScreenProps } from '../types'
import { api, RecipeOut } from '../api/client'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { ScreenFrame } from '../components/ScreenFrame'
import { RecipeDetail, tagLabel } from '../components/RecipeDetail'
import { LoadingView, ErrorView } from '../components/StatusViews'
import { useAsync } from '../lib/useAsync'

/** Meals tab: browse every recipe (GET /recipes), filter by tag, open one. Browsing logs nothing. */
export const MealsScreen: React.FC<ScreenProps> = ({ state, onNavigate }) => {
  const lang = state.language
  const list = useAsync<RecipeOut[]>(() => api.recipes(), [])
  const [tag, setTag] = useState<string | null>(null)
  const [open, setOpen] = useState<RecipeOut | null>(null)

  const tags = useMemo(() => [...new Set((list.data ?? []).flatMap((r) => r.tags))].sort(), [list.data])
  const shown = (list.data ?? []).filter((r) => !tag || r.tags.includes(tag))

  // Title and filter chips stay pinned (chips scroll sideways); the list is the only vertical scroll.
  const top = open ? null : (
    <>
      <header className="p-6 pb-0 flex flex-col gap-1">
        <h1 className="m-0 font-display tracking-tight text-[28px] font-semibold">Meals</h1>
        <p className="m-0 text-[14px] leading-relaxed text-[#3F4F45]">
          Simple home cooking from the region. General guidance, not medical advice.
        </p>
      </header>
      {tags.length > 0 && (
        <div className="px-6 py-3 flex gap-2 overflow-x-auto overflow-y-hidden" role="group" aria-label="Filter meals">
          {[null, ...tags].map((t) => (
            <button
              key={t ?? 'all'}
              type="button"
              aria-pressed={tag === t}
              onClick={() => setTag(t)}
              className={`flex-none min-h-[36px] px-3 rounded-full text-[13px] capitalize cursor-pointer whitespace-nowrap ${
                tag === t ? 'bg-[#8A4B0F] text-white font-semibold border-0' : 'bg-white border border-[#C5D0C7]'
              }`}
            >
              {t ? tagLabel(t) : 'All'}
            </button>
          ))}
        </div>
      )}
    </>
  )

  return (
    <ScreenFrame
      tab="meals"
      onNavigate={onNavigate}
      top={top}
      background={
        <>
          <TatreezPattern width={210} height={210} style={{ right: -110, bottom: 90, opacity: 0.07 }} />
          <ArabicCalligraphyRing width={440} height={440} style={{ left: -250, top: -140, opacity: 0.1 }} />
        </>
      }
    >
      {open ? (
        <div className="p-6">
          <button
            type="button"
            onClick={() => setOpen(null)}
            className="min-h-[44px] mb-1 flex items-center gap-1 bg-transparent border-0 p-0 cursor-pointer text-[14px] font-medium text-[#3E6B53]"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d="M15 18l-6-6 6-6" />
            </svg>
            All meals
          </button>
          <RecipeDetail recipe={open} lang={lang} />
        </div>
      ) : (
        <>
          <div className="px-6 pt-1 pb-6 flex flex-col gap-2.5">
            {list.loading && <LoadingView label="Loading meals…" />}
            {list.error && <ErrorView message={list.error} onRetry={list.reload} />}
            {shown.map((r) => (
              <button
                key={r.id}
                type="button"
                onClick={() => setOpen(r)}
                className="text-start bg-white/90 rounded-[20px] p-3.5 shadow-card flex items-center gap-3 border-0 cursor-pointer hover:shadow-card-hover"
              >
                <span className="w-11 h-11 rounded-full bg-[#F6E9DC] text-[#8A4B0F] flex items-center justify-center flex-none">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                    <path d="M4 11h16v3a6 6 0 0 1-6 6h-4a6 6 0 0 1-6-6zM2 11h20" />
                  </svg>
                </span>
                <span className="flex-1 flex flex-col gap-0.5">
                  <span className="text-[15px] font-semibold text-[#1B2A22]">{r.title[lang]}</span>
                  <span className="text-[12px] text-[#5A6A60] capitalize">
                    {r.minutes} min · {r.tags.map(tagLabel).join(' · ')}
                  </span>
                </span>
              </button>
            ))}
          </div>
        </>
      )}
    </ScreenFrame>
  )
}
