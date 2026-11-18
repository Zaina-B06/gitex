"""Rules around the optional LLM helpers (18 Nov): AI-assisted sign-up and the weekly recap.

The LLM is never trusted: sign-up suggestions are validated against our enums (anything else is dropped), and a
recap the LLM writes must pass every check below or the fixed template is used. Sign-up text is never stored or
logged, red-flag text never reaches the LLM, and the health check is never suggested."""

import logging
import re
from collections import Counter
from collections.abc import Callable
from typing import Any

from rebound_engine.models import (
    Behaviour,
    Condition,
    DayOutcome,
    Event,
    EventType,
    Household,
    Language,
    ReadingLevel,
    UserState,
)
from rebound_engine.safety import detect_red_flags

from .messages import FOLLOW_UPS, MESSAGES, RECAP, pick, show_follow_up
from .readability import fk_grade

log = logging.getLogger("rebound.personal")
Chat = Callable[[list[dict[str, str]]], str]
LLM_ERRORS = (OSError, ValueError, KeyError, TypeError, RuntimeError)  # network, timeout, odd reply, no provider

ANCHOR_MAX = 40
MOSTLY_DONE, MOSTLY_MISSED = 2 / 3, 1 / 3  # share of counted days done (docs/ASSUMPTIONS.md, "Weekly recap")
RECAP_MAX_CHARS, RECAP_MAX_EXTRAS = 400, 2
FK_MAX_GRADE = 6

# ---------- AI-assisted sign-up ----------

# Keyword fallback (no key, or the LLM failed): regexes, EN + AR (Arabic unreviewed). Order matters for household.
_GOALS = {
    Behaviour.movement: r"\b(walk\w*|exercis\w*|move|moving|active|gym|fitness|sport)\b|مشي|رياضة|حركة",
    Behaviour.sleep: r"\b(sleep\w*|insomnia)\b|نوم|أنام",
    Behaviour.nutrition: r"\b(eat\w*|food|diet|meals?|cook\w*)\b|أكل|طعام|وجبات",
    Behaviour.smoking: r"smok|cigarette|تدخين|سجائر|أدخن",
    Behaviour.recovery: r"\b(stress\w*|relax\w*|rest|burn(ed|t)? out)\b|توتر|راحة",
}
_SMOKER = r"\bi smoke\b|\bsmoker\b|\bcigarettes?\b|أدخن|مدخن"
_SHIFT = r"\bshifts?\b|night work|مناوب|دوام ليلي"
_FASTS = r"\bfast(s|ing)?\b|ramadan|صيام|أصوم|رمضان"
_HOUSEHOLD = (
    (Household.children, r"\b(kids?|children|sons?|daughters?)\b|أطفال|أولاد|ابني|بنتي"),
    (Household.older_relatives, r"\b(parents?|mother|father|mum|mom|dad|grand\w+)\b|والدي|أمي|أبي"),
    (Household.family, r"\b(wife|husband|family)\b|زوجتي|زوجي|عائلتي|أهلي"),
    (Household.alone, r"\blive alone\b|\bby myself\b|\bon my own\b|أعيش وحدي"),
)
_CAREGIVER = r"\bcar(e|ing) for\b|\blook(ing)? after\b|أعتني|أرعى"
_MANAGING = {
    Condition.diabetes: r"diabet|سكري",
    Condition.high_blood_pressure: r"blood pressure|hypertension|ضغط الدم",
    Condition.back_or_joint_pain: r"back pain|joint|knee|arthritis|ظهري|مفاصل|ركبة",
    Condition.stress: r"\bstress\w*|توتر|قلق",
    Condition.recovering_from_illness_or_injury: r"recover\w*|surgery|after (an )?(illness|injury)|أتعافى|عملية",
}


def _found(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.IGNORECASE) is not None


def keyword_answers(text: str) -> dict[str, Any]:
    """The same shape the LLM is asked for, from keywords."""
    return {
        "goals": [b.value for b, p in _GOALS.items() if _found(p, text)],
        "shift_worker": True if _found(_SHIFT, text) else None,
        "fasts_in_ramadan": True if _found(_FASTS, text) else None,
        "household": next((h.value for h, p in _HOUSEHOLD if _found(p, text)), None),
        "caregiver": True if _found(_CAREGIVER, text) else None,
        "current_smoker": True if _found(_SMOKER, text) else None,
        "managing": [c.value for c, p in _MANAGING.items() if _found(p, text)],
        "anchor": None,  # too easy to get wrong with keywords; the follow-up question asks for it
    }


