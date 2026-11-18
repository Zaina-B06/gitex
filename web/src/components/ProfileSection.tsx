import React from 'react'
import type { ExportOut } from '../api/client'
import { BEHAVIOUR_STYLE } from '../lib/behaviour'

const SEX: Record<string, string> = { female: 'Female', male: 'Male', prefer_not_to_say: 'Prefer not to say' }
const SCHEDULE: Record<string, string> = {
  office: 'Office hours',
  shift: 'Shifts',
  outdoor_manual: 'Outdoor / manual work',
  home_caregiver: 'At home / caring for family',
  student: 'Student',
  other: 'Something else',
}
const HOUSEHOLD: Record<string, string> = {
  alone: 'Alone',
  family: 'With family',
  children: 'With children',
  older_relatives: 'With older relatives',
}
const MOBILITY: Record<string, string> = { none: 'No limits', some: 'Some limits', mobility_aid: 'Uses a mobility aid or wheelchair' }
const SETTING: Record<string, string> = { indoor: 'Indoors', outdoor: 'Outdoors', either: 'Indoors or outdoors' }
const QUALITY = ['', 'Very poor', 'Poor', 'OK', 'Good', 'Very good']
const DAY: Record<string, string> = { mon: 'Mon', tue: 'Tue', wed: 'Wed', thu: 'Thu', fri: 'Fri', sat: 'Sat', sun: 'Sun' }

const Row: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <div className="px-4 py-2.5 flex justify-between gap-3 border-b border-[#E6EBE4] last:border-b-0">
    <span className="text-[14px] text-[#5A6A60] flex-none">{label}</span>
    <span className="text-[14px] text-end text-[#1B2A22]">{children}</span>
  </div>
)

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

  return (
    <div className="flex flex-col">
      <Row label="Age">{b.age_years}</Row>
      <Row label="Sex">{SEX[b.sex] ?? b.sex}</Row>
      <Row label="Your days">{SCHEDULE[b.schedule_type] ?? b.schedule_type}</Row>
      {b.shifts?.map((sh, i) => (
        <Row key={i} label="Shifts">
          {sh.days.map((d) => DAY[d] ?? d).join(', ')} · {String(sh.start).slice(0, 5)}–{String(sh.end).slice(0, 5)}
        </Row>
      ))}
      <Row label="Wake / sleep">
        {String(b.usual_wake_time).slice(0, 5)} / {String(b.usual_sleep_time).slice(0, 5)}
      </Row>
      <Row label="Goals">{b.goals.map((g) => BEHAVIOUR_STYLE[g]?.label ?? g).join(', ')}</Row>
      {b.goals.includes('movement') && <Row label="Active days a week">{p.baseline.active_days_per_week}</Row>}
      {b.goals.includes('sleep') && (
        <Row label="Usual sleep">
          {p.baseline.sleep_hours_typical} h · {QUALITY[p.baseline.sleep_quality_self] ?? ''}
        </Row>
      )}
      <Row label="Height and weight">{body ? 'Given, used only for a safe start' : 'Not given'}</Row>
      <Row label="Moving around">{MOBILITY[s.mobility_limitation] ?? s.mobility_limitation}</Row>
      {b.sex === 'female' && s.pregnant && (
        <Row label="Pregnant">{s.pregnant === 'yes' ? 'Yes (pregnancy-safe steps only)' : s.pregnant === 'no' ? 'No' : 'Prefer not to say'}</Row>
      )}
      <Row label="Health check">{anyYes ? 'Some answers were yes' : 'All answers were no'}</Row>
      {prefs?.household && <Row label="Lives">{HOUSEHOLD[prefs.household]}</Row>}
      {prefs && <Row label="Prefers">{SETTING[prefs.setting] ?? prefs.setting}</Row>}
      <Row label="Fasts in Ramadan">{prefs?.fasting_ramadan ? 'Yes' : 'No'}</Row>
      {anyYes && (
        <p className="m-0 px-4 py-2.5 text-[12px] leading-snug text-[#A02A1C] bg-[#FDE8E4]">
          Please check with your doctor before increasing intensity. Movement steps stay gentle for now.
        </p>
      )}
      <p className="m-0 px-4 py-2.5 text-[12px] leading-snug text-[#5A6A60]">
        These answers set your safe starting plan. Age, sex and the health check can't be changed here: to change
        them, delete your account and sign up again.
      </p>
    </div>
  )
}
