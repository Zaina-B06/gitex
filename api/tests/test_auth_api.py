"""Sign-in: optional username + password at sign-up or later, login issues a new token, logout revokes it."""

import pytest
from api.app import create_app
from api.auth import LOGIN_MAX_FAILURES
from fastapi.testclient import TestClient
from test_api import Clock, _body, onboard

PASSWORD = "correct horse 42"
LOGIN = {"username": "Zaina_B", "password": PASSWORD}
DEMO_KEY = {"X-Demo-Key": "test-demo-key"}


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def client(clock):
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock)) as c:
        yield c


def _signup(client, **login):
    r = client.post("/users", json={**_body(), "login": {**LOGIN, **login}})
    assert r.status_code == 201, r.text
    return r.json()["user_id"], {"Authorization": f"Bearer {r.json()['token']}"}


def _login(client, username="zaina_b", password=PASSWORD):
    return client.post("/auth/login", json={"username": username, "password": password})


def test_login_issues_a_new_token_and_both_work(client):
    uid, signup_headers = _signup(client)
    r = _login(client, username="ZAINA_B")  # usernames are case-insensitive
    assert r.status_code == 200 and r.json()["user_id"] == uid
    login_headers = {"Authorization": f"Bearer {r.json()['token']}"}
    assert login_headers != signup_headers
    for h in (signup_headers, login_headers):  # phone + laptop
        assert client.get(f"/users/{uid}/state", headers=h).status_code == 200


def test_wrong_password_and_unknown_username_get_the_same_401(client):
    _signup(client)
    wrong, unknown = _login(client, password="not the password"), _login(client, username="nobody")
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json()


def test_login_rules_and_password_never_echoed(client):
    _signup(client)
    taken = client.post("/users", json={**_body(), "login": LOGIN})
    assert taken.status_code == 409
    for bad in ({"username": "ab", "password": PASSWORD}, {"username": "has space", "password": PASSWORD},
                {"username": "x" * 31, "password": PASSWORD}, {"username": "fine_name", "password": "short7!"}):
        r = client.post("/users", json={**_body(), "login": bad})
        assert r.status_code == 422, bad
        assert bad["password"] not in r.text
    assert PASSWORD not in taken.text


def test_hash_and_password_are_not_in_export(client):
    uid, headers = _signup(client)
    export = client.get(f"/users/{uid}/export", headers=headers)
    assert export.json()["account"]["username"] == "zaina_b"
    stored = client.app.state.store.login("zaina_b")[1]
    assert stored.startswith("scrypt$") and PASSWORD not in stored
    assert stored not in export.text and PASSWORD not in export.text


def test_failed_logins_are_rate_limited_per_username(client, clock):
    _signup(client)
    for _ in range(LOGIN_MAX_FAILURES):
        assert _login(client, password="wrong password").status_code == 401
    assert _login(client).status_code == 429  # even the right password, until the window passes
    assert _login(client, username="someone_else").status_code == 401  # other usernames unaffected
    clock.advance(hours=1)  # past the 15-minute window
    assert _login(client).status_code == 200


def test_logout_revokes_only_the_current_token(client):
    uid, first = _signup(client)
    second = {"Authorization": f"Bearer {_login(client).json()['token']}"}
    assert client.post("/auth/logout", headers=second).status_code == 204
    assert client.get(f"/users/{uid}/state", headers=second).status_code == 401
    assert client.get(f"/users/{uid}/state", headers=first).status_code == 200
    assert client.post("/auth/logout").status_code == 401


def test_settings_add_login_once_for_users_without_one(client):
    uid, headers, _ = onboard(client)
    r = client.patch(f"/users/{uid}/settings", headers=headers, json={"login": LOGIN})
    assert r.status_code == 200 and PASSWORD not in r.text
    assert _login(client).json()["user_id"] == uid
    again = client.patch(f"/users/{uid}/settings", headers=headers, json={"login": {**LOGIN, "username": "new"}})
    assert again.status_code == 409


def test_delete_removes_the_login_and_every_token(client):
    uid, headers = _signup(client)
    other = {"Authorization": f"Bearer {_login(client).json()['token']}"}
    assert client.delete(f"/users/{uid}", headers=headers).status_code == 204
    assert _login(client).status_code == 401
    assert client.get(f"/users/{uid}/state", headers=other).status_code == 401
    _signup(client)  # the username is free again


def test_demo_personas_have_no_login(clock):
    app = create_app(database_url="sqlite:///:memory:", clock=clock, demo_mode=True, demo_key="test-demo-key")
    with TestClient(app) as c:
        for p in c.post("/demo/seed", headers=DEMO_KEY).json()["personas"]:
            h = {"Authorization": f"Bearer {p['token']}"}
            assert c.get(f"/users/{p['user_id']}/export", headers=h).json()["account"]["username"] is None
