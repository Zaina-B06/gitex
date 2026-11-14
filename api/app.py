"""Rebound API: a thin FastAPI wrapper. It calls Engine methods and never reimplements engine logic.

Auth is prototype-grade (see docs/ASSUMPTIONS.md, Limitations): POST /users returns a random bearer token once;
only its sha256 is stored, and every /users/{id}/* route requires it."""

import hashlib
import hmac
import json
import random
import secrets
from collections import Counter
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import Depends, FastAPI, Header, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from rebound_engine.calendar import RAMADAN, day_context
from rebound_engine.engine import Engine
from rebound_engine.models import (
    Barrier,
    Behaviour,
    CheckinResult,
    Conditions,
    ConsentGroup,
    ContextFlag,
    DayContext,
    DayLog,
    EngagementState,
    Event,
    EventType,
    History,
    Language,
    OnboardingPayload,
    Preferences,
    ScreeningResult,
    Shift,
    TodayResult,
    UserProfile,
    UserState,
)
from rebound_engine.plan import build_plan
from rebound_engine.policy import effective_flags
from rebound_engine.safety import detect_red_flags

from .demo import (
    DEMO_PERSONAS,
    ORG_DAYS,
    ORG_PATTERNS,
    ORG_SIZE,
    OUTCOMES,
    PATTERNS,
    PERSONA_WARMUP_DAYS,
    AdvanceIn,
    DayRow,
    SeedOut,
    SeedPersona,
    org_bodies,
)
from .llm_client import BarrierClassifier, default_classifier
from .messages import HOW_TO_TURN_OFF, render, render_reason
from .store import SQLiteStore, UserMeta, sqlite_path

DEFAULT_TIMEZONE = "Asia/Dubai"
LOCAL_FRONTEND = "http://localhost:5173"  # allowed only with DEMO_MODE or DEV_MODE
CATCH_UP_MAX_DAYS = 60  # unopened days filled in on return (docs/ASSUMPTIONS.md, API)
EMPLOYER_MIN_GROUP = 10  # k for employer aggregates (AGENTS.md §2.6)
PLAN_REASONS_SHOWN = 3  # the rest are behind "See why" (Task 05: no information dumping)
RAMADAN_MAX_SHIFT_DAYS = 2  # a "started today / ended" tap may move the table date by at most this many days


# ---------- request / response shapes ----------


class OnboardIn(OnboardingPayload):
    """OnboardingPayload (AGENTS.md §4) plus API-only fields the engine never sees."""

    timezone: str = DEFAULT_TIMEZONE
    org_id: str | None = Field(default=None, min_length=1, max_length=64)

    @field_validator("timezone")
    @classmethod
    def _known_timezone(cls, v: str) -> str:
        try:
            ZoneInfo(v)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError(f"unknown time zone {v!r}") from None
        return v

    @field_validator("consents")
    @classmethod
    def _screening_consent_needed(cls, v: dict[ConsentGroup, bool]) -> dict[ConsentGroup, bool]:
        if v.get(ConsentGroup.screening) is False:
            raise ValueError("the health check is needed to build a safe plan")
        return v


class StateOut(BaseModel):
    day: int
    habit_strength: dict[Behaviour, float]
    engagement_state: EngagementState
    tiers: dict[Behaviour, int]
    context_flags: set[ContextFlag]
    checkin_due: bool
    history: list[DayLog]  # recent days only (engine keeps HISTORY_KEEP_DAYS)


class TodayOut(TodayResult):
    messages: list[str]  # message_keys rendered in the user's language


class PlanOut(BaseModel):
    """What the user sees of their plan. Queued behaviours are internal and never included."""

    behaviours: list[Behaviour]  # with daily actions, in order
    reasons: list[str]  # at most PLAN_REASONS_SHOWN, most important first
    all_reasons: list[str]  # the full list, for "See why"


class OnboardOut(BaseModel):
    user_id: str
    token: str  # shown once; send as "Authorization: Bearer <token>"
    screening: ScreeningResult
    red_flag: bool
    state: StateOut
    today: TodayOut
    plan_summary: PlanOut


class EventIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action_id: str
    type: Literal["completed", "partial", "skipped"]


class StateResponse(BaseModel):
    state: StateOut


class CheckinIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    barriers: list[Barrier] = Field(default_factory=list)
    free_text: str | None = Field(default=None, max_length=500)


class CheckinOut(CheckinResult):
    message: str


class ExplainOut(BaseModel):
    bct_code: str
    bct_name: str
    rationale: str
    limits: str
    how_to_turn_off: str


class SettingsIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    preferences: dict[str, Any] | None = None  # partial Preferences, merged then validated
    consents: dict[ConsentGroup, bool] | None = None
    context: dict[ContextFlag, bool] | None = None  # e.g. {"heat": true}, {"illness": false} = "I'm OK now"
    conditions: Conditions | None = None  # replaces the "Anything you're managing?" answers
    shifts: list[Shift] | None = None  # replaces the weekly shift pattern; [] clears it. Takes effect the next day
    ramadan: Literal["started_today", "ended_today"] | None = None  # moon-sighting correction, applies today


class SettingsOut(BaseModel):
    preferences: Preferences
    consents: dict[ConsentGroup, bool]
    state: StateOut
    plan_summary: PlanOut  # re-built from the updated answers


class AdvanceOut(BaseModel):
    state: StateOut
    today: TodayOut  # the new day, already opened
    log: list[DayRow]  # one row per day that was filled in


class BarrierCount(BaseModel):
    barrier: Barrier
    count: int


class EmployerOut(BaseModel):
    """Aggregates for one org; only returned for groups of at least EMPLOYER_MIN_GROUP (AGENTS.md §2.6)."""

    org_id: str
    group_size: int
    active_share: float  # share of members whose engagement state is "active"
    average_habit_strength: dict[Behaviour, float]
    top_barriers: list[BarrierCount]  # most common check-in barriers, at most 3


class ExportOut(BaseModel):
    """Everything stored about the user (AGENTS.md §4.7), except the token hash."""

    account: dict[str, Any]  # time zone, org, onboarding date, demo day offset
    profile: UserProfile
    state: UserState
    events: list[Event]


# What a group goes back to when its consent is withdrawn. Screening can't be withdrawn (needed for safety).
_EMPTY_GROUP: dict[ConsentGroup, Callable[[], Any]] = {
    ConsentGroup.body: lambda: None,
    ConsentGroup.history: History,
    ConsentGroup.preferences: Preferences,
    ConsentGroup.conditions: Conditions,
}


def _withdrawn(consents: dict[ConsentGroup, bool]) -> dict[str, Any]:
    """Groups whose consent is withdrawn, set back to empty: their answers are deleted, and stay deleted on
    every later save until consent is given again."""
    return {g.value: _EMPTY_GROUP[g]() for g, ok in consents.items() if not ok and g in _EMPTY_GROUP}


def _plan_out(profile: UserProfile) -> PlanOut:
    plan = build_plan(profile)
    reasons = [render_reason(k, profile) for k in plan.reasons]
    return PlanOut(behaviours=plan.active, reasons=reasons[:PLAN_REASONS_SHOWN], all_reasons=reasons)


def _state_out(s: UserState) -> StateOut:
    return StateOut(
        day=s.day, habit_strength=s.habit_strength, engagement_state=s.engagement_state, tiers=s.current_tier,
        context_flags=effective_flags(s), checkin_due=s.checkin_due, history=s.history,
    )


def local_date_of(meta: UserMeta, day: int) -> date:
    """Engine day -> local date. Includes demo time travel, so `advance` moves the calendar too."""
    return meta.onboard_date + timedelta(days=day - 1)


def _ramadan_shift(today: date, tap: str) -> tuple[str, int] | None:
    """("start"/"end", days) to move the nearest Umm al-Qura date onto today; None if no Ramadan is that close."""
    field, index = ("ramadan_start_shift", 0) if tap == "started_today" else ("ramadan_end_shift", 1)
    for dates in RAMADAN:
        shift = (today - dates[index]).days
        if abs(shift) <= RAMADAN_MAX_SHIFT_DAYS:
            return field, shift
    return None


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# ---------- app ----------


