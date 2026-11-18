"""SQLite and Postgres implementations of the engine's `Store` protocol (the engine itself stays DB-free).

Sensitive profile groups (body, health check, history, conditions) live in their own table, apart from the rest of
the profile and from behaviour events (AGENTS.md §4.7). Both stores run the same SQL; Postgres only swaps the
connection, the placeholder style and the events id column. Tables are created on startup if missing; there is no
migrations framework (docs/ASSUMPTIONS.md, API)."""

import json
import sqlite3
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from typing import Any

from pydantic import BaseModel
from rebound_engine.models import Event, UserProfile, UserState

SENSITIVE_GROUPS = ("body", "screening", "history", "conditions")


class UserMeta(BaseModel):
    """API-only data the engine never sees: clock and org membership. Tokens and logins have their own tables."""

    user_id: str
    timezone: str
    onboard_date: date  # the user's local date at onboarding = engine day 1
    day_offset: int = 0  # demo time travel only
    org_id: str | None = None
    last_checkin_day: int | None = None  # engine day of the last check-in (one per day)
    # "Ramadan started today / ended" corrections to the Umm al-Qura table, in days (Task 05 A2)
    ramadan_start_shift: int = 0
    ramadan_end_shift: int = 0


_SCHEMA = """
CREATE TABLE IF NOT EXISTS user_meta (user_id TEXT PRIMARY KEY, org_id TEXT, data TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS user_meta_org ON user_meta (org_id);
CREATE TABLE IF NOT EXISTS profiles (user_id TEXT PRIMARY KEY, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS profiles_sensitive (user_id TEXT PRIMARY KEY, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS states (user_id TEXT PRIMARY KEY, data TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS events (id {id_column}, user_id TEXT NOT NULL, data TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS events_user ON events (user_id, id);
CREATE TABLE IF NOT EXISTS tokens (token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS tokens_user ON tokens (user_id);
CREATE TABLE IF NOT EXISTS logins (user_id TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL);
"""
USER_TABLES = ("user_meta", "profiles", "profiles_sensitive", "states", "events", "tokens", "logins")


def sqlite_path(database_url: str) -> str:
    """'sqlite:///rebound.db' -> 'rebound.db'; 'sqlite:///:memory:' -> ':memory:'."""
    prefix = "sqlite:///"
    if not database_url.startswith(prefix) or len(database_url) == len(prefix):
        raise ValueError(f"DATABASE_URL must look like sqlite:///path.db, got {database_url!r}")
    return database_url[len(prefix):]


def open_store(database_url: str) -> "SQLiteStore":
    """DATABASE_URL picks the store: sqlite:///... (default) or postgresql:// / postgres:// (Render)."""
    if database_url.startswith(("postgresql://", "postgres://")):
        return PostgresStore(database_url)
    return SQLiteStore(sqlite_path(database_url))


