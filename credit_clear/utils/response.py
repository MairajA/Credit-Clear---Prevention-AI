"""
Standardized API response format for Credit Clear.

Every endpoint returns one of these structures so the frontend team
can rely on a single, predictable contract.

SUCCESS (single object):
{
    "status": "success",
    "data": { ... }
}

SUCCESS (list):
{
    "status": "success",
    "data": [ ... ],
    "meta": { "count": 25, "page": 1, "page_size": 20, "total_pages": 2 }
}

ERROR:
{
    "status": "error",
    "code": "VALIDATION_ERROR",
    "message": "Human-readable message",
    "errors": { "field": ["detail"] }    # optional, for validation errors
}
"""

from __future__ import annotations

import math
from typing import Any

from rest_framework import status as http_status
from rest_framework.response import Response


# ---------------------------------------------------------------------------
# Success helpers
# ---------------------------------------------------------------------------

def success(data: Any = None, *, status: int = http_status.HTTP_200_OK, meta: dict | None = None) -> Response:
    """Return a standard success response."""
    body: dict[str, Any] = {"status": "success", "data": data}
    if meta:
        body["meta"] = meta
    return Response(body, status=status)


def created(data: Any = None) -> Response:
    """Shortcut for 201 Created."""
    return success(data, status=http_status.HTTP_201_CREATED)


def paginated(queryset_data: list, *, count: int, page: int = 1, page_size: int = 20) -> Response:
    """Return a paginated list response."""
    total_pages = math.ceil(count / page_size) if page_size else 1
    return success(
        queryset_data,
        meta={
            "count": count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        },
    )


def no_content() -> Response:
    """Return 204 No Content."""
    return Response(status=http_status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Error helpers
# ---------------------------------------------------------------------------

# Error codes — frontend can switch on these instead of parsing messages
VALIDATION_ERROR = "VALIDATION_ERROR"
AUTH_ERROR = "AUTH_ERROR"
NOT_FOUND = "NOT_FOUND"
RATE_LIMITED = "RATE_LIMITED"
FORBIDDEN = "FORBIDDEN"
CONFLICT = "CONFLICT"
SERVER_ERROR = "SERVER_ERROR"


def error(
    message: str,
    *,
    code: str = VALIDATION_ERROR,
    status: int = http_status.HTTP_400_BAD_REQUEST,
    errors: dict | None = None,
) -> Response:
    """Return a standard error response."""
    body: dict[str, Any] = {
        "status": "error",
        "code": code,
        "message": message,
    }
    if errors:
        body["errors"] = errors
    return Response(body, status=status)


def validation_error(form_errors: dict) -> Response:
    """Return 400 with form validation errors."""
    return error(
        "Validation failed.",
        code=VALIDATION_ERROR,
        status=http_status.HTTP_400_BAD_REQUEST,
        errors=form_errors,
    )


def auth_error(message: str = "Authentication credentials were not provided.") -> Response:
    """Return 401 Unauthorized."""
    return error(message, code=AUTH_ERROR, status=http_status.HTTP_401_UNAUTHORIZED)


def forbidden(message: str = "You do not have permission to perform this action.") -> Response:
    """Return 403 Forbidden."""
    return error(message, code=FORBIDDEN, status=http_status.HTTP_403_FORBIDDEN)


def not_found(message: str = "Resource not found.") -> Response:
    """Return 404 Not Found."""
    return error(message, code=NOT_FOUND, status=http_status.HTTP_404_NOT_FOUND)


def conflict(message: str = "Resource already exists.") -> Response:
    """Return 409 Conflict."""
    return error(message, code=CONFLICT, status=http_status.HTTP_409_CONFLICT)


def rate_limited(message: str = "Too many requests. Please try again later.") -> Response:
    """Return 429 Rate Limited."""
    return error(message, code=RATE_LIMITED, status=http_status.HTTP_429_TOO_MANY_REQUESTS)
