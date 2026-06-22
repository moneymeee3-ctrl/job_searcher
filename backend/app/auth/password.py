"""EMBEDHUNT AI — Password Hashing.

Uses the ``bcrypt`` library directly. (The previously-used ``passlib`` wrapper is
unmaintained and incompatible with bcrypt >= 4.1, which removed the internal
``__about__`` attribute passlib relied on.)

bcrypt only considers the first 72 bytes of a secret, and bcrypt >= 4.1 raises if
a longer secret is passed. We truncate to 72 bytes explicitly so long passwords
are handled deterministically instead of erroring.
"""
import bcrypt

from app.config.settings import settings

_MAX_BCRYPT_BYTES = 72


def _to_bytes(plain: str) -> bytes:
    return plain.encode("utf-8")[:_MAX_BCRYPT_BYTES]


def hash_password(plain: str) -> str:
    hashed = bcrypt.hashpw(_to_bytes(plain), bcrypt.gensalt(rounds=settings.BCRYPT_ROUNDS))
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_to_bytes(plain), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False
