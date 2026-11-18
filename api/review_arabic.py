"""Arabic review sheet (Task 05 Part D): every Arabic string, the English it was written from, and an LLM
back-translation, for a human reviewer. Safety-critical rows come first.

    python -m api.review_arabic            # writes review/arabic_review.csv (git-ignored)

This is not a test and doesn't make the Arabic "reviewed": a person must read the sheet and fix what drifted.
Without an LLM key (.env: LLM_PROVIDER=groq|openai|azure and that provider's keys, see llm/README.md), the sheet
is still written with the back-translation column empty, as a checklist."""

import csv
import sys
from collections.abc import Callable
from pathlib import Path

from dotenv import load_dotenv
from llm.providers import chat_from_env

from .messages import catalogue

OUT = Path(__file__).resolve().parents[1] / "review" / "arabic_review.csv"
PROMPT = "Translate this Arabic text into English as literally as you can. Reply with the translation only."


def _llm() -> Callable[[str], str] | None:
    """A back-translate function from .env (provider setup shared with the check-in classifier, llm/providers.py),
    or None (with the reason printed) if no provider is set up."""
    chat = chat_from_env(timeout=60)
    if chat is None:
        print("No LLM key in .env (set LLM_PROVIDER=groq with GROQ_API_KEY and GROQ_MODEL, LLM_PROVIDER=openai with "
              "OPENAI_API_KEY and OPENAI_MODEL, or LLM_PROVIDER=azure with AZURE_OPENAI_*). Writing the sheet with "
              "back_translation left empty.")
        return None

    def translate(arabic: str) -> str:
        return chat([{"role": "system", "content": PROMPT}, {"role": "user", "content": arabic}])

    return translate


def write_sheet(out: Path, translate: Callable[[str], str] | None) -> int:
    """Write the sheet; return how many back-translations failed (their cells are left empty)."""
    rows = []
    for e in catalogue():
        for variant, en, ar in (("standard", e["en"], e["ar"]), ("simple", e["simple_en"], e["simple_ar"])):
            if ar:
                rows.append({"key": e["key"], "variant": variant, "safety_critical": "yes" if e["safety"] else "no",
                             "english": en or "", "arabic": ar, "back_translation": "", "reviewer_note": ""})
    rows.sort(key=lambda r: r["safety_critical"] != "yes")  # stable: safety rows first, order kept otherwise
    failed = 0
    for i, r in enumerate(rows):
        if translate is None:
            break
        try:
            r["back_translation"] = translate(r["arabic"])
        except (OSError, ValueError, KeyError, IndexError) as err:  # network, bad JSON, odd reply: keep going
            failed += 1
            print(f"{r['key']} ({r['variant']}): back-translation failed: {err}", file=sys.stderr)
        print(f"{i + 1}/{len(rows)}", end="\r")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8-sig", newline="") as f:  # BOM so Excel shows the Arabic
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out}" + (f" ({failed} back-translations failed)" if failed else ""))
    return failed


if __name__ == "__main__":
    load_dotenv()
    write_sheet(OUT, _llm())
