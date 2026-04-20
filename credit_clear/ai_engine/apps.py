from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AiEngineConfig(AppConfig):
    name = "credit_clear.ai_engine"
    verbose_name = _("AI Engine")
