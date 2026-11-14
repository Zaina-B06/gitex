"""HTTP tests for the §7 endpoints (demo and dashboard routes are tested in their own files)."""

from datetime import UTC, datetime, timedelta

import pytest
from api.app import CATCH_UP_MAX_DAYS, create_app
from api.llm_client import KeywordClassifier
from api.messages import MESSAGES
from fastapi.testclient import TestClient
from rebound_engine.demo import demo_payload
from rebound_engine.policy import BARRIER_MESSAGE

BARRIER_ENGINE_KEYS = set(BARRIER_MESSAGE.values())
OTHER_ENGINE_KEYS = {"see_doctor", "check_with_doctor", "seek_care", "buddy_offer", "lighter_option", "eid_rest"}


class Clock:
    def __init__(self) -> None:
        self.now = datetime(2026, 11, 14, 5, 0, tzinfo=UTC)  # 09:00 in Abu Dhabi

    def __call__(self) -> datetime:
        return self.now

    def advance(self, days: int = 0, hours: int = 0) -> None:
        self.now += timedelta(days=days, hours=hours)


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def client(clock):
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock)) as c:
        yield c


def _body(**groups) -> dict:
    body = demo_payload().model_dump(mode="json")
    for group, fields in groups.items():
        body[group] = {**body[group], **fields} if isinstance(body.get(group), dict) else fields
    return body


def onboard(client, **groups):
    r = client.post("/users", json=_body(**groups))
    assert r.status_code == 201, r.text
    data = r.json()
    return data["user_id"], {"Authorization": f"Bearer {data['token']}"}, data


def complete_all(client, uid, headers, kind="completed"):
    for a in client.get(f"/users/{uid}/today", headers=headers).json()["actions"]:
        r = client.post(f"/users/{uid}/events", headers=headers, json={"action_id": a["action"]["id"], "type": kind})
        assert r.status_code == 200, r.text
    return client.get(f"/users/{uid}/state", headers=headers).json()


# ---------- onboarding and auth ----------


def test_onboard_returns_token_and_one_action_per_goal(client):
    uid, _, data = onboard(client)
    assert data["token"] and data["user_id"] == uid
    assert [a["action"]["behaviour"] for a in data["today"]["actions"]] == ["movement", "sleep"]
    assert data["today"]["day"] == 1
    assert data["state"]["engagement_state"] == "active"
    assert len(data["today"]["messages"]) == len(data["today"]["message_keys"])


def test_onboard_rejects_bad_input(client):
    assert client.post("/users", json={**_body(), "timezone": "Mars/Base"}).status_code == 422
    assert client.post("/users", json={**_body(), "surprise": 1}).status_code == 422
    assert client.post("/users", json=_body(basics={"age_years": 12})).status_code == 422


def test_onboard_needs_screening_consent(client):
    r = client.post("/users", json=_body(consents={"screening": False}))
    assert r.status_code == 422
    assert client.post("/users", json=_body(consents={"screening": True})).status_code == 201


def test_cors_allows_localhost_only_in_demo_or_dev(clock):
    def allowed(origin, **kw):
        with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock,
                                   frontend_url="https://app.example", **kw)) as c:
            r = c.options("/users", headers={"Origin": origin, "Access-Control-Request-Method": "POST"})
            return r.headers.get("access-control-allow-origin") == origin

    assert allowed("https://app.example")
    assert not allowed("http://localhost:5173")
    assert allowed("http://localhost:5173", dev_mode=True)
    assert allowed("http://localhost:5173", demo_mode=True)
    assert not allowed("https://evil.example", dev_mode=True)


def test_user_routes_need_that_users_token(client):
    uid, headers, _ = onboard(client)
    other_uid, other_headers, _ = onboard(client)
    assert client.get(f"/users/{uid}/today").status_code == 401
    assert client.get(f"/users/{uid}/today", headers={"Authorization": "Bearer nope"}).status_code == 401
    assert client.get(f"/users/{uid}/today", headers=other_headers).status_code == 401
    assert client.get("/users/nobody/today", headers=headers).status_code == 401  # same as a wrong token
    assert client.get(f"/users/{uid}/today", headers=headers).status_code == 200
    assert client.delete(f"/users/{other_uid}", headers=headers).status_code == 401


def test_token_is_stored_hashed(client):
    uid, headers, _ = onboard(client)
    token = headers["Authorization"].split()[1]
    meta = client.app.state.store.get_meta(uid)
    assert token not in meta.model_dump_json()


