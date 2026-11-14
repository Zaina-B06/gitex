"""Arabic review sheet (Task 05 Part D): every Arabic string, the English it was written from, and an LLM
back-translation, for a human reviewer. Safety-critical rows come first.

    python -m api.review_arabic            # writes review/arabic_review.csv (git-ignored)

This is not a test and doesn't make the Arabic "reviewed": a person must read the sheet and fix what drifted.
Without an LLM key (.env: LLM_PROVIDER=openai + OPENAI_API_KEY + OPENAI_MODEL, or LLM_PROVIDER=azure +
AZURE_OPENAI_*), the sheet is still written with the back-translation column empty, as a checklist."""

import csv
import json
import os
import sys
import urllib.request
from collections.abc import Callable
from pathlib import Path

from dotenv import load_dotenv

from .messages import catalogue

OUT = Path(__file__).resolve().parents[1] / "review" / "arabic_review.csv"
AZURE_API_VERSION = "2024-10-21"
PROMPT = "Translate this Arabic text into English as literally as you can. Reply with the translation only."


def _llm() -> Callable[[str], str] | None:
    """A back-translate function from .env, or None (with the reason printed) if no provider is set up."""
    provider = os.getenv("LLM_PROVIDER", "").strip().lower()
    if provider == "openai" and os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_MODEL"):
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"}
        extra = {"model": os.environ["OPENAI_MODEL"]}
    elif provider == "azure" and all(os.getenv(k) for k in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY",
                                                             "AZURE_OPENAI_DEPLOYMENT")):
        url = (f"{os.environ['AZURE_OPENAI_ENDPOINT'].rstrip('/')}/openai/deployments/"
               f"{os.environ['AZURE_OPENAI_DEPLOYMENT']}/chat/completions?api-version={AZURE_API_VERSION}")
        headers = {"api-key": os.environ["AZURE_OPENAI_API_KEY"]}
        extra = {}
    else:
        print("No LLM key in .env (set LLM_PROVIDER=openai with OPENAI_API_KEY and OPENAI_MODEL, or "
              "LLM_PROVIDER=azure with AZURE_OPENAI_*). Writing the sheet with back_translation left empty.")
        return None

    def translate(arabic: str) -> str:
        body = {**extra, "temperature": 0,
                "messages": [{"role": "system", "content": PROMPT}, {"role": "user", "content": arabic}]}
        req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                     headers={**headers, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)["choices"][0]["message"]["content"].strip()

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
