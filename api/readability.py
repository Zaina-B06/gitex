"""Flesch-Kincaid grade with a heuristic syllable count (docs/ASSUMPTIONS.md, "Health literacy").

Used by the readability tests and to check LLM-written recaps at the simple reading level."""

import re


def syllables(word: str) -> int:
    w = word.lower()
    count = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le", "ee")) and count > 1:
        count -= 1  # silent final e: "make", "home"
    return max(1, count)  # numbers and vowel-less tokens count as one


def fk_grade(text: str) -> float:
    words = re.findall(r"[A-Za-z0-9']+", text)
    if not words:
        return 0.0
    sentences = [s for s in re.split(r"[.!?]+", text) if re.search(r"[A-Za-z0-9]", s)]
    syl = sum(syllables(w) for w in words)
    return 0.39 * len(words) / max(1, len(sentences)) + 11.8 * syl / len(words) - 15.59
