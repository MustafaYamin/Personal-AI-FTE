import hashlib
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any

import bcrypt
import jwt

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError

settings = get_settings()


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass
class TokenPairData:
    """Plain data holder for a freshly issued (access, refresh) pair — lives
    here (not in a feature module) so both the auth and organizations features
    can depend on it without creating a cross-feature import cycle."""

    access_token: str
    refresh_token: str


# --- Password hashing -------------------------------------------------------
# Using bcrypt directly (not passlib) — passlib's bcrypt backend has known
# incompatibilities with bcrypt>=4.1's version metadata.

def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        # Malformed hash — treat as a failed verification, not a 500.
        return False


# --- JWT ---------------------------------------------------------------------

def _create_token(subject: uuid.UUID, token_type: TokenType, expires_delta: timedelta) -> tuple[str, str]:
    """Returns (encoded_jwt, jti). jti lets refresh tokens be revoked/rotated
    by looking up a hash of it in the DB without decoding every stored token."""
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type.value,
        "iat": now,
        "exp": now + expires_delta,
        "jti": jti,
    }
    encoded = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded, jti


def create_access_token(user_id: uuid.UUID) -> str:
    token, _ = _create_token(user_id, TokenType.ACCESS, timedelta(minutes=settings.access_token_expire_minutes))
    return token


def create_refresh_token(user_id: uuid.UUID) -> tuple[str, str, datetime]:
    """Returns (token, jti, expires_at) — caller persists sha256(token) + expires_at
    so the refresh token can be revoked/rotated server-side."""
    expires_delta = timedelta(days=settings.refresh_token_expire_days)
    token, jti = _create_token(user_id, TokenType.REFRESH, expires_delta)
    expires_at = datetime.now(timezone.utc) + expires_delta
    return token, jti, expires_at


def hash_token(token: str) -> str:
    """One-way digest used to look up/revoke refresh tokens without storing them raw."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise UnauthorizedError("Invalid token") from exc

    if payload.get("type") != expected_type.value:
        raise UnauthorizedError("Incorrect token type")

    return payload
