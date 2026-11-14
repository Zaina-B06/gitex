"""Shared store tests: SQLiteStore must behave exactly like the engine's InMemoryStore."""

import json
import random
import sqlite3
from datetime import date

import pytest
from api.store import USER_TABLES, SQLiteStore, UserMeta, sqlite_path
from rebound_engine.demo import demo_payload, simulate_outcome
from rebound_engine.engine import Engine, InMemoryStore
from rebound_engine.models import Barrier, ContextFlag, Event, EventType


@pytest.fixture(params=["in_memory", "sqlite"])
def store(request, tmp_path):
    if request.param == "in_memory":
        yield InMemoryStore()
    else:
        s = SQLiteStore(str(tmp_path / "test.db"))
        yield s
        s.close()


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


def test_sqlite_matches_in_memory_over_a_journey(tmp_path):
    """Same inputs through the engine give identical state and event log on both stores."""
    mem, sql = InMemoryStore(), SQLiteStore(str(tmp_path / "j.db"))
    for s in (mem, sql):
        engine = Engine(store=s)
        engine.onboard(demo_payload(), user_id="u1")
        _journey(engine, "u1")
    assert sql.get_state("u1") == mem.get_state("u1")
    assert sql.events("u1") == mem.events("u1")
    assert len(mem.events("u1")) > 50
    sql.close()


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


def test_sqlite_delete_leaves_no_rows(tmp_path):
    path = str(tmp_path / "d.db")
    s = SQLiteStore(path)
    engine = Engine(store=s)
    engine.onboard(demo_payload(), user_id="u1")
    engine.today("u1", 1, hour=9)
    s.save_meta(UserMeta(user_id="u1", timezone="Asia/Dubai", onboard_date=date(2026, 11, 14), token_hash="x"))
    s.delete_user("u1")
    s.close()
    conn = sqlite3.connect(path)
    for table in USER_TABLES:
        assert conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0, table
    conn.close()


def test_sensitive_groups_stored_apart(tmp_path):
    path = str(tmp_path / "s.db")
    s = SQLiteStore(path)
    Engine(store=s).onboard(demo_payload(), user_id="u1")
    s.close()
    conn = sqlite3.connect(path)
    main = json.loads(conn.execute("SELECT data FROM profiles").fetchone()[0])
    sensitive = json.loads(conn.execute("SELECT data FROM profiles_sensitive").fetchone()[0])
    conn.close()
    assert set(sensitive) == {"body", "screening", "history", "conditions"}
    assert not {"body", "screening", "history", "conditions"} & set(main)
    assert "Keep up with my kids" not in json.dumps(main)


def test_data_survives_reopen(tmp_path):
    path = str(tmp_path / "r.db")
    s = SQLiteStore(path)
    engine = Engine(store=s)
    engine.onboard(demo_payload(), user_id="u1")
    _journey(engine, "u1", days=5)
    state, events = s.get_state("u1"), s.events("u1")
    s.close()
    s2 = SQLiteStore(path)
    assert s2.get_state("u1") == state
    assert s2.events("u1") == events
    s2.close()


@pytest.mark.parametrize(
    ("url", "path"), [("sqlite:///rebound.db", "rebound.db"), ("sqlite:///:memory:", ":memory:")]
)
def test_sqlite_path(url, path):
    assert sqlite_path(url) == path


@pytest.mark.parametrize("url", ["postgres://x/y", "sqlite:///", "rebound.db"])
def test_sqlite_path_rejects_other_urls(url):
    with pytest.raises(ValueError):
        sqlite_path(url)
