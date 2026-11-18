import React, { useEffect, useRef, useState } from 'react'
import { ScreenProps } from '../types'
import { api, ApiError, Barrier, errorText, ScheduledAction, StateOut, TodayOut } from '../api/client'
import { BEHAVIOUR_STYLE, pct } from '../lib/behaviour'

type Reply = { label: string; run: () => void }
interface Msg {
  id: number
  from: 'bot' | 'me'
  text: string
  care?: boolean
}

const QUICK_BARRIERS: { value: Barrier; label: string }[] = [
  { value: 'time', label: 'No time' },
  { value: 'energy_fatigue', label: 'Tired' },
  { value: 'illness_pain', label: 'Sick or in pain' },
  { value: 'stress', label: 'Stressed' },
  { value: 'schedule_change', label: 'Schedule changed' },
  { value: 'forgot', label: 'Forgot' },
  { value: 'low_motivation', label: 'Not feeling it' },
]

let nextId = 1

/**
 * Chat check-in (WhatsApp-style channel, CLAUDE.md §4.6). Uses the same API as the app:
 * steps → POST /events, "something got in the way" → POST /checkin. Coaching text comes from the backend's
 * fixed templates; this screen only adds short connecting lines. A red flag switches to the care message.
 */
export const ChatNudgeScreen: React.FC<ScreenProps> = ({ state, setState, onNavigate }) => {
  const session = state.session!
  const lang = state.language
  const [msgs, setMsgs] = useState<Msg[]>([])
  const [replies, setReplies] = useState<Reply[]>([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [mode, setMode] = useState<'steps' | 'checkin'>('steps')
  const bottom = useRef<HTMLDivElement>(null)
  const started = useRef(false)

  const say = (from: Msg['from'], text: string, care = false) =>
    setMsgs((m) => [...m, { id: nextId++, from, text, care }])

  // Braces matter: newer browsers return a Promise from scrollIntoView, and React would treat it as a cleanup.
  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: 'smooth' })
  }, [msgs, replies])

  const load = async () => (await Promise.all([api.today(session), api.state(session)])) as [TodayOut, StateOut]

  /** Ask about the next unanswered step, or offer the end-of-day options. */
  const nextStep = async () => {
    setBusy(true)
    try {
      const [today, st] = await load()
      const answered = new Set(st.history.filter((d) => d.day === today.day && d.action_id).map((d) => d.action_id))
      const open = today.actions.find((s) => !answered.has(s.action.id))
      if (open) askStep(open)
      else endOptions(st)
    } catch (e) {
      say('bot', errorText(e))
    } finally {
      setBusy(false)
    }
  }

  const askStep = (s: ScheduledAction) => {
    const st = BEHAVIOUR_STYLE[s.action.behaviour]
    say('bot', `${st.label}: ${s.action.title[lang]} (about ${s.action.duration_min} min). How did it go?`)
    const answer = (type: 'completed' | 'partial' | 'skipped', label: string) => async () => {
      setReplies([])
      say('me', label)
      setBusy(true)
      try {
        const res = await api.recordEvent(session, s.action.id, type)
        say(
          'bot',
          res.encouragement?.message ??
            (type === 'completed' ? 'Nice one. Saved.' : type === 'partial' ? 'A smaller version counts. Saved.' : 'No problem. Your progress is safe.'),
        )
      } catch (e) {
        say('bot', e instanceof ApiError && e.status === 409 ? 'That one was already answered today.' : errorText(e))
      } finally {
        setBusy(false)
      }
      nextStep()
    }
    setReplies([
      { label: 'Done', run: answer('completed', 'Done') },
      { label: 'Did less', run: answer('partial', 'Did a smaller version') },
      { label: 'Skip', run: answer('skipped', 'Skip today') },
    ])
  }

  const endOptions = (st?: StateOut) => {
    say('bot', st ? "That's everything for today." : 'Anything else?')
    setReplies([
      { label: 'Something got in the way', run: startCheckin },
      {
        label: 'How am I doing?',
        run: async () => {
          setReplies([])
          say('me', 'How am I doing?')
          try {
            const [, s] = await load()
            const parts = Object.entries(s.habit_strength)
              .filter(([b]) => b in BEHAVIOUR_STYLE)
              .map(([b, h]) => `${BEHAVIOUR_STYLE[b as keyof typeof BEHAVIOUR_STYLE].label} ${pct(h)}`)
            say('bot', `Habit strength (0–100): ${parts.join(' · ')}. It fades slowly on missed days and never resets to zero.`)
          } catch (e) {
            say('bot', errorText(e))
          }
          endOptions()
        },
      },
    ])
  }

  const startCheckin = () => {
    setReplies([])
    say('me', 'Something got in the way')
    say('bot', 'Thanks for telling me. What got in the way? Tap one, or type it in your own words.')
    setMode('checkin')
    setReplies(QUICK_BARRIERS.map((b) => ({ label: b.label, run: () => sendCheckin([b.value], b.label) })))
  }

  const sendCheckin = async (barriers: Barrier[], shown: string, text?: string) => {
    setReplies([])
    say('me', shown)
    if (text && mode !== 'checkin') say('bot', "Thanks for telling me. Let me adjust today's plan.")
    setMode('steps')
    setBusy(true)
    let continueSteps = false
    try {
      const out = await api.checkin(session, barriers, text)
      if (out.red_flag) {
        say('bot', out.message, true)
        setState((prev) => ({ ...prev, careReason: 'red_flag', lastCheckin: out }))
        setReplies([{ label: 'Get help now', run: () => onNavigate('care') }])
      } else {
        say('bot', out.message)
        if (out.adjusted_actions.length)
          say('bot', `Today's lighter steps: ${out.adjusted_actions.map((a) => a.title[lang]).join(' · ')}`)
        continueSteps = true
      }
    } catch (e) {
      say(
        'bot',
        e instanceof ApiError && e.status === 409 ? "You've already checked in today. I'll ask again tomorrow." : errorText(e),
      )
      endOptions()
    } finally {
      setBusy(false)
    }
    if (continueSteps) nextStep()
  }

  const sendText = () => {
    const text = input.trim()
    if (!text || busy) return
    setInput('')
    // Typed text always goes to the check-in: buttons decide the barrier, free text fills in (and is red-flag checked).
    sendCheckin([], text, text)
  }

  useEffect(() => {
    if (started.current) return
    started.current = true
    say('bot', `Hi${state.displayName ? ` ${state.displayName}` : ''}! Let's go through today's steps.`)
    nextStep()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="h-full w-full flex flex-col bg-[#E8ECE2] font-sans text-[#1B2A22]" dir={lang === 'ar' ? 'rtl' : 'ltr'}>
      <header className="flex items-center gap-3 px-3 py-2.5 bg-[#263A30] text-white">
        <button
          type="button"
          onClick={() => onNavigate('today')}
          aria-label="Back"
          className="w-10 h-10 flex items-center justify-center bg-transparent border-0 text-white cursor-pointer"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <path d="M15 18l-6-6 6-6" />
          </svg>
        </button>
        <span className="w-9 h-9 rounded-full bg-[#3E6B53] flex items-center justify-center font-display font-semibold">R</span>
        <span className="flex flex-col">
          <span className="text-[15px] font-semibold">Rebound</span>
          <span className="text-[11px] text-[#A2C7B0]">{busy ? 'typing…' : 'check-in chat'}</span>
        </span>
      </header>

      <div className="flex-1 min-h-0 overflow-y-auto overscroll-contain px-3 py-3 flex flex-col gap-2" aria-live="polite">
        {msgs.map((m) => (
          <div
            key={m.id}
            className={`max-w-[82%] px-3 py-2 rounded-[14px] text-[14px] leading-snug whitespace-pre-line shadow-sm ${
              m.from === 'me'
                ? 'self-end bg-[#D4EAD9] rounded-ee-[4px]'
                : m.care
                  ? 'self-start bg-[#FDE8E4] text-[#7A1F14] rounded-es-[4px]'
                  : 'self-start bg-white rounded-es-[4px]'
            }`}
          >
            {m.text}
          </div>
        ))}
        {replies.length > 0 && (
          <div className="flex flex-wrap gap-1.5 pt-1">
            {replies.map((r) => (
              <button
                key={r.label}
                type="button"
                disabled={busy}
                onClick={r.run}
                className="min-h-[36px] px-3 rounded-full bg-white border border-[#3E6B53] text-[#2C5140] text-[13px] font-semibold cursor-pointer disabled:opacity-50"
              >
                {r.label}
              </button>
            ))}
          </div>
        )}
        <div ref={bottom} />
      </div>

      <form
        className="flex gap-2 p-2.5 bg-[#F3F5EF] border-t border-[#DCE3DA]"
        onSubmit={(e) => {
          e.preventDefault()
          sendText()
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          maxLength={500}
          placeholder="Tell me what's going on…"
          aria-label="Message"
          className="flex-1 min-h-[44px] rounded-full border border-[#C5D0C7] px-4 text-[14px] bg-white"
        />
        <button
          type="submit"
          disabled={!input.trim() || busy}
          aria-label="Send"
          className="w-11 h-11 rounded-full bg-[#3E6B53] text-white flex items-center justify-center border-0 cursor-pointer disabled:opacity-50"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
            <path d="M22 2L11 13M22 2l-7 20-4-9-9-4z" />
          </svg>
        </button>
      </form>
    </div>
  )
}
