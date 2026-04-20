"""
Shared authentication helpers for API views.

All views use bearer_auth() to get the authenticated user.
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from rest_framework.response import Response

from credit_clear.users.api.tokens import TokenError
from credit_clear.users.api.tokens import decode_access_token
from credit_clear.utils.response import auth_error

User = get_user_model()


def _extract_bearer_token(request: HttpRequest) -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.removeprefix("Bearer ").strip()


def get_authenticated_user(request: HttpRequest) -> User | None:
    """Extract and verify the user from the Bearer token. Returns None on failure."""
    token = _extract_bearer_token(request)
    if not token:
        return None
    try:
        payload = decode_access_token(token)
    except TokenError:
        return None
    user_id = payload.get("sub")
    if user_id is None:
        return None
    try:
        return User.objects.get(pk=int(user_id), is_active=True)
    except (User.DoesNotExist, ValueError):
        return None


def bearer_auth(request: HttpRequest) -> tuple[User | None, Response | None]:
    """
    Authenticate the request. Returns (user, None) on success,
    or (None, error_response) on failure.

    Usage in views:
        user, err = bearer_auth(request)
        if err:
            return err
    """
    user = get_authenticated_user(request)
    if user is None:
        return None, auth_error()
    return user, None
