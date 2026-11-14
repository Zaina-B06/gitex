"""Pydantic models. Onboarding fields are grouped as in AGENTS.md §4 so the UI can show them as steps."""

from datetime import date, datetime, time
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ---------- Enums ----------


class Language(StrEnum):
    en = "en"
    ar = "ar"


class Sex(StrEnum):
    female = "female"
    male = "male"
    prefer_not_to_say = "prefer_not_to_say"


class Behaviour(StrEnum):
    movement = "movement"
    sleep = "sleep"
    # Task 05 Part B. The lapse-risk features stay on movement and sleep (risk/features.py RISK_BEHAVIOURS).
    nutrition = "nutrition"
    smoking = "smoking"
    recovery = "recovery"


class ScheduleType(StrEnum):
    office = "office"
    shift = "shift"
    outdoor_manual = "outdoor_manual"
    home_caregiver = "home_caregiver"
    student = "student"
    other = "other"


class PastHelper(StrEnum):
    small_steps = "small_steps"
    reminders = "reminders"
    buddy = "buddy"
    tracking = "tracking"
    rewards = "rewards"
    routine_anchor = "routine_anchor"
    other = "other"


class Barrier(StrEnum):
    time = "time"
    energy_fatigue = "energy_fatigue"
    illness_pain = "illness_pain"
    schedule_change = "schedule_change"
    environment = "environment"
    low_motivation = "low_motivation"
    social_family = "social_family"
    forgot = "forgot"
    other = "other"
    # Task 05 Part B (not used by the simulator or the risk features)
    craving = "craving"
    stress = "stress"
    others_smoking = "others_smoking"
    no_healthy_food_nearby = "no_healthy_food_nearby"


class SmokingStatus(StrEnum):
    never = "never"
    former = "former"
    current = "current"
    prefer_not_to_say = "prefer_not_to_say"


class PregnancyAnswer(StrEnum):
    yes = "yes"
    no = "no"
    prefer_not_to_say = "prefer_not_to_say"


class MobilityLimitation(StrEnum):
    none = "none"
    some = "some"
    mobility_aid = "mobility_aid"  # uses a mobility aid or wheelchair


class PlaceSetting(StrEnum):
    indoor = "indoor"
    outdoor = "outdoor"
    either = "either"


class SocialPreference(StrEnum):
    alone = "alone"
    with_others = "with_others"
    either = "either"


class SpacePreference(StrEnum):
    home = "home"
    women_only_spaces = "women_only_spaces"
    any = "any"


class Channel(StrEnum):
    app = "app"
    whatsapp_style = "whatsapp_style"
    voice_note = "voice_note"


class Accessibility(StrEnum):
    large_text = "large_text"
    high_contrast = "high_contrast"
    screen_reader = "screen_reader"


class ConsentGroup(StrEnum):
    body = "body"
    screening = "screening"
    history = "history"
    preferences = "preferences"
    conditions = "conditions"


class Condition(StrEnum):
    """ "Anything you're managing?" chips (Task 05). Pregnancy and smoking come from their existing fields."""

    diabetes = "diabetes"
    high_blood_pressure = "high_blood_pressure"
    back_or_joint_pain = "back_or_joint_pain"
    stress = "stress"
    recovering_from_illness_or_injury = "recovering_from_illness_or_injury"


PlanBehaviour = Behaviour  # Part A's separate enum, merged into Behaviour in Part B


class ActionSetting(StrEnum):
    indoor = "indoor"
    outdoor = "outdoor"
    any = "any"


class EngagementState(StrEnum):
    active = "active"
    drifting = "drifting"
    lapsed = "lapsed"
    recovering = "recovering"


class ContextFlag(StrEnum):
    ramadan = "ramadan"
    heat = "heat"
    shift_pattern = "shift_pattern"
    travel = "travel"
    illness = "illness"
    paused = "paused"
    eid = "eid"  # set by the calendar only (Task 05 A2): rest-friendly days


class Weekday(StrEnum):
    mon = "mon"
    tue = "tue"
    wed = "wed"
    thu = "thu"
    fri = "fri"
    sat = "sat"
    sun = "sun"


class TimeWindow(StrEnum):
    morning = "morning"
    afternoon = "afternoon"
    evening = "evening"


