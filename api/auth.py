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


class FailedLogins:
    """Failed tries per username in the last LOGIN_WINDOW.
    shortcut: in memory and per process, so it resets on restart and isn't shared between workers; move it to the
    database (or Redis) before running more than one API process."""

    def __init__(self, clock: Callable[[], datetime]) -> None:
        self._clock = clock
        self._tries: dict[str, list[datetime]] = {}
        self._lock = threading.Lock()

    def _recent(self, username: str) -> list[datetime]:
        cutoff = self._clock() - LOGIN_WINDOW
        recent = [t for t in self._tries.get(username, []) if t > cutoff]
        self._tries[username] = recent
        return recent

    def blocked(self, username: str) -> bool:
        with self._lock:
            return len(self._recent(username)) >= LOGIN_MAX_FAILURES

    def add(self, username: str) -> None:
        with self._lock:
            self._recent(username).append(self._clock())

    def clear(self, username: str) -> None:
        with self._lock:
            self._tries.pop(username, None)
