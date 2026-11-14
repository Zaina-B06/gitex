"""Task 05 Part D: simple variants, readability, safety wording, reading_level over HTTP, the Arabic review sheet."""

import csv
import re

import pytest
from api.app import create_app
from api.messages import MESSAGES, catalogue
from api.review_arabic import write_sheet
from fastapi.testclient import TestClient
from rebound_engine.actions import load_actions
from rebound_engine.recipes import load_recipes
from rebound_engine.safety import SCREENING_QUESTIONS
from test_api import Clock, onboard

FK_MAX_GRADE = 6  # docs/ASSUMPTIONS.md, "Health literacy"
SAKINA = "800 SAKINA (800 725462)"
DOCTOR = {"en": "doctor", "ar": "طبيب"}  # "طبيب" also matches "الطبيب" and "طبيبك"
# Strings that must keep the advice to see a doctor in every language and reading level.
DOCTOR_KEYS = ("message.seek_care", "message.see_doctor", "message.check_with_doctor",
               "message.diet_check_with_doctor", "reason.see_doctor_gentle")
VARIANTS = ("en", "ar", "simple_en", "simple_ar")


# ---------- readability (Flesch-Kincaid grade, heuristic syllables) ----------


def syllables(word: str) -> int:
    w = word.lower()
    count = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and not w.endswith(("le", "ee")) and count > 1:
        count -= 1  # silent final e: "make", "home"
    return max(1, count)  # numbers and vowel-less tokens count as one


def fk_grade(text: str) -> float:
    words = re.findall(r"[A-Za-z0-9']+", text)
    sentences = [s for s in re.split(r"[.!?]+", text) if re.search(r"[A-Za-z0-9]", s)]
    syl = sum(syllables(w) for w in words)
    return 0.39 * len(words) / max(1, len(sentences)) + 11.8 * syl / len(words) - 15.59


def test_fk_grade_on_known_sentences():
    assert fk_grade("The cat sat on the mat.") == pytest.approx(-1.45, abs=0.01)
    # A hard sentence must score high, so the check can't pass by always returning a low grade.
    assert fk_grade("Implementation intentions substantially increase behavioural consistency.") > 12
    assert syllables("make") == 1 and syllables("table") == 2 and syllables("minutes") == 3


def _simple_english() -> list[tuple[str, str]]:
    # Recipe titles are dish names ("Shakshuka"): FK is meaningless on a name, so they aren't scored.
    return [(e["key"], e["simple_en"]) for e in catalogue() if e["simple_en"]]


def test_recipe_titles_stay_short():
    long = [r.title.en for r in load_recipes() if len(r.title.en.split()) > 6]
    assert not long, long


def test_every_english_simple_string_is_grade_6_or_lower():
    too_hard = [(k, t, round(fk_grade(t.replace("{reason}", "")), 1)) for k, t in _simple_english()
                if fk_grade(t.replace("{reason}", "")) > FK_MAX_GRADE]
    assert not too_hard, "\n".join(f"{k}: grade {g}: {t}" for k, t, g in too_hard)


def test_no_one_word_simple_messages():
    short = [(k, t) for k, t in _simple_english() if len(t.split()) < 2]
    assert not short, short


# ---------- every string has real simple variants ----------


def test_every_user_facing_string_has_simple_variants_in_both_languages():
    for e in catalogue():
        if e["key"].startswith("recipe."):
            continue  # dish names stay as they are
        assert e["simple_en"] and e["simple_ar"], e["key"]
        assert e["simple_ar"] != e["ar"], f"{e['key']}: simple Arabic is a copy of the standard text"


def test_catalogue_covers_messages_actions_and_the_health_check():
    keys = {e["key"] for e in catalogue()}
    assert {f"message.{k}" for k in MESSAGES} <= keys
    assert {f"action.{a.id}" for a in load_actions()} <= keys
    assert {f"question.{q}" for q in SCREENING_QUESTIONS} <= keys


# ---------- safety wording survives simplification ----------


def test_any_mention_of_sakina_uses_the_exact_number():
    texts = [(e["key"], e[v]) for e in catalogue() for v in VARIANTS if e[v]]
    texts += [(f"limits.{a.id}", a.limits) for a in load_actions()]
    wrong = [(k, t) for k, t in texts if "SAKINA" in t and SAKINA not in t]
    assert not wrong, wrong


def test_red_flag_message_keeps_998_and_sakina_in_every_variant():
    seek = next(e for e in catalogue() if e["key"] == "message.seek_care")
    for v in VARIANTS:
        assert "998" in seek[v] and SAKINA in seek[v], v


