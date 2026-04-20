"""
OTP (One-Time Password) generation and verification.

Supports both phone and email verification flows:
- Phone Number Verification: 6-digit code entry
- Forgot Password - Verify Email: 4-digit code with 60s timer

Uses Django cache backend (Redis in production) for storage.
"""

from __future__ import annotations

import secrets
from datetime import timedelta

from django.core.cache import cache

OTP_LENGTH = 6
OTP_TTL = timedelta(minutes=5)
OTP_MAX_ATTEMPTS = 5
OTP_COOLDOWN = timedelta(seconds=60)

CACHE_PREFIX = "otp:"
COOLDOWN_PREFIX = "otp:cooldown:"
ATTEMPTS_PREFIX = "otp:attempts:"


def _cache_key(purpose: str, identifier: str) -> str:
    return f"{CACHE_PREFIX}{purpose}:{identifier}"


def _cooldown_key(purpose: str, identifier: str) -> str:
    return f"{COOLDOWN_PREFIX}{purpose}:{identifier}"


def _attempts_key(purpose: str, identifier: str) -> str:
    return f"{ATTEMPTS_PREFIX}{purpose}:{identifier}"


def generate_otp(purpose: str, identifier: str) -> str | None:
    """
    Generate and store an OTP for the given purpose and identifier.

    Args:
        purpose: "phone_verify", "email_verify", or "password_reset"
        identifier: phone number or email address

    Returns:
        The OTP string, or None if cooldown is active.
    """
    cooldown_key = _cooldown_key(purpose, identifier)
    if cache.get(cooldown_key):
        return None

    code = "".join(secrets.choice("0123456789") for _ in range(OTP_LENGTH))

    cache.set(_cache_key(purpose, identifier), code, timeout=int(OTP_TTL.total_seconds()))
    cache.set(cooldown_key, True, timeout=int(OTP_COOLDOWN.total_seconds()))
    cache.delete(_attempts_key(purpose, identifier))

    return code


def verify_otp(purpose: str, identifier: str, code: str) -> bool:
    """
    Verify an OTP. Returns True if valid, False otherwise.
    Deletes the OTP on success. Tracks failed attempts.
    """
    attempts_key = _attempts_key(purpose, identifier)
    attempts = cache.get(attempts_key, 0)
    if attempts >= OTP_MAX_ATTEMPTS:
        return False

    stored_code = cache.get(_cache_key(purpose, identifier))
    if stored_code is None or stored_code != code:
        cache.set(attempts_key, attempts + 1, timeout=int(OTP_TTL.total_seconds()))
        return False

    # Valid — clean up
    cache.delete(_cache_key(purpose, identifier))
    cache.delete(attempts_key)
    return True


def get_cooldown_remaining(purpose: str, identifier: str) -> int:
    """Return seconds remaining on cooldown, or 0 if no cooldown."""
    cooldown_key = _cooldown_key(purpose, identifier)
    ttl = cache.ttl(cooldown_key) if hasattr(cache, "ttl") else 0
    return max(0, ttl) if isinstance(ttl, int) else 0
