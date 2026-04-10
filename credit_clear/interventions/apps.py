from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InterventionsConfig(AppConfig):
    name = "credit_clear.interventions"
    verbose_name = _("Interventions")
