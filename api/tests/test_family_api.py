"""Task 05 Part E over HTTP: family fields at onboarding and in settings, export, the "Family things" reply, demo."""

import pytest
from api.app import create_app
from api.messages import MESSAGES, REASONS
from fastapi.testclient import TestClient
from test_api import Clock, _body, onboard

DEMO_KEY = {"X-Demo-Key": "test-demo-key"}


@pytest.fixture
def client():
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=Clock())) as c:
        yield c


def test_family_fields_are_optional_and_set_at_onboarding(client):
    uid, headers, _ = onboard(client)
    prefs = client.get(f"/users/{uid}/export", headers=headers).json()["profile"]["preferences"]
    assert prefs["household"] is None and prefs["caregiver"] is False and prefs["family_fasting"] is False
    uid, headers, _ = onboard(client, preferences={"household": "children", "caregiver": True, "family_fasting": True})
    prefs = client.get(f"/users/{uid}/export", headers=headers).json()["profile"]["preferences"]
    assert (prefs["household"], prefs["caregiver"], prefs["family_fasting"]) == ("children", True, True)
    assert client.post("/users", json=_body(preferences={"household": "neighbours"})).status_code == 422


def test_settings_change_household_and_today_follows(client):
    uid, headers, data = onboard(client, basics={"goals": ["nutrition"]})
    assert "family" not in data["today"]["actions"][0]["action"]["tags"]
    r = client.patch(f"/users/{uid}/settings", headers=headers, json={"preferences": {"household": "family"}})
    assert r.status_code == 200 and r.json()["preferences"]["household"] == "family"
    r = client.post(f"/users/{uid}/checkin", headers=headers, json={"barriers": ["social_family"]}).json()
    assert r["message_key"] == "family_together" and r["message"] == MESSAGES["family_together"]["en"]
    assert any("family" in a["tags"] for a in r["adjusted_actions"])


def test_social_family_without_household_keeps_the_old_reply(client):
    uid, headers, _ = onboard(client)
    r = client.post(f"/users/{uid}/checkin", headers=headers, json={"barriers": ["social_family"]}).json()
    assert r["message_key"] == "thanks_for_sharing"


def test_caregiver_reason_shows_with_a_rest_goal(client):
    _, _, data = onboard(client, basics={"goals": ["recovery"]}, preferences={"caregiver": True})
    assert REASONS["caregiver"]["en"] in data["plan_summary"]["all_reasons"]


def test_delete_removes_family_answers(client):
    uid, headers, _ = onboard(client, preferences={"household": "children"})
    assert client.delete(f"/users/{uid}", headers=headers).status_code == 204
    assert client.get(f"/users/{uid}/export", headers=headers).status_code == 401


@pytest.fixture
def demo():
    app = create_app(database_url="sqlite:///:memory:", clock=Clock(), demo_mode=True, demo_key="test-demo-key")
    with TestClient(app) as c:
        yield c


def test_demo_ahmed_has_a_family_and_gets_family_steps(demo):
    personas = {p["name"].split(",")[0]: p for p in demo.post("/demo/seed", headers=DEMO_KEY).json()["personas"]}
    ahmed = personas["Ahmed"]
    h = {"Authorization": f"Bearer {ahmed['token']}"}
    prefs = demo.get(f"/users/{ahmed['user_id']}/export", headers=h).json()["profile"]["preferences"]
    assert prefs["household"] == "children" and prefs["family_fasting"] is True
    today = demo.get(f"/users/{ahmed['user_id']}/today", headers=h).json()
    assert any({"family", "family_iftar"} & set(a["action"]["tags"]) for a in today["actions"])
    sara = personas["Sara"]
    sara_today = demo.get(f"/users/{sara['user_id']}/today",
                          headers={"Authorization": f"Bearer {sara['token']}"}).json()
    assert not any("family" in a["action"]["tags"] for a in sara_today["actions"])
