"""Rebound API: a thin FastAPI wrapper. It calls Engine methods and never reimplements engine logic.

Auth is prototype-grade (see docs/ASSUMPTIONS.md, Limitations): POST /users returns a random bearer token once;
only its sha256 is stored, and every /users/{id}/* route requires it."""

import hashlib
import hmac
import json
import random
import re
import secrets
from collections import Counter
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Annotated, Any, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
from rebound_engine import config as engine_config
from rebound_engine.calendar import RAMADAN, day_context
from rebound_engine.engine import Engine
from rebound_engine.models import (
    Action,
    Barrier,
    Behaviour,
    CheckinResult,
    Condition,
    Conditions,
    ConsentGroup,
    ContextFlag,
    DayContext,
    DayLog,
    Encouragement,
    EngagementState,
    Event,
    EventType,
    History,
    Language,
    LocalizedText,
    OnboardingPayload,
    Preferences,
    ReadingLevel,
    ScreeningResult,
    Shift,
    TierChange,
    TierChangeKind,
    TodayResult,
    UserProfile,
    UserState,
)
from rebound_engine.plan import build_plan
from rebound_engine.policy import effective_flags, tier_cap
from rebound_engine.recipes import NOTE as RECIPE_NOTE
from rebound_engine.recipes import Recipe, load_recipes, suggest_recipe
from rebound_engine.safety import detect_red_flags, screening_flags
from rebound_engine.state import movement_start

from .auth import (
    DUMMY_HASH,
    LOGIN_MAX_FAILURES,
    LOGIN_WINDOW,
    SUGGEST_MAX_CALLS,
    SUGGEST_WINDOW,
    LoginIn,
    RecentTries,
    TokenOut,
    hash_password,
    verify_password,
)
from .community import CommunityEvent, Household, filter_events
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
from .llm_client import BarrierClassifier, RedFlagCheck, default_classifier, default_red_flag_check
from .messages import (
    ANCHOR_PHRASES,
    HOW_TO_TURN_OFF,
    PLAN_TEXT,
    onboarding_text,
    pick,
    render,
    render_encouragement,
    render_reason,
    render_rotation_note,
)
from .personal import Chat, recap_facts, recap_summary, suggest
from .store import UserMeta, open_store

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
    login: LoginIn | None = None  # optional username + password, so the account can be opened on another device

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


class RecipeOut(Recipe):
    note: str = RECIPE_NOTE  # shown with every recipe


class EncouragementOut(BaseModel):
    """A small pop-up: a real moment and its message (Task 05 Part C)."""

    moment: str
    message: str
    behaviour: Behaviour | None = None


class TodayOut(TodayResult):
    messages: list[str]  # message_keys rendered in the user's language
    recipes: dict[str, RecipeOut] = Field(default_factory=dict)  # action id -> suggestion, for cooking steps only
    encouragement: EncouragementOut | None = None  # today's moment, if one happened


class LevelChangeOut(BaseModel):
    day: int
    kind: TierChangeKind  # stepped_up | eased | shrunk_after_slip
    reason: str  # in the user's language and reading level
    barrier: Barrier | None = None  # the check-in barrier behind an "eased", if there was one


class GoalOut(BaseModel):
    """One active behaviour on the plan screen: where it is, why, and how far to the next level."""

    behaviour: Behaviour
    tier: int
    max_tier: int  # the safety cap for this person
    start_reason: str  # why it started at its first level
    good_days_to_next: int | None  # full completions still needed to step up; None at the top level
    last_change: LevelChangeOut | None = None
    today_note: str | None = None  # why today's step looks different (illness, Ramadan, heat, a check-in)


class PlanOut(BaseModel):
    """What the user sees of their plan. Queued behaviours are internal and never included."""

    behaviours: list[Behaviour]  # with daily actions, in order
    reasons: list[str]  # at most PLAN_REASONS_SHOWN, most important first
    all_reasons: list[str]  # the full list, for "See why"
    rotation_note: str | None = None  # only with more goals than daily actions: the third step changes each day
    goals: list[GoalOut] = Field(default_factory=list)  # one per active behaviour, in plan order


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
    encouragement: EncouragementOut | None = None  # set when this event created a moment (Task 05 Part C)


class CheckinIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    barriers: list[Barrier] = Field(default_factory=list)
    free_text: str | None = Field(default=None, max_length=500)


class CheckinOut(CheckinResult):
    message: str


