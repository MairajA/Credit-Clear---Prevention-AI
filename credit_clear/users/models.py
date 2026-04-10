from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import EmailField
from django.db.models import TextChoices
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """
    Default custom user model for Credit Clear.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)

    class Role(TextChoices):
        CONSUMER = "consumer", _("Consumer")
        SUPPORT_AGENT = "support_agent", _("Support Agent")
        RISK_ANALYST = "risk_analyst", _("Risk Analyst")
        ADMIN = "admin", _("Admin")

    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]
    role = CharField(max_length=32, choices=Role.choices, default=Role.CONSUMER, db_index=True)
    terms_accepted_at = DateTimeField(null=True, blank=True)
    privacy_accepted_at = DateTimeField(null=True, blank=True)
    marketing_consent = BooleanField(default=False)
    email_verified_at = DateTimeField(null=True, blank=True)
    onboarding_completed_at = DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})
