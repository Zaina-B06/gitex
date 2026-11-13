"""Pydantic models. Onboarding fields are grouped as in AGENTS.md §4 so the UI can show them as steps."""

from datetime import datetime, time
from enum import StrEnum
from typing import Any

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
    notification_window: TimeRange | None = None
    quiet_hours: TimeRange | None = None
    channel: Channel = Channel.app
    accessibility: list[Accessibility] = Field(default_factory=list)


class OnboardingPayload(_Input):
    basics: Basics
    body: Body | None = None
    screening: Screening
    baseline: Baseline
    history: History = Field(default_factory=History)
    preferences: Preferences = Field(default_factory=Preferences)
    consents: dict[ConsentGroup, bool] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _pregnancy_only_for_female(self) -> "OnboardingPayload":
        if self.basics.sex != Sex.female and self.screening.pregnant is not None:
            raise ValueError("pregnant is only asked when sex is female")
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


class Context(BaseModel):
    flags: set[ContextFlag] = Field(default_factory=set)
    hour: int = Field(ge=0, le=23)


# ---------- Results ----------


class ScreeningResult(BaseModel):
    flag: bool
    positive: list[str]  # screening questions answered "yes"
    movement_tier_cap: int
    see_doctor: bool  # chest pain or dizziness/fainting: also start with sleep/gentle only
    pregnancy_safe_only: bool
    seated_only: bool


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


class TodayResult(BaseModel):
    day: int
    actions: list[ScheduledAction]  # one per goal, movement first
    message_keys: list[str]
    channel: Channel
    checkin_due: bool
    state_summary: StateSummary


class CheckinResult(BaseModel):
    barrier: Barrier | None
    adjusted_actions: list[Action]
    message_key: str
    red_flag: bool