class OnboardingTextOut(BaseModel):
    questions: dict[str, str]  # health-check question key (Screening field) -> text
    why_we_ask: dict[str, str]  # field group -> the "why we ask" line
    reading_level_examples: dict[str, str]  # "standard" / "simple" -> the same step at each level
    translation_note: str | None  # Arabic only: "draft translation, pending native review"
    follow_ups: list[dict[str, Any]]  # {id, fills, show_if: [{field, op, value}], text}; show only if all rules match


class SuggestIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: str = Field(min_length=1, max_length=1000)  # never stored or logged
    lang: Language = Language.en


class SuggestedAnswers(BaseModel):
    """Suggestions to pre-fill sign-up; the user confirms each. Never the health check."""

    goals: list[Behaviour]
    schedule_type: Literal["shift"] | None
    fasting_ramadan: bool | None
    household: Household | None
    caregiver: bool | None
    smoking_status: Literal["current"] | None
    managing: list[Condition]  # suggestions only: shown as pre-selected chips the user can untick
    anchor: str | None


class SuggestOut(BaseModel):
    red_flag: bool
    message: str | None  # the care message when red_flag is true
    suggestions: SuggestedAnswers | None
    follow_ups: list[str]  # follow-up question ids these answers unlock
    source: Literal["llm", "keywords"] | None


class RecapOut(BaseModel):
    days: int
    facts: dict[str, Any]  # computed by rules from the user's own events
    summary: str  # 2-3 sentences in the user's language and reading level
    written_by: Literal["llm", "template"]


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
    login: LoginIn | None = None  # add sign-in details to an account created without them (once)
    language: Language | None = None  # switches every text the API sends (steps, reasons, messages, recap)


class SettingsOut(BaseModel):
    preferences: Preferences
    consents: dict[ConsentGroup, bool]
    state: StateOut
    plan_summary: PlanOut  # re-built from the updated answers
    today: TodayOut  # today's steps and messages, in the (possibly new) language


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


def _encouragement_out(e: Encouragement | None, profile: UserProfile) -> EncouragementOut | None:
    if e is None:
        return None
    return EncouragementOut(moment=e.moment, message=render_encouragement(e.moment, profile, e.day),
                            behaviour=e.behaviour)


def _today_note(b: Behaviour, state: UserState) -> str | None:
    """Why today's step for `b` looks different, most important first."""
    flags = effective_flags(state)
    if ContextFlag.illness in flags:
        return "today.illness" if b == Behaviour.movement else "today.illness_gentle"
    if ContextFlag.ramadan in flags:
        return "today.ramadan"
    if ContextFlag.heat in flags and b == Behaviour.movement:
        return "today.heat"
    return "today.checkin" if state.last_barrier is not None else None


def _change_key(c: TierChange) -> str:
    if c.kind == "eased":
        return "change.eased_checkin" if c.barrier else "change.eased_missed"
    return f"change.{c.kind}"


def _goal_out(b: Behaviour, profile: UserProfile, state: UserState) -> GoalOut:
    def text(key: str) -> str:
        return pick(PLAN_TEXT[key], profile.basics.language, profile.preferences.reading_level)

    tier, top = state.current_tier[b], tier_cap(profile, b)
    start = movement_start(profile, screening_flags(profile))[1] if b == Behaviour.movement else "smallest_step"
    last = next((c for c in reversed(state.tier_changes) if c.behaviour == b), None)
    note = _today_note(b, state)
    return GoalOut(
        behaviour=b, tier=tier, max_tier=top, start_reason=text(f"start.{start}"),
        good_days_to_next=None if tier >= top else engine_config.STEP_UP_SUCCESSES - state.successes_at_tier[b],
        last_change=last and LevelChangeOut(day=last.day, kind=last.kind, reason=text(_change_key(last)),
                                            barrier=last.barrier),
        today_note=note and text(note),
    )


def _plan_out(profile: UserProfile, state: UserState) -> PlanOut:
    plan = build_plan(profile)
    rotating = len(profile.basics.goals) > engine_config.MAX_ACTIVE_BEHAVIOURS
    note = render_rotation_note(profile) if rotating else None
    # The rotation note says it already; don't repeat it as a reason.
    reasons = [render_reason(k, profile) for k in plan.reasons if not (note and k == "rotating")]
    return PlanOut(behaviours=plan.active, reasons=reasons[:PLAN_REASONS_SHOWN], all_reasons=reasons,
                   rotation_note=note,
                   goals=[_goal_out(b, profile, state) for b in plan.active if b in state.current_tier])


