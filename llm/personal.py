"""Two optional helpers for personalisation (18 Nov). Both are checked and can be replaced by rules in api/personal.py.

- suggest_answers: sign-up free text -> suggested answers as JSON. Only the text and language are sent. The API
  runs the red-flag keywords first (red-flag text is never sent) and drops anything not in our enums.
- write_recap: facts computed by rules -> 2-3 friendly sentences. Only the facts are sent (no name, no user id, no
  health answers). The API checks the text and uses a fixed template if it fails any check."""

import json

from rebound_engine.models import Behaviour, Condition, Household

from .providers import Chat

TIMEOUT_S = 5.0  # sign-up and the recap never wait longer than this for the LLM

SUGGEST_PROMPT = (
    "A person is signing up to a small-steps health-habit app and describes themselves in their own words "
    "(English or Arabic, any dialect, possibly mixed). Pick out ONLY what they clearly say. Reply with JSON only:\n"
    '{"goals": [any of ' + ", ".join(f'"{b.value}"' for b in Behaviour) + "], "
    '"shift_worker": true|false|null, "fasts_in_ramadan": true|false|null, '
    '"household": one of ' + ", ".join(f'"{h.value}"' for h in Household) + " or null, "
    '"caregiver": true|false|null, "current_smoker": true|false|null, '
    '"managing": [any of ' + ", ".join(f'"{c.value}"' for c in Condition) + "], "
    '"anchor": "a daily routine they mention that a step could follow, copied from their words" or null}\n'
    "Use null or [] when they don't say. Never guess health conditions they don't name. Never add other keys or text."
)

RECAP_PROMPT = (
    "Write a short, warm weekly recap for a small-steps health-habit app, using ONLY the facts given as JSON. "
    "Write 2 or 3 short sentences in {language}{level}. Rules: no numbers except level numbers from the facts; "
    "never count days or steps; no streaks; no health, medical or diet advice and no claims about health; no "
    "blame; don't invent anything that isn't in the facts. Reply with the sentences only."
)


def suggest_answers(text: str, lang: str, chat: Chat) -> dict:
    """The LLM's reply as a dict. Raises ValueError/TypeError if it isn't a JSON object (the caller uses keywords)."""
    reply = chat([{"role": "system", "content": SUGGEST_PROMPT}, {"role": "user", "content": f"[lang={lang}]\n{text}"}])
    start, end = reply.find("{"), reply.rfind("}")  # tolerate code fences or a stray word around the JSON
    data = json.loads(reply[start:end + 1]) if start != -1 else None
    if not isinstance(data, dict):
        raise TypeError("not a JSON object")
    return data


def write_recap(facts: dict, lang: str, simple: bool, chat: Chat) -> str:
    language = "Arabic (Modern Standard, simple)" if lang == "ar" else "English"
    level = ", very simple words, one idea per sentence (reading age about 11)" if simple else ""
    system = RECAP_PROMPT.format(language=language, level=level)
    return chat([{"role": "system", "content": system},
                 {"role": "user", "content": json.dumps(facts, ensure_ascii=False)}]).strip()
