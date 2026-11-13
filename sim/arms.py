"""The compared arms. A/A0 = static streak app, B = Engine(rules), C = Engine(bandit),
C4 = C with STEP_UP_SUCCESSES = 4 (pre-registered step-up test).

B and C call the real Engine. A reuses the engine only to pick its *starting* plan (same starting
tier and safety cap Rebound would assign), then never adapts."""

import random
from datetime import UTC, datetime

import numpy as np
from rebound_engine import config as engine_config
from rebound_engine.engine import Engine, NoCopyStore
from rebound_engine.models import (
    Action,
    Barrier,
    ContextFlag,
    DayLog,
    DayOutcome,
    EngagementState,
    Event,
    EventType,
    OnboardingPayload,
    UserProfile,
)
from rebound_engine.policy import choose_actions
from rebound_engine.risk import compute_features
from rebound_engine.safety import SCREENING_QUESTIONS, screening_flags
from rebound_engine.state import compute_engagement_state, initial_state

from .personas import HiddenTraits
from .user_model import HEAT_END, HEAT_START, PersonaSim

ARMS = ("A", "A0", "B", "C", "C4")
_ARM_INDEX = {a: i for i, a in enumerate(ARMS)}
# Pre-registered test (docs/ASSUMPTIONS.md, "Step-up 3 → 4"): C4 is C with one engine constant changed.
ARM_ENGINE_OVERRIDES = {"C4": {"STEP_UP_SUCCESSES": 4}}
_BANDIT_ARMS = ("C", "C4")
_RNG_ARM = {"C4": "C"}  # same bandit random seed as C, so the threshold is the only difference
_EPOCH = datetime(2026, 1, 1, tzinfo=UTC)
HISTORY_DAYS = 21


# ---------- independent checks (not the engine's own filter) ----------


def in_quiet_hours(hour: int, payload: OnboardingPayload) -> bool:
    q = payload.preferences.quiet_hours
    if q is None:
        return False
    s, e = q.start.hour, q.end.hour
    return s <= hour < e if s <= e else (hour >= s or hour < e)


def audit(action: Action, hour: int, payload: OnboardingPayload, flags: set[ContextFlag]) -> str:
    """Comma-separated safety rules this shown action breaks, re-derived from AGENTS.md §4.3/§6.3."""
    s = payload.screening
    positive = {q for q in SCREENING_QUESTIONS if getattr(s, q)}
    cap = 1 if s.chest_pain or s.dizziness_or_fainting else 2 if positive else 4
    movement = action.behaviour.value == "movement"
    problems = []
    if movement and action.tier > cap:
        problems.append("tier_cap")
    if s.pregnant is not None and s.pregnant.value in ("yes", "prefer_not_to_say") and not action.pregnancy_safe:
        problems.append("pregnancy")
    if s.mobility_limitation.value != "none" and movement and not action.seated:
        problems.append("mobility")
    if set(action.contraindications) & positive:
        problems.append("contraindication")
    if ContextFlag.ramadan in flags and not action.fasting_safe:
        problems.append("fasting")
    if ContextFlag.heat in flags and action.setting.value == "outdoor" and HEAT_START <= hour < HEAT_END:
        problems.append("heat")
    if ContextFlag.illness in flags and movement:
        problems.append("illness")
    return ",".join(problems)


# ---------- runners ----------


class _Day:
    """Collects one persona-day's rows and keeps the uniform engagement replay used for metrics."""

    def __init__(self, seed: int, arm: str, pid: int) -> None:
        self.base = {"seed": seed, "arm": arm, "persona_id": pid}
        self.history: list[DayLog] = []
        self.state = EngagementState.active
        self.rows: list[dict] = []

    def action(
        self, day: int, action: Action, window: str, hour: int, outcome: str, quiet: bool, violation: str,
        sim: PersonaSim,
    ):
        self.rows.append(
            self.base
            | {
                "day": day,
                "kind": "action",
                "behaviour": action.behaviour.value,
                "action_id": action.id,
                "tier": action.tier,
                "bct": action.bct_code,
                "setting": action.setting.value,
                "duration_min": action.duration_min,
                "window": window,
                "hour": hour,
                "outcome": outcome,
                "quiet": quiet,
                "violation": violation,
                "app_open": sim.app_open,
                # Ground truth for metrics only (lapse attribution); never passed to the engine.
                "labelled": sim.labelled_today(),
                "shock": sim.shock_today(),
            }
        )
        self.history.append(DayLog(day=day, outcome=DayOutcome(outcome)))

    def event(self, day: int, kind: str, detail: str = "") -> None:
        self.rows.append(self.base | {"day": day, "kind": kind, "detail": detail})

    def close(self, day: int) -> None:
        """Same 7-day engagement rule for every arm (rebound_engine.state.compute_engagement_state)."""
        self.history = [d for d in self.history if d.day > day - HISTORY_DAYS]
        self.state = compute_engagement_state(self.history, self.state)
        for r in reversed(self.rows):
            if r["day"] != day:
                break
            r["state"] = self.state.value


def _profile(payload: OnboardingPayload, pid: int) -> UserProfile:
    return UserProfile.model_validate({**payload.model_dump(), "user_id": f"p{pid}", "created_at": _EPOCH})


