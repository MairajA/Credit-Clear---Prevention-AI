from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FallbackPaymentConfig(AppConfig):
    name = "credit_clear.fallback_payment"
    verbose_name = _("Fallback Payment")