class SQLiteStore:
    def __init__(self, path: str = "rebound.db") -> None:
        # One connection shared by FastAPI's worker threads, serialised by a lock.
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._lock = threading.Lock()
        self._local = threading.local()  # the open batch of this thread, if any
        self._unique_violation: type[Exception] = sqlite3.IntegrityError
        with self._tx() as c:
            c.executescript(_SCHEMA.format(id_column="INTEGER PRIMARY KEY AUTOINCREMENT"))

    @contextmanager
    def _tx(self) -> Iterator[Any]:
        """One transaction; yields something with .execute(sql, params) using ? placeholders."""
        with self._lock, self._conn:
            yield self._conn

    # ---------- batching (demo seed and time travel) ----------

    def _buf(self) -> dict[str, Any] | None:
        return getattr(self._local, "buf", None)

    @contextmanager
    def batch(self) -> Iterator[None]:
        """Profiles, states, metas and events written inside are kept in memory (reads see them) and written at the
        end in ONE transaction with bulk inserts; on an error nothing is written. Tokens and logins go straight
        through. Per thread, so other requests are unaffected (they see the data once the batch is written)."""
        if self._buf() is not None:  # already batching: join it
            yield
            return
        self._local.buf = {"profile": {}, "state": {}, "meta": {}, "dirty": set(), "events": []}
        try:
            yield
            buf = self._local.buf
            self._local.buf = None
            self._flush(buf)
        finally:
            self._local.buf = None

    def _flush(self, buf: dict[str, Any]) -> None:
        def dirty(kind: str) -> list[Any]:
            return [buf[kind][uid] for k, uid in sorted(buf["dirty"]) if k == kind]

        upsert = "INSERT INTO {t} (user_id, data) VALUES (?, ?) ON CONFLICT (user_id) DO UPDATE SET data = excluded.data"
        profiles = [(p.user_id, _split_profile(p)) for p in dirty("profile")]
        with self._tx() as c:
            c.executemany(upsert.format(t="profiles"), [(uid, json.dumps(main)) for uid, (main, _) in profiles])
            c.executemany(upsert.format(t="profiles_sensitive"), [(uid, json.dumps(s)) for uid, (_, s) in profiles])
            c.executemany(upsert.format(t="states"), [(s.user_id, s.model_dump_json()) for s in dirty("state")])
            c.executemany(_META_UPSERT, [(m.user_id, m.org_id, m.model_dump_json()) for m in dirty("meta")])
            c.executemany("INSERT INTO events (user_id, data) VALUES (?, ?)",
                          [(e.user_id, e.model_dump_json()) for e in buf["events"]])

    def _cached(self, kind: str, user_id: str, load: Any) -> Any:
        """Inside a batch: the buffered copy (loaded from the database once). Outside: straight from the database."""
        buf = self._buf()
        if buf is None:
            return load()
        if user_id not in buf[kind]:
            buf[kind][user_id] = load()
        return buf[kind][user_id].model_copy(deep=True)

    def _buffered_save(self, kind: str, user_id: str, obj: BaseModel) -> bool:
        buf = self._buf()
        if buf is None:
            return False
        buf[kind][user_id] = obj.model_copy(deep=True)
        buf["dirty"].add((kind, user_id))
        return True

    # ---------- the engine's Store protocol ----------

    def save_profile(self, profile: UserProfile) -> None:
        if self._buffered_save("profile", profile.user_id, profile):
            return
        main, sensitive = _split_profile(profile)
        with self._tx() as c:
            _upsert(c, "profiles", profile.user_id, main)
            _upsert(c, "profiles_sensitive", profile.user_id, sensitive)

    def get_profile(self, user_id: str) -> UserProfile:
        def load() -> UserProfile:
            with self._tx() as c:
                data = _get(c, "profiles", user_id) | _get(c, "profiles_sensitive", user_id)
            return UserProfile.model_validate(data)

        return self._cached("profile", user_id, load)

    def save_state(self, state: UserState) -> None:
        if self._buffered_save("state", state.user_id, state):
            return
        with self._tx() as c:
            _upsert(c, "states", state.user_id, state.model_dump(mode="json"))

    def get_state(self, user_id: str) -> UserState:
        def load() -> UserState:
            with self._tx() as c:
                return UserState.model_validate(_get(c, "states", user_id))

        return self._cached("state", user_id, load)

    def append_event(self, event: Event) -> None:
        buf = self._buf()
        if buf is not None:
            buf["events"].append(event.model_copy(deep=True))
            return
        with self._tx() as c:
            c.execute("INSERT INTO events (user_id, data) VALUES (?, ?)", (event.user_id, event.model_dump_json()))

    def events(self, user_id: str) -> list[Event]:
        with self._tx() as c:
            rows = c.execute("SELECT data FROM events WHERE user_id = ? ORDER BY id", (user_id,)).fetchall()
        buffered = [e.model_copy(deep=True) for e in (self._buf() or {"events": []})["events"] if e.user_id == user_id]
        return [Event.model_validate_json(data) for (data,) in rows] + buffered

    def delete_user(self, user_id: str) -> None:
        buf = self._buf()
        if buf is not None:  # drop anything buffered for this user too
            for kind in ("profile", "state", "meta"):
                buf[kind].pop(user_id, None)
            buf["dirty"] = {(k, u) for k, u in buf["dirty"] if u != user_id}
            buf["events"] = [e for e in buf["events"] if e.user_id != user_id]
        with self._tx() as c:
            for table in USER_TABLES:
                c.execute(f"DELETE FROM {table} WHERE user_id = ?", (user_id,))

    # ---------- API-only (not part of the engine's Store protocol) ----------

    def save_meta(self, meta: UserMeta) -> None:
        if self._buffered_save("meta", meta.user_id, meta):
            return
        with self._tx() as c:
            c.execute(_META_UPSERT, (meta.user_id, meta.org_id, meta.model_dump_json()))

    def get_meta(self, user_id: str) -> UserMeta:
        def load() -> UserMeta:
            with self._tx() as c:
                row = c.execute("SELECT data FROM user_meta WHERE user_id = ?", (user_id,)).fetchone()
            if row is None:
                raise KeyError(user_id)
            return UserMeta.model_validate_json(row[0])

        return self._cached("meta", user_id, load)

    def org_user_ids(self, org_id: str) -> list[str]:
        with self._tx() as c:
            rows = c.execute("SELECT user_id FROM user_meta WHERE org_id = ? ORDER BY user_id", (org_id,)).fetchall()
        return [uid for (uid,) in rows]

    # Bearer tokens: only their sha256 is stored. A user can have several (phone + laptop).
    def add_token(self, user_id: str, token_hash: str) -> None:
        with self._tx() as c:
            c.execute("INSERT INTO tokens (token_hash, user_id) VALUES (?, ?)", (token_hash, user_id))

    def token_user(self, token_hash: str) -> str | None:
        with self._tx() as c:
            row = c.execute("SELECT user_id FROM tokens WHERE token_hash = ?", (token_hash,)).fetchone()
        return row[0] if row else None

    def delete_token(self, token_hash: str) -> None:
        with self._tx() as c:
            c.execute("DELETE FROM tokens WHERE token_hash = ?", (token_hash,))

    # Logins: username (lower-case, unique) + salted password hash. ValueError if the username is taken.
    def save_login(self, user_id: str, username: str, password_hash: str) -> None:
        try:
            with self._tx() as c:
                c.execute("INSERT INTO logins (user_id, username, password_hash) VALUES (?, ?, ?)",
                          (user_id, username, password_hash))
        except self._unique_violation:
            raise ValueError("username taken, or the user already has a login") from None

    def login(self, username: str) -> tuple[str, str] | None:
        """(user_id, password_hash) for a username, or None."""
        with self._tx() as c:
            row = c.execute("SELECT user_id, password_hash FROM logins WHERE username = ?", (username,)).fetchone()
        return (row[0], row[1]) if row else None

    def username(self, user_id: str) -> str | None:
        with self._tx() as c:
            row = c.execute("SELECT username FROM logins WHERE user_id = ?", (user_id,)).fetchone()
        return row[0] if row else None

    def close(self) -> None:
        self._conn.close()


