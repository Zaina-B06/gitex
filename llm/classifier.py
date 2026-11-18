"""Check-in free text → one Barrier (TASK_01_C, lean). The LLM only classifies; it never writes user-facing text.

Only the free text and the language are sent: no user id, no profile, no health answers. Anything other than strict
JSON naming a known barrier with confidence ≥ MIN_CONFIDENCE becomes `None`. Provider errors are raised so the API
can fall back to its keyword classifier (api/llm_client.py)."""

import json

from rebound_engine.models import Barrier

from .providers import Chat, chat_from_env

MIN_CONFIDENCE = 0.6
TIMEOUT_S = 3.0  # a check-in must never wait longer than this for the LLM

_BARRIER_HELP = {
    Barrier.time: "no time, too busy, work ran late",
    Barrier.energy_fatigue: "tired, exhausted, no energy, slept badly",
    Barrier.illness_pain: "sick, in pain, injured, unwell (not an emergency)",
    Barrier.schedule_change: "schedule or shifts changed, travelling, routine disrupted",
    Barrier.environment: "too hot, bad weather, no safe or private space to be active",
    Barrier.low_motivation: "not in the mood, can't be bothered, lost motivation",
    Barrier.social_family: "family duties, guests, children, social events",
    Barrier.forgot: "forgot, slipped their mind",
    Barrier.craving: "craving a cigarette or to smoke",
    Barrier.stress: "stressed, anxious, overwhelmed (not self-harm)",
    Barrier.others_smoking: "people smoking around them",
    Barrier.no_healthy_food_nearby: "no healthy food available nearby",
    Barrier.other: "a clear reason that fits none of the above",
}

CLASSIFY_PROMPT = (
    "You sort short check-in messages from a health-habit app into ONE barrier: what stopped the person doing "
    "their small daily step. Messages may be English, Arabic (any dialect), Arabizi or mixed, with typos.\n"
    "Barriers:\n" + "\n".join(f"- {b.value}: {h}" for b, h in _BARRIER_HELP.items()) + "\n"
    'Reply with JSON only: {"barrier": "<one value above, or null if no barrier is stated>", '
    '"confidence": <0 to 1>}. Never add other text.'
)

RED_FLAG_PROMPT = (
    "You are a safety check for a health-habit app. Does this message describe any of: chest pain or tightness, "
    "fainting or nearly fainting, severe breathlessness, wanting to harm or kill themselves, or disordered "
    "eating (starving, purging, bingeing)? Messages may be English, Arabic (any dialect), Arabizi or mixed. "
    'Reply with JSON only: {"red_flag": true} or {"red_flag": false}.'
)


def _messages(system: str, text: str, lang: str) -> list[dict[str, str]]:
    return [{"role": "system", "content": system}, {"role": "user", "content": f"[lang={lang}]\n{text}"}]


def _chat(chat: Chat | None) -> Chat:
    chat = chat or chat_from_env(timeout=TIMEOUT_S, json_mode=True)
    if chat is None:
        raise RuntimeError("no LLM provider configured")
    return chat


def classify_barrier(text: str, lang: str, chat: Chat | None = None) -> dict:
    """{"barrier": Barrier | None, "confidence": float}. Bad or low-confidence output → barrier None.

    Raises when the provider is missing or fails, so the caller can use its keyword fallback."""
    reply = _chat(chat)(_messages(CLASSIFY_PROMPT, text, lang))
    try:
        data = json.loads(reply)
        confidence = float(data["confidence"])
        barrier = Barrier(data["barrier"]) if data["barrier"] is not None else None
    except (ValueError, TypeError, KeyError):  # not JSON, wrong shape, or not one of our barriers
        return {"barrier": None, "confidence": 0.0}
    if not MIN_CONFIDENCE <= confidence <= 1.0:  # low, out of range or NaN
        return {"barrier": None, "confidence": confidence if 0.0 <= confidence <= 1.0 else 0.0}
    return {"barrier": barrier, "confidence": confidence}


def check_red_flag(text: str, lang: str, chat: Chat | None = None) -> bool:
    """True only if the LLM clearly says red flag. It can only ADD a red flag: odd output means False, and the
    engine's keyword check (which runs first) is still the guarantee. Raises when the provider fails."""
    reply = _chat(chat)(_messages(RED_FLAG_PROMPT, text, lang))
    try:
        return json.loads(reply).get("red_flag") is True
    except (ValueError, AttributeError):
        return False
