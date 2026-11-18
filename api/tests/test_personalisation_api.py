"""Backend personalisation over HTTP: per-goal plan details, the daily anchor, follow-up questions, AI-assisted
sign-up and the weekly recap. The LLM is always a fake here: no real calls."""

import json
import logging

import pytest
from api.app import create_app
from api.auth import SUGGEST_MAX_CALLS
from api.messages import FOLLOW_UPS, MESSAGES, catalogue, show_follow_up
from fastapi.testclient import TestClient
from rebound_engine import config
from test_api import Clock, _body, complete_all, onboard

NAME = "Zaina"
SECRET_TEXT = "I work night shifts and have two kids"


class FakeChat:
    """Records every message it is sent and answers with a fixed reply (or raises)."""

    def __init__(self, reply: str | Exception = "{}") -> None:
        self.reply, self.sent = reply, []

    def __call__(self, messages):
        self.sent.append(messages)
        if isinstance(self.reply, Exception):
            raise self.reply
        return self.reply

    def text(self) -> str:
        return json.dumps(self.sent, ensure_ascii=False)


@pytest.fixture
def clock():
    return Clock()


def make_client(clock, chat=None):
    return TestClient(create_app(database_url="sqlite:///:memory:", clock=clock, llm_chat=chat))


@pytest.fixture
def client(clock):
    with make_client(clock) as c:
        yield c


# ---------- 1. per-goal plan details ----------


def test_plan_has_one_goal_entry_per_active_behaviour(client):
    _, _, data = onboard(client)
    goals = data["plan_summary"]["goals"]
    assert [g["behaviour"] for g in goals] == data["plan_summary"]["behaviours"]
    move = goals[0]
    assert move["tier"] >= 1 and move["max_tier"] >= move["tier"] and move["start_reason"]
    assert move["good_days_to_next"] == config.STEP_UP_SUCCESSES
    assert move["last_change"] is None and move["today_note"] is None


def test_plan_shows_the_step_up_and_counts_down(client, clock):
    uid, headers, _ = onboard(client, basics={"goals": ["movement"]})
    complete_all(client, uid, headers)
    goal = client.get(f"/users/{uid}/plan", headers=headers).json()["goals"][0]
    assert goal["good_days_to_next"] == config.STEP_UP_SUCCESSES - 1
    for _ in range(config.STEP_UP_SUCCESSES - 1):
        clock.advance(days=1)
        complete_all(client, uid, headers)
    goal = client.get(f"/users/{uid}/plan", headers=headers).json()["goals"][0]
    assert goal["last_change"]["kind"] == "stepped_up" and goal["last_change"]["reason"]
    assert goal["good_days_to_next"] == config.STEP_UP_SUCCESSES


def test_check_in_shows_as_last_change_and_today_note(client):
    uid, headers, _ = onboard(client, basics={"goals": ["movement"]}, baseline={"active_days_per_week": 3})
    client.post(f"/users/{uid}/checkin", headers=headers, json={"barriers": ["time"]})
    goal = client.get(f"/users/{uid}/plan", headers=headers).json()["goals"][0]
    assert goal["last_change"]["kind"] == "eased" and goal["last_change"]["barrier"] == "time"
    assert goal["today_note"]


def test_top_level_has_no_good_days_to_next(client):
    _, _, data = onboard(client, screening={"chest_pain": True})  # movement capped at the gentle level
    move = data["plan_summary"]["goals"][0]
    assert move["tier"] == move["max_tier"] and move["good_days_to_next"] is None


# ---------- 2. anchor ----------


def test_anchor_replaces_the_generic_phrase_only(client):
    _, _, data = onboard(client, basics={"goals": ["movement"]}, baseline={"active_days_per_week": 3},
                         preferences={"anchor": "after maghrib"})
    move = data["today"]["actions"][0]["action"]
    assert move["id"] == "mv_t2_march_in_place"  # tier 2, indoor first: the step with the generic phrase
    assert move["title"]["en"].endswith("right after maghrib") and "something you" not in move["title"]["en"]


def test_anchor_used_in_simple_and_arabic_titles(client):
    from api.app import with_anchor
    from rebound_engine.actions import default_library
    march = next(a for a in default_library() if a.id == "mv_t2_march_in_place")
    for lang in ("en", "ar"):
        anchored = with_anchor(march, "after maghrib")
        assert "maghrib" in getattr(anchored.title, lang) and "maghrib" in getattr(anchored.simple, lang)
    other = next(a for a in default_library() if a.id == "mv_t1_home_walk")
    assert with_anchor(other, "after maghrib") == other