def test_doctor_advice_survives_in_every_variant():
    by_key = {e["key"]: e for e in catalogue()}
    for key in DOCTOR_KEYS:
        for v in VARIANTS:
            assert DOCTOR[v.removeprefix("simple_")] in by_key[key][v].lower(), (key, v)


def test_safety_critical_strings_are_marked():
    safety = {e["key"] for e in catalogue() if e["safety"]}
    assert set(DOCTOR_KEYS) <= safety
    assert {f"question.{q}" for q in SCREENING_QUESTIONS} <= safety


# ---------- reading_level over HTTP ----------


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def client(clock):
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock)) as c:
        yield c


def _titles(today: dict) -> list[str]:
    return [s["action"]["title"]["en"] for s in today["actions"]]


def test_reading_level_changes_what_today_returns(client):
    _, _, standard = onboard(client)
    _, _, simple = onboard(client, preferences={"reading_level": "simple"})
    library = {a.id: a for a in load_actions()}
    std_today, simple_today = standard["today"], simple["today"]
    assert [s["action"]["id"] for s in std_today["actions"]] == [s["action"]["id"] for s in simple_today["actions"]]
    assert _titles(std_today) == [library[s["action"]["id"]].title.en for s in std_today["actions"]]
    assert _titles(simple_today) == [library[s["action"]["id"]].simple.en for s in simple_today["actions"]]
    assert _titles(std_today) != _titles(simple_today)


def test_reading_level_can_be_switched_in_settings(client):
    uid, headers, data = onboard(client)
    before = _titles(data["today"])
    r = client.patch(f"/users/{uid}/settings", headers=headers, json={"preferences": {"reading_level": "simple"}})
    assert r.status_code == 200 and r.json()["preferences"]["reading_level"] == "simple"
    after = _titles(client.get(f"/users/{uid}/today", headers=headers).json())
    assert after != before


def test_simple_level_uses_simple_messages_and_reasons(client):
    _, _, data = onboard(client, preferences={"reading_level": "simple"},
                         screening={"chest_pain": True})
    by_key = {e["key"]: e for e in catalogue()}
    assert by_key["reason.see_doctor_gentle"]["simple_en"] in data["plan_summary"]["all_reasons"]
    uid, headers, _ = onboard(client, preferences={"reading_level": "simple"})
    r = client.post(f"/users/{uid}/checkin", headers=headers, json={"barriers": ["time"]}).json()
    assert r["message"] == by_key[f"message.{r['message_key']}"]["simple_en"]


def test_red_flag_in_simple_arabic_still_gives_the_numbers(client):
    uid, headers, _ = onboard(client, basics={"language": "ar"}, preferences={"reading_level": "simple"})
    r = client.post(f"/users/{uid}/checkin", headers=headers, json={"free_text": "I have chest pain"}).json()
    assert r["red_flag"] and "998" in r["message"] and SAKINA in r["message"]


def test_read_aloud_is_stored_and_returned(client):
    uid, headers, _ = onboard(client)
    r = client.patch(f"/users/{uid}/settings", headers=headers, json={"preferences": {"read_aloud": True}})
    assert r.json()["preferences"]["read_aloud"] is True


def test_onboarding_text_in_each_language_and_level(client):
    std = client.get("/content/onboarding").json()
    assert set(std["questions"]) >= set(SCREENING_QUESTIONS) | {"pregnant", "mobility_limitation"}
    assert {"screening", "body", "motivation_reason", "conditions"} <= set(std["why_we_ask"])
    assert std["reading_level_examples"]["standard"] != std["reading_level_examples"]["simple"]
    assert std["translation_note"] is None
    simple_ar = client.get("/content/onboarding", params={"lang": "ar", "reading_level": "simple"}).json()
    assert simple_ar["questions"]["chest_pain"] != std["questions"]["chest_pain"]
    assert simple_ar["translation_note"]  # Arabic is a draft, pending native review


def test_explain_has_a_simple_turn_off_line(client):
    action = load_actions()[0].id
    std = client.get(f"/actions/{action}/explain").json()
    simple = client.get(f"/actions/{action}/explain", params={"reading_level": "simple"}).json()
    assert std["how_to_turn_off"] != simple["how_to_turn_off"]


# ---------- Arabic review sheet ----------


def test_review_sheet_without_a_key_lists_safety_rows_first(tmp_path):
    out = tmp_path / "arabic_review.csv"
    write_sheet(out, translate=None)
    with out.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    assert rows and all(r["back_translation"] == "" for r in rows)
    flags = [r["safety_critical"] == "yes" for r in rows]
    assert flags == sorted(flags, reverse=True)  # every safety row comes before every other row
    assert any(r["key"] == "message.seek_care" and r["variant"] == "simple" for r in rows)
    assert not any(r["arabic"] == "" for r in rows)
