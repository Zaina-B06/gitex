"""Read-only community events: token required, filtered to the user, no personal data, every entry real or labelled."""

import pytest
from api.app import create_app
from api.community import CommunityEvent, load_events
from fastapi.testclient import TestClient
from test_api import Clock, onboard

FIELDS = set(CommunityEvent.model_fields)


@pytest.fixture
def client():
    with TestClient(create_app(database_url="sqlite:///:memory:", clock=Clock())) as c:
        yield c


def events(client, uid, headers, **params):
    r = client.get("/community/events", headers=headers, params={"user_id": uid, **params})
    assert r.status_code == 200, r.text
    return r.json()


def test_every_entry_is_real_with_a_source_or_labelled_example():
    entries = load_events()
    assert any(not e.example for e in entries) and any(e.example for e in entries)
    for e in entries:
        if e.example:
            assert e.title.en.startswith("Example:") and e.source_url is None
        else:
            assert e.source_url.startswith("https://") and e.last_checked is not None


def test_needs_the_users_token(client):
    uid, headers, _ = onboard(client)
    assert client.get("/community/events", params={"user_id": uid}).status_code == 401
    assert client.get("/community/events", params={"user_id": uid},
                      headers={"Authorization": "Bearer nope"}).status_code == 401


def test_no_personal_data_in_the_response(client):
    uid, headers, _ = onboard(client, history={"motivation_reason": "Keep up with my kids"})
    r = client.get("/community/events", headers=headers, params={"user_id": uid})
    assert all(set(e) == FIELDS for e in r.json())
    assert uid not in r.text and "Keep up with my kids" not in r.text


def test_filters_follow_goals_space_mobility_language_and_household(client):
    uid, h, _ = onboard(client, basics={"goals": ["sleep"]})
    assert all(not e["behaviours"] or "sleep" in e["behaviours"] for e in events(client, uid, h))

    uid, h, _ = onboard(client, preferences={"space_preference": "women_only_spaces"})
    got = events(client, uid, h)
    assert got and all(e["women_only"] for e in got if "movement" in e["behaviours"])

    uid, h, _ = onboard(client, screening={"mobility_limitation": "mobility_aid"})
    got = events(client, uid, h)
    assert got and all(e["wheelchair_accessible"] for e in got)

    uid, h, _ = onboard(client, basics={"language": "ar"})
    assert all(not e["languages"] or "ar" in e["languages"] for e in events(client, uid, h))

    uid, h, _ = onboard(client)
    family = events(client, uid, h, household="children")
    assert family and all(e["family_friendly"] for e in family)
    assert all(e["city"] == "Dubai" for e in events(client, uid, h, city="dubai"))
    assert client.get("/community/events", headers=h, params={"user_id": uid, "household": "zoo"}).status_code == 422
