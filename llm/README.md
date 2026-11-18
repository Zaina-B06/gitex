# llm — check-in classifier (TASK_01_C, lean)

## What it does
When someone types a check-in in their own words and presses no button, the LLM picks **one barrier** from our
fixed list (`time`, `energy_fatigue`, `schedule_change`, …). Check-in replies stay fixed EN/AR templates in
`api/messages.py`.

Two more optional helpers (`personal.py`, 18 Nov):
- **Sign-up suggestions:** from a few sentences the person types, the LLM suggests answers (goals, shift work,
  fasting, household, caregiver, smoking, things they mention managing, a daily anchor). The API keeps only values
  from our enums, and the person confirms each one. Red-flag text never reaches the LLM, and the health check is
  never suggested.
- **Weekly recap:** the only place the LLM writes text users read. It sees only rule-computed facts (no name, no
  user id). Its text must pass strict checks (no numbers except levels, no health or medical words, no streaks,
  2–3 sentences, the right language). If it fails any of them, the user gets a fixed template instead.

The app works fully without it. With no key, a timeout (3 s), an error or odd output, the API uses the keyword
classifier in `api/llm_client.py`. A check-in never fails or slows down because of the LLM.

## Safety
- The engine's keyword red-flag check runs first and stays the guarantee. Text it flags never reaches the LLM.
- Optional second check (`LLM_RED_FLAG_CHECK=true`, off by default): the LLM may **add** a red flag the keywords
  missed (e.g. "my chest feels tight", Arabic paraphrases), never remove one. It then gets the normal care response.
- Buttons the user pressed always win over the classified text.

## What is sent
Only the free text and the language (`[lang=en]` / `[lang=ar]`). No user id, profile or health answers.
Temperature 0. Replies must be strict JSON naming a known barrier with confidence ≥ 0.6, else "no barrier".

## Switch it on
In `.env` (never committed):

```
LLM_PROVIDER=groq
GROQ_API_KEY=...
GROQ_MODEL=openai/gpt-oss-20b
# optional
LLM_RED_FLAG_CHECK=true
```

`openai` (`OPENAI_API_KEY`, `OPENAI_MODEL`) and `azure` (`AZURE_OPENAI_*`) work the same way. Restart the API.
The log line `check-in barrier classified by llm|keywords` says which one answered (never shown to users).

## Files
- `providers.py`: provider setup from `.env` (also used by `python -m api.review_arabic`). Stdlib only.
- `classifier.py`: `classify_barrier(text, lang) -> {barrier, confidence}` and `check_red_flag(text, lang)`.
- `personal.py`: `suggest_answers(text, lang, chat)` and `write_recap(facts, lang, simple, chat)`; the checks and
  fallbacks are in `api/personal.py`.
- `eval/checkins.jsonl`: 61 made-up check-ins (EN, AR, Arabizi, mixed, typos, no-barrier, red flags).
- `eval/__main__.py`: `python -m llm.eval` compares keywords and the LLM. Without a key it runs keywords only.

Tests (offline, fake provider): `api/tests/test_llm.py`.
