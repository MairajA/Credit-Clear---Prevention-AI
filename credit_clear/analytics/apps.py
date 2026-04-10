from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AnalyticsConfig(AppConfig):
    name = "credit_clear.analytics"
    verbose_name = _("Analytics")