def with_anchor(action: Action, anchor: str | None) -> Action:
    """The user's own daily anchor in place of the generic phrase, in the title and its simple version. Wording
    only: the action, its safety flags, rationale and limits are unchanged."""
    if not anchor:
        return action
    thing = re.sub(r"^(after|بعد)\s+", "", anchor.strip(), flags=re.IGNORECASE)  # the title already says "after"

    def swap(text: LocalizedText, standard: bool) -> LocalizedText:
        en, ar = ("en", "ar") if standard else ("simple_en", "simple_ar")
        return text.model_copy(update={"en": text.en.replace(ANCHOR_PHRASES[en], thing),
                                       "ar": text.ar.replace(ANCHOR_PHRASES[ar], thing)})

    title, simple = swap(action.title, True), action.simple and swap(action.simple, False)
    if title == action.title and simple == action.simple:
        return action
    return action.model_copy(update={"title": title, "simple": simple})


def _leveled(action: Action, profile: UserProfile) -> Action:
    """The user's anchor, then at reading_level "simple" the plain-language title (Task 05 Part D)."""
    action = with_anchor(action, profile.preferences.anchor)
    if profile.preferences.reading_level == ReadingLevel.simple and action.simple:
        return action.model_copy(update={"title": action.simple})
    return action


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


def _env_chats() -> tuple[Chat | None, Chat | None]:
    """(JSON-mode chat for sign-up suggestions, plain chat for the recap) from .env, or (None, None)."""
    try:
        from llm import chat_from_env
        from llm.personal import TIMEOUT_S
    except ImportError:
        return None, None
    return chat_from_env(timeout=TIMEOUT_S, json_mode=True), chat_from_env(timeout=TIMEOUT_S)


# ---------- app ----------


