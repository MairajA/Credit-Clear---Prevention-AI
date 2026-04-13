from __future__ import annotations

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegisterForm(forms.Form):
    """Signup — full name, email, password, confirm password, terms checkbox."""

    name = forms.CharField(max_length=255)
    email = forms.EmailField()
    password = forms.CharField()
    confirm_password = forms.CharField()
    terms_accepted = forms.BooleanField(required=True)
    privacy_accepted = forms.BooleanField(required=True)
    marketing_consent = forms.BooleanField(required=False)

    def clean_email(self) -> str:
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email=email).exists():
            msg = _("A user with this email already exists.")
            raise forms.ValidationError(msg)
        return email

    def clean_password(self) -> str:
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def clean(self) -> dict:
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", _("Passwords do not match."))
        return cleaned_data


class LoginForm(forms.Form):
    """Login — email + password."""

    email = forms.EmailField()
    password = forms.CharField()

    def clean(self) -> dict:
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if not email or not password:
            return cleaned_data
        user = authenticate(username=email, password=password)
        if user is None:
            msg = _("Invalid credentials.")
            raise forms.ValidationError(msg)
        if not user.is_active:
            msg = _("This account is inactive.")
            raise forms.ValidationError(msg)
        cleaned_data["user"] = user
        return cleaned_data


class PhoneNumberForm(forms.Form):
    """Phone number input — country code + phone number."""

    phone_country_code = forms.CharField(max_length=5, required=True)
    phone_number = forms.CharField(max_length=20, required=True)

    def clean_phone_number(self) -> str:
        phone = self.cleaned_data["phone_number"].strip()
        # Strip non-digit characters for storage
        digits_only = "".join(c for c in phone if c.isdigit())
        if len(digits_only) < 7 or len(digits_only) > 15:
            msg = _("Enter a valid phone number.")
            raise forms.ValidationError(msg)
        return digits_only


class OTPVerifyForm(forms.Form):
    """Verify Code — 6-digit OTP input."""

    code = forms.CharField(min_length=6, max_length=6)

    def clean_code(self) -> str:
        code = self.cleaned_data["code"].strip()
        if not code.isdigit():
            msg = _("Code must be numeric.")
            raise forms.ValidationError(msg)
        return code


class OTPResendForm(forms.Form):
    """Resend OTP code."""

    purpose = forms.ChoiceField(choices=[
        ("phone_verify", "Phone Verification"),
        ("email_verify", "Email Verification"),
        ("password_reset", "Password Reset"),
    ])


class RefreshTokenForm(forms.Form):
    refresh_token = forms.CharField()


class LogoutForm(forms.Form):
    refresh_token = forms.CharField(required=False)


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField()
    new_password = forms.CharField()


class PasswordResetRequestForm(forms.Form):
    """Forgot Password — request reset via email."""

    email = forms.EmailField()


class PasswordResetOTPForm(forms.Form):
    """Verify email — 4-digit code with 60s timer."""

    email = forms.EmailField()
    code = forms.CharField(min_length=6, max_length=6)


class PasswordResetConfirmForm(forms.Form):
    uid = forms.CharField()
    token = forms.CharField()
    new_password = forms.CharField()


class ProfileUpdateForm(forms.Form):
    """Profile/settings — editable user fields."""

    name = forms.CharField(max_length=255, required=False)
    phone_country_code = forms.CharField(max_length=5, required=False)
    phone_number = forms.CharField(max_length=20, required=False)
    marketing_consent = forms.BooleanField(required=False)