class _PgConnection:
    """Lets the shared ? placeholders run on psycopg (%s). Our SQL never contains a literal ?."""

    def __init__(self, conn: Any) -> None:
        self._conn = conn

    def execute(self, sql: str, params: tuple = ()) -> Any:
        return self._conn.execute(sql.replace("?", "%s"), params)

    def executemany(self, sql: str, rows: list[tuple]) -> None:
        if rows:
            with self._conn.cursor() as cur:  # psycopg pipelines these: one round trip for the whole list
                cur.executemany(sql.replace("?", "%s"), rows)


class PostgresStore(SQLiteStore):
    """Same tables and SQL as SQLiteStore, on Postgres (data survives Render restarts). Needs psycopg (v3)."""

    def __init__(self, database_url: str) -> None:
        import psycopg  # only needed when DATABASE_URL is Postgres
        from psycopg_pool import ConnectionPool

        # A small pool that checks connections before use, so a dropped connection (DB restart) is replaced.
        # prepare_threshold=None: no server-side prepared statements, which transaction-mode poolers (Supabase
        # port 6543, PgBouncer) can't keep between transactions.
        self._pool = ConnectionPool(database_url, min_size=1, max_size=5, open=True,
                                    check=ConnectionPool.check_connection, kwargs={"prepare_threshold": None})
        self._unique_violation = psycopg.errors.UniqueViolation
        self._local = threading.local()
        with self._tx() as c:
            for statement in filter(str.strip, _SCHEMA.format(id_column="BIGSERIAL PRIMARY KEY").split(";")):
                c.execute(statement)

    @contextmanager
    def _tx(self) -> Iterator[Any]:
        with self._pool.connection() as conn:  # commits on success, rolls back on error
            yield _PgConnection(conn)

    def close(self) -> None:
        self._pool.close()


_META_UPSERT = ("INSERT INTO user_meta (user_id, org_id, data) VALUES (?, ?, ?) ON CONFLICT (user_id) "
                "DO UPDATE SET org_id = excluded.org_id, data = excluded.data")


def _split_profile(profile: UserProfile) -> tuple[dict, dict]:
    """(main, sensitive): the sensitive groups are stored in their own table (AGENTS.md §4.7)."""
    data = profile.model_dump(mode="json")
    sensitive = {g: data.pop(g) for g in SENSITIVE_GROUPS}
    return data, sensitive


def _upsert(c: Any, table: str, user_id: str, data: dict) -> None:
    c.execute(
        f"INSERT INTO {table} (user_id, data) VALUES (?, ?) ON CONFLICT (user_id) DO UPDATE SET data = excluded.data",
        (user_id, json.dumps(data)),
    )


def _get(c: Any, table: str, user_id: str) -> dict:
    row = c.execute(f"SELECT data FROM {table} WHERE user_id = ?", (user_id,)).fetchone()
    if row is None:
        raise KeyError(user_id)  # same as InMemoryStore
    return json.loads(row[0])