# ---------- daily loop ----------


def test_today_is_stable_within_a_day(client, clock):
    uid, headers, data = onboard(client)
    clock.advance(hours=8)
    again = client.get(f"/users/{uid}/today", headers=headers).json()
    assert [a["action"]["id"] for a in again["actions"]] == [a["action"]["id"] for a in data["today"]["actions"]]


def test_complete_raises_habit_strength_and_rejects_repeats(client):
    uid, headers, data = onboard(client)
    before = data["state"]["habit_strength"]["movement"]
    move_id = data["today"]["actions"][0]["action"]["id"]
    r = client.post(f"/users/{uid}/events", headers=headers, json={"action_id": move_id, "type": "completed"})
    assert r.status_code == 200
    assert r.json()["state"]["habit_strength"]["movement"] > before
    again = client.post(f"/users/{uid}/events", headers=headers, json={"action_id": move_id, "type": "completed"})
    assert again.status_code == 409
    assert client.post(f"/users/{uid}/events", headers=headers,
                       json={"action_id": "made_up", "type": "completed"}).status_code == 409
    assert client.post(f"/users/{uid}/events", headers=headers,
                       json={"action_id": move_id, "type": "no_response"}).status_code == 422


def test_unopened_days_count_as_no_response(client, clock):
    uid, headers, _ = onboard(client)
    clock.advance(days=4)
    state = client.get(f"/users/{uid}/state", headers=headers).json()
    assert state["day"] == 5  # any user route brings the engine up to today
    assert {d["day"] for d in state["history"] if d["outcome"] == "no_response"} == {1, 2, 3, 4}
    events = client.get(f"/users/{uid}/export", headers=headers).json()["events"]
    assert {e["day"] for e in events if e["type"] == "no_response"} == {1, 2, 3, 4}


def test_catch_up_is_capped(client, clock):
    uid, headers, _ = onboard(client)
    clock.advance(days=100)
    assert client.get(f"/users/{uid}/today", headers=headers).json()["day"] == 101
    events = client.get(f"/users/{uid}/export", headers=headers).json()["events"]
    shown_days = {e["day"] for e in events if e["type"] == "action_shown"}
    assert shown_days == {1} | set(range(101 - CATCH_UP_MAX_DAYS, 102))


def test_day_follows_the_users_time_zone(client, clock):
    clock.now = datetime(2026, 11, 14, 19, 30, tzinfo=UTC)  # 23:30 Abu Dhabi, 14:30 New York
    dubai, dubai_h, _ = onboard(client)
    ny_body = {**_body(), "timezone": "America/New_York"}
    ny = client.post("/users", json=ny_body).json()
    clock.advance(hours=1)  # 00:30 next day in Abu Dhabi, still the 14th in New York
    assert client.get(f"/users/{dubai}/today", headers=dubai_h).json()["day"] == 2
    ny_h = {"Authorization": f"Bearer {ny['token']}"}
    assert client.get(f"/users/{ny['user_id']}/today", headers=ny_h).json()["day"] == 1


def test_quiet_hours_respected(client):
    quiet = {"start": "05:00", "end": "12:00"}
    _uid, _headers, data = onboard(client, preferences={"quiet_hours": quiet})
    for a in data["today"]["actions"]:
        assert not 5 <= a["hour"] < 12, a


# ---------- lapse, check-in, recovery ----------


def test_lapse_then_checkin_then_recovery(client, clock):
    uid, headers, _ = onboard(client)
    for _ in range(5):
        complete_all(client, uid, headers)
        clock.advance(days=1)
    tiers_before = client.get(f"/users/{uid}/state", headers=headers).json()["tiers"]
    clock.advance(days=6)  # a week without opening the app
    today = client.get(f"/users/{uid}/today", headers=headers).json()
    assert today["checkin_due"]
    assert today["state_summary"]["engagement_state"] in ("drifting", "lapsed")

    r = client.post(f"/users/{uid}/checkin", headers=headers, json={"barriers": ["time"]}).json()
    assert r["barrier"] == "time" and not r["red_flag"]
    assert r["message_key"] == "implementation_intention" and r["message"]
    assert r["adjusted_actions"]
    assert all(a["tier"] <= tiers_before[a["behaviour"]] for a in r["adjusted_actions"])

    for _ in range(4):
        state = complete_all(client, uid, headers)
        clock.advance(days=1)
    assert state["engagement_state"] in ("recovering", "active")
    assert all(h > 0 for h in state["habit_strength"].values())  # decayed, never reset to zero


