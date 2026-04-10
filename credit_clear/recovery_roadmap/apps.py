from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RecoveryRoadmapConfig(AppConfig):
    name = "credit_clear.recovery_roadmap"
    verbose_name = _("Recovery Roadmap")
