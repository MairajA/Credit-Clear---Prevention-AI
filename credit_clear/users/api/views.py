from __future__ import annotations

import json
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from credit_clear.users.api.forms import LoginForm
from credit_clear.users.api.forms import LogoutForm
from credit_clear.users.api.forms import OTPResendForm
from credit_clear.users.api.forms import OTPVerifyForm
from credit_clear.users.api.forms import PasswordChangeForm
from credit_clear.users.api.forms import PasswordResetConfirmForm
from credit_clear.users.api.forms import PasswordResetRequestForm
from credit_clear.users.api.forms import PhoneNumberForm
from credit_clear.users.api.forms import ProfileUpdateForm
from credit_clear.users.api.forms import RefreshTokenForm
from credit_clear.users.api.forms import RegisterForm
from credit_clear.users.api.otp import generate_otp
from credit_clear.users.api.otp import verify_otp
from credit_clear.users.api.services import issue_token_pair_for_user
from credit_clear.users.api.services import register_user
from credit_clear.users.api.services import reset_password
from credit_clear.users.api.services import send_password_reset_email
from credit_clear.users.api.tokens import TokenError
from credit_clear.users.api.tokens import decode_refresh_token
from credit_clear.users.api.tokens import revoke_refresh_token
from credit_clear.utils.auth import bearer_auth
from credit_clear.utils.response import auth_error
from credit_clear.utils.response import created
from credit_clear.utils.response import error
from credit_clear.utils.response import rate_limited
from credit_clear.utils.response import success
from credit_clear.utils.response import validation_error
from credit_clear.utils.response import AUTH_ERROR
from credit_clear.utils.response import VALIDATION_ERROR

User = get_user_model()
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _json_body(request: HttpRequest) -> dict:
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return {}


def _user_data(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "phone_number": user.phone_number,
        "phone_country_code": user.phone_country_code,
        "phone_verified_at": user.phone_verified_at.isoformat() if user.phone_verified_at else None,
        "email_verified_at": user.email_verified_at.isoformat() if user.email_verified_at else None,
        "marketing_consent": user.marketing_consent,
        "terms_accepted_at": user.terms_accepted_at.isoformat() if user.terms_accepted_at else None,
        "privacy_accepted_at": user.privacy_accepted_at.isoformat() if user.privacy_accepted_at else None,
        "onboarding_step": user.onboarding_step,
        "onboarding_completed_at": (
            user.onboarding_completed_at.isoformat() if user.onboarding_completed_at else None
        ),
    }


# ---------------------------------------------------------------------------
# POST /api/v1/auth/register/
# Fields: name, email, password, confirm_password, terms_accepted, privacy_accepted
# ---------------------------------------------------------------------------

@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(APIView):
    def post(self, request: HttpRequest):
        form = RegisterForm(_json_body(request))
        if not form.is_valid():
            return validation_error(form.errors.get_json_data())
        user = register_user(
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
            name=form.cleaned_data["name"],
            marketing_consent=form.cleaned_data.get("marketing_consent", False),
        )
        login(request, user)
        tokens = issue_token_pair_for_user(user)
        return created({"user": _user_data(user), "tokens": tokens})


# ---------------------------------------------------------------------------
# POST /api/v1/auth/login/
# ---------------------------------------------------------------------------

@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    def post(self, request: HttpRequest):
        form = LoginForm(_json_body(request))
        if not form.is_valid():
            return error("Invalid credentials.", code=AUTH_ERROR, status=401, errors=form.errors.get_json_data())
        user = form.cleaned_data["user"]
        login(request, user)
        tokens = issue_token_pair_for_user(user)
        return success({"user": _user_data(user), "tokens": tokens})


# ---------------------------------------------------------------------------
# POST /api/v1/auth/phone/submit/
# Saves phone number and sends OTP
# ---------------------------------------------------------------------------

@method_decorator(csrf_exempt, name="dispatch")
class PhoneSubmitView(APIView):
    def post(self, request: HttpRequest):
        user, err = bearer_auth(request)
        if err:
            return err
        form = PhoneNumberForm(_json_body(request))
        if not form.is_valid():
            return validation_error(form.errors.get_json_data())

        user.phone_number = form.cleaned_data["phone_number"]
        user.phone_country_code = form.cleaned_data["phone_country_code"]
        user.save(update_fields=["phone_number", "phone_country_code"])

        full_phone = f"{user.phone_country_code}{user.phone_number}"
        code = generate_otp("phone_verify", full_phone)
        if code is None:
            return rate_limited("Please wait before requesting a new code.")

        # In production, send via Twilio. For now, log it.
        logger.info("Phone OTP for %s: %s", full_phone, code)

        return success({"detail": "Verification code sent.", "phone_number": user.phone_number})