def test_adjusted_action_can_be_done_today(client):
    uid, headers, data = onboard(client, baseline={"active_days_per_week": 7})
    move = data["today"]["actions"][0]["action"]
    assert move["tier"] == 3
    r = client.post(f"/users/{uid}/checkin", headers=headers, json={"barriers": ["time"]}).json()
    smaller = next(a for a in r["adjusted_actions"] if a["behaviour"] == "movement")
    assert smaller["tier"] == 2
    today_ids = [a["action"]["id"] for a in client.get(f"/users/{uid}/today", headers=headers).json()["actions"]]
    assert smaller["id"] in today_ids and move["id"] not in today_ids
    done = client.post(f"/users/{uid}/events", headers=headers, json={"action_id": smaller["id"], "type": "completed"})
    assert done.status_code == 200, done.text


def test_free_text_fills_in_only_without_buttons(client, clock):
    uid, headers, _ = onboard(client)
    r = client.post(f"/users/{uid}/checkin", headers=headers, json={"free_text": "Too tired after work"}).json()
    assert r["barrier"] == "energy_fatigue"
    clock.advance(days=1)
    r = client.post(f"/users/{uid}/checkin", headers=headers,
                    json={"barriers": ["forgot"], "free_text": "Too tired after work"}).json()
    assert r["barrier"] == "forgot"


def test_red_flag_free_text_stops_coaching(client):
    uid, headers, _ = onboard(client)
    r = client.post(f"/users/{uid}/checkin", headers=headers, json={"free_text": "I had chest pain on my walk"})
    body = r.json()
    assert body["red_flag"] is True
    assert body["adjusted_actions"] == []
    assert body["message_key"] == "seek_care" and "998" in body["message"] and "800 725462" in body["message"]
    assert "seek_care" in client.get(f"/users/{uid}/today", headers=headers).json()["message_keys"]
    unpause = client.patch(f"/users/{uid}/settings", headers=headers, json={"context": {"paused": False}})
    assert unpause.status_code == 409


def test_red_flag_text_never_reaches_the_classifier(clock):
    seen = []

    class Spy(KeywordClassifier):
        def classify_barrier(self, text):
            seen.append(text)
            return super().classify_barrier(text)

    with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock, classifier=Spy())) as c:
        uid, headers, _ = onboard(c)
        uid2, headers2, _ = onboard(c)
        c.post(f"/users/{uid}/checkin", headers=headers, json={"free_text": "I passed out yesterday"})
        c.post(f"/users/{uid2}/checkin", headers=headers2, json={"free_text": "busy week"})
    assert seen == ["busy week"]


def test_checkin_after_days_away_uses_todays_state(client, clock):
    uid, headers, _ = onboard(client)
    complete_all(client, uid, headers)
    clock.advance(days=6)
    r = client.post(f"/users/{uid}/checkin", headers=headers, json={"barriers": ["time"]})
    assert r.status_code == 200, r.text
    today = client.get(f"/users/{uid}/today", headers=headers).json()
    assert today["day"] == 7
    assert today["checkin_due"] is False  # the lapse was found before the check-in, so no second ask today


def test_one_checkin_per_day_but_red_flags_always_get_through(client, clock):
    uid, headers, _ = onboard(client)
    assert client.post(f"/users/{uid}/checkin", headers=headers, json={"barriers": ["time"]}).status_code == 200
    assert client.post(f"/users/{uid}/checkin", headers=headers, json={"barriers": ["forgot"]}).status_code == 409
    r = client.post(f"/users/{uid}/checkin", headers=headers, json={"free_text": "I can’t breathe on the stairs"})
    assert r.status_code == 200 and r.json()["red_flag"] is True
    clock.advance(days=1)
    assert client.post(f"/users/{uid}/checkin", headers=headers, json={"barriers": ["time"]}).status_code == 200


# ---------- explain, settings, delete ----------


def test_explain(client):
    _, _, data = onboard(client)
    action = data["today"]["actions"][0]["action"]
    r = client.get(f"/actions/{action['id']}/explain").json()
    assert r["bct_code"] == action["bct_code"] and r["rationale"] and r["limits"] and r["how_to_turn_off"]
    assert client.get(f"/actions/{action['id']}/explain?lang=ar").json()["how_to_turn_off"] != r["how_to_turn_off"]
    assert client.get("/actions/nope/explain").status_code == 404


