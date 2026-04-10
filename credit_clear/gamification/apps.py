from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class GamificationConfig(AppConfig):
    name = "credit_clear.gamification"
    verbose_name = _("Gamification")
