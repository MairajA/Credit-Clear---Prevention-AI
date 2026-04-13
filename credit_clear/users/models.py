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

    class OnboardingStep(TextChoices):
        REGISTERED = "registered", _("Registered")
        PHONE_VERIFIED = "phone_verified", _("Phone Verified")
        ACCOUNTS_CONNECTED = "accounts_connected", _("Accounts Connected")
        CARDS_CONFIRMED = "cards_confirmed", _("Cards Confirmed")
        BILLS_ADDED = "bills_added", _("Bills Added")
        ANALYSIS_COMPLETE = "analysis_complete", _("Analysis Complete")
        COMPLETED = "completed", _("Completed")

    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]
    role = CharField(max_length=32, choices=Role.choices, default=Role.CONSUMER, db_index=True)

    # Phone verification
    phone_number = CharField(_("phone number"), max_length=20, blank=True)
    phone_country_code = CharField(_("country code"), max_length=5, blank=True, default="+1")
    phone_verified_at = DateTimeField(null=True, blank=True)

    # Consent tracking
    terms_accepted_at = DateTimeField(null=True, blank=True)
    privacy_accepted_at = DateTimeField(null=True, blank=True)
    marketing_consent = BooleanField(default=False)

    # Verification
    email_verified_at = DateTimeField(null=True, blank=True)

    # Onboarding progress
    onboarding_step = CharField(
        max_length=32,
        choices=OnboardingStep.choices,
        default=OnboardingStep.REGISTERED,
        db_index=True,
    )
    onboarding_completed_at = DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    @property
    def is_phone_verified(self) -> bool:
        return self.phone_verified_at is not None

    @property
    def is_email_verified(self) -> bool:
        return self.email_verified_at is not None

    @property
    def is_onboarding_complete(self) -> bool:
        return self.onboarding_completed_at is not None

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"pk": self.id})
