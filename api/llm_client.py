"""Barrier classification for check-in free text, with the LLM layer (llm/, TASK_01_C) plugged in when configured.

Red flags never go through the classifier: the engine's keyword check runs first inside Engine.checkin(), and the
check-in buttons always win over a classified barrier. Every LLM problem (no key, timeout, error, odd output) falls
back to keywords, so a check-in never fails or waits on the LLM. Which classifier answered is logged, never shown."""

import logging
import os
from collections.abc import Callable
from typing import Protocol

from rebound_engine.models import Barrier

log = logging.getLogger("rebound.checkin")

# chat(messages) -> reply text; see llm/providers.py
Chat = Callable[[list[dict[str, str]]], str]


class BarrierClassifier(Protocol):
    def classify_barrier(self, text: str, lang: str = "en") -> Barrier | None: ...


# Checked in this order; first match wins. EN + AR (Arabic unreviewed, like api/messages.py).
_KEYWORDS: tuple[tuple[Barrier, tuple[str, ...]], ...] = (
    # Substrings, so no short words that hide inside others ("ill" in "still").
    (Barrier.illness_pain, ("sick", "unwell", "pain", "hurt", "injur", "fever", "مريض", "ألم", "وجع", "إصابة")),
    (Barrier.energy_fatigue, ("tired", "exhausted", "no energy", "fatigue", "sleepy", "متعب", "تعبان", "إرهاق")),
    (Barrier.time, ("no time", "busy", "work late", "deadline", "ما عندي وقت", "مشغول", "ضيق الوقت")),
    (Barrier.schedule_change, ("new shift", "schedule changed", "travel", "سفر", "مناوبة", "تغير الدوام")),
    (Barrier.environment, ("too hot", "the heat", "weather", "no space", "unsafe", "الحر", "الجو", "لا يوجد مكان")),
    (Barrier.forgot, ("forgot", "forget", "slipped my mind", "نسيت")),
    (Barrier.social_family, ("family", "kids", "guests", "wedding", "العائلة", "الأطفال", "ضيوف")),
    (Barrier.low_motivation, ("motivat", "didn't feel like", "not in the mood", "lazy", "ما لي خلق", "كسل")),
)


class KeywordClassifier:
    """The keyword fallback, used when no LLM is configured or a call fails."""

    def classify_barrier(self, text: str, lang: str = "en") -> Barrier | None:
        t = text.lower()
        barrier = next((b for b, words in _KEYWORDS if any(w in t for w in words)), None)
        log.info("check-in barrier classified by keywords: %s", barrier)
        return barrier


class LLMClassifier:
    """llm.classify_barrier, falling back to keywords on any error. Low confidence or invalid output → None."""

    def __init__(self, chat: Chat) -> None:
        self.chat = chat
        self.fallback = KeywordClassifier()

    def classify_barrier(self, text: str, lang: str = "en") -> Barrier | None:
        from llm import classify_barrier

        try:
            barrier = classify_barrier(text, lang, chat=self.chat)["barrier"]
        except Exception:  # network, timeout, auth, missing key: never break a check-in
            log.warning("LLM classifier unavailable; using keywords", exc_info=True)
            return self.fallback.classify_barrier(text, lang)
        log.info("check-in barrier classified by llm: %s", barrier)
        return barrier


def default_classifier() -> BarrierClassifier:
    """The LLM classifier when llm/ is importable and a provider is configured in .env, else keywords."""
    try:
        from llm import TIMEOUT_S, chat_from_env
    except ImportError:
        return KeywordClassifier()
    chat = chat_from_env(timeout=TIMEOUT_S, json_mode=True)
    return LLMClassifier(chat) if chat else KeywordClassifier()


RedFlagCheck = Callable[[str, str], bool]


def llm_red_flag_check(chat: Chat) -> RedFlagCheck:
    """Optional second safety check: may only ADD a red flag. Any error → False (keywords stay the guarantee)."""

    def check(text: str, lang: str) -> bool:
        from llm import check_red_flag

        try:
            flagged = check_red_flag(text, lang, chat=chat)
        except Exception:  # the keyword check already ran; a failed second check adds nothing
            log.warning("LLM red-flag check unavailable", exc_info=True)
            return False
        if flagged:
            log.info("check-in red flag added by llm")
        return flagged

    return check


def default_red_flag_check() -> RedFlagCheck | None:
    """Only with LLM_RED_FLAG_CHECK=true and a configured provider; off by default."""
    if os.getenv("LLM_RED_FLAG_CHECK", "").strip().lower() != "true":
        return None
    try:
        from llm import TIMEOUT_S, chat_from_env
    except ImportError:
        return None
    chat = chat_from_env(timeout=TIMEOUT_S, json_mode=True)
    return llm_red_flag_check(chat) if chat else None
