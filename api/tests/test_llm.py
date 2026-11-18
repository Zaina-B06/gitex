"""LLM layer (TASK_01_C), offline: a fake provider stands in for Groq/OpenAI/Azure. No network calls."""

import json

import pytest
from api.app import create_app
from api.llm_client import KeywordClassifier, LLMClassifier, default_classifier, llm_red_flag_check
from fastapi.testclient import TestClient
from llm import classify_barrier
from rebound_engine.models import Barrier
from test_api import Clock, onboard


class FakeChat:
    """Returns a fixed reply (or raises) and records every message it was sent."""

    def __init__(self, reply: str | None = None, error: Exception | None = None) -> None:
        self.reply, self.error, self.seen = reply, error, []

    def __call__(self, messages):
        self.seen.append(messages[-1]["content"])
        if self.error:
            raise self.error
        return self.reply


def answer(barrier, confidence=0.9) -> str:
    return json.dumps({"barrier": barrier, "confidence": confidence})


# ---------- llm.classify_barrier ----------

def test_valid_reply_is_a_barrier():
    out = classify_barrier("night shifts all week", "en", chat=FakeChat(answer("schedule_change")))
    assert out == {"barrier": Barrier.schedule_change, "confidence": 0.9}


@pytest.mark.parametrize("reply", ["not json", answer("sleepy"), '{"barrier": "time"}', "[1, 2]",
                                   answer("time", "high"), answer("time", 1.7)])
def test_bad_output_is_none(reply):
    assert classify_barrier("busy", "en", chat=FakeChat(reply))["barrier"] is None


def test_low_confidence_is_none():
    assert classify_barrier("meh", "en", chat=FakeChat(answer("low_motivation", 0.4)))["barrier"] is None


def test_only_text_and_language_are_sent():
    chat = FakeChat(answer("time"))
    classify_barrier("too busy", "ar", chat=chat)
    assert chat.seen == ["[lang=ar]\ntoo busy"]


# ---------- api/llm_client.py fallbacks ----------

def test_timeout_falls_back_to_keywords():
    assert LLMClassifier(FakeChat(error=TimeoutError())).classify_barrier("so tired today") == Barrier.energy_fatigue


def test_no_key_means_keywords(monkeypatch):
    for k in ("LLM_PROVIDER", "GROQ_API_KEY", "OPENAI_API_KEY", "AZURE_OPENAI_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    assert isinstance(default_classifier(), KeywordClassifier)


def test_red_flag_check_errors_add_nothing():
    assert llm_red_flag_check(FakeChat(error=OSError()))("my chest feels tight", "en") is False
    assert llm_red_flag_check(FakeChat("garbage"))("my chest feels tight", "en") is False


# ---------- through the check-in endpoint ----------

@pytest.fixture
def clock():
    return Clock()


def test_llm_barrier_used_when_no_button(clock):
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock,
                               classifier=LLMClassifier(FakeChat(answer("schedule_change"))))) as c:
        uid, headers, _ = onboard(c)
        r = c.post(f"/users/{uid}/checkin", headers=headers, json={"free_text": "rota got moved around"}).json()
    assert r["barrier"] == "schedule_change"


def test_buttons_beat_the_classifier(clock):
    chat = FakeChat(answer("schedule_change"))
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock, classifier=LLMClassifier(chat))) as c:
        uid, headers, _ = onboard(c)
        r = c.post(f"/users/{uid}/checkin", headers=headers,
                   json={"barriers": ["forgot"], "free_text": "rota got moved around"}).json()
    assert r["barrier"] == "forgot" and chat.seen == []


def test_red_flag_text_never_reaches_the_provider(clock):
    classify, flag = FakeChat(answer("time")), FakeChat('{"red_flag": false}')
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock, classifier=LLMClassifier(classify),
                               red_flag_check=llm_red_flag_check(flag))) as c:
        uid, headers, _ = onboard(c)
        r = c.post(f"/users/{uid}/checkin", headers=headers, json={"free_text": "I had chest pain on my walk"}).json()
    assert r["red_flag"] is True
    assert classify.seen == [] and flag.seen == []


def test_llm_can_add_a_red_flag(clock):
    flag = FakeChat('{"red_flag": true}')
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock,
                               red_flag_check=llm_red_flag_check(flag))) as c:
        uid, headers, _ = onboard(c)
        r = c.post(f"/users/{uid}/checkin", headers=headers, json={"free_text": "my chest feels tight lately"}).json()
        today = c.get(f"/users/{uid}/today", headers=headers).json()
        unpause = c.patch(f"/users/{uid}/settings", headers=headers, json={"context": {"paused": False}})
    assert r["red_flag"] is True and r["adjusted_actions"] == []
    assert "998" in r["message"] and "800 725462" in r["message"]
    assert "seek_care" in today["message_keys"]  # coaching stopped, like a keyword red flag
    assert unpause.status_code == 409


def test_llm_cannot_remove_a_red_flag(clock):
    flag = FakeChat('{"red_flag": false}')
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=clock,
                               red_flag_check=llm_red_flag_check(flag))) as c:
        uid, headers, _ = onboard(c)
        r = c.post(f"/users/{uid}/checkin", headers=headers, json={"free_text": "I passed out yesterday"}).json()
    assert r["red_flag"] is True
