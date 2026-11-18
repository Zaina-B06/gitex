import React, { useState } from 'react'
import { ScreenProps } from '../types'
import { api, CommunityEvent } from '../api/client'
import { TatreezPattern, ArabicCalligraphyRing } from '../components/BackgroundMotifs'
import { ScreenFrame } from '../components/ScreenFrame'
import { LoadingView, ErrorView } from '../components/StatusViews'
import { useAsync } from '../lib/useAsync'
import { tr } from '../i18n'

// The API filters by the English city name; the label is translated.
const CITIES = [
  { key: 'abu_dhabi', query: 'Abu Dhabi' },
  { key: 'al_ain', query: 'Al Ain' },
  { key: 'all', query: undefined },
] as const
type City = (typeof CITIES)[number]['key']

const CATEGORY_COLOR: Record<CommunityEvent['category'], string> = {
  walking_group: '#3E6B53',
  park_run: '#3E6B53',
  sports_night: '#3F4FA8',
  free_health_screening: '#A02A1C',
  family_activity: '#8A4B0F',
  women_only: '#6E4A8E',
  wheelchair_accessible: '#3F4FA8',
}

/** "Near you": GET /users/{id}/community/events, filtered to the user's goals. City is a request filter only. */
export const CommunityScreen: React.FC<ScreenProps> = ({ state, onNavigate }) => {
  const lang = state.language
  const [city, setCity] = useState<City>('abu_dhabi')
  const events = useAsync(
    () => api.communityEvents(state.session!, CITIES.find((c) => c.key === city)?.query),
    [state.session, city],
  )

  return (
    <ScreenFrame
      tab="community"
      onNavigate={onNavigate}
      background={
        <>
          <TatreezPattern width={210} height={210} style={{ right: -110, bottom: 90, opacity: 0.07 }} />
          <ArabicCalligraphyRing width={460} height={460} style={{ right: -240, top: -150, opacity: 0.12 }} />
        </>
      }
    >
      <header className="p-6 pb-0 flex flex-col gap-1">
        <h1 className="m-0 font-display tracking-tight text-[28px] font-semibold">{tr('app.community.title')}</h1>
        <p className="m-0 text-[14px] leading-relaxed text-[#3F4F45]">{tr('app.community.intro')}</p>
      </header>

      <div className="sticky top-0 z-10 bg-[#EEF1EA]/95 backdrop-blur px-6 py-3 flex gap-2" role="group" aria-label={tr('app.community.city')}>
        {CITIES.map(({ key: c }) => (
          <button
            key={c}
            type="button"
            aria-pressed={city === c}
            onClick={() => setCity(c)}
            className={`min-h-[36px] px-3 rounded-full text-[13px] cursor-pointer ${
              city === c ? 'bg-[#3E6B53] text-white font-semibold border-0' : 'bg-white border border-[#C5D0C7]'
            }`}
          >
            {tr(`app.community.city.${c}`)}
          </button>
        ))}
      </div>

      <div className="px-6 py-3 flex flex-col gap-2.5">
        {events.loading && <LoadingView />}
        {events.error && <ErrorView message={events.error} onRetry={events.reload} />}
        {events.data?.length === 0 && (
          <p className="m-0 p-4 rounded-[20px] bg-white/90 text-[14px] text-[#3F4F45]">
            {tr('app.community.nothing')}
          </p>
        )}
        {events.data?.map((ev) => {
          const cat = { label: tr(`app.community.cat.${ev.category}`), color: CATEGORY_COLOR[ev.category] ?? '#3E6B53' }
          return (
            <article key={ev.id} className="bg-white/90 rounded-[20px] p-3.5 shadow-card flex flex-col gap-1.5">
              {ev.example && (
                <span className="self-start px-2 py-0.5 rounded-full bg-[#E6EBE4] text-[11px] font-semibold text-[#5A6A60]">
                  {tr('app.community.example')}
                </span>
              )}
              <div className="flex justify-between items-center gap-2">
                <span className="text-[12px] font-semibold" style={{ color: cat.color }}>
                  {cat.label}
                </span>
                {ev.last_checked && <span className="text-[12px] text-[#5A6A60]">{tr('app.community.checked', { date: ev.last_checked })}</span>}
              </div>
              <h2 className="m-0 text-[16px] font-semibold leading-snug">{ev.title[lang]}</h2>
              <p className="m-0 text-[13px] leading-snug text-[#3F4F45]">
                {ev.area}, {ev.city} · {ev.schedule}
              </p>
              <p className="m-0 text-[13px] leading-snug text-[#3F4F45]">
                {ev.cost} · {ev.accessibility}
              </p>
              <div className="flex justify-between items-center gap-2">
                <span className="text-[12px] text-[#5A6A60]">{ev.organiser}</span>
                {ev.source_url && !ev.example && (
                  <a
                    href={ev.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[13px] font-semibold text-[#3E6B53]"
                  >
                    {tr('app.community.source')}
                  </a>
                )}
              </div>
            </article>
          )
        })}
        <p className="m-0 text-[12px] text-[#5A6A60]">{tr('app.community.confirm')}</p>
      </div>

    </ScreenFrame>
  )
}