# ---------------------------------------------------------------------------
# POST /api/v1/auth/phone/verify/
# ---------------------------------------------------------------------------

@method_decorator(csrf_exempt, name="dispatch")
class PhoneVerifyView(APIView):
    def post(self, request: HttpRequest):
        user, err = bearer_auth(request)
        if err:
            return err
        form = OTPVerifyForm(_json_body(request))
        if not form.is_valid():
            return validation_error(form.errors.get_json_data())

        full_phone = f"{user.phone_country_code}{user.phone_number}"
        if not full_phone or not user.phone_number:
            return error("No phone number on file. Submit phone number first.", code=VALIDATION_ERROR, status=400)

        if not verify_otp("phone_verify", full_phone, form.cleaned_data["code"]):
            return error("Invalid or expired verification code.", code=VALIDATION_ERROR, status=400)

        user.phone_verified_at = timezone.now()
        if user.onboarding_step == User.OnboardingStep.REGISTERED:
            user.onboarding_step = User.OnboardingStep.PHONE_VERIFIED
        user.save(update_fields=["phone_verified_at", "onboarding_step"])

        return success({"detail": "Phone verified successfully.", "user": _user_data(user)})


# ---------------------------------------------------------------------------
# POST /api/v1/auth/otp/resend/
# ---------------------------------------------------------------------------

@method_decorator(csrf_exempt, name="dispatch")
class OTPResendView(APIView):
    def post(self, request: HttpRequest):
        user, err = bearer_auth(request)
        if err:
            return err
        form = OTPResendForm(_json_body(request))
        if not form.is_valid():
            return validation_error(form.errors.get_json_data())

        purpose = form.cleaned_data["purpose"]
        if purpose == "phone_verify":
            identifier = f"{user.phone_country_code}{user.phone_number}"
            if not user.phone_number:
                return error("No phone number on file.", code=VALIDATION_ERROR, status=400)
        else:
            identifier = user.email

        code = generate_otp(purpose, identifier)
        if code is None:
            return rate_limited("Please wait before requesting a new code.")

        logger.info("OTP resend [%s] for %s: %s", purpose, identifier, code)

        return success({"detail": "Verification code sent."})


# ---------------------------------------------------------------------------
# Token refresh / logout
# ---------------------------------------------------------------------------

@method_decorator(csrf_exempt, name="dispatch")
class RefreshTokenView(APIView):
    def post(self, request: HttpRequest):
        form = RefreshTokenForm(_json_body(request))
        if not form.is_valid():
            return validation_error(form.errors.get_json_data())

        refresh_token = form.cleaned_data["refresh_token"]
        try:
            payload = decode_refresh_token(refresh_token)
        except TokenError as exc:
            return auth_error(str(exc))

        revoke_refresh_token(payload)
        user_id = payload.get("sub")
        if user_id is None:
            return auth_error("Invalid refresh token payload.")
        try:
            user = User.objects.get(pk=int(user_id), is_active=True)
        except (User.DoesNotExist, ValueError):
            return auth_error("User not found.")
        tokens = issue_token_pair_for_user(user)
        return success({"tokens": tokens})


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    def post(self, request: HttpRequest):
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
        return success({"detail": "Logged out successfully."})


# ---------------------------------------------------------------------------
# GET  /api/v1/auth/me/      — full profile
# PATCH /api/v1/auth/me/     — update profile
# ---------------------------------------------------------------------------

class MeView(APIView):
    def get(self, request: HttpRequest):
        user, err = bearer_auth(request)
        if err:
            return err
        return success(_user_data(user))

    def patch(self, request: HttpRequest):
        user, err = bearer_auth(request)
        if err:
            return err
        form = ProfileUpdateForm(_json_body(request))
        if not form.is_valid():
            return validation_error(form.errors.get_json_data())

        update_fields = []
        for field in ("name", "phone_country_code", "phone_number", "marketing_consent"):
            value = form.cleaned_data.get(field)
            if value is not None and value != "":
                setattr(user, field, value)
                update_fields.append(field)

        if update_fields:
            user.save(update_fields=update_fields)

        return success(_user_data(user))


# ---------------------------------------------------------------------------
# GET  /api/v1/auth/onboarding/status/
# POST /api/v1/auth/onboarding/advance/
# ---------------------------------------------------------------------------

