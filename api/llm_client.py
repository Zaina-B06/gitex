"""Barrier classification for check-in free text, behind an interface the LLM layer (TASK_01_C) plugs into.

No provider calls here. Red flags never go through this: the engine's keyword check runs first inside
Engine.checkin(), and the check-in buttons always win over a classified barrier."""

from typing import Protocol

from rebound_engine.models import Barrier


class BarrierClassifier(Protocol):
    def classify_barrier(self, text: str) -> Barrier | None: ...


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
    """FakeLLM: a keyword fallback used when no LLM is configured."""

    def classify_barrier(self, text: str) -> Barrier | None:
        t = text.lower()
        return next((b for b, words in _KEYWORDS if any(w in t for w in words)), None)


def default_classifier() -> BarrierClassifier:
    """The teammate's `llm` package once it exposes `classify_barrier`, else the keyword fallback."""
    try:
        from llm import classify_barrier  # type: ignore[attr-defined]  # TASK_01_C
    except ImportError:
        return KeywordClassifier()

    class _LLM:
        def classify_barrier(self, text: str) -> Barrier | None:
            try:
                return classify_barrier(text)
            except Exception:  # noqa: BLE001  any provider failure (network, auth, bad output) must not break a check-in
                return KeywordClassifier().classify_barrier(text)

    return _LLM()