class EventType(StrEnum):
    action_shown = "action_shown"
    completed = "completed"
    partial = "partial"
    skipped = "skipped"
    no_response = "no_response"
    checkin = "checkin"
    checkin_sent = "checkin_sent"
    pause = "pause"
    screening_flag = "screening_flag"
    red_flag = "red_flag"
    context_change = "context_change"
    risk_alert = "risk_alert"
    encouragement = "encouragement"  # Task 05 Part C: payload {moment, behaviour?}


class DayOutcome(StrEnum):
    completed = "completed"
    partial = "partial"
    skipped = "skipped"
    no_response = "no_response"
    paused = "paused"  # doesn't count toward H or engagement
    illness = "illness"  # doesn't count toward H or engagement


# ---------- Onboarding (input: reject unknown fields) ----------


class _Input(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TimeRange(_Input):
    start: time
    end: time  # may be earlier than start (crosses midnight)


class Shift(_Input):
    """One line of a weekly shift pattern, e.g. Sun-Thu 22:00-06:00 (end before start = overnight)."""

    days: list[Weekday] = Field(min_length=1)  # the day each shift starts
    start: time
    end: time


class Basics(_Input):
    language: Language
    age_years: int = Field(ge=18, le=100)
    sex: Sex
    goals: list[Behaviour] = Field(min_length=1)
    schedule_type: ScheduleType
    usual_wake_time: time
    usual_sleep_time: time
    work_hours: list[TimeRange] = Field(default_factory=list)
    # Shift workers: one list of work ranges per day of their rotation.
    shift_cycle: list[list[TimeRange]] | None = None
    # Real shift timings (Task 05 A2), editable in settings. Used only with a calendar (the API), never in the sim.
    shifts: list[Shift] | None = None

    @field_validator("goals")
    @classmethod
    def _unique_goals(cls, v: list[Behaviour]) -> list[Behaviour]:
        if len(set(v)) != len(v):
            raise ValueError("goals must not repeat")
        return v


class Body(_Input):
    """Used only to set a safe starting intensity, never shown as a target."""

    height_cm: float | None = Field(default=None, ge=100, le=250)
    weight_kg: float | None = Field(default=None, ge=30, le=300)


class Screening(_Input):
    """PAR-Q+-style yes/no questions (paraphrased), plus pregnancy and mobility."""

    heart_condition_or_high_bp: bool
    chest_pain: bool
    dizziness_or_fainting: bool
    other_long_term_condition: bool
    prescribed_medication: bool
    bone_joint_muscle_problem: bool
    supervised_exercise_only: bool
    pregnant: PregnancyAnswer | None = None  # only asked if sex = female
    mobility_limitation: MobilityLimitation


class Baseline(_Input):
    active_days_per_week: int = Field(ge=0, le=7)
    typical_daily_steps: int | None = Field(default=None, ge=0, le=100_000)
    sleep_hours_typical: float = Field(ge=0, le=24)
    sleep_quality_self: int = Field(ge=1, le=5)


class History(_Input):
    tried_before: bool | None = None
    past_helpers: list[PastHelper] = Field(default_factory=list)
    past_stop_reasons: list[Barrier] = Field(default_factory=list)
    smoking_status: SmokingStatus | None = None
    # Shown back on low_motivation (AGENTS.md §6.3); red-flag checked at onboarding.
    motivation_reason: str | None = Field(default=None, max_length=200)


class Preferences(_Input):
    setting: PlaceSetting = PlaceSetting.either
    social: SocialPreference = SocialPreference.either
    space_preference: SpacePreference = SpacePreference.any
    fasting_ramadan: bool = False
    iftar_time: time | None = None  # overrides the Abu Dhabi sunset table (Task 05 A2)
    notification_window: TimeRange | None = None
    quiet_hours: TimeRange | None = None
    channel: Channel = Channel.app
    accessibility: list[Accessibility] = Field(default_factory=list)
    encouragement: bool = True  # Task 05 Part C: small "well done" moments; users can turn them off


class Conditions(_Input):
    """Optional and sensitive. No free-text medical history."""

    managing: list[Condition] = Field(default_factory=list)

    @field_validator("managing")
    @classmethod
    def _unique(cls, v: list[Condition]) -> list[Condition]:
        if len(set(v)) != len(v):
            raise ValueError("conditions must not repeat")
        return v


class OnboardingPayload(_Input):
    basics: Basics
    body: Body | None = None
    screening: Screening
    baseline: Baseline
    history: History = Field(default_factory=History)
    conditions: Conditions = Field(default_factory=Conditions)
    preferences: Preferences = Field(default_factory=Preferences)
    consents: dict[ConsentGroup, bool] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _pregnancy_only_for_female(self) -> "OnboardingPayload":
        if self.basics.sex != Sex.female and self.screening.pregnant is not None:
            raise ValueError("pregnant is only asked when sex is female")
        if Behaviour.smoking in self.basics.goals and self.history.smoking_status != SmokingStatus.current:
            raise ValueError("the smoking goal is for people who currently smoke")
        return self


class UserProfile(OnboardingPayload):
    user_id: str
    created_at: datetime


# ---------- Actions ----------


class LocalizedText(BaseModel):
    en: str = Field(min_length=1)
    ar: str = Field(min_length=1)
    ar_reviewed: bool = False


class Action(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    behaviour: Behaviour
    tier: int = Field(ge=1, le=4)
    title: LocalizedText
    bct_code: str = Field(pattern=r"^\d+\.\d+$")
    bct_name: str
    rationale: str
    limits: str
    setting: ActionSetting
    fasting_safe: bool
    low_energy_ok: bool
    pregnancy_safe: bool
    seated: bool = False
    seated_variant_id: str | None = None
    contraindications: list[str] = Field(default_factory=list)  # screening question names
    duration_min: int = Field(gt=0)
    # Task 05 Part B: plain-language variant, icon key (actions.ICONS), and tags the rules prefer (e.g. "substitution",
    # "cue_avoidance", "no_shopping", "ramadan_only", "cooking", "diabetes", "not_for_diabetes", "after_illness").
    simple: LocalizedText | None = None
    icon: str | None = None
    tags: list[str] = Field(default_factory=list)


# ---------- Events and state ----------


class Event(BaseModel):
    user_id: str
    day: int = Field(ge=0)
    type: EventType
    action_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class DayLog(BaseModel):
    day: int
    behaviour: Behaviour | None = None
    action_id: str | None = None
    outcome: DayOutcome


Moment = Literal[
    "first_day_done", "three_good_days", "comeback", "habit_strength_50", "first_week_done", "tried_something_new",
]


class Encouragement(BaseModel):
    """Task 05 Part C: a real moment worth a small "well done". Never a count, never a streak."""

    moment: Moment
    day: int
    behaviour: Behaviour | None = None  # for habit_strength_50 and tried_something_new


class DayTimes(BaseModel):
    """One day's timings from real shifts (Task 05 A2). Hours 0-23; busy ranges are [start, end), may wrap."""

    wake: int
    sleep: int
    sleep_prompt: int | None = None  # after a night shift: wind-down as the shift ends, before their sleep
    busy: list[tuple[int, int]] = Field(default_factory=list)  # work, and sleep after a night shift


class DayContext(BaseModel):
    """What the calendar works out for one user-day (Task 05 A2)."""

    local_date: date
    flags: set[ContextFlag] = Field(default_factory=set)
    iftar_hour: int | None = None  # set during Ramadan for fasting users
    day_times: DayTimes | None = None


class UserState(BaseModel):
    user_id: str
    day: int = 0
    habit_strength: dict[Behaviour, float]
    current_tier: dict[Behaviour, int]
    successes_at_tier: dict[Behaviour, int]  # consecutive full completions at the current tier
    fails_at_tier: dict[Behaviour, int]  # consecutive skipped/no_response at the current tier
    engagement_state: EngagementState = EngagementState.active
    checkin_due: bool = False
    context_flags: set[ContextFlag] = Field(default_factory=set)
    bandit_params: dict[str, list[float]] = Field(default_factory=dict)  # "action@window" -> [alpha, beta]
    last_barrier: Barrier | None = None  # cleared by the next full completion
    shown_today: list[tuple[str, TimeWindow, int]] = Field(default_factory=list)  # (action id, window, hour)
    pending: list[str] = Field(default_factory=list)  # shown on `day`, no outcome yet
    time_window: TimeWindow = TimeWindow.morning  # rules mode: movement window; sleep is always evening
    channel: Channel = Channel.app
    prefer_indoor: bool = False
    red_flag: bool = False
    history: list[DayLog] = Field(default_factory=list)
    # H at the start of each recent day, oldest first (observation only; used by lapse-risk features).
    h_daily: dict[Behaviour, list[float]] = Field(default_factory=dict)
    # Lapse-risk hook (Task 02b): today's lighter offers (shown action id -> lighter action id) and message pacing.
    lighter_offers: dict[str, str] = Field(default_factory=dict)
    last_risk: float | None = None
    last_risk_reasons: list[str] = Field(default_factory=list)
    last_risk_checkin_day: int = -999
    last_checkin_sent_day: int = -999  # at most one check-in message per day, of any kind
    # Task 05 A2, set from the calendar when a day opens (only when the engine has one). Explicit flags stay in
    # context_flags; the calendar never removes them.
    auto_flags: set[ContextFlag] = Field(default_factory=set)
    iftar_hour: int | None = None
    day_times: DayTimes | None = None
    # Task 05 Part B: goals in plan order (most important first) and a day counter that rotates extra goals when
    # there are more than MAX_ACTIVE_BEHAVIOURS. Empty order = Behaviour order (movement, sleep, …).
    order: list[Behaviour] = Field(default_factory=list)
    rotation: int = 0
    # Task 05 Part C (observation only: nothing here changes which actions are chosen)
    encouragement: Encouragement | None = None  # the latest one; shown on its own day
    moments: dict[str, int] = Field(default_factory=dict)  # moment key -> day it last fired
    done_actions: set[str] = Field(default_factory=set)  # action ids completed at least once
    slip_day: int = -1  # last day the state entered drifting or lapsed


class Context(BaseModel):
    flags: set[ContextFlag] = Field(default_factory=set)
    hour: int = Field(ge=0, le=23)


# ---------- Results ----------


class ScreeningResult(BaseModel):
    flag: bool  # any "yes", or a condition chip that maps onto a health-check question
    positive: list[str]  # screening questions answered "yes"
    movement_tier_cap: int
    see_doctor: bool  # chest pain or dizziness/fainting: also start with sleep/gentle only
    pregnancy_safe_only: bool
    seated_only: bool
    # Questions whose rules apply: `positive` plus the equivalents of condition chips (e.g. high blood pressure -> Q1).
    contraindicated: list[str] = Field(default_factory=list)


class PlanSummary(BaseModel):
    """What the engine will do for this person and why (Task 05 Part A). Derived from the profile alone."""

    active: list[Behaviour]  # behaviours with daily actions, in order (at most MAX_ACTIVE_BEHAVIOURS)
    queued: list[PlanBehaviour]  # internal until they have actions (Part B): never shown to users
    queued_reasons: list[str]  # internal, same rule
    start_tiers: dict[Behaviour, int]
    movement_tier_cap: int
    reasons: list[str]  # user-facing reason keys, most important first (the API shows at most 3)


class StateSummary(BaseModel):
    habit_strength: dict[Behaviour, float]
    engagement_state: EngagementState
    tiers: dict[Behaviour, int]


class OnboardResult(BaseModel):
    user_id: str
    state: UserState
    screening: ScreeningResult
    red_flag: bool = False  # motivation_reason contained red-flag language


class ScheduledAction(BaseModel):
    action: Action
    time_window: TimeWindow
    hour: int  # prompt hour; never inside quiet hours unless every window is
    explanation_id: str  # GET /actions/{id}/explain
    lighter: Action | None = None  # "Busy week ahead? Here's a lighter version" (risk hook), same safety filter


class TodayResult(BaseModel):
    day: int
    actions: list[ScheduledAction]  # one per goal, movement first
    message_keys: list[str]
    channel: Channel
    checkin_due: bool
    state_summary: StateSummary
    risk: float | None = None  # lapse risk for the next 7 days, if a risk model is loaded
    risk_reasons: list[str] = Field(default_factory=list)  # plain-language, only when an alert fired
    encouragement: Encouragement | None = None  # today's, if one fired (Task 05 Part C)


class CheckinResult(BaseModel):
    barrier: Barrier | None
    adjusted_actions: list[Action]
    message_key: str
    red_flag: bool
