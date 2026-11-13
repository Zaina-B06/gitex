"""SQLite implementation of the engine's `Store` protocol (stdlib sqlite3; the engine itself stays DB-free).

Sensitive profile groups (body, health check, history) live in their own table, apart from the rest of the
profile and from behaviour events (AGENTS.md §4.7)."""

import json
import sqlite3
import threading
from datetime import date

from pydantic import BaseModel
from rebound_engine.models import Event, UserProfile, UserState

SENSITIVE_GROUPS = ("body", "screening", "history")


class UserMeta(BaseModel):
    """API-only data the engine never sees: clock, org membership, auth."""

    user_id: str
    timezone: str
    onboard_date: date  # the user's local date at onboarding = engine day 1
    day_offset: int = 0  # demo time travel only
    org_id: str | None = None
    token_hash: str  # sha256 of the bearer token; the token itself is never stored


_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_meta (user_id TEXT PRIMARY KEY, org_id TEXT, data TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS user_meta_org ON user_meta (org_id);
CREATE TABLE IF NOT EXISTS profiles (user_id TEXT PRIMARY KEY, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS profiles_sensitive (user_id TEXT PRIMARY KEY, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS states (user_id TEXT PRIMARY KEY, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    data TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS events_user ON events (user_id, id);
"""
USER_TABLES = ("user_meta", "profiles", "profiles_sensitive", "states", "events")


def sqlite_path(database_url: str) -> str:
    """'sqlite:///rebound.db' -> 'rebound.db'; 'sqlite:///:memory:' -> ':memory:'."""
    prefix = "sqlite:///"
    if not database_url.startswith(prefix) or len(database_url) == len(prefix):
        raise ValueError(f"DATABASE_URL must look like sqlite:///path.db, got {database_url!r}")
    return database_url[len(prefix):]


class SQLiteStore:
    def __init__(self, path: str = "rebound.db") -> None:
        # One connection shared by FastAPI's worker threads, serialised by a lock.
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._lock = threading.Lock()
        with self._lock, self._conn:
            self._conn.executescript(_SCHEMA)

    def save_profile(self, profile: UserProfile) -> None:
        data = profile.model_dump(mode="json")
        sensitive = {g: data.pop(g) for g in SENSITIVE_GROUPS}
        with self._lock, self._conn:
            self._upsert("profiles", profile.user_id, data)
            self._upsert("profiles_sensitive", profile.user_id, sensitive)

    def get_profile(self, user_id: str) -> UserProfile:
        with self._lock:
            data = self._get("profiles", user_id) | self._get("profiles_sensitive", user_id)
        return UserProfile.model_validate(data)

    def save_state(self, state: UserState) -> None:
        with self._lock, self._conn:
            self._upsert("states", state.user_id, state.model_dump(mode="json"))

    def get_state(self, user_id: str) -> UserState:
        with self._lock:
            return UserState.model_validate(self._get("states", user_id))

    def append_event(self, event: Event) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                "INSERT INTO events (user_id, data) VALUES (?, ?)", (event.user_id, event.model_dump_json())
            )

    def events(self, user_id: str) -> list[Event]:
        with self._lock:
            rows = self._conn.execute("SELECT data FROM events WHERE user_id = ? ORDER BY id", (user_id,))
            return [Event.model_validate_json(data) for (data,) in rows]

    def delete_user(self, user_id: str) -> None:
        with self._lock, self._conn:
            for table in USER_TABLES:
                self._conn.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))

    # ---------- API-only (not part of the engine's Store protocol) ----------

    def save_meta(self, meta: UserMeta) -> None:
        with self._lock, self._conn:
            self._conn.execute(
                "INSERT INTO user_meta (user_id, org_id, data) VALUES (?, ?, ?) ON CONFLICT (user_id) "
                "DO UPDATE SET org_id = excluded.org_id, data = excluded.data",
                (meta.user_id, meta.org_id, meta.model_dump_json()),
            )

    def get_meta(self, user_id: str) -> UserMeta:
        with self._lock:
            row = self._conn.execute("SELECT data FROM user_meta WHERE user_id = ?", (user_id,)).fetchone()
        if row is None:
            raise KeyError(user_id)
        return UserMeta.model_validate_json(row[0])

    def org_user_ids(self, org_id: str) -> list[str]:
        with self._lock:
            rows = self._conn.execute("SELECT user_id FROM user_meta WHERE org_id = ? ORDER BY user_id", (org_id,))
            return [uid for (uid,) in rows]

    def close(self) -> None:
        self._conn.close()

    def _upsert(self, table: str, user_id: str, data: dict) -> None:
        self._conn.execute(
            f"INSERT INTO {table} (user_id, data) VALUES (?, ?) "
            "ON CONFLICT (user_id) DO UPDATE SET data = excluded.data",
            (user_id, json.dumps(data)),
        )

    def _get(self, table: str, user_id: str) -> dict:
        row = self._conn.execute(f"SELECT data FROM {table} WHERE user_id = ?", (user_id,)).fetchone()
        if row is None:
            raise KeyError(user_id)  # same as InMemoryStore
        return json.loads(row[0])
