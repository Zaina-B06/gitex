"""Task 05 Part A over HTTP: plan_summary, GET /plan, conditions consent, reason wording."""

import json
import re

import pytest
from api.app import create_app
from api.messages import REASONS
from fastapi.testclient import TestClient
from rebound_engine.plan import REASON_KEYS
from test_api import Clock, _body, onboard


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def client(clock):
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock)) as c:
        yield c



QUEUED_WORDS = ("nutrition", "smoking", "recovery")
# Reasons describe plan choices, never health outcomes or medical claims. Whole words only: an outcome verb aimed at
# a health target ("lower your blood pressure"), or a word that is never plan wording ("cure", "dose", "calories").
_VERB = r"(lowers?|reduces?|cuts?|improves?|prevents?|cures?|treats?|heals?|protects?|controls?|fix(es)?|reverses?|helps?)"
_TARGET = r"(blood|sugar|glucose|pressure|weight|risk|pain|symptoms?|diabetes|stress|health|heart)"
BANNED = re.compile(
    rf"\b{_VERB}\s+((your|the)\s+)?{_TARGET}\b"
    r"|\b(cures?|diagnos\w*|medications?|dose|doses|dosage|calories?|kg|weight|guarantee[sd]?)\b",
    re.IGNORECASE,
)
MAX_SHOWN, MAX_WORDS = 3, 12


@pytest.mark.parametrize("claim", [
    "This will lower your blood pressure", "Walking helps control diabetes", "to reduce stress",
    "it can cure back pain", "lose weight", "no medication needed", "improves your heart",
])
def test_banned_wording_catches_outcome_claims(claim):
    assert BANNED.search(claim)


@pytest.mark.parametrize("plain", [
    "We'll start at a lower level", "You mentioned high blood pressure, so movement stays gentle",
    "We picked low-impact steps for your back", "We will keep steps small", "Better to start small",
])
def test_banned_wording_allows_plan_wording(plain):
    assert not BANNED.search(plain)


def test_every_reason_key_has_short_en_and_ar_text_without_outcome_claims():
    assert set(REASONS) == REASON_KEYS
    for key, text in REASONS.items():
        assert text["en"] and text["ar"], key
        assert len(text["en"].split()) <= MAX_WORDS, key
        assert not BANNED.search(text["en"]), (key, text["en"])


def test_onboarding_returns_a_light_plan_summary(client):
    _, _, data = onboard(client, baseline={"active_days_per_week": 7},
                         conditions={"managing": ["high_blood_pressure", "back_or_joint_pain", "stress", "diabetes",
                                                  "recovering_from_illness_or_injury"]},
                         screening={"mobility_limitation": "some"}, history={"smoking_status": "current"})
    plan = data["plan_summary"]
    assert plan["behaviours"] == ["movement", "sleep"]
    assert 1 <= len(plan["reasons"]) <= MAX_SHOWN
    assert len(plan["all_reasons"]) > len(plan["reasons"])  # the rest is behind "See why"
    assert plan["all_reasons"][:MAX_SHOWN] == plan["reasons"]
    assert all(len(r.split()) <= MAX_WORDS for r in plan["all_reasons"])
    text = json.dumps(plan).lower()
    assert not any(w in text for w in QUEUED_WORDS)  # queued behaviours stay internal until Part B


def test_two_people_see_different_plans(client):
    _, _, a = onboard(client, conditions={"managing": ["back_or_joint_pain"]})
    _, _, b = onboard(client, conditions={"managing": ["recovering_from_illness_or_injury"]})
    assert a["plan_summary"]["reasons"] != b["plan_summary"]["reasons"]


def test_get_plan_needs_the_token_and_follows_settings(client, clock):
    uid, headers, data = onboard(client, baseline={"active_days_per_week": 7})
    assert client.get(f"/users/{uid}/plan").status_code == 401
    assert client.get(f"/users/{uid}/plan", headers=headers).json() == data["plan_summary"]
    r = client.patch(f"/users/{uid}/settings", headers=headers,
                     json={"conditions": {"managing": ["high_blood_pressure"]}})
    assert r.status_code == 200, r.text
    plan = client.get(f"/users/{uid}/plan", headers=headers).json()
    assert plan != data["plan_summary"]
    clock.advance(days=1)
    today = client.get(f"/users/{uid}/today", headers=headers).json()
    assert all(a["action"]["tier"] <= 2 for a in today["actions"] if a["action"]["behaviour"] == "movement")


def test_conditions_are_sensitive_and_deleted_on_withdrawal(client):
    uid, headers, _ = onboard(client, conditions={"managing": ["diabetes", "stress"]})
    store = client.app.state.store
    main = store._conn.execute("SELECT data FROM profiles WHERE user_id = ?", (uid,)).fetchone()[0]
    sensitive = store._conn.execute("SELECT data FROM profiles_sensitive WHERE user_id = ?", (uid,)).fetchone()[0]
    assert "diabetes" not in main and "diabetes" in sensitive
    r = client.patch(f"/users/{uid}/settings", headers=headers, json={"consents": {"conditions": False}})
    assert r.status_code == 200, r.text
    assert store.get_profile(uid).conditions.managing == []
    _, _, kept_out = onboard(client, conditions={"managing": ["diabetes"]}, consents={"conditions": False})
    assert client.app.state.store.get_profile(kept_out["user_id"]).conditions.managing == []


def test_unknown_condition_is_rejected(client):
    r = client.post("/users", json=_body(conditions={"managing": ["flu"]}))
    assert r.status_code == 422
