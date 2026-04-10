from __future__ import annotations

import uuid
from datetime import UTC
from datetime import datetime
from datetime import timedelta

from django.core import signing
from django.core.cache import cache

ACCESS_TOKEN_TTL = timedelta(minutes=15)
REFRESH_TOKEN_TTL = timedelta(days=30)
TOKEN_SALT = "credit_clear.auth.tokens"
REFRESH_BLACKLIST_PREFIX = "auth:refresh:blacklist:"


class TokenError(Exception):
    """Raised when token is invalid or expired."""


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _to_timestamp(value: datetime) -> int:
    return int(value.timestamp())


def _build_payload(user_id: int, token_type: str, ttl: timedelta) -> dict[str, int | str]:
    now = _utcnow()
    exp = now + ttl
    return {
        "sub": str(user_id),
        "type": token_type,
        "iat": _to_timestamp(now),
        "exp": _to_timestamp(exp),
        "jti": str(uuid.uuid4()),
    }


def _encode(payload: dict[str, int | str]) -> str:
    return signing.dumps(payload, salt=TOKEN_SALT, compress=True)


def _decode(token: str, expected_type: str) -> dict[str, int | str]:
    try:
        payload = signing.loads(token, salt=TOKEN_SALT)
    except signing.BadSignature as exc:
        msg = "Invalid token signature."
        raise TokenError(msg) from exc

    if payload.get("type") != expected_type:
        msg = "Invalid token type."
        raise TokenError(msg)

    exp = payload.get("exp")
    if not isinstance(exp, int) or exp <= _to_timestamp(_utcnow()):
        msg = "Token expired."
        raise TokenError(msg)
    return payload


def create_token_pair(user_id: int) -> dict[str, str | int]:
    access_payload = _build_payload(user_id=user_id, token_type="access", ttl=ACCESS_TOKEN_TTL)
    refresh_payload = _build_payload(user_id=user_id, token_type="refresh", ttl=REFRESH_TOKEN_TTL)
    return {
        "access_token": _encode(access_payload),
        "refresh_token": _encode(refresh_payload),
        "token_type": "Bearer",
        "expires_in": int(ACCESS_TOKEN_TTL.total_seconds()),
    }


def decode_access_token(token: str) -> dict[str, int | str]:
    return _decode(token=token, expected_type="access")


def decode_refresh_token(token: str) -> dict[str, int | str]:
    payload = _decode(token=token, expected_type="refresh")
    jti = payload.get("jti")
    if isinstance(jti, str) and cache.get(f"{REFRESH_BLACKLIST_PREFIX}{jti}"):
        msg = "Refresh token revoked."
        raise TokenError(msg)
    return payload


def revoke_refresh_token(payload: dict[str, int | str]) -> None:
    jti = payload.get("jti")
    exp = payload.get("exp")
    if not isinstance(jti, str) or not isinstance(exp, int):
        return
    ttl = max(1, exp - _to_timestamp(_utcnow()))
    cache.set(f"{REFRESH_BLACKLIST_PREFIX}{jti}", True, timeout=ttl)
