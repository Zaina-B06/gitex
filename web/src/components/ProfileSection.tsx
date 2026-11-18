import React from 'react'
import type { ExportOut } from '../api/client'
import { BEHAVIOUR_STYLE } from '../lib/behaviour'
import { tr } from '../i18n'

const Row: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <div className="px-4 py-2.5 flex justify-between gap-3 border-b border-[#E6EBE4] last:border-b-0">
    <span className="text-[14px] text-[#5A6A60] flex-none">{label}</span>
    <span className="text-[14px] text-end text-[#1B2A22]">{children}</span>
  </div>
)

const hm = (t: unknown) => String(t).slice(0, 5)

/**
 * "What you told us" in Settings: what sign-up recorded (from GET /export), read-only.
 * Height and weight are never displayed (CLAUDE.md §4.2): we only say whether they were given.
 */
export const ProfileSection: React.FC<{ exp: ExportOut }> = ({ exp }) => {
  const p = exp.profile
  const b = p.basics
  const s = p.screening
  const prefs = p.preferences
  const anyYes = [
    s.heart_condition_or_high_bp,
    s.chest_pain,
    s.dizziness_or_fainting,
    s.other_long_term_condition,
    s.prescribed_medication,
    s.bone_joint_muscle_problem,
    s.supervised_exercise_only,
  ].some(Boolean)
  const body = p.body && (p.body.height_cm || p.body.weight_kg)
  const S = (key: string) => tr(`settings.${key}`)

  return (
    <div className="flex flex-col">
      <Row label={S('p.age')}>{b.age_years}</Row>
      <Row label={S('p.sex')}>{tr(`onboarding.sex.${b.sex}`)}</Row>
      <Row label={S('p.days')}>{tr(`onboarding.schedule.${b.schedule_type}`)}</Row>
      {b.shifts?.map((sh, i) => (
        <Row key={i} label={S('p.shifts')}>
          {sh.days.map((d) => tr(`onboarding.day.${d}`)).join(' ')} · {hm(sh.start)}–{hm(sh.end)}
        </Row>
      ))}
      <Row label={S('p.wakeSleep')}>
        {hm(b.usual_wake_time)} / {hm(b.usual_sleep_time)}
      </Row>
      <Row label={S('p.goals')}>{b.goals.map((g) => BEHAVIOUR_STYLE[g]?.label ?? g).join(' · ')}</Row>
      {b.goals.includes('movement') && <Row label={S('p.activeDays')}>{p.baseline.active_days_per_week}</Row>}
      {b.goals.includes('sleep') && (
        <Row label={S('p.usualSleep')}>
          {tr('settings.p.hours', {
            h: p.baseline.sleep_hours_typical,
            q: tr(`onboarding.quality.${p.baseline.sleep_quality_self}`),
          })}
        </Row>
      )}
      <Row label={S('p.body')}>{body ? S('p.bodyGiven') : S('p.bodyNot')}</Row>
      <Row label={S('p.moving')}>{S(`p.mob.${s.mobility_limitation}`)}</Row>
      {b.sex === 'female' && s.pregnant && (
        <Row label={S('p.pregnant')}>{s.pregnant === 'yes' ? S('p.pregYes') : tr(`onboarding.pregnancy.${s.pregnant}`)}</Row>
      )}
      <Row label={S('p.healthCheck')}>{anyYes ? S('p.someYes') : S('p.allNo')}</Row>
      {prefs?.household && <Row label={S('p.lives')}>{tr(`onboarding.household.${prefs.household}`)}</Row>}
      {prefs?.setting && <Row label={S('p.prefers')}>{S(`p.place.${prefs.setting}`)}</Row>}
      <Row label={S('p.fasts')}>{prefs?.fasting_ramadan ? tr('common.yes') : tr('common.no')}</Row>
      {anyYes && (
        <p className="m-0 px-4 py-2.5 text-[12px] leading-snug text-[#A02A1C] bg-[#FDE8E4]">{S('p.doctor')}</p>
      )}
      <p className="m-0 px-4 py-2.5 text-[12px] leading-snug text-[#5A6A60]">{S('p.footer')}</p>
    </div>
  )
}
