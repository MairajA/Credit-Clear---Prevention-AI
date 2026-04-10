from __future__ import annotations

import json
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from credit_clear.users.api.forms import LoginForm
from credit_clear.users.api.forms import LogoutForm
from credit_clear.users.api.forms import PasswordChangeForm
from credit_clear.users.api.forms import PasswordResetConfirmForm
from credit_clear.users.api.forms import PasswordResetRequestForm
from credit_clear.users.api.forms import RefreshTokenForm
from credit_clear.users.api.forms import RegisterForm
from credit_clear.users.api.services import issue_token_pair_for_user
from credit_clear.users.api.services import register_user
from credit_clear.users.api.services import reset_password
from credit_clear.users.api.services import send_password_reset_email
from credit_clear.users.api.tokens import TokenError
from credit_clear.users.api.tokens import decode_access_token
from credit_clear.users.api.tokens import decode_refresh_token
from credit_clear.users.api.tokens import revoke_refresh_token

User = get_user_model()


def _json_body(request: HttpRequest) -> dict:
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return {}


def _error(message: str, *, status: HTTPStatus = HTTPStatus.BAD_REQUEST) -> Response:
    return Response({"detail": message}, status=status)


def _extract_bearer_token(request: HttpRequest) -> str | None:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.removeprefix("Bearer ").strip()


def _authenticated_user_from_access_token(request: HttpRequest) -> User | None:
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


@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    def post(self, request: HttpRequest) -> Response:
        form = RegisterForm(_json_body(request))
        if not form.is_valid():
            return Response({"errors": form.errors.get_json_data()}, status=HTTPStatus.BAD_REQUEST)
        user = register_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
            name=form.cleaned_data.get("name", ""),
            role=form.cleaned_data.get("role", User.Role.CONSUMER),
            marketing_consent=form.cleaned_data.get("marketing_consent", False),
        )
        login(request, user)
        tokens = issue_token_pair_for_user(user)
        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "role": user.role,
                    "marketing_consent": user.marketing_consent,
                    "terms_accepted_at": user.terms_accepted_at.isoformat() if user.terms_accepted_at else None,
                    "privacy_accepted_at": user.privacy_accepted_at.isoformat() if user.privacy_accepted_at else None,
                },
                "tokens": tokens,
            },
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    def post(self, request: HttpRequest) -> Response:
        form = LoginForm(_json_body(request))
        if not form.is_valid():
            return Response({"errors": form.errors.get_json_data()}, status=HTTPStatus.UNAUTHORIZED)
        user = form.cleaned_data["user"]
        login(request, user)
        tokens = issue_token_pair_for_user(user)
        return Response(
            {
                "user": {"id": user.id, "email": user.email, "name": user.name, "role": user.role},
                "tokens": tokens,
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class RefreshTokenView(APIView):
    def post(self, request: HttpRequest) -> Response:
        form = RefreshTokenForm(_json_body(request))
        if not form.is_valid():
            return Response({"errors": form.errors.get_json_data()}, status=HTTPStatus.BAD_REQUEST)

        refresh_token = form.cleaned_data["refresh_token"]
        try:
            payload = decode_refresh_token(refresh_token)
        except TokenError as exc:
            return _error(str(exc), status=HTTPStatus.UNAUTHORIZED)

        revoke_refresh_token(payload)
        user_id = payload.get("sub")
        if user_id is None:
            return _error("Invalid refresh token payload.", status=HTTPStatus.UNAUTHORIZED)
        try:
            user = User.objects.get(pk=int(user_id), is_active=True)
        except (User.DoesNotExist, ValueError):
            return _error("User not found.", status=HTTPStatus.UNAUTHORIZED)
        tokens = issue_token_pair_for_user(user)
        return Response({"tokens": tokens}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    def post(self, request: HttpRequest) -> Response:
        form = LogoutForm(_json_body(request))
        if form.is_valid():
            refresh_token = form.cleaned_data.get("refresh_token")
            if refresh_token:
                try:
                    payload = decode_refresh_token(refresh_token)
                    revoke_refresh_token(payload)
                except TokenError:
                    pass
        logout(request)
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)


class MeView(APIView):
    def get(self, request: HttpRequest) -> Response:
        user = _authenticated_user_from_access_token(request)
        if user is None:
            return _error("Authentication credentials were not provided.", status=HTTPStatus.UNAUTHORIZED)
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "role": user.role,
                "marketing_consent": user.marketing_consent,
                "email_verified_at": user.email_verified_at.isoformat() if user.email_verified_at else None,
                "onboarding_completed_at": (
                    user.onboarding_completed_at.isoformat() if user.onboarding_completed_at else None
                ),
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class PasswordChangeApiView(APIView):
    def post(self, request: HttpRequest) -> Response:
        user = _authenticated_user_from_access_token(request)
        if user is None:
            return _error("Authentication required.", status=HTTPStatus.UNAUTHORIZED)
        form = PasswordChangeForm(_json_body(request))
        if not form.is_valid():
            return Response({"errors": form.errors.get_json_data()}, status=HTTPStatus.BAD_REQUEST)
        if not user.check_password(form.cleaned_data["current_password"]):
            return _error("Current password is incorrect.", status=HTTPStatus.BAD_REQUEST)

        new_password = form.cleaned_data["new_password"]
        try:
            validate_password(new_password, user)
        except ValidationError as exc:
            return Response({"errors": {"new_password": exc.messages}}, status=HTTPStatus.BAD_REQUEST)
        user.set_password(new_password)
        user.save(update_fields=["password"])
        update_session_auth_hash(request, user)
        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class PasswordResetRequestView(APIView):
    def post(self, request: HttpRequest) -> Response:
        form = PasswordResetRequestForm(_json_body(request))
        if not form.is_valid():
            return Response({"errors": form.errors.get_json_data()}, status=HTTPStatus.BAD_REQUEST)
        send_password_reset_email(form.cleaned_data["email"])
        return Response(
            {"detail": "If the account exists, password reset instructions have been sent."},
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class PasswordResetConfirmView(APIView):
    def post(self, request: HttpRequest) -> Response:
        form = PasswordResetConfirmForm(_json_body(request))
        if not form.is_valid():
            return Response({"errors": form.errors.get_json_data()}, status=HTTPStatus.BAD_REQUEST)
        new_password = form.cleaned_data["new_password"]
        try:
            validate_password(new_password)
        except ValidationError as exc:
            return Response({"errors": {"new_password": exc.messages}}, status=HTTPStatus.BAD_REQUEST)
        is_reset = reset_password(
            uid=form.cleaned_data["uid"],
            token=form.cleaned_data["token"],
            new_password=new_password,
        )
        if not is_reset:
            return _error("Invalid reset token.", status=HTTPStatus.BAD_REQUEST)
        return Response({"detail": "Password reset successful."}, status=status.HTTP_200_OK)