def test_settings_merge_and_validate(client):
    uid, headers, _ = onboard(client, preferences={"channel": "whatsapp_style"})
    r = client.patch(f"/users/{uid}/settings", headers=headers,
                     json={"preferences": {"setting": "indoor"}, "consents": {"body": False}})
    assert r.status_code == 200, r.text
    assert r.json()["preferences"]["setting"] == "indoor"
    assert r.json()["preferences"]["channel"] == "whatsapp_style"  # untouched fields kept
    assert r.json()["consents"]["body"] is False
    assert client.patch(f"/users/{uid}/settings", headers=headers,
                        json={"preferences": {"nope": 1}}).status_code == 422
    assert client.patch(f"/users/{uid}/settings", headers=headers,
                        json={"preferences": {"setting": "space"}}).status_code == 422
    r = client.patch(f"/users/{uid}/settings", headers=headers, json={"context": {"heat": True}})
    assert "heat" in r.json()["state"]["context_flags"]


def test_withdrawing_consent_deletes_that_groups_answers(client):
    uid, headers, _ = onboard(client, body={"height_cm": 170, "weight_kg": 70},
                              preferences={"quiet_hours": {"start": "22:00", "end": "06:00"}})
    store = client.app.state.store
    assert store.get_profile(uid).body is not None
    r = client.patch(f"/users/{uid}/settings", headers=headers,
                     json={"consents": {"body": False, "history": False}})
    assert r.status_code == 200, r.text
    profile = store.get_profile(uid)
    assert profile.body is None
    assert profile.history.motivation_reason is None and profile.history.past_helpers == []
    assert profile.preferences.quiet_hours is not None  # other groups untouched
    assert "Keep up with my kids" not in store._conn.execute("SELECT data FROM profiles_sensitive").fetchone()[0]
    # Stays deleted: a later save can't bring the answers back while consent is withdrawn.
    client.patch(f"/users/{uid}/settings", headers=headers, json={"preferences": {"setting": "indoor"}})
    assert store.get_profile(uid).body is None
    # The health check can't be withdrawn; it's needed for a safe plan.
    r = client.patch(f"/users/{uid}/settings", headers=headers, json={"consents": {"screening": False}})
    assert r.status_code == 409


def test_answers_given_without_consent_are_not_stored(client):
    uid, _, _ = onboard(client, body={"height_cm": 170, "weight_kg": 70}, consents={"body": False})
    assert client.app.state.store.get_profile(uid).body is None


def test_export_returns_all_the_users_data(client):
    uid, headers, _ = onboard(client)
    complete_all(client, uid, headers)
    assert client.get(f"/users/{uid}/export").status_code == 401
    r = client.get(f"/users/{uid}/export", headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["profile"]["user_id"] == uid
    assert data["profile"]["history"]["motivation_reason"] == "Keep up with my kids"
    assert data["state"]["user_id"] == uid
    assert {e["type"] for e in data["events"]} >= {"action_shown", "completed"}
    assert data["account"]["timezone"] == "Asia/Dubai"
    assert "token_hash" not in data["account"]
    assert headers["Authorization"].split()[1] not in r.text


def test_delete_removes_every_row(client):
    uid, headers, _ = onboard(client)
    complete_all(client, uid, headers)
    store = client.app.state.store
    assert client.delete(f"/users/{uid}", headers=headers).status_code == 204
    assert client.get(f"/users/{uid}/state", headers=headers).status_code == 401
    for table in ("user_meta", "profiles", "profiles_sensitive", "states", "events"):
        n = store._conn.execute(f"SELECT COUNT(*) FROM {table} WHERE user_id = ?", (uid,)).fetchone()[0]
        assert n == 0, table


# ---------- messages ----------


def test_every_engine_message_key_has_en_and_ar():
    for key in BARRIER_ENGINE_KEYS | OTHER_ENGINE_KEYS:
        assert MESSAGES[key]["en"] and MESSAGES[key]["ar"], key


def test_arabic_user_gets_arabic_messages(client):
    _, _, data = onboard(client, basics={"language": "ar"}, screening={"heart_condition_or_high_bp": True})
    assert "check_with_doctor" in data["today"]["message_keys"]
    assert MESSAGES["check_with_doctor"]["ar"] in data["today"]["messages"]
