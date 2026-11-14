"""Engine facade used by both the simulator and the API."""

import random
from datetime import UTC, datetime
from typing import Any, Literal, Protocol
from uuid import uuid4

from . import config
from .actions import default_library
from .calendar import Calendar
from .models import (
    Action,
    Barrier,
    Behaviour,
    CheckinResult,
    ContextFlag,
    DayLog,
    DayOutcome,
    EngagementState,
    Event,
    EventType,
    OnboardingPayload,
    OnboardResult,
    ScheduledAction,
    StateSummary,
    TodayResult,
    UserProfile,
    UserState,
)
from .policy import (
    BARRIER_MESSAGE,
    Bandit,
    RulesBandit,
    ThompsonBandit,
    apply_barrier,
    arm_key,
    choose_actions,
    init_bandit_params,
    lighter_option,
    primary_barrier,
    shrink_on_slip,
    tier_cap,
    update_arm,
    update_tier_counters,
)
from .risk.features import compute_features
from .risk.model import RiskModel
from .safety import detect_red_flags, screening_flags
from .state import compute_engagement_state, initial_state, update_habit_strength

_OUTCOME_EVENTS = (EventType.completed, EventType.partial, EventType.skipped, EventType.no_response)


class Store(Protocol):
    def save_profile(self, profile: UserProfile) -> None: ...
    def get_profile(self, user_id: str) -> UserProfile: ...
    def save_state(self, state: UserState) -> None: ...
    def get_state(self, user_id: str) -> UserState: ...
    def append_event(self, event: Event) -> None: ...
    def events(self, user_id: str) -> list[Event]: ...
    def delete_user(self, user_id: str) -> None: ...


class InMemoryStore:
    """Copies on read/write so callers can't mutate stored data by accident (same as a DB would behave)."""

    def __init__(self) -> None:
        self._profiles: dict[str, UserProfile] = {}
        self._states: dict[str, UserState] = {}
        self._events: dict[str, list[Event]] = {}

    def save_profile(self, profile: UserProfile) -> None:
        self._profiles[profile.user_id] = profile.model_copy(deep=True)

    def get_profile(self, user_id: str) -> UserProfile:
        return self._profiles[user_id].model_copy(deep=True)

    def save_state(self, state: UserState) -> None:
        self._states[state.user_id] = state.model_copy(deep=True)

    def get_state(self, user_id: str) -> UserState:
        return self._states[user_id].model_copy(deep=True)

    def append_event(self, event: Event) -> None:
        self._events.setdefault(event.user_id, []).append(event.model_copy(deep=True))

    def events(self, user_id: str) -> list[Event]:
        return [e.model_copy(deep=True) for e in self._events.get(user_id, [])]

    def delete_user(self, user_id: str) -> None:
        for d in (self._profiles, self._states, self._events):
            d.pop(user_id, None)


class NoCopyStore(InMemoryStore):
    """For the simulator: hands out the stored objects themselves (no copies) for speed.
    Safe only when one caller owns each user, as in a simulation run."""

    def save_profile(self, profile: UserProfile) -> None:
        self._profiles[profile.user_id] = profile

    def get_profile(self, user_id: str) -> UserProfile:
        return self._profiles[user_id]

    def save_state(self, state: UserState) -> None:
        self._states[state.user_id] = state

    def get_state(self, user_id: str) -> UserState:
        return self._states[user_id]

    def append_event(self, event: Event) -> None:
        self._events.setdefault(event.user_id, []).append(event)

    def events(self, user_id: str) -> list[Event]:
        return list(self._events.get(user_id, []))


PolicyMode = Literal["rules", "bandit"]


