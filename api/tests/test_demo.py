"""Demo routes (DEMO_MODE=true): time travel and seeded personas."""

import pytest
from api.app import create_app
from api.demo import ORG_DAYS, ORG_SIZE, PERSONA_WARMUP_DAYS
from fastapi.testclient import TestClient
from test_api import Clock, complete_all, onboard

DEMO_KEY = {"X-Demo-Key": "test-demo-key"}


@pytest.fixture
def demo():
    app = create_app(database_url="sqlite:///:memory:", clock=Clock(), demo_mode=True, demo_key="test-demo-key")
    with TestClient(app) as c:
        yield c


def test_seed_needs_the_demo_key(demo):
    assert demo.post("/demo/seed").status_code == 401
    assert demo.post("/demo/seed", headers={"X-Demo-Key": "wrong"}).status_code == 401
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=Clock(), demo_mode=True)) as no_key:
        assert no_key.post("/demo/seed", headers=DEMO_KEY).status_code == 401  # no DEMO_KEY set: refused


def advance(client, uid, headers, **body):
    r = client.post(f"/demo/users/{uid}/advance", headers=headers, json=body)
    assert r.status_code == 200, r.text
    return r.json()


def test_demo_routes_exist_only_in_demo_mode():
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=Clock())) as c:
        uid, headers, _ = onboard(c)
        assert c.post("/demo/seed").status_code == 404
        assert c.post(f"/demo/users/{uid}/advance", headers=headers,
                      json={"days": 1, "pattern": "good"}).status_code == 404


def test_advance_needs_the_users_token_and_valid_input(demo):
    uid, headers, _ = onboard(demo)
    assert demo.post(f"/demo/users/{uid}/advance", json={"days": 1, "pattern": "good"}).status_code == 401
    for bad in ({"days": 0, "pattern": "good"}, {"days": 61, "pattern": "good"}, {"days": 3, "pattern": "great"},
                {"days": 3, "pattern": "good", "scenario": "snow"}):
        assert demo.post(f"/demo/users/{uid}/advance", headers=headers, json=bad).status_code == 422, bad


def test_full_journey_lapse_checkin_recovery(demo):
    """Task 03: onboard -> today -> complete -> advance "lapse" -> drifting/lapsed -> check-in -> adjusted -> recovery."""
    uid, headers, data = onboard(demo)
    assert len(data["today"]["actions"]) == 2
    complete_all(demo, uid, headers)

    lapse = advance(demo, uid, headers, days=6, pattern="lapse")
    assert len(lapse["log"]) == 6
    assert all(o == "no_response" for row in lapse["log"][1:] for o in row["outcomes"].values())
    assert lapse["state"]["engagement_state"] in ("drifting", "lapsed")
    assert lapse["today"]["checkin_due"] and lapse["today"]["day"] == 7
    assert all(h > 0 for h in lapse["state"]["habit_strength"].values())  # decayed, never reset

    r = demo.post(f"/users/{uid}/checkin", headers=headers, json={"barriers": ["time"]}).json()
    assert r["adjusted_actions"] and not r["red_flag"]
    today_ids = {a["action"]["id"] for a in demo.get(f"/users/{uid}/today", headers=headers).json()["actions"]}
    assert {a["id"] for a in r["adjusted_actions"]} == today_ids

    back = advance(demo, uid, headers, days=4, pattern="good")
    assert back["state"]["engagement_state"] in ("recovering", "active")


def test_good_days_build_habit_strength(demo):
    uid, headers, data = onboard(demo)
    before = data["state"]["habit_strength"]
    out = advance(demo, uid, headers, days=5, pattern="good")
    assert [row["day"] for row in out["log"]] == [1, 2, 3, 4, 5]
    assert {o for row in out["log"] for o in row["outcomes"].values()} <= {"completed", "partial", "skipped"}
    assert all(out["state"]["habit_strength"][b] > before[b] for b in before)


def test_scenario_turns_on_its_context_flag(demo):
    uid, headers, _ = onboard(demo)
    out = advance(demo, uid, headers, days=1, pattern="mixed", scenario="heat")
    assert "heat" in out["state"]["context_flags"]


def test_seed_creates_three_personas_and_an_org(demo):
    r = demo.post("/demo/seed", headers=DEMO_KEY)
    assert r.status_code == 201, r.text
    data = r.json()
    assert len(data["personas"]) == 3 and data["org_size"] == ORG_SIZE
    profiles = {}
    for p in data["personas"]:
        h = {"Authorization": f"Bearer {p['token']}"}
        export = demo.get(f"/users/{p['user_id']}/export", headers=h).json()
        assert export["state"]["day"] == PERSONA_WARMUP_DAYS + 1
        profiles[p["name"]] = (export, demo.get(f"/users/{p['user_id']}/today", headers=h).json())
    ahmed = next(v for k, v in profiles.items() if k.startswith("Ahmed"))
    assert ahmed[0]["profile"]["basics"]["schedule_type"] == "shift"
    assert ahmed[0]["profile"]["basics"]["language"] == "ar"
    mariam = next(v for k, v in profiles.items() if k.startswith("Mariam"))
    assert all(a["action"]["seated"] for a in mariam[1]["actions"] if a["action"]["behaviour"] == "movement")
    assert all(a["action"]["tier"] <= 2 for a in ahmed[1]["actions"] if a["action"]["behaviour"] == "movement")

    store = demo.app.state.store
    members = store.org_user_ids(data["org_id"])
    assert len(members) == ORG_SIZE
    assert {store.get_state(uid).day for uid in members} == {ORG_DAYS}
    assert demo.post("/demo/seed", headers=DEMO_KEY).json()["org_id"] != data["org_id"]  # a fresh org every time


def test_seeded_personas_show_different_plans(demo):
    personas = demo.post("/demo/seed", headers=DEMO_KEY).json()["personas"]
    plans = {
        p["name"].split(",")[0]: demo.get(f"/users/{p['user_id']}/plan",
                                          headers={"Authorization": f"Bearer {p['token']}"}).json()
        for p in personas
    }
    assert len({tuple(p["all_reasons"]) for p in plans.values()}) == 3  # all different
    assert any("ضغط الدم" in r for r in plans["Ahmed"]["all_reasons"])  # Ahmed is Arabic: high blood pressure
    assert len(plans["Mariam"]["all_reasons"]) >= 2  # mobility + recovering
    assert all(len(p["reasons"]) <= 3 for p in plans.values())
