"""Shared store tests: SQLiteStore and PostgresStore must behave exactly like the engine's InMemoryStore.

Postgres tests run only with TEST_DATABASE_URL set (use a throwaway database: its tables are emptied)."""

import json
import os
import random
from datetime import date

import pytest
from api.store import USER_TABLES, PostgresStore, SQLiteStore, UserMeta, open_store, sqlite_path
from rebound_engine.demo import demo_payload, simulate_outcome
from rebound_engine.engine import Engine, InMemoryStore
from rebound_engine.models import Barrier, ContextFlag, Event, EventType

PG_URL = os.getenv("TEST_DATABASE_URL")
needs_pg = pytest.mark.skipif(not PG_URL, reason="set TEST_DATABASE_URL=postgresql://... to test PostgresStore")
DATABASES = ["sqlite", pytest.param("postgres", marks=needs_pg)]


def _count(store, table: str) -> int:
    with store._tx() as c:
        return c.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


@pytest.fixture(params=DATABASES)
def open_db(request, tmp_path):
    """Opens the same database on every call (for reopen tests). Postgres starts with empty tables."""
    opened = []

    def open_():
        s = SQLiteStore(str(tmp_path / "test.db")) if request.param == "sqlite" else PostgresStore(PG_URL)
        opened.append(s)
        return s

    if request.param == "postgres":
        with open_()._tx() as c:
            for table in USER_TABLES:
                c.execute(f"DELETE FROM {table}")
    yield open_
    for s in opened:
        s.close()


@pytest.fixture(params=["in_memory", "db"])
def store(request, open_db):
    yield InMemoryStore() if request.param == "in_memory" else open_db()


def _journey(engine: Engine, uid: str, days: int = 25, seed: int = 1) -> None:
    """A run that exercises every state field: outcomes, a lapse, a check-in and a context flag."""
    rng = random.Random(seed)
    for day in range(1, days + 1):
        if engine.get_state(uid).checkin_due:
            engine.checkin(uid, [Barrier.time])
        if day == 5:
            engine.set_context(uid, ContextFlag.heat, True)
        for s in engine.today(uid, day, hour=9).actions:
            engine.record(Event(user_id=uid, day=day, type=simulate_outcome(rng, day, s.action.tier),
                                action_id=s.action.id))


def test_profile_state_events_round_trip(store):
    engine = Engine(store=store)
    uid = engine.onboard(demo_payload(), user_id="u1").user_id
    _journey(engine, uid)
    profile, state, events = store.get_profile(uid), store.get_state(uid), store.events(uid)
    store.save_profile(profile)
    store.save_state(state)
    assert store.get_profile(uid) == profile
    assert store.get_state(uid) == state
    assert store.events(uid) == events


def test_database_matches_in_memory_over_a_journey(open_db):
    """Same inputs through the engine give identical state and event log on every store."""
    mem, sql = InMemoryStore(), open_db()
    for s in (mem, sql):
        engine = Engine(store=s)
        engine.onboard(demo_payload(), user_id="u1")
        _journey(engine, "u1")
    assert sql.get_state("u1") == mem.get_state("u1")
    assert sql.events("u1") == mem.events("u1")
    assert len(mem.events("u1")) > 50


def test_events_keep_order_and_are_per_user(store):
    for i in range(5):
        store.append_event(Event(user_id="a", day=i, type=EventType.completed, action_id=f"x{i}"))
        store.append_event(Event(user_id="b", day=i, type=EventType.skipped))
    assert [e.day for e in store.events("a")] == [0, 1, 2, 3, 4]
    assert {e.type for e in store.events("b")} == {EventType.skipped}
    assert store.events("nobody") == []


def test_returned_objects_are_copies(store):
    engine = Engine(store=store)
    uid = engine.onboard(demo_payload(), user_id="u1").user_id
    state = store.get_state(uid)
    state.context_flags.add(ContextFlag.paused)
    state.habit_strength.clear()
    assert ContextFlag.paused not in store.get_state(uid).context_flags
    assert store.get_state(uid).habit_strength


def test_missing_user_raises_key_error(store):
    with pytest.raises(KeyError):
        store.get_profile("nobody")
    with pytest.raises(KeyError):
        store.get_state("nobody")