class Engine:
    def __init__(
        self,
        store: Store | None = None,
        library: list[Action] | None = None,
        bandit: Bandit | None = None,
        policy_mode: PolicyMode = "rules",
        rng: random.Random | None = None,
        risk_model: RiskModel | None = None,
        calendar: Calendar | None = None,
    ) -> None:
        """policy_mode="rules": deterministic choice, default window (Task 01 behaviour).
        policy_mode="bandit": Thompson sampling over (action, window) arms, seeded by `rng`.
        risk_model: optional lapse-risk model (Task 02b). When risk is above its threshold and the user is still
        active, each action comes with a lighter option, plus a gentle check-in at most once per 7 days."""
        self.risk_model = risk_model
        # Task 05 A2: Ramadan, Eid, heat and shift timings worked out per day. None (the simulator) = explicit flags only.
        self.calendar = calendar
        if policy_mode not in ("rules", "bandit"):
            raise ValueError(f"unknown policy_mode {policy_mode!r}")
        self.store = store or InMemoryStore()
        self.library = list(library) if library is not None else list(default_library())
        self._by_id = {a.id: a for a in self.library}
        self.policy_mode = policy_mode
        if bandit is not None:
            self.bandit = bandit
        elif policy_mode == "bandit":
            self.bandit = ThompsonBandit(rng or random.Random(0))
        else:
            self.bandit = RulesBandit()

    # ---------- public API ----------

    def onboard(self, payload: OnboardingPayload, user_id: str | None = None) -> OnboardResult:
        profile = UserProfile.model_validate(
            {
                **payload.model_dump(),
                "user_id": user_id or uuid4().hex,
                "created_at": datetime.now(UTC),
            }
        )
        screening = screening_flags(profile)
        state = initial_state(profile, screening)
        if self.policy_mode == "bandit":
            state.bandit_params = init_bandit_params(profile, self.library)
        reason = profile.history.motivation_reason
        red_flag = bool(reason) and detect_red_flags(reason)
        if red_flag:
            state.red_flag = True
            state.context_flags.add(ContextFlag.paused)  # no coaching until a person has checked in
        self.store.save_profile(profile)
        self.store.save_state(state)
        if red_flag:
            self._log(profile.user_id, 0, EventType.red_flag, payload={"source": "motivation_reason"})
        if screening.flag:
            self._log(
                profile.user_id,
                0,
                EventType.screening_flag,
                payload={"positive": screening.positive, "see_doctor": screening.see_doctor,
                         "contraindicated": screening.contraindicated},
            )
        return OnboardResult(
            user_id=profile.user_id, state=state, screening=screening, red_flag=red_flag
        )

    def today(self, user_id: str, day: int, hour: int | None = None) -> TodayResult:
        """Today's actions, one per goal. A new day first closes the previous one:
        anything still unanswered is recorded as no_response."""
        profile, state = self._load(user_id)
        if day > state.day:
            for action_id in list(state.pending):
                self._apply_outcome(profile, state, self._by_id[action_id], DayOutcome.no_response, state.day)
                self._log(user_id, state.day, EventType.no_response, action_id=action_id)
            if state.pending:
                state.pending = []
                self._end_day(profile, state)
            for b, h in state.habit_strength.items():
                state.h_daily[b] = [*state.h_daily.get(b, []), h][-config.H_DAILY_KEEP :]
            self._set_day_context(profile, state, day)  # after closing yesterday, which keeps yesterday's context
            scheduled = choose_actions(profile, state, library=self.library, bandit=self.bandit)
            self._risk_hook(profile, state, scheduled, day)
            state.day = day
            state.shown_today = [(s.action.id, s.time_window, s.hour) for s in scheduled]
            state.pending = [s.action.id for s in scheduled]
            for s in scheduled:
                payload = {"window": s.time_window.value, "hour": s.hour}
                if s.lighter is not None:
                    payload["lighter"] = s.lighter.id
                self._log(user_id, day, EventType.action_shown, action_id=s.action.id, payload=payload)
        else:
            scheduled = [
                ScheduledAction(
                    action=self._by_id[i], time_window=w, hour=h, explanation_id=i,
                    lighter=self._by_id.get(state.lighter_offers.get(i, "")),
                )
                for i, w, h in state.shown_today
            ]
        self.store.save_state(state)
        return TodayResult(
            day=day,
            actions=scheduled,
            message_keys=self._message_keys(profile, state),
            channel=state.channel,
            checkin_due=state.checkin_due,
            state_summary=self._summary(state),
            risk=state.last_risk,
            risk_reasons=state.last_risk_reasons,
        )

    def record(self, event: Event) -> UserState:
        profile, state = self._load(event.user_id)
        if event.type == EventType.pause:
            self._set_flag(state, ContextFlag.paused, bool(event.payload.get("on", True)))
            self.store.append_event(event)
            self.store.save_state(state)
            return state
        if event.type not in _OUTCOME_EVENTS:
            raise ValueError(f"record() takes an outcome or pause event, got {event.type}")
        action = self._by_id.get(event.action_id or "")
        if action is None or action.behaviour not in state.current_tier:
            raise ValueError(f"unknown action {event.action_id!r} for this user")

        self._apply_outcome(profile, state, action, DayOutcome(event.type), event.day)
        self.store.append_event(event)
        # The user may have taken today's lighter option instead of the shown action: it answers that action.
        answered = action.id
        if answered not in state.pending:
            answered = next((shown for shown, lighter in state.lighter_offers.items() if lighter == action.id), answered)
        if answered in state.pending:
            state.pending.remove(answered)
            if not state.pending:
                self._end_day(profile, state)
        self.store.save_state(state)
        return state

    def checkin(
        self, user_id: str, barriers: list[Barrier], free_text: str | None = None, replace_pending: bool = False
    ) -> CheckinResult:
        """replace_pending=True (the API): today's still-open action of each behaviour is swapped for its adjusted
        action, so the user can do the smaller step today. The simulator keeps False (adjusted from tomorrow)."""
        profile, state = self._load(user_id)
        primary = primary_barrier(barriers)
        # Free text isn't stored (data minimisation); only whether it raised a red flag.
        if free_text and detect_red_flags(free_text):
            state.red_flag = True
            state.context_flags.add(ContextFlag.paused)  # stop coaching
            state.checkin_due = False
            self._log(user_id, state.day, EventType.red_flag, payload={"source": "keyword"})
            self.store.save_state(state)
            return CheckinResult(barrier=primary, adjusted_actions=[], message_key="seek_care", red_flag=True)
        barrier = primary or Barrier.other
        message_key = apply_barrier(profile, state, barrier)
        if self.policy_mode == "bandit" and barrier in (Barrier.forgot, Barrier.schedule_change):
            # The bandit owns the window: count one failure against every arm in the last movement window.
            window = next((w for i, w, _ in state.shown_today if self._by_id[i].behaviour == Behaviour.movement), None)
            for key in [k for k in state.bandit_params if window and k.endswith(f"@{window.value}")]:
                state.bandit_params[key][1] += 1
        scheduled = choose_actions(profile, state, library=self.library, bandit=self.bandit)
        state.checkin_due = False
        self._log(
            user_id,
            state.day,
            EventType.checkin,
            payload={"barriers": [b.value for b in barriers], "primary": barrier.value},
        )
        if replace_pending:
            self._replace_pending(state, scheduled)
        self.store.save_state(state)
        actions = [s.action for s in scheduled]
        return CheckinResult(
            barrier=barrier, adjusted_actions=actions, message_key=message_key, red_flag=False
        )

    def set_context(self, user_id: str, flag: ContextFlag, on: bool) -> UserState:
        """Turn a context flag on/off, e.g. heat mode, Ramadan, or 'I'm OK now' after illness."""
        _, state = self._load(user_id)
        self._set_flag(state, flag, on)
        self._log(user_id, state.day, EventType.context_change, payload={"flag": flag.value, "on": on})
        self.store.save_state(state)
        return state

    def refresh_context(self, user_id: str) -> UserState:
        """Re-read the calendar for today (e.g. after "Ramadan started today") and re-choose today's still-open
        actions, so a fasting user isn't left with a step that isn't fasting-safe."""
        profile, state = self._load(user_id)
        if self.calendar is None or state.day < 1:
            return state
        self._set_day_context(profile, state, state.day)
        for s in choose_actions(profile, state, library=self.library, bandit=self.bandit):
            old = next((i for i in state.pending if self._by_id[i].behaviour == s.action.behaviour), None)
            if old is None:
                continue
            shown = next(((w, h) for i, w, h in state.shown_today if i == old), None)
            if old == s.action.id and shown == (s.time_window, s.hour):
                continue
            state.pending[state.pending.index(old)] = s.action.id
            state.shown_today = [
                (s.action.id, s.time_window, s.hour) if i == old else (i, w, h) for i, w, h in state.shown_today
            ]
            self._log(user_id, state.day, EventType.action_shown, action_id=s.action.id,
                      payload={"window": s.time_window.value, "hour": s.hour, "replaces": old})
        self.store.save_state(state)
        return state

    def get_state(self, user_id: str) -> UserState:
        return self.store.get_state(user_id)

    def events(self, user_id: str) -> list[Event]:
        return self.store.events(user_id)

    def delete_user(self, user_id: str) -> None:
        self.store.delete_user(user_id)

    # ---------- helpers ----------

    def _load(self, user_id: str) -> tuple[UserProfile, UserState]:
        return self.store.get_profile(user_id), self.store.get_state(user_id)

    def _apply_outcome(
        self, profile: UserProfile, state: UserState, action: Action, outcome: DayOutcome, day: int
    ) -> None:
        if ContextFlag.paused in state.context_flags:
            outcome = DayOutcome.paused
        elif ContextFlag.illness in state.context_flags:
            outcome = DayOutcome.illness
        elif ContextFlag.eid in state.auto_flags and outcome in (DayOutcome.skipped, DayOutcome.no_response):
            outcome = DayOutcome.paused  # Eid is rest-friendly: a missed step doesn't count
        b = action.behaviour
        state.habit_strength[b] = update_habit_strength(state.habit_strength[b], outcome)
        state.history.append(DayLog(day=day, behaviour=b, action_id=action.id, outcome=outcome))
        if outcome == DayOutcome.completed:
            state.last_barrier = None  # temporary adjustments (low energy) end here
        update_tier_counters(state, b, action.tier, outcome, tier_cap(profile, b))
        if self.policy_mode == "bandit" and outcome in config.OUTCOME_VALUE:
            window = next((w for i, w, _ in state.shown_today if i == action.id), None)
            if window is not None:
                update_arm(state, arm_key(action.id, window), config.OUTCOME_VALUE[outcome])

    def _replace_pending(self, state: UserState, scheduled: list[ScheduledAction]) -> None:
        for s in scheduled:
            old = next((i for i in state.pending if self._by_id[i].behaviour == s.action.behaviour), None)
            if old is None or old == s.action.id:
                continue
            state.pending[state.pending.index(old)] = s.action.id
            state.shown_today = [
                (s.action.id, s.time_window, s.hour) if i == old else (i, w, h) for i, w, h in state.shown_today
            ]
            state.lighter_offers.pop(old, None)
            self._log(
                state.user_id, state.day, EventType.action_shown, action_id=s.action.id,
                payload={"window": s.time_window.value, "hour": s.hour, "replaces": old},
            )

    def _risk_hook(self, profile: UserProfile, state: UserState, scheduled: list[ScheduledAction], day: int) -> None:
        """Task 02b. Runs before today's actions are logged. Never punitive: it only adds a lighter option to each
        action (same safety filter, same hour) and, at most once per 7 days, a gentle check-in. Doesn't change the
        tier, the shown action, or anything else."""
        state.lighter_offers, state.last_risk, state.last_risk_reasons = {}, None, []
        if self.risk_model is None or not scheduled:
            return
        features = compute_features(profile, state, self.store.events(state.user_id), day - 1)
        risk = self.risk_model.predict(features)
        state.last_risk = risk
        if risk < self.risk_model.threshold or state.engagement_state != EngagementState.active:
            return
        for s in scheduled:
            s.lighter = lighter_option(profile, state, s, self.library)
            if s.lighter is not None:
                state.lighter_offers[s.action.id] = s.lighter.id
        state.last_risk_reasons = self.risk_model.reasons(features)
        self._log(state.user_id, day, EventType.risk_alert,
                  payload={"risk": risk, "reasons": state.last_risk_reasons, "offers": dict(state.lighter_offers)})
        recent = day - state.last_risk_checkin_day < config.RISK_CHECKIN_EVERY_DAYS
        if not state.checkin_due and not recent and state.last_checkin_sent_day != day:
            state.checkin_due = True
            state.last_risk_checkin_day = state.last_checkin_sent_day = day
            self._log(state.user_id, day, EventType.checkin_sent, payload={"state": "at_risk"})

    def _end_day(self, profile: UserProfile, state: UserState) -> None:
        """All of the day's actions have an outcome: update engagement, shrink tiers on a slip."""
        keep_from = state.day - config.HISTORY_KEEP_DAYS
        state.history = [d for d in state.history if d.day > keep_from]
        new = compute_engagement_state(state.history, state.engagement_state)
        if new == state.engagement_state:
            return
        shrink_on_slip(state, new)
        state.checkin_due = new in (EngagementState.drifting, EngagementState.lapsed)
        if state.checkin_due and state.last_checkin_sent_day != state.day:  # at most one check-in message a day
            self._log(state.user_id, state.day, EventType.checkin_sent, payload={"state": new.value})
            state.last_checkin_sent_day = state.day
        state.engagement_state = new

    def _log(
        self,
        user_id: str,
        day: int,
        type: EventType,
        action_id: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        self.store.append_event(
            Event(user_id=user_id, day=day, type=type, action_id=action_id, payload=payload or {})
        )

    @staticmethod
    def _set_flag(state: UserState, flag: ContextFlag, on: bool) -> None:
        if on:
            state.context_flags.add(flag)
            return
        state.context_flags.discard(flag)
        if flag == ContextFlag.illness and state.last_barrier == Barrier.illness_pain:
            state.last_barrier = None

    @staticmethod
    def _message_keys(profile: UserProfile, state: UserState) -> list[str]:
        screening = screening_flags(profile)
        keys = []
        if screening.see_doctor:
            keys.append("see_doctor")
        elif screening.flag:
            keys.append("check_with_doctor")
        if state.red_flag and ContextFlag.paused in state.context_flags:
            keys.append("seek_care")
        if state.last_barrier is not None:
            keys.append(BARRIER_MESSAGE[state.last_barrier])
            if state.last_barrier == Barrier.low_motivation:
                keys.append("buddy_offer")
        if state.lighter_offers:
            keys.append("lighter_option")  # "Busy week ahead? Here's a lighter version"
        if ContextFlag.eid in state.auto_flags:
            keys.append("eid_rest")
        return keys

    def _set_day_context(self, profile: UserProfile, state: UserState, day: int) -> None:
        if self.calendar is None:
            return
        ctx = self.calendar.day(profile, day)
        state.auto_flags, state.iftar_hour, state.day_times = set(ctx.flags), ctx.iftar_hour, ctx.day_times

    @staticmethod
    def _summary(state: UserState) -> StateSummary:
        return StateSummary(
            habit_strength=state.habit_strength,
            engagement_state=state.engagement_state,
            tiers=state.current_tier,
        )
