from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class RiskMonitoringConfig(AppConfig):
    name = "credit_clear.risk_monitoring"
    verbose_name = _("Risk Monitoring")