def clean_answers(raw: dict[str, Any], text: str) -> dict[str, Any]:
    """Keep only values that are exactly one of ours; drop everything else (including any health-check field)."""
    def flag(key: str) -> bool | None:
        return raw.get(key) if isinstance(raw.get(key), bool) else None

    def members(key: str, allowed: set[str]) -> list[str]:
        items = raw.get(key)
        return list(dict.fromkeys(i for i in items if isinstance(i, str) and i in allowed)) \
            if isinstance(items, list) else []

    smoker = flag("current_smoker") is True
    goals = [g for g in members("goals", {b.value for b in Behaviour}) if smoker or g != Behaviour.smoking]
    household = raw.get("household")
    anchor = raw.get("anchor").strip() if isinstance(raw.get("anchor"), str) else None
    # The anchor must be the person's own words and short, and it's shown back to them: no red-flag text.
    if anchor and not (len(anchor) <= ANCHOR_MAX and anchor.casefold() in text.casefold()
                       and not detect_red_flags(anchor)):
        anchor = None
    return {
        "goals": goals,
        "schedule_type": "shift" if flag("shift_worker") else None,
        "fasting_ramadan": flag("fasts_in_ramadan"),
        "household": household if isinstance(household, str) and household in {h.value for h in Household} else None,
        "caregiver": flag("caregiver"),
        "smoking_status": "current" if smoker else None,
        "managing": members("managing", {c.value for c in Condition}),  # suggestions only, the user confirms
        "anchor": anchor or None,
    }


def suggest(text: str, lang: Language, chat: Chat | None) -> dict[str, Any]:
    """Suggested sign-up answers and the follow-up questions they unlock. Red-flag text gets the care message and
    goes nowhere else. The text is never stored or logged."""
    if detect_red_flags(text):
        return {"red_flag": True, "message": pick(MESSAGES["seek_care"], lang), "suggestions": None,
                "follow_ups": [], "source": None}
    source, raw = "keywords", None
    if chat is not None:
        from llm.personal import suggest_answers

        try:
            raw, source = suggest_answers(text, lang.value, chat), "llm"
        except LLM_ERRORS:
            log.warning("sign-up suggestion: LLM unavailable or unreadable; using keywords")  # never the text
    answers = clean_answers(raw if raw is not None else keyword_answers(text), text)
    profile_shaped = {
        "basics": {"goals": answers["goals"], "schedule_type": answers["schedule_type"]},
        "preferences": {k: answers[k] for k in ("fasting_ramadan", "household", "caregiver")},
        "history": {"smoking_status": answers["smoking_status"]},
    }
    follow_ups = [q["id"] for q in FOLLOW_UPS if show_follow_up(q, profile_shaped)]
    return {"red_flag": False, "message": None, "suggestions": answers, "follow_ups": follow_ups, "source": source}


# ---------- weekly recap ----------