def test_anchor_never_appears_in_care_or_safety_text(client):
    uid, headers, _ = onboard(client, preferences={"anchor": "after maghrib"})
    care = client.post(f"/users/{uid}/checkin", headers=headers, json={"barriers": ["illness_pain"]}).json()
    assert "maghrib" not in care["message"]
    red = client.post(f"/users/{uid}/checkin", headers=headers, json={"free_text": "I have chest pain"}).json()
    assert red["red_flag"] and "maghrib" not in red["message"]
    for action in care["adjusted_actions"]:
        assert "maghrib" not in action["limits"] and "maghrib" not in action["rationale"]


# ---------- 3. follow-up questions ----------


def test_follow_up_bank_is_served_with_rules(client):
    content = client.get("/content/onboarding").json()
    ids = {q["id"] for q in content["follow_ups"]}
    assert {"anchor", "shifts", "iftar_time", "family_fasting", "caregiver", "quiet_hours", "smoking_goal"} <= ids
    for q in content["follow_ups"]:
        assert q["text"] and q["fills"] and q["show_if"]
        assert not q["fills"].startswith("screening.")  # the health check is always asked in full
    assert set(content["questions"]) >= {"chest_pain", "dizziness_or_fainting"}


@pytest.mark.parametrize(("answers", "shown", "hidden"), [
    ({"basics": {"goals": ["sleep"]}}, "quiet_hours", "anchor"),
    ({"basics": {"goals": ["movement"]}}, "anchor", "quiet_hours"),
    ({"history": {"smoking_status": "current"}}, "smoking_goal", "shifts"),
    ({"basics": {"schedule_type": "shift"}}, "shifts", "smoking_goal"),
    ({"preferences": {"fasting_ramadan": True, "household": "family"}}, "family_fasting", "shifts"),
    ({"preferences": {"fasting_ramadan": True, "household": "alone"}}, "iftar_time", "family_fasting"),
    ({"preferences": {"household": "children"}}, "caregiver", "iftar_time"),
    ({"preferences": {"household": "alone"}}, None, "caregiver"),
])
def test_show_if_rules(answers, shown, hidden):
    by_id = {q["id"]: q for q in FOLLOW_UPS}
    if shown:
        assert show_follow_up(by_id[shown], answers)
    assert not show_follow_up(by_id[hidden], answers)


def test_follow_up_texts_have_simple_variants():
    keys = {e["key"] for e in catalogue()}
    assert {f"follow_up.{q['id']}" for q in FOLLOW_UPS} <= keys


# ---------- 4. AI-assisted sign-up ----------

GOOD_REPLY = json.dumps({
    "goals": ["movement", "sleep", "flying"], "shift_worker": True, "fasts_in_ramadan": "yes",
    "household": "children", "caregiver": False, "current_smoker": False, "managing": ["diabetes", "cancer"],
    "anchor": "after my night shift", "screening": {"chest_pain": False}, "pregnant": "no",
})


def test_suggest_keeps_valid_answers_and_drops_invalid_ones(clock):
    chat = FakeChat(GOOD_REPLY)
    with make_client(clock, chat) as c:
        r = c.post("/content/onboarding/suggest",
                   json={"text": "I want to walk more and sleep better. Night shifts, two kids, diabetes. "
                                 "Best time is after my night shift.", "lang": "en"}).json()
    s = r["suggestions"]
    assert r["red_flag"] is False and r["source"] == "llm"
    assert s["goals"] == ["movement", "sleep"]  # "flying" dropped
    assert s["schedule_type"] == "shift" and s["fasting_ramadan"] is None  # "yes" isn't a bool: dropped
    assert s["household"] == "children" and s["managing"] == ["diabetes"]  # "cancer" isn't a chip: dropped
    assert s["anchor"] == "after my night shift"
    assert "screening" not in s and "pregnant" not in s  # the health check is never suggested
    assert {"shifts", "anchor", "caregiver", "quiet_hours"} <= set(r["follow_ups"])


def test_suggest_drops_an_anchor_the_person_never_wrote(clock):
    with make_client(clock, FakeChat(json.dumps({"anchor": "after fajr prayer"}))) as c:
        r = c.post("/content/onboarding/suggest", json={"text": "I want to move more", "lang": "en"}).json()
    assert r["suggestions"]["anchor"] is None


