"""Task 05 Part B over HTTP: new goals, the 3-a-day cap, craving help, recipes."""

import pytest
from api.app import create_app
from fastapi.testclient import TestClient
from rebound_engine.models import Behaviour
from test_api import Clock, _body, onboard

ALL_GOALS = ["movement", "sleep", "nutrition", "smoking", "recovery"]


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def client(clock):
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock)) as c:
        yield c


def test_five_goals_give_at_most_three_actions_a_day(client, clock):
    uid, headers, data = onboard(client, basics={"goals": ALL_GOALS}, history={"smoking_status": "current"})
    assert len(data["plan_summary"]["behaviours"]) == 3
    seen = set()
    for _ in range(6):
        today = client.get(f"/users/{uid}/today", headers=headers).json()
        assert len(today["actions"]) <= 3
        seen |= {a["action"]["behaviour"] for a in today["actions"]}
        clock.advance(days=1)
    assert seen == set(ALL_GOALS)


def test_rotation_note_only_with_more_than_three_goals(client):
    _, _, many = onboard(client, basics={"goals": ALL_GOALS}, history={"smoking_status": "current"})
    assert many["plan_summary"]["rotation_note"] == "You have more than 3 goals, so your third step changes each day."
    _, _, few = onboard(client)
    assert few["plan_summary"]["rotation_note"] is None
    _, _, ar = onboard(client, basics={"goals": ALL_GOALS, "language": "ar"}, history={"smoking_status": "current"})
    assert ar["plan_summary"]["rotation_note"].startswith("لديك")


def test_smoking_goal_needs_a_current_smoker(client):
    assert client.post("/users", json=_body(basics={"goals": ["smoking"]})).status_code == 422


def test_craving_checkin_offers_help_without_medicine_advice(client):
    uid, headers, _ = onboard(client, basics={"goals": ["smoking"]}, history={"smoking_status": "current"})
    r = client.post(f"/users/{uid}/checkin", headers=headers, json={"barriers": ["craving"]}).json()
    assert r["message_key"] == "craving_tip"
    assert "pharmacist" in r["message"] and "licensed smoking-cessation clinic" in r["message"]
    assert "80050" not in r["message"]  # no unverified phone numbers
    assert "substitution" in r["adjusted_actions"][0]["tags"]


def test_recipes_endpoint_and_cooking_steps_come_with_a_recipe(client, clock):
    all_recipes = client.get("/recipes").json()
    assert len(all_recipes) >= 18 and all(r["note"] == "General guidance, not medical advice." for r in all_recipes)
    diabetic = client.get("/recipes?tag=diabetes_friendly").json()
    assert diabetic and all("diabetes_friendly" in r["tags"] for r in diabetic)
    assert client.get(f"/recipes/{all_recipes[0]['id']}").json()["id"] == all_recipes[0]["id"]
    assert client.get("/recipes/nope").status_code == 404

    uid, headers, data = onboard(client, basics={"goals": ["nutrition"]})
    assert data["today"]["recipes"] == {}  # tier 1 is water with meals: no cooking
    store = client.app.state.store
    state = store.get_state(uid)
    state.current_tier[Behaviour.nutrition] = 4
    store.save_state(state)
    clock.advance(days=1)
    today = client.get(f"/users/{uid}/today", headers=headers).json()
    cooking = [a["action"]["id"] for a in today["actions"] if "cooking" in a["action"]["tags"]]
    assert cooking and set(today["recipes"]) == set(cooking)
