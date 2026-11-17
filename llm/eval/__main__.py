"""python -m llm.eval: barrier accuracy, keywords vs LLM, on llm/eval/checkins.jsonl (made-up texts only).

Rows marked red_flag are handled like the API does: the engine's keyword check runs first and those texts never reach
the classifier. With LLM_RED_FLAG_CHECK=true, the LLM's extra catches (red flags the keywords miss) are reported too.
Without a provider in .env, only the keyword result is printed."""

import json
import os
from collections import Counter
from pathlib import Path

from api.llm_client import KeywordClassifier
from dotenv import load_dotenv
from rebound_engine.models import Barrier
from rebound_engine.safety import detect_red_flags

from llm import TIMEOUT_S, chat_from_env, check_red_flag, classify_barrier, provider_name

DATA = Path(__file__).with_name("checkins.jsonl")


def load() -> list[dict]:
    return [json.loads(line) for line in DATA.read_text(encoding="utf-8").splitlines() if line.strip()]


def score(name: str, rows: list[dict], predict) -> None:
    hits, misses = 0, Counter()
    for r in rows:
        want = Barrier(r["barrier"]) if r["barrier"] else None
        got = predict(r)
        if got == want:
            hits += 1
        else:
            misses[f"{want.value if want else 'none'} -> {got.value if got else 'none'}"] += 1
    print(f"{name:<22} {hits}/{len(rows)} correct ({hits / len(rows):.0%})")
    for k, n in misses.most_common(6):
        print(f"    missed {n}x  {k}")


def main() -> None:
    load_dotenv()
    rows = load()
    red = [r for r in rows if r.get("red_flag")]
    barrier_rows = [r for r in rows if not r.get("red_flag")]
    print(f"{len(rows)} made-up check-ins: {len(barrier_rows)} barrier texts, {len(red)} red-flag texts\n")

    print("Red flags (engine keywords, always on):")
    kw_caught = [r for r in red if detect_red_flags(r["text"])]
    print(f"    keywords catch {len(kw_caught)}/{len(red)}")

    print("\nBarrier classification:")
    keywords = KeywordClassifier()
    score("keywords", barrier_rows, lambda r: keywords.classify_barrier(r["text"], r["lang"]))

    chat = chat_from_env(timeout=TIMEOUT_S, json_mode=True)
    if chat is None:
        print("\nLLM not run: no provider in .env (LLM_PROVIDER + keys, see llm/README.md).")
        return

    errors = 0

    def llm(r: dict) -> Barrier | None:
        nonlocal errors
        try:
            return classify_barrier(r["text"], r["lang"], chat=chat)["barrier"]
        except Exception:  # count it; the app would fall back to keywords here
            errors += 1
            return keywords.classify_barrier(r["text"], r["lang"])

    score(f"llm ({provider_name()})", barrier_rows, llm)
    if errors:
        print(f"    ({errors} calls failed or timed out and used keywords, as the app would)")

    if os.getenv("LLM_RED_FLAG_CHECK", "").strip().lower() == "true":
        missed = [r for r in red if not detect_red_flags(r["text"])]  # only these would reach the LLM
        extra = [r for r in missed if check_red_flag(r["text"], r["lang"], chat=chat)]
        print(f"\nLLM red-flag check: adds {len(extra)}/{len(missed)} the keywords missed")
        false_alarms = [r for r in barrier_rows if check_red_flag(r["text"], r["lang"], chat=chat)]
        print(f"    false alarms on ordinary check-ins: {len(false_alarms)}/{len(barrier_rows)}")
        for r in false_alarms:
            print(f"      {r['text']!r}")


if __name__ == "__main__":
    main()
