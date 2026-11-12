"""Engine facade used by both the simulator and the API."""

from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import uuid4

from .actions import default_library
from .models import (
    Action,
    Barrier,
    CheckinResult,
    ContextFlag,
    DayLog,
    DayOutcome,
    EngagementState,
    Event,
    EventType,
    OnboardingPayload,
    OnboardResult,
    StateSummary,
    TodayResult,
    UserProfile,
    UserState,
)
from .policy import (
    BARRIER_MESSAGE,
    Bandit,
    RulesBandit,
    choose_action,
    primary_barrier,
    register_success,
    tier_cap,
)
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


class Engine:
    def __init__(
        self,
        store: Store | None = None,
        library: list[Action] | None = None,
        bandit: Bandit | None = None,
    ) -> None:
        self.store = store or InMemoryStore()
        self.library = list(library) if library is not None else list(default_library())
        self._by_id = {a.id: a for a in self.library}
        self.bandit = bandit or RulesBandit()

    # ---------- public API ----------

    def onboard(self, payload: OnboardingPayload, user_id: str | None = None) -> OnboardResult:
        profile = UserProfile.model_validate(
            {
                **payload.model_dump(),
                "user_id": user_id or uuid4().hex,
                "created_at": datetime.now(timezone.utc),
            }
        )
        screening = screening_flags(profile)
        state = initial_state(profile, screening)
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
                payload={"positive": screening.positive, "see_doctor": screening.see_doctor},
            )
        return OnboardResult(
            user_id=profile.user_id, state=state, screening=screening, red_flag=red_flag
        )

    def today(self, user_id: str, day: int, hour: int | None = None) -> TodayResult:
        profile, state = self._load(user_id)
        action = choose_action(profile, state, hour=hour, library=self.library, bandit=self.bandit)
        state.day = day
        if action is not None:
            state.last_behaviour = action.behaviour
            self._log(user_id, day, EventType.action_shown, action_id=action.id)
        self.store.save_state(state)
        return TodayResult(
            day=day,
            action=action,
            explanation_id=action.id if action else None,
            message_keys=self._message_keys(profile, state),
            time_window=state.time_window,
            channel=state.channel,
            checkin_due=state.checkin_due,
            state_summary=self._summary(state),
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

        outcome = DayOutcome(event.type)
        if ContextFlag.paused in state.context_flags:
            outcome = DayOutcome.paused
        elif ContextFlag.illness in state.context_flags:
            outcome = DayOutcome.illness
        b = action.behaviour
        state.habit_strength[b] = update_habit_strength(state.habit_strength[b], outcome)
        state.history.append(DayLog(day=event.day, behaviour=b, action_id=action.id, outcome=outcome))
        if outcome == DayOutcome.completed:
            state.last_barrier = None  # temporary adjustments (low energy, sleep first) end here
            register_success(state, b, action.tier, tier_cap(profile, b))

        new = compute_engagement_state(state.history, state.engagement_state)
        if new != state.engagement_state:
            state.checkin_due = new in (EngagementState.drifting, EngagementState.lapsed)
            state.engagement_state = new
        self.store.append_event(event)
        self.store.save_state(state)
        return state

    def checkin(
        self, user_id: str, barriers: list[Barrier], free_text: str | None = None
    ) -> CheckinResult:
        profile, state = self._load(user_id)
        primary = primary_barrier(barriers)
        # Free text isn't stored (data minimisation); only whether it raised a red flag.
        if free_text and detect_red_flags(free_text):
            state.red_flag = True
            state.context_flags.add(ContextFlag.paused)  # stop coaching
            state.checkin_due = False
            self._log(user_id, state.day, EventType.red_flag, payload={"source": "keyword"})
            self.store.save_state(state)
            return CheckinResult(
                barrier=primary, adjusted_action=None, message_key="seek_care", red_flag=True
            )
        barrier = primary or Barrier.other
        action = choose_action(profile, state, barrier=barrier, library=self.library, bandit=self.bandit)
        state.checkin_due = False
        self._log(
            user_id,
            state.day,
            EventType.checkin,
            payload={"barriers": [b.value for b in barriers], "primary": barrier.value},
        )
        self.store.save_state(state)
        return CheckinResult(
            barrier=barrier,
            adjusted_action=action,
            message_key=BARRIER_MESSAGE[barrier],
            red_flag=False,
        )

    def set_context(self, user_id: str, flag: ContextFlag, on: bool) -> UserState:
        """Turn a context flag on/off, e.g. heat mode, Ramadan, or 'I'm OK now' after illness."""
        _, state = self._load(user_id)
        self._set_flag(state, flag, on)
        self._log(user_id, state.day, EventType.context_change, payload={"flag": flag.value, "on": on})
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
        return keys

    @staticmethod
    def _summary(state: UserState) -> StateSummary:
        return StateSummary(
            habit_strength=state.habit_strength,
            engagement_state=state.engagement_state,
            tiers=state.current_tier,
        )
