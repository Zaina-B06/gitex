"""Task 05 Part C over HTTP: encouragement in /events and /today, wording rules, turning it off."""

import re

import pytest
from api.app import create_app
from api.messages import ENCOURAGEMENT
from fastapi.testclient import TestClient
from test_api import Clock, onboard

MOMENTS = {"first_day_done", "three_good_days", "comeback", "habit_strength_50", "first_week_done",
           "tried_something_new"}
# Never a count, never streak language, never how many days were missed.
BANNED = re.compile(r"\d|\b(two|three|four|five|six|seven|eight|nine|ten|streak|in a row|don't break|"
                    r"days? missed|missed \w+ days?)\b", re.IGNORECASE)


@pytest.fixture
def client():
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=Clock())) as c:
        yield c


def test_every_moment_has_several_short_kind_variants():
    assert set(ENCOURAGEMENT) == MOMENTS
    for moment, variants in ENCOURAGEMENT.items():
        assert len(variants) >= 3, moment
        for v in variants:
            assert v["en"] and v["ar"] and v["simple"], moment
            for text in (v["en"], v["simple"]):
                assert not BANNED.search(text), (moment, text)
                assert len(text.split()) <= 14, (moment, text)
            assert not re.search(r"\d|[٠-٩]", v["ar"]), (moment, v["ar"])


def test_first_completion_returns_a_moment_and_today_shows_it(client):
    uid, headers, data = onboard(client)
    first = data["today"]["actions"][0]["action"]["id"]
    r = client.post(f"/users/{uid}/events", headers=headers, json={"action_id": first, "type": "completed"}).json()
    assert r["encouragement"]["moment"] == "first_day_done" and r["encouragement"]["message"]
    second = data["today"]["actions"][1]["action"]["id"]
    r2 = client.post(f"/users/{uid}/events", headers=headers, json={"action_id": second, "type": "completed"}).json()
    assert r2["encouragement"] is None  # at most one a day
    today = client.get(f"/users/{uid}/today", headers=headers).json()
    assert today["encouragement"]["moment"] == "first_day_done"


def test_skips_get_nothing_and_users_can_turn_it_off(client):
    uid, headers, data = onboard(client)
    first = data["today"]["actions"][0]["action"]["id"]
    r = client.post(f"/users/{uid}/events", headers=headers, json={"action_id": first, "type": "skipped"}).json()
    assert r["encouragement"] is None
    uid, headers, data = onboard(client, preferences={"encouragement": False})
    first = data["today"]["actions"][0]["action"]["id"]
    r = client.post(f"/users/{uid}/events", headers=headers, json={"action_id": first, "type": "completed"}).json()
    assert r["encouragement"] is None


def test_arabic_users_get_arabic_encouragement(client):
    uid, headers, data = onboard(client, basics={"language": "ar"})
    first = data["today"]["actions"][0]["action"]["id"]
    r = client.post(f"/users/{uid}/events", headers=headers, json={"action_id": first, "type": "completed"}).json()
    assert r["encouragement"]["message"] in {v["ar"] for v in ENCOURAGEMENT["first_day_done"]}
