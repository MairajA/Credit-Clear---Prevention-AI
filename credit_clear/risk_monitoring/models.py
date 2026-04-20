from django.conf import settings
from django.db import models

from credit_clear.accounts.models import LinkedAccount


class RiskScoreSnapshot(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="risk_scores")
    account = models.ForeignKey(LinkedAccount, on_delete=models.SET_NULL, null=True, blank=True)
    missed_payment_probability = models.DecimalField(max_digits=5, decimal_places=2)
    threshold = models.DecimalField(max_digits=5, decimal_places=2, default=70)
    score_factors = models.JSONField(default=dict, blank=True)
    evaluated_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [models.Index(fields=["user", "evaluated_at"])]


class RiskAlert(models.Model):
    class AlertStatus(models.TextChoices):
        OPEN = "open", "Open"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="risk_alerts")
    risk_score = models.ForeignKey(RiskScoreSnapshot, on_delete=models.CASCADE, related_name="alerts")
    title = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=AlertStatus.choices, default=AlertStatus.OPEN, db_index=True)
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
