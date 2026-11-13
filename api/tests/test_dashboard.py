"""Outcome dashboard (simulation JSON) and employer view (aggregates only, k >= 10)."""

import json

import pytest
from api.app import EMPLOYER_MIN_GROUP, create_app
from fastapi.testclient import TestClient
from test_api import Clock, _body

ORG_KEY = {"X-Org-Key": "test-org-key"}


@pytest.fixture
def client(tmp_path):
    dashboard = tmp_path / "dashboard.json"
    dashboard.write_text(json.dumps({"run": "run_x", "scenarios": {}}), encoding="utf-8")
    app = create_app(database_url="sqlite:///:memory:", clock=Clock(), org_key="test-org-key",
                     dashboard_path=dashboard)
    with TestClient(app) as c:
        yield c


def join(client, org_id, n):
    users = []
    for _ in range(n):
        r = client.post("/users", json={**_body(), "org_id": org_id}).json()
        users.append((r["user_id"], {"Authorization": f"Bearer {r['token']}"}))
    return users


def test_outcomes_serves_the_exported_file(client, tmp_path):
    assert client.get("/dashboard/outcomes").json()["run"] == "run_x"
    with TestClient(create_app(database_url="sqlite:///:memory:", dashboard_path=tmp_path / "absent.json")) as c:
        assert c.get("/dashboard/outcomes").status_code == 404


def test_employer_needs_the_org_key(client):
    join(client, "acme", EMPLOYER_MIN_GROUP)
    assert client.get("/dashboard/employer?org_id=acme").status_code == 401
    assert client.get("/dashboard/employer?org_id=acme", headers={"X-Org-Key": "wrong"}).status_code == 401
    with TestClient(create_app(database_url="sqlite:///:memory:")) as no_key:
        assert no_key.get("/dashboard/employer?org_id=acme", headers=ORG_KEY).status_code == 401


def test_employer_refuses_groups_below_ten(client):
    join(client, "small", EMPLOYER_MIN_GROUP - 1)
    assert client.get("/dashboard/employer?org_id=small", headers=ORG_KEY).status_code == 403
    assert client.get("/dashboard/employer?org_id=unknown", headers=ORG_KEY).status_code == 403
    join(client, "small", 1)
    assert client.get("/dashboard/employer?org_id=small", headers=ORG_KEY).status_code == 200


def test_employer_returns_aggregates_only(client):
    users = join(client, "acme", EMPLOYER_MIN_GROUP)
    for uid, headers in users[:4]:
        client.post(f"/users/{uid}/checkin", headers=headers, json={"barriers": ["time"]})
    client.post(f"/users/{users[4][0]}/checkin", headers=users[4][1], json={"barriers": ["forgot"]})
    r = client.get("/dashboard/employer?org_id=acme", headers=ORG_KEY)
    assert r.status_code == 200
    data = r.json()
    assert data["group_size"] == EMPLOYER_MIN_GROUP
    assert 0 <= data["active_share"] <= 1
    assert set(data["average_habit_strength"]) == {"movement", "sleep"}
    assert data["top_barriers"][0] == {"barrier": "time", "count": 4}
    for uid, _ in users:
        assert uid not in r.text  # no individual identifiers