def test_suggest_smoking_goal_needs_a_current_smoker(clock):
    with make_client(clock, FakeChat(json.dumps({"goals": ["smoking"], "current_smoker": False}))) as c:
        r = c.post("/content/onboarding/suggest", json={"text": "I want to quit", "lang": "en"}).json()
    assert "smoking" not in r["suggestions"]["goals"]


@pytest.mark.parametrize("reply", ["not json at all", "[1, 2]", RuntimeError("down")])
def test_unreadable_llm_output_or_errors_fall_back_to_keywords(clock, reply):
    with make_client(clock, FakeChat(reply)) as c:
        r = c.post("/content/onboarding/suggest", json={"text": SECRET_TEXT, "lang": "en"})
    assert r.status_code == 200
    data = r.json()
    assert data["source"] == "keywords" and data["suggestions"]["schedule_type"] == "shift"


def test_wrongly_typed_llm_fields_are_dropped_not_guessed(clock):
    with make_client(clock, FakeChat(json.dumps({"goals": "movement", "household": 3, "caregiver": "true"}))) as c:
        s = c.post("/content/onboarding/suggest", json={"text": SECRET_TEXT, "lang": "en"}).json()["suggestions"]
    assert s["goals"] == [] and s["household"] is None and s["caregiver"] is None


def test_keyword_fallback_without_a_key(client):
    r = client.post("/content/onboarding/suggest",
                    json={"text": "I smoke and fast in Ramadan, I live with my parents and have diabetes",
                          "lang": "en"}).json()
    s = r["suggestions"]
    assert r["source"] == "keywords"
    assert s["smoking_status"] == "current" and s["fasting_ramadan"] is True
    assert s["household"] == "older_relatives" and s["managing"] == ["diabetes"]
    assert "smoking_goal" in r["follow_ups"] and "iftar_time" in r["follow_ups"]


def test_red_flag_text_never_reaches_the_llm(clock):
    chat = FakeChat(GOOD_REPLY)
    with make_client(clock, chat) as c:
        r = c.post("/content/onboarding/suggest", json={"text": "I get chest pain when I walk", "lang": "en"}).json()
    assert r["red_flag"] is True and r["message"] == MESSAGES["seek_care"]["en"]
    assert r["suggestions"] is None and chat.sent == []


def test_suggest_text_is_not_stored_or_logged(clock, caplog):
    chat = FakeChat(GOOD_REPLY)
    with caplog.at_level(logging.DEBUG), make_client(clock, chat) as c:
        c.post("/content/onboarding/suggest", json={"text": SECRET_TEXT, "lang": "en"})
        store = c.app.state.store
        with store._tx() as db:
            for table in ("user_meta", "profiles", "profiles_sensitive", "states", "events"):
                assert db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0
    assert SECRET_TEXT not in caplog.text


def test_suggest_sends_only_the_text_and_language(clock):
    chat = FakeChat(GOOD_REPLY)
    with make_client(clock, chat) as c:
        c.post("/content/onboarding/suggest", json={"text": SECRET_TEXT, "lang": "ar"})
    user_messages = [m["content"] for call in chat.sent for m in call if m["role"] == "user"]
    assert user_messages == [f"[lang=ar]\n{SECRET_TEXT}"]


def test_suggest_text_limit(client):
    ok = client.post("/content/onboarding/suggest", json={"text": "x" * 1000, "lang": "en"})
    too_long = client.post("/content/onboarding/suggest", json={"text": "x" * 1001, "lang": "en"})
    assert ok.status_code == 200 and too_long.status_code == 422
    assert "x" * 1001 not in too_long.text  # validation errors don't echo the text


def test_suggest_is_limited_per_ip_per_hour(clock):
    chat = FakeChat(GOOD_REPLY)
    with make_client(clock, chat) as c:
        def call(ip="203.0.113.7"):
            return c.post("/content/onboarding/suggest", json={"text": "I want to walk", "lang": "en"},
                          headers={"X-Forwarded-For": f"{ip}, 10.0.0.1"})

        for _ in range(SUGGEST_MAX_CALLS):
            assert call().status_code == 200
        assert call().status_code == 429
        assert len(chat.sent) == SUGGEST_MAX_CALLS  # a blocked call never reaches the LLM
        assert call(ip="198.51.100.9").status_code == 200  # other people unaffected
        clock.advance(hours=1)
        assert call().status_code == 200


# ---------- 5. weekly recap ----------


def _week(client, clock, uid, headers):
    for _ in range(7):
        complete_all(client, uid, headers)
        clock.advance(days=1)