def create_app(
    database_url: str = "sqlite:///rebound.db",
    frontend_url: str | None = None,
    demo_mode: bool = False,
    clock: Callable[[], datetime] | None = None,
    classifier: BarrierClassifier | None = None,
    dev_mode: bool = False,
    demo_key: str | None = None,
    org_key: str | None = None,
    dashboard_path: Path | None = None,
) -> FastAPI:
    store = SQLiteStore(sqlite_path(database_url))

    class UserCalendar:
        """Engine day -> the user's local date (onboarding day = day 1), then the offline calendar rules."""

        def day(self, profile: UserProfile, day: int) -> DayContext:
            meta = store.get_meta(profile.user_id)
            return day_context(profile, local_date_of(meta, day), meta.ramadan_start_shift, meta.ramadan_end_shift)

    # Rules mode, no risk model (hook off: ASSUMPTIONS.md, "Arm D"); calendar context on (the simulator has none).
    engine = Engine(store=store, calendar=UserCalendar())
    classifier = classifier or default_classifier()

    app = FastAPI(title="Rebound API", version="0.1.0")
    app.state.store, app.state.engine, app.state.demo_mode = store, engine, demo_mode
    app.state.clock = clock or (lambda: datetime.now(UTC))  # tests swap this
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o for o in (LOCAL_FRONTEND if demo_mode or dev_mode else None, frontend_url) if o],
        allow_methods=["*"],
        allow_headers=["Authorization", "Content-Type"],
    )
    bearer = HTTPBearer(auto_error=False)

    def authed(
        user_id: str, creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]
    ) -> UserMeta:
        try:
            meta = store.get_meta(user_id)
        except KeyError:
            meta = None  # same answer as a wrong token, so user ids can't be probed
        if meta is None or creds is None or not hmac.compare_digest(meta.token_hash, _hash(creds.credentials)):
            raise HTTPException(401, "invalid or missing token", headers={"WWW-Authenticate": "Bearer"})
        return meta

    Authed = Annotated[UserMeta, Depends(authed)]

    def current_day(meta: UserMeta) -> int:
        """Calendar days in the user's time zone; the onboarding day is engine day 1."""
        local = app.state.clock().astimezone(ZoneInfo(meta.timezone)).date()
        return max(1, (local - meta.onboard_date).days + 1 + meta.day_offset)

    def open_day(meta: UserMeta) -> TodayResult:
        """Bring the engine up to today, one day at a time. A day the app wasn't opened is a day the action was
        shown and got no response, exactly as in the simulator."""
        day, start = current_day(meta), engine.get_state(meta.user_id).day + 1
        # Bounded work per request; days beyond the cap are simply not logged.
        for d in range(max(start, day - CATCH_UP_MAX_DAYS), day):
            engine.today(meta.user_id, d)
        return engine.today(meta.user_id, day)

    def today_out(meta: UserMeta, result: TodayResult) -> TodayOut:
        profile = store.get_profile(meta.user_id)
        return TodayOut.model_validate(
            {**result.model_dump(), "messages": [render(k, profile) for k in result.message_keys]}
        )

    @app.post("/users", status_code=201, response_model=OnboardOut)
    def onboard(body: OnboardIn) -> OnboardOut:
        # Answers for a group given without consent are dropped before the engine sees them.
        payload = OnboardingPayload.model_validate(
            {**body.model_dump(exclude={"timezone", "org_id"}), **_withdrawn(body.consents)}
        )
        result = engine.onboard(payload)
        token = secrets.token_urlsafe(32)
        meta = UserMeta(
            user_id=result.user_id, timezone=body.timezone, org_id=body.org_id, token_hash=_hash(token),
            onboard_date=app.state.clock().astimezone(ZoneInfo(body.timezone)).date(),
        )
        store.save_meta(meta)
        today = today_out(meta, open_day(meta))
        return OnboardOut(
            user_id=result.user_id, token=token, screening=result.screening, red_flag=result.red_flag,
            state=_state_out(engine.get_state(result.user_id)), today=today,
            plan_summary=_plan_out(store.get_profile(result.user_id)),
        )

    @app.get("/users/{user_id}/plan", response_model=PlanOut)
    def plan(meta: Authed) -> PlanOut:
        return _plan_out(store.get_profile(meta.user_id))

    @app.get("/users/{user_id}/today", response_model=TodayOut)
    def today(meta: Authed) -> TodayOut:
        return today_out(meta, open_day(meta))

    @app.post("/users/{user_id}/events", response_model=StateResponse)
    def record(body: EventIn, meta: Authed) -> StateResponse:
        open_day(meta)
        state = engine.get_state(meta.user_id)
        if body.action_id not in state.pending:
            raise HTTPException(409, "not one of today's open actions (unknown, or already answered)")
        event = Event(user_id=meta.user_id, day=state.day, type=EventType(body.type), action_id=body.action_id)
        return StateResponse(state=_state_out(engine.record(event)))

    @app.post("/users/{user_id}/checkin", response_model=CheckinOut)
    def checkin(body: CheckinIn, meta: Authed) -> CheckinOut:
        open_day(meta)  # check in on today's state, or a lapse found later would ask again the same day
        day = engine.get_state(meta.user_id).day
        red_flag_text = bool(body.free_text) and detect_red_flags(body.free_text)
        if meta.last_checkin_day == day and not red_flag_text:  # a red flag always gets through
            raise HTTPException(409, "already checked in today")
        barriers = list(body.barriers)  # buttons decide; free text only fills in when none were pressed
        # The engine's red-flag keywords run first (inside checkin); red-flag text never goes to the classifier.
        if not barriers and body.free_text and not red_flag_text:
            guess = classifier.classify_barrier(body.free_text)
            barriers = [guess] if guess else []
        result = engine.checkin(meta.user_id, barriers, free_text=body.free_text, replace_pending=True)
        store.save_meta(meta.model_copy(update={"last_checkin_day": day}))
        profile = store.get_profile(meta.user_id)
        return CheckinOut.model_validate({**result.model_dump(), "message": render(result.message_key, profile)})

    @app.get("/users/{user_id}/state", response_model=StateOut)
    def get_state(meta: Authed) -> StateOut:
        open_day(meta)
        return _state_out(engine.get_state(meta.user_id))

    @app.patch("/users/{user_id}/settings", response_model=SettingsOut)
    def settings(body: SettingsIn, meta: Authed) -> SettingsOut:
        open_day(meta)
        uid = meta.user_id
        profile = store.get_profile(uid)
        if body.context and body.context.get(ContextFlag.paused) is False and engine.get_state(uid).red_flag:
            raise HTTPException(409, "coaching stays paused after a safety concern until a person has checked in")
        if (body.consents or {}).get(ConsentGroup.screening) is False:
            raise HTTPException(409, "the health check is needed for a safe plan; delete your account instead")
        ramadan_fix = None
        if body.ramadan is not None:
            ramadan_fix = _ramadan_shift(local_date_of(meta, engine.get_state(uid).day), body.ramadan)
            if ramadan_fix is None:
                raise HTTPException(409, f"no Ramadan within {RAMADAN_MAX_SHIFT_DAYS} days of today in the calendar")
        try:
            prefs = Preferences.model_validate({**profile.preferences.model_dump(), **(body.preferences or {})})
        except ValidationError as e:
            raise RequestValidationError(e.errors(include_url=False)) from None
        consents = {**profile.consents, **(body.consents or {})}
        update: dict[str, Any] = {"preferences": prefs, "consents": consents}
        if body.conditions is not None:
            update["conditions"] = body.conditions
        if body.shifts is not None:  # takes effect when the next day opens
            update["basics"] = profile.basics.model_copy(update={"shifts": body.shifts or None})
        profile = profile.model_copy(update={**update, **_withdrawn(consents)})
        store.save_profile(profile)
        for flag, on in (body.context or {}).items():
            engine.set_context(uid, flag, on)
        if ramadan_fix is not None:
            field, shift = ramadan_fix
            store.save_meta(meta.model_copy(update={field: shift}))
        if ramadan_fix is not None or "iftar_time" in (body.preferences or {}):
            engine.refresh_context(uid)  # applies today: today's open steps become fasting-safe at the right hour
        return SettingsOut(preferences=profile.preferences, consents=profile.consents,
                           state=_state_out(engine.get_state(uid)), plan_summary=_plan_out(profile))

    @app.get("/users/{user_id}/export", response_model=ExportOut)
    def export(meta: Authed) -> ExportOut:
        open_day(meta)
        uid = meta.user_id
        return ExportOut(
            account=meta.model_dump(exclude={"token_hash"}), profile=store.get_profile(uid),
            state=engine.get_state(uid), events=engine.events(uid),
        )

    @app.delete("/users/{user_id}", status_code=204)
    def delete_user(meta: Authed) -> Response:
        engine.delete_user(meta.user_id)  # SQLiteStore also removes user_meta
        return Response(status_code=204)

    @app.get("/actions/{action_id}/explain", response_model=ExplainOut)
    def explain(action_id: str, lang: Language = Language.en) -> ExplainOut:
        action = next((a for a in engine.library if a.id == action_id), None)
        if action is None:
            raise HTTPException(404, "unknown action")
        return ExplainOut(
            bct_code=action.bct_code, bct_name=action.bct_name, rationale=action.rationale, limits=action.limits,
            how_to_turn_off=HOW_TO_TURN_OFF["ar" if lang == Language.ar else "en"],
        )

    # ---------- dashboards: aggregates only, never individual data ----------

    @app.get("/dashboard/outcomes")
    def outcomes() -> dict[str, Any]:
        """Simulation results by arm and scenario (docs/results/dashboard.json, from sim.export_dashboard)."""
        if dashboard_path is None or not dashboard_path.exists():
            raise HTTPException(404, "no dashboard.json; run python -m sim.export_dashboard")
        return json.loads(dashboard_path.read_text(encoding="utf-8"))

    @app.get("/dashboard/employer", response_model=EmployerOut)
    def employer(org_id: str, x_org_key: Annotated[str | None, Header()] = None) -> EmployerOut:
        if not org_key or not x_org_key or not hmac.compare_digest(x_org_key, org_key):
            raise HTTPException(401, "missing or wrong X-Org-Key")
        members = store.org_user_ids(org_id)
        if len(members) < EMPLOYER_MIN_GROUP:  # same answer for an unknown org
            raise HTTPException(403, f"group too small to report (minimum {EMPLOYER_MIN_GROUP})")
        states = [engine.get_state(uid) for uid in members]
        barriers = Counter(
            e.payload["primary"] for uid in members for e in engine.events(uid) if e.type == EventType.checkin
        )
        return EmployerOut(
            org_id=org_id,
            group_size=len(members),
            active_share=sum(s.engagement_state == EngagementState.active for s in states) / len(states),
            average_habit_strength={
                b: sum(hs) / len(hs) for b in Behaviour
                if (hs := [s.habit_strength[b] for s in states if b in s.habit_strength])
            },
            top_barriers=[BarrierCount(barrier=b, count=n) for b, n in barriers.most_common(3)],
        )

    if not demo_mode:
        return app

    # ---------- demo only (DEMO_MODE=true): time travel and seeded personas ----------

    def advance_days(meta: UserMeta, days: int, pattern: str) -> tuple[UserMeta, list[DayRow]]:
        """Answer each day's open actions by the pattern (seeded per user and day), then move the clock a day."""
        rows = []
        for _ in range(days):
            today = open_day(meta)
            rng = random.Random(f"{meta.user_id}:{today.day}")
            outcomes = {}
            for s in today.actions:
                if s.action.id not in engine.get_state(meta.user_id).pending:
                    continue  # the user already answered it
                o = rng.choices(OUTCOMES, weights=PATTERNS[pattern])[0]
                outcomes[s.action.id] = o
                if o != "no_response":  # left open: the engine closes it as no_response when the next day opens
                    engine.record(Event(user_id=meta.user_id, day=today.day, type=EventType(o), action_id=s.action.id))
            state = engine.get_state(meta.user_id)
            rows.append(DayRow(day=today.day, outcomes=outcomes, engagement_state=state.engagement_state,
                               habit_strength=state.habit_strength, checkin_due=state.checkin_due))
            meta = meta.model_copy(update={"day_offset": meta.day_offset + 1})
            store.save_meta(meta)
        return meta, rows

    @app.post("/demo/users/{user_id}/advance", response_model=AdvanceOut)
    def advance(body: AdvanceIn, meta: Authed) -> AdvanceOut:
        if body.scenario:
            engine.set_context(meta.user_id, ContextFlag(body.scenario), True)
        meta, log = advance_days(meta, body.days, body.pattern)
        today = today_out(meta, open_day(meta))  # opens the new day, which closes the last one
        return AdvanceOut(state=_state_out(engine.get_state(meta.user_id)), today=today, log=log)

    @app.post("/demo/seed", response_model=SeedOut, status_code=201)
    def seed(x_demo_key: Annotated[str | None, Header()] = None) -> SeedOut:
        # No DEMO_KEY configured = seeding refused, never open.
        if not demo_key or not x_demo_key or not hmac.compare_digest(x_demo_key, demo_key):
            raise HTTPException(401, "missing or wrong X-Demo-Key")
        personas = []
        for name, data in DEMO_PERSONAS:
            out = onboard(OnboardIn.model_validate(data))
            advance_days(store.get_meta(out.user_id), PERSONA_WARMUP_DAYS, "good")
            personas.append(SeedPersona(name=name, user_id=out.user_id, token=out.token))
        org_id = f"demo-org-{secrets.token_hex(3)}"  # a fresh org per call, so repeated seeding never mixes orgs
        for i, data in enumerate(org_bodies(org_id)):
            out = onboard(OnboardIn.model_validate(data))
            advance_days(store.get_meta(out.user_id), ORG_DAYS, ORG_PATTERNS[i % len(ORG_PATTERNS)])
        return SeedOut(personas=personas, org_id=org_id, org_size=ORG_SIZE)

    return app