def test_delete_user_removes_only_that_user(store):
    engine = Engine(store=store)
    for uid in ("u1", "u2"):
        engine.onboard(demo_payload(), user_id=uid)
        engine.today(uid, 1, hour=9)
    store.delete_user("u1")
    with pytest.raises(KeyError):
        store.get_profile("u1")
    with pytest.raises(KeyError):
        store.get_state("u1")
    assert store.events("u1") == []
    assert store.get_profile("u2").user_id == "u2"
    assert store.events("u2")


def test_delete_leaves_no_rows(open_db):
    s = open_db()
    engine = Engine(store=s)
    engine.onboard(demo_payload(), user_id="u1")
    engine.today("u1", 1, hour=9)
    s.save_meta(UserMeta(user_id="u1", timezone="Asia/Dubai", onboard_date=date(2026, 11, 14)))
    s.add_token("u1", "hash-1")
    s.add_token("u1", "hash-2")
    s.save_login("u1", "zaina", "scrypt$x")
    s.delete_user("u1")
    for table in USER_TABLES:
        assert _count(s, table) == 0, table


def test_sensitive_groups_stored_apart(open_db):
    s = open_db()
    Engine(store=s).onboard(demo_payload(), user_id="u1")
    with s._tx() as c:
        main = json.loads(c.execute("SELECT data FROM profiles").fetchone()[0])
        sensitive = json.loads(c.execute("SELECT data FROM profiles_sensitive").fetchone()[0])
    assert set(sensitive) == {"body", "screening", "history", "conditions"}
    assert not {"body", "screening", "history", "conditions"} & set(main)
    assert "Keep up with my kids" not in json.dumps(main)


def test_data_survives_reopen(open_db):
    s = open_db()
    engine = Engine(store=s)
    engine.onboard(demo_payload(), user_id="u1")
    _journey(engine, "u1", days=5)
    s.add_token("u1", "hash-1")
    s.save_login("u1", "zaina", "scrypt$x")
    state, events = s.get_state("u1"), s.events("u1")
    s.close()
    s2 = open_db()
    assert s2.get_state("u1") == state
    assert s2.events("u1") == events
    assert s2.token_user("hash-1") == "u1" and s2.login("zaina") == ("u1", "scrypt$x")


def test_tokens_several_per_user_and_revocable(open_db):
    s = open_db()
    s.add_token("u1", "phone")
    s.add_token("u1", "laptop")
    s.add_token("u2", "other")
    assert s.token_user("phone") == s.token_user("laptop") == "u1"
    s.delete_token("phone")
    assert s.token_user("phone") is None and s.token_user("laptop") == "u1" and s.token_user("other") == "u2"


def test_usernames_are_unique(open_db):
    s = open_db()
    s.save_login("u1", "zaina", "scrypt$a")
    with pytest.raises(ValueError):
        s.save_login("u2", "zaina", "scrypt$b")
    assert s.login("zaina") == ("u1", "scrypt$a") and s.username("u1") == "zaina"
    assert s.login("nobody") is None and s.username("u2") is None


def test_open_store_picks_the_store_from_the_url(tmp_path):
    s = open_store(f"sqlite:///{tmp_path / 'u.db'}")
    assert isinstance(s, SQLiteStore) and not isinstance(s, PostgresStore)
    s.close()
    with pytest.raises(ValueError):
        open_store("mysql://x/y")


@needs_pg
@pytest.mark.parametrize("scheme", ["postgresql://", "postgres://"])
def test_open_store_uses_postgres_for_both_schemes(scheme):
    s = open_store(scheme + PG_URL.split("://", 1)[1])
    assert isinstance(s, PostgresStore)
    s.close()


@pytest.mark.parametrize(
    ("url", "path"), [("sqlite:///rebound.db", "rebound.db"), ("sqlite:///:memory:", ":memory:")]
)
def test_sqlite_path(url, path):
    assert sqlite_path(url) == path


@pytest.mark.parametrize("url", ["postgres://x/y", "sqlite:///", "rebound.db"])
def test_sqlite_path_rejects_other_urls(url):
    with pytest.raises(ValueError):
        sqlite_path(url)