def create_app(
    database_url: str = "sqlite:///rebound.db",
    frontend_url: str | None = None,
    demo_mode: bool = False,
    clock: Callable[[], datetime] | None = None,
    classifier: BarrierClassifier | None = None,
    dev_mode: bool = False,
    red_flag_check: RedFlagCheck | None = None,
    demo_key: str | None = None,
    org_key: str | None = None,
    dashboard_path: Path | None = None,
    llm_chat: Chat | None = None,
) -> FastAPI:
    store = open_store(database_url)
    # Optional LLM for sign-up suggestions and the recap (tests pass a fake). Without one: keywords and templates.
    suggest_chat, recap_chat = (llm_chat, llm_chat) if llm_chat else _env_chats()
    failed_logins = RecentTries(lambda: app.state.clock(), LOGIN_MAX_FAILURES, LOGIN_WINDOW)
    suggest_calls = RecentTries(lambda: app.state.clock(), SUGGEST_MAX_CALLS, SUGGEST_WINDOW)
    # user id -> (engine day, {(days, lang, level): RecapOut}, LLM already called that day)
    # shortcut: in memory, per process; lost on restart (then one more LLM call that day at most per process).
    recap_cache: dict[str, tuple[int | None, dict[tuple, RecapOut], bool]] = {}

    class UserCalendar:
        """Engine day -> the user's local date (onboarding day = day 1), then the offline calendar rules."""

        def day(self, profile: UserProfile, day: int) -> DayContext:
            meta = store.get_meta(profile.user_id)
            return day_context(profile, local_date_of(meta, day), meta.ramadan_start_shift, meta.ramadan_end_shift)

    # Rules mode, no risk model (hook off: ASSUMPTIONS.md, "Arm D"); calendar context on (the simulator has none).
    engine = Engine(store=store, calendar=UserCalendar())
    classifier = classifier or default_classifier()
    # Optional LLM second safety check (LLM_RED_FLAG_CHECK=true); it can only add a red flag.
    red_flag_check = red_flag_check or default_red_flag_check()

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
        # Unknown user and wrong token get the same answer, so user ids can't be probed.
        if creds is None or store.token_user(_hash(creds.credentials)) != user_id:
            raise HTTPException(401, "invalid or missing token", headers={"WWW-Authenticate": "Bearer"})
        try:
            return store.get_meta(user_id)
        except KeyError:
            raise HTTPException(401, "invalid or missing token", headers={"WWW-Authenticate": "Bearer"}) from None

    Authed = Annotated[UserMeta, Depends(authed)]

    def new_token(user_id: str) -> str:
        token = secrets.token_urlsafe(32)
        store.add_token(user_id, _hash(token))  # only the sha256 is stored
        return token

    def save_login(user_id: str, login: LoginIn) -> None:
        try:
            store.save_login(user_id, login.username.lower(), hash_password(login.password.get_secret_value()))
        except ValueError:
            raise HTTPException(409, "that username is taken") from None

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Any, exc: RequestValidationError) -> JSONResponse:
        # FastAPI echoes each bad value back as "input"; drop it so a rejected password is never returned.
        errors = [{k: v for k, v in e.items() if k != "input"} for e in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": jsonable_encoder(errors)})

    @app.post("/auth/login", response_model=TokenOut)
    def login(body: LoginIn) -> TokenOut:
        """A new token for this device; earlier tokens keep working. Same 401 for a wrong username or password."""
        username = body.username.lower()
        if failed_logins.blocked(username):
            raise HTTPException(429, "too many failed sign-ins; try again in 15 minutes")
        found = store.login(username)
        ok = verify_password(body.password.get_secret_value(), found[1] if found else DUMMY_HASH)
        if not (found and ok):
            failed_logins.add(username)
            raise HTTPException(401, "wrong username or password")
        failed_logins.clear(username)
        return TokenOut(user_id=found[0], token=new_token(found[0]))

    @app.post("/auth/logout", status_code=204)
    def logout(creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> Response:
        """Revokes the token this request was sent with (other devices stay signed in)."""
        if creds is None or store.token_user(_hash(creds.credentials)) is None:
            raise HTTPException(401, "invalid or missing token", headers={"WWW-Authenticate": "Bearer"})
        store.delete_token(_hash(creds.credentials))
        return Response(status_code=204)

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
        flags = effective_flags(engine.get_state(meta.user_id))
        recipes = {
            s.action.id: RecipeOut(**r.model_dump())
            for s in result.actions if (r := suggest_recipe(profile, s.action, result.day, flags))
        }
        actions = [s.model_copy(update={"action": _leveled(s.action, profile),
                                        "lighter": s.lighter and _leveled(s.lighter, profile)})
                   for s in result.actions]
        return TodayOut.model_validate({
            **result.model_dump(), "actions": [s.model_dump() for s in actions],
            "messages": [render(k, profile) for k in result.message_keys], "recipes": recipes,
            "encouragement": _encouragement_out(result.encouragement, profile),
        })

    @app.post("/users", status_code=201, response_model=OnboardOut)
    def onboard(body: OnboardIn) -> OnboardOut:
        # Answers for a group given without consent are dropped before the engine sees them.
        payload = OnboardingPayload.model_validate(
            {**body.model_dump(exclude={"timezone", "org_id", "login"}), **_withdrawn(body.consents)}
        )
        if body.login and store.login(body.login.username.lower()):
            raise HTTPException(409, "that username is taken")  # checked before anything is stored
        result = engine.onboard(payload)
        if body.login:
            try:
                save_login(result.user_id, body.login)
            except HTTPException:
                engine.delete_user(result.user_id)  # taken in the meantime: leave nothing behind
                raise
        token = new_token(result.user_id)
        meta = UserMeta(
            user_id=result.user_id, timezone=body.timezone, org_id=body.org_id,
            onboard_date=app.state.clock().astimezone(ZoneInfo(body.timezone)).date(),
        )
        store.save_meta(meta)
        today = today_out(meta, open_day(meta))
        return OnboardOut(
            user_id=result.user_id, token=token, screening=result.screening, red_flag=result.red_flag,
            state=_state_out(engine.get_state(result.user_id)), today=today,
            plan_summary=_plan_out(store.get_profile(result.user_id), engine.get_state(result.user_id)),
        )

    @app.get("/users/{user_id}/plan", response_model=PlanOut)
    def plan(meta: Authed) -> PlanOut:
        open_day(meta)  # today's notes and counts are about today
        return _plan_out(store.get_profile(meta.user_id), engine.get_state(meta.user_id))

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
        before = state.encouragement
        after = engine.record(event)
        fresh = after.encouragement if after.encouragement != before else None
        return StateResponse(state=_state_out(after),
                             encouragement=_encouragement_out(fresh, store.get_profile(meta.user_id)))

    def _llm_red_flag(meta: UserMeta, day: int, profile: UserProfile) -> CheckinOut:
        """The engine's keyword red-flag response, done in the API for a flag the LLM added (engine/ unchanged):
        stop coaching, log a red_flag event, return the care message."""
        state = engine.get_state(meta.user_id)
        state.red_flag = True
        state.context_flags.add(ContextFlag.paused)
        state.checkin_due = False
        store.append_event(Event(user_id=meta.user_id, day=day, type=EventType.red_flag, payload={"source": "llm"}))
        store.save_state(state)
        store.save_meta(meta.model_copy(update={"last_checkin_day": day}))
        return CheckinOut(barrier=None, adjusted_actions=[], message_key="seek_care", red_flag=True,
                          message=render("seek_care", profile))

    @app.post("/users/{user_id}/checkin", response_model=CheckinOut)
    def checkin(body: CheckinIn, meta: Authed) -> CheckinOut:
        open_day(meta)  # check in on today's state, or a lapse found later would ask again the same day
        day = engine.get_state(meta.user_id).day
        profile = store.get_profile(meta.user_id)
        lang = profile.basics.language.value
        red_flag_text = bool(body.free_text) and detect_red_flags(body.free_text)
        # Optional LLM second check, only on text the keywords didn't flag (so red-flag text never reaches it).
        llm_flag = bool(body.free_text) and not red_flag_text and red_flag_check is not None             and red_flag_check(body.free_text, lang)
        if meta.last_checkin_day == day and not (red_flag_text or llm_flag):  # a red flag always gets through
            raise HTTPException(409, "already checked in today")
        if llm_flag:
            return _llm_red_flag(meta, day, profile)
        barriers = list(body.barriers)  # buttons decide; free text only fills in when none were pressed
        # The engine's red-flag keywords run first (inside checkin); red-flag text never goes to the classifier.
        if not barriers and body.free_text and not red_flag_text:
            guess = classifier.classify_barrier(body.free_text, lang)
            barriers = [guess] if guess else []
        result = engine.checkin(meta.user_id, barriers, free_text=body.free_text, replace_pending=True)
        store.save_meta(meta.model_copy(update={"last_checkin_day": day}))
        adjusted = [_leveled(a, profile).model_dump() for a in result.adjusted_actions]
        return CheckinOut.model_validate({**result.model_dump(), "adjusted_actions": adjusted,
                                          "message": render(result.message_key, profile)})

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
        if body.login is not None:  # last check before anything changes
            if store.username(uid) is not None:
                raise HTTPException(409, "this account already has sign-in details")
            save_login(uid, body.login)
        consents = {**profile.consents, **(body.consents or {})}
        update: dict[str, Any] = {"preferences": prefs, "consents": consents}
        if body.conditions is not None:
            update["conditions"] = body.conditions
        basics: dict[str, Any] = {}
        if body.shifts is not None:  # takes effect when the next day opens
            basics["shifts"] = body.shifts or None
        if body.language is not None:  # applies at once: every text is rendered per request
            basics["language"] = body.language
        if basics:
            update["basics"] = profile.basics.model_copy(update=basics)
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
                           state=_state_out(engine.get_state(uid)),
                           plan_summary=_plan_out(profile, engine.get_state(uid)),
                           today=today_out(meta, open_day(meta)))

    @app.get("/users/{user_id}/export", response_model=ExportOut)
    def export(meta: Authed) -> ExportOut:
        open_day(meta)
        uid = meta.user_id
        return ExportOut(
            account={**meta.model_dump(), "username": store.username(uid)}, profile=store.get_profile(uid),
            state=engine.get_state(uid), events=engine.events(uid),
        )

    @app.delete("/users/{user_id}", status_code=204)
    def delete_user(meta: Authed) -> Response:
        engine.delete_user(meta.user_id)  # SQLiteStore also removes user_meta
        recap_cache.pop(meta.user_id, None)
        return Response(status_code=204)

    @app.get("/users/{user_id}/community/events", response_model=list[CommunityEvent])
    def community_events(
        meta: Authed, household: Household | None = None, behaviour: Behaviour | None = None,
        city: str | None = Query(default=None, max_length=40),
    ) -> list[CommunityEvent]:
        """Read-only events that fit the user (goals, women-only spaces, mobility, language). `household` and `city`
        are request filters only: no location tracking, nothing stored."""
        return filter_events(store.get_profile(meta.user_id), household=household, behaviour=behaviour, city=city)

    @app.get("/recipes", response_model=list[RecipeOut])
    def recipes(tag: str | None = None) -> list[RecipeOut]:
        """The curated recipe set (general content, no auth), optionally filtered by one tag."""
        return [RecipeOut(**r.model_dump()) for r in load_recipes() if tag is None or tag in r.tags]

    @app.get("/recipes/{recipe_id}", response_model=RecipeOut)
    def recipe(recipe_id: str) -> RecipeOut:
        found = next((r for r in load_recipes() if r.id == recipe_id), None)
        if found is None:
            raise HTTPException(404, "unknown recipe")
        return RecipeOut(**found.model_dump())

    @app.get("/actions/{action_id}/explain", response_model=ExplainOut)
    def explain(action_id: str, lang: Language = Language.en,
                reading_level: ReadingLevel = ReadingLevel.standard) -> ExplainOut:
        action = next((a for a in engine.library if a.id == action_id), None)
        if action is None:
            raise HTTPException(404, "unknown action")
        return ExplainOut(
            bct_code=action.bct_code, bct_name=action.bct_name, rationale=action.rationale, limits=action.limits,
            how_to_turn_off=pick(HOW_TO_TURN_OFF, lang, reading_level),
        )

    @app.get("/content/onboarding", response_model=OnboardingTextOut)
    def onboarding_content(lang: Language = Language.en,
                           reading_level: ReadingLevel = ReadingLevel.standard) -> OnboardingTextOut:
        """Health-check questions, "why we ask" lines, a reading-level example and the follow-up question bank,
        before the user exists."""
        return OnboardingTextOut(**onboarding_text(lang, reading_level))

    @app.post("/content/onboarding/suggest", response_model=SuggestOut)
    def onboarding_suggest(body: SuggestIn, request: Request) -> SuggestOut:
        """Optional: suggested sign-up answers from a few sentences, for the user to confirm. Red-flag text gets the
        care message and never reaches the LLM. The text is not stored or logged; the health check is never
        suggested. Open route, so at most SUGGEST_MAX_CALLS per IP per SUGGEST_WINDOW (429 after that)."""
        # shortcut: X-Forwarded-For can be spoofed, and the limit is per process; fine for the pilot, not abuse-proof.
        forwarded = request.headers.get("x-forwarded-for", "")
        ip = forwarded.split(",")[0].strip() or (request.client.host if request.client else "unknown")
        if suggest_calls.blocked(ip):
            raise HTTPException(429, "too many requests; try again in an hour, or fill in the questions yourself")
        suggest_calls.add(ip)
        return SuggestOut(**suggest(body.text, body.lang, suggest_chat))

    @app.get("/users/{user_id}/recap", response_model=RecapOut)
    def recap(meta: Authed, days: int = Query(default=7, ge=1, le=engine_config.HISTORY_KEEP_DAYS)) -> RecapOut:
        """Facts from the user's own events (rules), plus 2-3 friendly sentences. Not shown after a safety concern."""
        open_day(meta)
        state = engine.get_state(meta.user_id)
        if state.red_flag:
            raise HTTPException(409, "no recap while coaching is paused after a safety concern")
        profile = store.get_profile(meta.user_id)
        lang, level = profile.basics.language, profile.preferences.reading_level
        # One result per user per engine day (and per days/language/level), and at most one LLM call a day.
        cached_day, results, llm_tried = recap_cache.get(meta.user_id, (None, {}, False))
        if cached_day != state.day:
            results, llm_tried = {}, False
        key = (days, lang, level)
        if key not in results:
            facts = recap_facts(state, engine.events(meta.user_id), days)
            summary, written_by = recap_summary(facts, lang, level, None if llm_tried else recap_chat)
            llm_tried = llm_tried or recap_chat is not None
            results[key] = RecapOut(days=days, facts=facts, summary=summary, written_by=written_by)
        recap_cache[meta.user_id] = (state.day, results, llm_tried)
        return results[key]

    @app.get("/health")
    def health() -> dict[str, bool]:
        """Wake-up check for the frontend (free hosting sleeps when idle). No auth, no database work."""
        return {"ok": True}

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
        with store.batch():  # every day's rows in one transaction
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
        # One batch per person: their rows are written in one transaction with bulk inserts (fast on Postgres).
        for name, data in DEMO_PERSONAS:
            with store.batch():
                out = onboard(OnboardIn.model_validate(data))
                advance_days(store.get_meta(out.user_id), PERSONA_WARMUP_DAYS, "good")
            personas.append(SeedPersona(name=name, user_id=out.user_id, token=out.token))
        org_id = f"demo-org-{secrets.token_hex(3)}"  # a fresh org per call, so repeated seeding never mixes orgs
        for i, data in enumerate(org_bodies(org_id)):
            with store.batch():
                out = onboard(OnboardIn.model_validate(data))
                advance_days(store.get_meta(out.user_id), ORG_DAYS, ORG_PATTERNS[i % len(ORG_PATTERNS)])
        return SeedOut(personas=personas, org_id=org_id, org_size=ORG_SIZE)

    return app
