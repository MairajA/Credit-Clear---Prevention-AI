from __future__ import annotations

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from credit_clear.users.api.tokens import create_token_pair

User = get_user_model()


def register_user(*, email: str, password: str, name: str, role: str, marketing_consent: bool) -> User:
    now = timezone.now()
    user = User.objects.create_user(
        email=email,
        password=password,
        name=name,
        role=role,
        terms_accepted_at=now,
        privacy_accepted_at=now,
        marketing_consent=marketing_consent,
    )
    return user


def issue_token_pair_for_user(user: User) -> dict[str, str | int]:
    return create_token_pair(user.id)


def send_password_reset_email(email: str) -> None:
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
    reset_link = f"{frontend_url}/reset-password?uid={uid}&token={token}"
    send_mail(
        subject="Credit Clear password reset",
        message=f"Use this link to reset your password: {reset_link}",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@credit-clear.app"),
        recipient_list=[email],
    )


def reset_password(*, uid: str, token: str, new_password: str) -> bool:
    try:
        user_id = urlsafe_base64_decode(uid).decode()
        user = User.objects.get(pk=user_id)
    except (ValueError, TypeError, OverflowError, User.DoesNotExist):
        return False

    if not default_token_generator.check_token(user, token):
        return False
    user.set_password(new_password)
    user.save(update_fields=["password"])
    return True
