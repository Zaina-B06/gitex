"""Sign-in: username + password (stdlib scrypt), and a small in-memory limit on failed logins.

No email or phone is collected. Passwords are never stored, logged or returned: only a salted scrypt hash is kept,
and SecretStr keeps the value out of reprs and logs."""

import hashlib
import hmac
import secrets
import threading
from collections.abc import Callable
from datetime import datetime, timedelta

from pydantic import BaseModel, ConfigDict, Field, SecretStr

# scrypt cost: 2**14 x 8 = 16 MB per hash (OWASP's minimum for scrypt), about 50 ms.
SCRYPT_N, SCRYPT_R, SCRYPT_P, SALT_BYTES, KEY_BYTES = 2**14, 8, 1, 16, 32
LOGIN_MAX_FAILURES = 5
LOGIN_WINDOW = timedelta(minutes=15)
SUGGEST_MAX_CALLS = 10  # POST /content/onboarding/suggest, per IP (it's open and each call can cost an LLM call)
SUGGEST_WINDOW = timedelta(hours=1)


class LoginIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(pattern=r"^[A-Za-z0-9._-]{3,30}$")  # stored lower-case
    password: SecretStr = Field(min_length=8, max_length=128)


class TokenOut(BaseModel):
    user_id: str
    token: str  # shown once; send as "Authorization: Bearer <token>"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    key = hashlib.scrypt(password.encode(), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=KEY_BYTES)
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${key.hex()}"


def verify_password(password: str, stored: str) -> bool:
    _, n, r, p, salt, key = stored.split("$")
    test = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p),
                          dklen=len(key) // 2)
    return hmac.compare_digest(test.hex(), key)


# Checked when the username doesn't exist, so a wrong username takes as long as a wrong password.
DUMMY_HASH = hash_password(secrets.token_hex(16))


class RecentTries:
    """At most `limit` tries per key (a username, an IP) in the last `window`: failed logins, suggest calls.
    shortcut: in memory and per process, so it resets on restart and isn't shared between workers; move it to the
    database (or Redis) before running more than one API process."""

    def __init__(self, clock: Callable[[], datetime], limit: int, window: timedelta) -> None:
        self._clock, self._limit, self._window = clock, limit, window
        self._tries: dict[str, list[datetime]] = {}
        self._lock = threading.Lock()

    def _recent(self, key: str) -> list[datetime]:
        cutoff = self._clock() - self._window
        recent = [t for t in self._tries.get(key, []) if t > cutoff]
        if recent:
            self._tries[key] = recent
        else:
            self._tries.pop(key, None)  # keys with nothing recent don't pile up
        return recent

    def blocked(self, key: str) -> bool:
        with self._lock:
            return len(self._recent(key)) >= self._limit

    def add(self, key: str) -> None:
        with self._lock:
            self._tries[key] = [*self._recent(key), self._clock()]

    def clear(self, key: str) -> None:
        with self._lock:
            self._tries.pop(key, None)
