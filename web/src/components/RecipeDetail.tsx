import React from 'react'
import type { RecipeOut } from '../api/client'

export const tagLabel = (t: string) => t.replace(/_/g, ' ')

/** Full recipe: title, tags, ingredients, steps, swap and the "not medical advice" note. */
export const RecipeDetail: React.FC<{ recipe: RecipeOut; lang: 'en' | 'ar' }> = ({ recipe, lang }) => (
  <div className="flex flex-col" dir={lang === 'ar' ? 'rtl' : 'ltr'}>
    <h1 className="m-0 mb-0.5 font-display tracking-tight text-[26px] leading-tight font-semibold">{recipe.title[lang]}</h1>
    <span className="text-[13px] text-[#5A6A60]">
      {recipe.cuisine} · {recipe.minutes} min
    </span>

    <div className="mt-2.5 flex flex-wrap gap-1.5">
      {recipe.tags.map((t) => (
        <span key={t} className="px-2.5 py-1 rounded-full bg-[#F6E9DC] text-[#8A4B0F] text-[12px] font-medium">
          {tagLabel(t)}
        </span>
      ))}
    </div>

    <section className="mt-4 bg-white/90 rounded-[20px] p-4 shadow-card flex flex-col gap-2">
      <h2 className="m-0 text-[15px] font-semibold">You'll need</h2>
      <ul className="m-0 ps-5 text-[14px] leading-relaxed text-[#3F4F45] list-disc">
        {recipe.ingredients.map((i) => (
          <li key={i}>{i}</li>
        ))}
      </ul>
    </section>

    <section className="mt-3 bg-white/90 rounded-[20px] p-4 shadow-card flex flex-col gap-2">
      <h2 className="m-0 text-[15px] font-semibold">{recipe.steps.length} steps</h2>
      <ol className="m-0 ps-5 text-[14px] leading-relaxed text-[#3F4F45]">
        {recipe.steps.map((s) => (
          <li key={s}>{s}</li>
        ))}
      </ol>
    </section>

    <p className="mt-3 mb-0 text-[13px] leading-relaxed text-[#3F4F45]">
      <strong>Easy swap:</strong> {recipe.swap}
    </p>
    <p className="mt-1 mb-0 text-[12px] text-[#5A6A60]">{recipe.note}</p>
  </div>
)