def test_recap_facts_from_the_users_own_events(client, clock):
    uid, headers, _ = onboard(client)
    _week(client, clock, uid, headers)
    r = client.get(f"/users/{uid}/recap", headers=headers).json()
    assert r["written_by"] == "template" and r["summary"]
    facts = r["facts"]
    assert {g["behaviour"] for g in facts["goals"]} == {"movement", "sleep"}
    assert all(g["how"] == "mostly_done" for g in facts["goals"])
    assert any(c["kind"] == "stepped_up" for g in facts["goals"] for c in g["level_changes"])


def test_recap_llm_writes_from_facts_only_and_never_sees_the_name(clock):
    chat = FakeChat("You did most of your steps this week. One step moved up to level 2. Keep it gentle.")
    with make_client(clock, chat) as c:
        uid, headers, _ = onboard(c, preferences={"display_name": NAME})
        _week(c, clock, uid, headers)
        r = c.get(f"/users/{uid}/recap", headers=headers).json()
    assert r["written_by"] == "llm" and r["summary"].startswith("You did most")
    assert NAME not in chat.text() and uid not in chat.text()


@pytest.mark.parametrize("reply", [
    "You did 6 of 7 steps this week. Great job.",  # a count, not a level
    "Great week. You should see a doctor about your blood pressure.",  # medical advice
    "Great week. Keep your streak going!",  # streak language
    "Great week.",  # one sentence
    RuntimeError("timeout"),
])
def test_recap_falls_back_to_the_template_on_bad_llm_text(clock, reply):
    with make_client(clock, FakeChat(reply)) as c:
        uid, headers, _ = onboard(c)
        _week(c, clock, uid, headers)
        r = c.get(f"/users/{uid}/recap", headers=headers).json()
    assert r["written_by"] == "template"
    assert "streak" not in r["summary"] and "doctor" not in r["summary"]


def test_recap_calls_the_llm_at_most_once_a_day(clock):
    chat = FakeChat("You did most of your steps this week. One step moved up to level 2. Keep it gentle.")
    with make_client(clock, chat) as c:
        uid, headers, _ = onboard(c)
        _week(c, clock, uid, headers)
        first = c.get(f"/users/{uid}/recap", headers=headers).json()
        assert c.get(f"/users/{uid}/recap", headers=headers).json() == first  # cached
        other = c.get(f"/users/{uid}/recap", headers=headers, params={"days": 14}).json()
        assert other["written_by"] == "template" and len(chat.sent) == 1  # no second LLM call today
        clock.advance(days=1)
        c.get(f"/users/{uid}/recap", headers=headers)
        assert len(chat.sent) == 2  # a new day, a new recap


def test_recap_template_in_arabic_and_simple(client, clock):
    uid, headers, _ = onboard(client, basics={"language": "ar"}, preferences={"reading_level": "simple"})
    _week(client, clock, uid, headers)
    summary = client.get(f"/users/{uid}/recap", headers=headers).json()["summary"]
    assert any("؀" <= ch <= "ۿ" for ch in summary)


def test_recap_hidden_after_a_red_flag(client):
    uid, headers, _ = onboard(client)
    client.post(f"/users/{uid}/checkin", headers=headers, json={"free_text": "I have chest pain"})
    assert client.get(f"/users/{uid}/recap", headers=headers).status_code == 409


def test_recap_needs_the_token_and_valid_days(client):
    uid, headers, _ = onboard(client)
    assert client.get(f"/users/{uid}/recap").status_code == 401
    assert client.get(f"/users/{uid}/recap", headers=headers, params={"days": 0}).status_code == 422
    assert client.get(f"/users/{uid}/recap", headers=headers,
                      params={"days": config.HISTORY_KEEP_DAYS + 1}).status_code == 422


# ---------- display name ----------


def test_display_name_set_at_sign_up_and_settings_and_exported(client):
    r = client.post("/users", json=_body(preferences={"display_name": "  Zaina  "}))
    uid, headers = r.json()["user_id"], {"Authorization": f"Bearer {r.json()['token']}"}
    assert client.get(f"/users/{uid}/export", headers=headers).json()["profile"]["preferences"]["display_name"] == NAME
    r = client.patch(f"/users/{uid}/settings", headers=headers, json={"preferences": {"display_name": "Z"}})
    assert r.json()["preferences"]["display_name"] == "Z"
    assert client.patch(f"/users/{uid}/settings", headers=headers,
                        json={"preferences": {"display_name": " "}}).status_code == 422
    assert client.delete(f"/users/{uid}", headers=headers).status_code == 204