class OnboardingStatusView(APIView):
    def get(self, request: HttpRequest):
        user, err = bearer_auth(request)
        if err:
            return err
        return success({
            "onboarding_step": user.onboarding_step,
            "is_complete": user.is_onboarding_complete,
            "steps": {
                "registered": True,
                "phone_verified": user.is_phone_verified,
                "accounts_connected": user.onboarding_step in (
                    User.OnboardingStep.ACCOUNTS_CONNECTED,
                    User.OnboardingStep.CARDS_CONFIRMED,
                    User.OnboardingStep.BILLS_ADDED,
                    User.OnboardingStep.ANALYSIS_COMPLETE,
                    User.OnboardingStep.COMPLETED,
                ),
                "cards_confirmed": user.onboarding_step in (
                    User.OnboardingStep.CARDS_CONFIRMED,
                    User.OnboardingStep.BILLS_ADDED,
                    User.OnboardingStep.ANALYSIS_COMPLETE,
                    User.OnboardingStep.COMPLETED,
                ),
                "bills_added": user.onboarding_step in (
                    User.OnboardingStep.BILLS_ADDED,
                    User.OnboardingStep.ANALYSIS_COMPLETE,
                    User.OnboardingStep.COMPLETED,
                ),
                "analysis_complete": user.onboarding_step in (
                    User.OnboardingStep.ANALYSIS_COMPLETE,
                    User.OnboardingStep.COMPLETED,
                ),
                "completed": user.onboarding_step == User.OnboardingStep.COMPLETED,
            },
        })


@method_decorator(csrf_exempt, name="dispatch")
class OnboardingAdvanceView(APIView):
    """Advance onboarding to the next step. Called by frontend after each flow completes."""

    STEP_ORDER = [
        User.OnboardingStep.REGISTERED,
        User.OnboardingStep.PHONE_VERIFIED,
        User.OnboardingStep.ACCOUNTS_CONNECTED,
        User.OnboardingStep.CARDS_CONFIRMED,
        User.OnboardingStep.BILLS_ADDED,
        User.OnboardingStep.ANALYSIS_COMPLETE,
        User.OnboardingStep.COMPLETED,
    ]

    def post(self, request: HttpRequest):
        user, err = bearer_auth(request)
        if err:
            return err

        body = _json_body(request)
        target_step = body.get("step")

        if target_step and target_step in User.OnboardingStep.values:
            user.onboarding_step = target_step
        else:
            try:
                current_idx = self.STEP_ORDER.index(user.onboarding_step)
            except ValueError:
                current_idx = 0
            next_idx = min(current_idx + 1, len(self.STEP_ORDER) - 1)
            user.onboarding_step = self.STEP_ORDER[next_idx]

        update_fields = ["onboarding_step"]
        if user.onboarding_step == User.OnboardingStep.COMPLETED:
            user.onboarding_completed_at = timezone.now()
            update_fields.append("onboarding_completed_at")

        user.save(update_fields=update_fields)
        return success({
            "onboarding_step": user.onboarding_step,
            "is_complete": user.is_onboarding_complete,
        })


# ---------------------------------------------------------------------------
# Password management
# ---------------------------------------------------------------------------

@method_decorator(csrf_exempt, name="dispatch")
class PasswordChangeApiView(APIView):
    def post(self, request: HttpRequest):
        user, err = bearer_auth(request)
        if err:
            return err
        form = PasswordChangeForm(_json_body(request))
        if not form.is_valid():
            return validation_error(form.errors.get_json_data())
        if not user.check_password(form.cleaned_data["current_password"]):
            return error("Current password is incorrect.", code=VALIDATION_ERROR, status=400)

        new_password = form.cleaned_data["new_password"]
        try:
            validate_password(new_password, user)
        except ValidationError as exc:
            return validation_error({"new_password": exc.messages})
        user.set_password(new_password)
        user.save(update_fields=["password"])
        update_session_auth_hash(request, user)
        return success({"detail": "Password changed successfully."})


@method_decorator(csrf_exempt, name="dispatch")
class PasswordResetRequestView(APIView):
    """Forgot Password — sends OTP to email."""

    def post(self, request: HttpRequest):
        form = PasswordResetRequestForm(_json_body(request))
        if not form.is_valid():
            return validation_error(form.errors.get_json_data())

        email = form.cleaned_data["email"]

        code = generate_otp("password_reset", email)
        if code:
            logger.info("Password reset OTP for %s: %s", email, code)

        send_password_reset_email(email)

        return success({"detail": "If the account exists, password reset instructions have been sent."})


@method_decorator(csrf_exempt, name="dispatch")
class PasswordResetConfirmView(APIView):
    def post(self, request: HttpRequest):
        form = PasswordResetConfirmForm(_json_body(request))
        if not form.is_valid():
            return validation_error(form.errors.get_json_data())
        new_password = form.cleaned_data["new_password"]
        try:
            validate_password(new_password)
        except ValidationError as exc:
            return validation_error({"new_password": exc.messages})
        is_reset = reset_password(
            uid=form.cleaned_data["uid"],
            token=form.cleaned_data["token"],
            new_password=new_password,
        )
        if not is_reset:
            return error("Invalid reset token.", code=VALIDATION_ERROR, status=400)
        return success({"detail": "Password reset successful."})
