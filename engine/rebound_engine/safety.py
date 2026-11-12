"""Safety layer: screening rules, context filters and red-flag detection. Runs before any personalisation."""

import re
from collections.abc import Iterable

from . import config
from .models import (
    Action,
    ActionSetting,
    Behaviour,
    ContextFlag,
    MobilityLimitation,
    PregnancyAnswer,
    ScreeningResult,
    UserProfile,
)

SCREENING_QUESTIONS = (
    "heart_condition_or_high_bp",
    "chest_pain",
    "dizziness_or_fainting",
    "other_long_term_condition",
    "prescribed_medication",
    "bone_joint_muscle_problem",
    "supervised_exercise_only",
)
SEE_DOCTOR_QUESTIONS = ("chest_pain", "dizziness_or_fainting")


def screening_flags(profile: UserProfile) -> ScreeningResult:
    s = profile.screening
    positive = [q for q in SCREENING_QUESTIONS if getattr(s, q)]
    see_doctor = any(q in positive for q in SEE_DOCTOR_QUESTIONS)
    if see_doctor:
        cap = config.GENTLE_TIER_CAP
    elif positive:
        cap = config.SCREENING_TIER_CAP
    else:
        cap = config.MAX_TIER
    return ScreeningResult(
        flag=bool(positive),
        positive=positive,
        movement_tier_cap=cap,
        see_doctor=see_doctor,
        # "prefer not to say" gets the pregnancy-safe subset too (safer default).
        pregnancy_safe_only=s.pregnant in (PregnancyAnswer.yes, PregnancyAnswer.prefer_not_to_say),
        seated_only=s.mobility_limitation != MobilityLimitation.none,
    )


def context_filter(
    actions: Iterable[Action],
    context_flags: set[ContextFlag],
    hour: int,
    screening: ScreeningResult | None = None,
) -> list[Action]:
    """Drop actions that context (heat, fasting, illness) or screening (tier cap, pregnancy, mobility) rule out."""
    in_heat = (
        ContextFlag.heat in context_flags and config.HEAT_START_HOUR <= hour < config.HEAT_END_HOUR
    )

    def allowed(a: Action) -> bool:
        movement = a.behaviour == Behaviour.movement
        if in_heat and a.setting == ActionSetting.outdoor:
            return False
        if ContextFlag.ramadan in context_flags and not a.fasting_safe:
            return False
        if ContextFlag.illness in context_flags and movement:
            return False
        if screening is None:
            return True
        if movement and a.tier > screening.movement_tier_cap:
            return False
        if screening.pregnancy_safe_only and not a.pregnancy_safe:
            return False
        if screening.seated_only and movement and not a.seated:
            return False
        return not set(a.contraindications) & set(screening.positive)

    return [a for a in actions if allowed(a)]


# ---------- Red flags (keyword list; the LLM check is added in Task 03) ----------

# Substring match after normalisation, so "fainted" matches "faint". False positives are acceptable here.
_RED_FLAG_PHRASES = (
    # chest pain
    "chest pain", "pain in my chest", "chest hurts", "chest tight", "chest pressure",
    "ألم في الصدر", "ألم بالصدر", "ألم صدري", "وجع في الصدر", "وجع بصدري", "ضيق في الصدر",
    # fainting
    "faint", "passed out", "blacked out", "lost consciousness",
    "إغماء", "أغمي علي", "فقدت الوعي",
    # severe breathlessness
    "can't breathe", "cannot breathe", "couldn't breathe", "struggling to breathe",
    "severe breathlessness", "short of breath", "gasping",
    "لا أستطيع التنفس", "ما أقدر أتنفس", "صعوبة شديدة في التنفس", "ضيق تنفس شديد",
    # self-harm
    "kill myself", "killing myself", "suicide", "suicidal", "end my life", "hurt myself",
    "harm myself", "self-harm", "self harm", "want to die", "don't want to live", "better off dead",
    "انتحار", "أنتحر", "أقتل نفسي", "أنهي حياتي", "أؤذي نفسي", "إيذاء النفس", "أريد أن أموت",
    "أبي أموت", "ابغى اموت",
    # disordered eating
    "starve myself", "starving myself", "myself vomit", "myself sick", "myself throw up",
    "throw up after eating", "purging", "laxatives", "binge eating", "stopped eating",
    "أجوع نفسي", "أتقيأ بعد الأكل", "أستفرغ بعد الأكل", "ملينات", "توقفت عن الأكل",
)

_AR_MARKS = re.compile("[ً-ْـ]")  # harakat + tatweel
_ALEF = re.compile("[أإآ]")
_NON_WORD = re.compile(r"[^\w\s]")


def _normalise(text: str) -> str:
    t = _AR_MARKS.sub("", text.lower())
    t = _ALEF.sub("ا", t).replace("ى", "ي").replace("ة", "ه")
    return " ".join(_NON_WORD.sub(" ", t).split())


_NORMALISED_PHRASES = tuple(_normalise(p) for p in _RED_FLAG_PHRASES)


def detect_red_flags(text: str) -> bool:
    t = _normalise(text)
    return any(p in t for p in _NORMALISED_PHRASES)
