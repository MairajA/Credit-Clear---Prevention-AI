from __future__ import annotations

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class RegisterForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()
    name = forms.CharField(required=False, max_length=255)
    role = forms.ChoiceField(choices=User.Role.choices, required=False)
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


class LoginForm(forms.Form):
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


class RefreshTokenForm(forms.Form):
    refresh_token = forms.CharField()


class LogoutForm(forms.Form):
    refresh_token = forms.CharField(required=False)


class PasswordChangeForm(forms.Form):
    current_password = forms.CharField()
    new_password = forms.CharField()


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()


class PasswordResetConfirmForm(forms.Form):
    uid = forms.CharField()
    token = forms.CharField()
    new_password = forms.CharField()
