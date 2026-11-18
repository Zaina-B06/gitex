"""Fixes after the frontend round: language change in settings, /health, batched demo writes, the anchor on more
steps, the extra follow-up question."""

import pytest
from api.app import create_app, with_anchor
from api.messages import ANCHOR_PHRASES, FOLLOW_UPS, show_follow_up
from fastapi.testclient import TestClient
from rebound_engine.actions import default_library
from test_api import Clock, onboard

DEMO_KEY = {"X-Demo-Key": "test-demo-key"}
ARABIC = range(0x0600, 0x0700)
# Tier-1/2 steps that read "... right after something you do daily" (habit stacking). Wording only.
ANCHORED = ("mv_t1_home_walk", "mv_t1_outdoor_walk", "mv_t1_balance", "mv_t1_seated", "mv_t2_march_in_place",
            "mv_t2_seated", "sl_t2_wind_down", "sm_t1_delay_first", "rc_t1_breathing", "rc_t2_screen_free")


def _arabic(text: str) -> bool:
    return any(ord(ch) in ARABIC for ch in text)


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def client(clock):
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock)) as c:
        yield c


# ---------- 1. language ----------


def test_language_change_switches_every_api_text(client):
    uid, headers, data = onboard(client)
    assert not any(_arabic(r) for r in data["plan_summary"]["all_reasons"])
    r = client.patch(f"/users/{uid}/settings", headers=headers, json={"language": "ar"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["plan_summary"]["all_reasons"] and all(_arabic(x) for x in out["plan_summary"]["all_reasons"])
    assert all(_arabic(g["start_reason"]) for g in out["plan_summary"]["goals"])
    assert out["today"]["actions"] and all(_arabic(m) for m in out["today"]["messages"])
    assert client.get(f"/users/{uid}/export", headers=headers).json()["profile"]["basics"]["language"] == "ar"
    assert _arabic(client.get(f"/users/{uid}/recap", headers=headers).json()["summary"])
    assert client.patch(f"/users/{uid}/settings", headers=headers, json={"language": "fr"}).status_code == 422


# ---------- 2. /health ----------


def test_health_needs_no_auth(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json() == {"ok": True}


# ---------- 3. batched demo writes ----------


def test_demo_seed_writes_in_few_transactions(clock):
    app = create_app(database_url="sqlite:///:memory:", clock=clock, demo_mode=True, demo_key="test-demo-key")
    store = app.state.store
    calls = {"n": 0}
    real_tx = store._tx

    def counting_tx():
        calls["n"] += 1
        return real_tx()

    store._tx = counting_tx
    with TestClient(app) as c:
        assert c.post("/demo/seed", headers=DEMO_KEY).status_code == 201
    # 15 people x 1-3 weeks of days: thousands of writes one by one, a handful per person when batched.
    assert calls["n"] < 250, calls["n"]


def test_advance_is_batched_and_keeps_its_result(clock):
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock, demo_mode=True,
                               demo_key="test-demo-key")) as c:
        uid, headers, _ = onboard(c)
        r = c.post(f"/demo/users/{uid}/advance", headers=headers, json={"days": 3, "pattern": "good"})
        assert r.status_code == 200 and len(r.json()["log"]) == 3
        state = c.get(f"/users/{uid}/state", headers=headers).json()
        assert state["day"] == 4 and state["history"]  # the batched writes landed


# ---------- 4. anchor on more steps ----------


def test_anchored_steps_read_naturally_without_an_anchor():
    library = {a.id: a for a in default_library()}
    for aid in ANCHORED:
        a = library[aid]
        assert ANCHOR_PHRASES["en"] in a.title.en and ANCHOR_PHRASES["ar"] in a.title.ar, aid
        assert ANCHOR_PHRASES["simple_en"] in a.simple.en and ANCHOR_PHRASES["simple_ar"] in a.simple.ar, aid
        for phrase in ANCHOR_PHRASES.values():
            assert phrase not in a.limits and phrase not in a.rationale, aid


def test_anchored_steps_show_the_users_anchor():
    library = {a.id: a for a in default_library()}
    for aid in ANCHORED:
        a = with_anchor(library[aid], "after maghrib")
        for text in (a.title.en, a.title.ar, a.simple.en, a.simple.ar):
            assert "maghrib" in text and "something you" not in text, (aid, text)
        assert "maghrib" not in a.limits


# ---------- 5. follow-up question bank ----------


def test_indoor_or_outdoor_follow_up_for_movement_only():
    q = next(q for q in FOLLOW_UPS if q["id"] == "setting")
    assert q["fills"] == "preferences.setting"
    assert show_follow_up(q, {"basics": {"goals": ["movement"]}})
    assert not show_follow_up(q, {"basics": {"goals": ["sleep"]}})
