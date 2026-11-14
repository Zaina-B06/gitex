"""Task 05 A2 over HTTP: Ramadan from the calendar, the moon-sighting tap, heat months, real shift timings."""

from datetime import UTC, datetime

import pytest
from api.app import create_app
from fastapi.testclient import TestClient
from test_api import Clock, onboard

NIGHT = [{"days": ["sun", "mon", "tue", "wed", "thu"], "start": "22:00", "end": "06:00"}]


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def client(clock):
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock)) as c:
        yield c


def at(clock, y, m, d):
    clock.now = datetime(y, m, d, 5, 0, tzinfo=UTC)  # 09:00 in Abu Dhabi


def flags(client, uid, headers):
    return set(client.get(f"/users/{uid}/state", headers=headers).json()["context_flags"])


def test_ramadan_turns_on_by_itself_for_fasting_users(client, clock):
    at(clock, 2027, 2, 6)
    fast_uid, fast_h, _ = onboard(client, preferences={"fasting_ramadan": True})
    other_uid, other_h, _ = onboard(client)
    clock.advance(days=2)  # 8 Feb 2027 = 1 Ramadan 1448
    today = client.get(f"/users/{fast_uid}/today", headers=fast_h).json()
    assert "ramadan" in flags(client, fast_uid, fast_h)
    assert all(a["action"]["fasting_safe"] for a in today["actions"])
    assert "ramadan" not in flags(client, other_uid, other_h)


def test_started_today_tap_corrects_the_table_and_applies_now(client, clock):
    at(clock, 2027, 2, 7)  # the table says tomorrow; the moon was sighted tonight
    uid, headers, _ = onboard(client, preferences={"fasting_ramadan": True})
    assert "ramadan" not in flags(client, uid, headers)
    r = client.patch(f"/users/{uid}/settings", headers=headers, json={"ramadan": "started_today"})
    assert r.status_code == 200, r.text
    assert "ramadan" in r.json()["state"]["context_flags"]
    today = client.get(f"/users/{uid}/today", headers=headers).json()
    assert all(a["action"]["fasting_safe"] for a in today["actions"])
    move = next(a for a in today["actions"] if a["action"]["behaviour"] == "movement")
    assert move["hour"] >= 18  # after iftar


def test_ended_today_tap_and_taps_far_from_ramadan(client, clock):
    at(clock, 2027, 3, 8)  # table: last fasting day; the moon says Eid is today
    uid, headers, _ = onboard(client, preferences={"fasting_ramadan": True})
    assert "ramadan" in flags(client, uid, headers)
    r = client.patch(f"/users/{uid}/settings", headers=headers, json={"ramadan": "ended_today"})
    assert r.status_code == 200, r.text
    assert "ramadan" not in r.json()["state"]["context_flags"] and "eid" in r.json()["state"]["context_flags"]
    at(clock, 2027, 11, 14)
    uid2, h2, _ = onboard(client, preferences={"fasting_ramadan": True})
    assert client.patch(f"/users/{uid2}/settings", headers=h2, json={"ramadan": "started_today"}).status_code == 409


def test_heat_is_on_in_summer_for_everyone(client, clock):
    at(clock, 2027, 7, 15)
    uid, headers, _ = onboard(client)
    assert "heat" in flags(client, uid, headers)


def test_shifts_from_settings_move_prompts_the_next_day(client, clock):
    at(clock, 2027, 11, 8)  # Monday
    uid, headers, data = onboard(client)
    before = {a["action"]["behaviour"]: a["hour"] for a in data["today"]["actions"]}
    r = client.patch(f"/users/{uid}/settings", headers=headers, json={"shifts": NIGHT})
    assert r.status_code == 200, r.text
    same_day = {a["action"]["behaviour"]: a["hour"]
                for a in client.get(f"/users/{uid}/today", headers=headers).json()["actions"]}
    assert same_day == before  # today stays as shown
    clock.advance(days=1)  # Tuesday, after Monday's night shift
    after = {a["action"]["behaviour"]: a["hour"]
             for a in client.get(f"/users/{uid}/today", headers=headers).json()["actions"]}
    assert after != before
    assert all(not 7 <= h < 14 for h in after.values())  # never during their post-shift sleep
    assert after["sleep"] == 6  # wind-down as the shift ends
    assert client.patch(f"/users/{uid}/settings", headers=headers,
                        json={"shifts": [{"days": [], "start": "22:00", "end": "06:00"}]}).status_code == 422