_COUNTED = {DayOutcome.completed, DayOutcome.partial, DayOutcome.skipped, DayOutcome.no_response}
_DONE = {DayOutcome.completed, DayOutcome.partial}
_BANNED = re.compile(
    r"\b(streaks?|in a row|doctors?|medic\w*|diagnos\w*|treat\w*|cur(e|es|ed|ing)|disease\w*|symptom\w*|"
    r"blood pressure|diabet\w*|weight|calori\w*|kg|diet\w*|heal\w*|prescri\w*|dos(e|es|age)|risk\w*)\b"
    r"|سلسل|طبيب|دواء|علاج|تشخيص|مرض|وزن|سعرات|حمية|صحت|صحي",
    re.IGNORECASE,
)
_ARABIC = re.compile(r"[؀-ۿ]")
_ARABIC_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def recap_facts(state: UserState, events: list[Event], days: int) -> dict[str, Any]:
    """Facts from the user's own history and events in the last `days` engine days. Rules only, no LLM."""
    since = state.day - days
    goals = []
    for b in [b for b in (state.order or list(Behaviour)) if b in state.current_tier]:
        logs = [h.outcome for h in state.history if h.behaviour == b and h.day > since and h.outcome in _COUNTED]
        share = sum(o in _DONE for o in logs) / len(logs) if logs else None
        how = ("no_steps" if share is None else "mostly_done" if share >= MOSTLY_DONE
               else "mostly_missed" if share <= MOSTLY_MISSED else "mixed")
        changes = [{"day": c.day, "kind": c.kind, "from_level": c.from_tier, "to_level": c.to_tier,
                    "barrier": c.barrier.value if c.barrier else None}
                   for c in state.tier_changes if c.behaviour == b and c.day > since]
        goals.append({"behaviour": b.value, "how": how, "level": state.current_tier[b], "level_changes": changes})
    barriers = Counter(e.payload.get("primary") for e in events
                       if e.type == EventType.checkin and e.day > since and e.payload.get("primary"))
    return {
        "days": days,
        "goals": goals,
        "top_barrier": barriers.most_common(1)[0][0] if barriers else None,
        "comeback": state.moments.get("comeback", -1) > since,
    }


def template_summary(facts: dict[str, Any], lang: Language, level: ReadingLevel) -> str:
    hows = [g["how"] for g in facts["goals"] if g["how"] != "no_steps"]
    overall = ("quiet" if not hows else "good" if all(h == "mostly_done" for h in hows)
               else "hard" if all(h == "mostly_missed" for h in hows) else "mixed")
    kinds = {c["kind"] for g in facts["goals"] for c in g["level_changes"]}
    extras = [key for key, applies in (
        ("comeback", facts["comeback"]),
        ("stepped_up", "stepped_up" in kinds),
        ("eased", bool(kinds & {"eased", "shrunk_after_slip"})),
        ("barrier", facts["top_barrier"] is not None),
    ) if applies][:RECAP_MAX_EXTRAS]
    return " ".join(pick(RECAP[k], lang, level) for k in (overall, *extras))


def _for_llm(facts: dict[str, Any]) -> dict[str, Any]:
    """What the LLM sees: no day numbers (it must not count days), no user id, no name."""
    return {
        "goals": [{"behaviour": g["behaviour"], "how": g["how"], "level": g["level"],
                   "level_changes": [{k: c[k] for k in ("kind", "from_level", "to_level", "barrier")}
                                     for c in g["level_changes"]]} for g in facts["goals"]],
        "top_barrier": facts["top_barrier"],
        "comeback": facts["comeback"],
    }


def recap_text_ok(text: str, facts: dict[str, Any], lang: Language, level: ReadingLevel) -> bool:
    """Every check an LLM-written recap must pass; any failure means the template is used instead."""
    sentences = [s for s in re.split(r"[.!?؟]+", text) if s.strip()]
    levels = {str(n) for g in facts["goals"] for n in
              (g["level"], *(c[k] for c in g["level_changes"] for k in ("from_level", "to_level")))}
    numbers = set(re.findall(r"\d+", text.translate(_ARABIC_DIGITS)))
    in_arabic = _ARABIC.search(text) is not None
    return (
        2 <= len(sentences) <= 3 and len(text) <= RECAP_MAX_CHARS
        and numbers <= levels  # no numbers except levels
        and not _BANNED.search(text)  # no medical advice or claims, no streaks
        and not detect_red_flags(text)
        and in_arabic == (lang == Language.ar)
        and (lang == Language.ar or level != ReadingLevel.simple or fk_grade(text) <= FK_MAX_GRADE)
    )


def recap_summary(facts: dict[str, Any], lang: Language, level: ReadingLevel, chat: Chat | None) -> tuple[str, str]:
    """(summary, "llm" | "template"). The LLM sees the facts only and its text must pass recap_text_ok."""
    if chat is not None:
        from llm.personal import write_recap

        try:
            text = write_recap(_for_llm(facts), lang.value, level == ReadingLevel.simple, chat)
        except LLM_ERRORS:
            log.warning("recap: LLM unavailable; using the template")
        else:
            if recap_text_ok(text, facts, lang, level):
                return text, "llm"
            log.info("recap: LLM text failed the checks; using the template")
    return template_summary(facts, lang, level), "template"