def _run_static(arm: str, payload, traits: HiddenTraits, sim: PersonaSim, days: int, log: _Day) -> None:
    profile = _profile(payload, traits.persona_id)
    plan = choose_actions(profile, initial_state(profile, screening_flags(profile)))  # fixed forever
    sensitivity = 0.0 if arm == "A0" else traits.streak_sensitivity
    streak = {s.action.behaviour.value: 0 for s in plan}
    for day in range(1, days + 1):
        sim.start_day(day)
        outcomes = []
        for s in plan:
            o = sim.outcome(s.action, s.time_window.value, s.hour)
            b = s.action.behaviour.value
            if o == "completed":
                streak[b] += 1
            elif streak[b] > 0:  # the visible streak resets to zero on any miss
                streak[b] = 0
                sim.streak_reset(sensitivity)
                log.event(day, "streak_reset", b)
            outcomes.append(o)
            log.action(day, s.action, s.time_window.value, s.hour, o, in_quiet_hours(s.hour, payload), "", sim)
        sim.end_day(outcomes)
        log.close(day)
        if sim.churned_on is not None:
            log.event(day, "churn")
            return


def _run_engine(
    arm: str, payload, traits: HiddenTraits, sim: PersonaSim, days: int, log: _Day, seed: int,
    features: list[dict] | None = None,
):
    pid = traits.persona_id
    engine = Engine(
        store=NoCopyStore(),
        policy_mode="bandit" if arm in _BANDIT_ARMS else "rules",
        rng=random.Random(seed * 1_000_003 + pid * 101 + _ARM_INDEX[_RNG_ARM.get(arm, arm)]),
    )
    uid = engine.onboard(payload, user_id=f"p{pid}").user_id
    told: set[ContextFlag] = set()
    for day in range(1, days + 1):
        sim.start_day(day)
        # Labelled disruptions the engine may know about: Ramadan (calendar) and heat (weather).
        want = {f for f, days_on in ((ContextFlag.heat, sim.heat), (ContextFlag.ramadan, sim.ramadan)) if day in days_on}
        for flag in (ContextFlag.heat, ContextFlag.ramadan):
            if (flag in want) != (flag in told):
                engine.set_context(uid, flag, flag in want)
        told = want
        state = engine.get_state(uid)
        if ContextFlag.illness in state.context_flags and not sim.is_ill():
            engine.set_context(uid, ContextFlag.illness, False)  # "I'm OK now"
        if state.checkin_due:
            answer = sim.answer_checkin()
            if answer is not None:
                engine.checkin(uid, [Barrier(answer)])
                log.event(day, "checkin_answered", answer)
        today = engine.today(uid, day)
        flags = set(engine.get_state(uid).context_flags)
        outcomes = []
        for s in today.actions:
            o = sim.outcome(s.action, s.time_window.value, s.hour)
            outcomes.append(o)
            violation = audit(s.action, s.hour, payload, flags)
            log.action(
                day, s.action, s.time_window.value, s.hour, o, in_quiet_hours(s.hour, payload), violation, sim
            )
            engine.record(Event(user_id=uid, day=day, type=EventType(o), action_id=s.action.id))
        sim.end_day(outcomes)
        log.close(day)
        if features is not None:
            # Task 02b: only what the engine itself holds (profile, state, its own event log) goes in.
            state = engine.get_state(uid)
            features.append({
                "seed": seed, "persona_id": pid, "day": day, "engine_state": state.engagement_state.value,
                **compute_features(engine.store.get_profile(uid), state, engine.events(uid), day),
            })
        if sim.churned_on is not None:
            log.event(day, "churn")
            break
    for e in engine.events(uid):
        if e.type == EventType.checkin_sent:
            log.event(e.day, "checkin_sent", e.payload.get("state", ""))


def run_persona(
    arm: str, payload, traits: HiddenTraits, cfg: dict, days: int, seed: int, features: list[dict] | None = None
) -> list[dict]:
    """Rows for one persona in one arm. Pass a list as `features` (engine arms only) to also collect one
    lapse-risk feature row per day into it."""
    # Same stream per persona in every arm (common random numbers): identical disruption schedule.
    rng = np.random.default_rng([seed, traits.persona_id, 11])
    day_rng = np.random.default_rng([seed, traits.persona_id, 13])  # motivation + app-open: arm-independent
    shock_rng = np.random.default_rng([seed, traits.persona_id, 17])  # unlabelled shocks: arm-independent
    sim = PersonaSim(traits, cfg, days, rng, day_rng, shock_rng)
    log = _Day(seed, arm, traits.persona_id)
    if arm in ("A", "A0"):
        _run_static(arm, payload, traits, sim, days, log)
        return log.rows
    overrides = ARM_ENGINE_OVERRIDES.get(arm, {})
    saved = {k: getattr(engine_config, k) for k in overrides}
    try:  # arm-specific engine constants, always restored (runs are sequential within a process)
        for k, v in overrides.items():
            setattr(engine_config, k, v)
        _run_engine(arm, payload, traits, sim, days, log, seed, features)
    finally:
        for k, v in saved.items():
            setattr(engine_config, k, v)
    return log.rows
