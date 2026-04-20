from django.conf import settings
from django.db import models

from credit_clear.risk_monitoring.models import RiskAlert


class Creditor(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    api_endpoint = models.URLField(blank=True)
    api_key_ref = models.CharField(max_length=255, blank=True)
    supported_strategies = models.JSONField(default=list, blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    supports_auto_negotiation = models.BooleanField(default=False)
    avg_response_time_hours = models.PositiveIntegerField(null=True, blank=True)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]


class Intervention(models.Model):
    class Strategy(models.TextChoices):
        EXTENSION = "extension", "Payment Extension"
        GRACE_PERIOD = "grace_period", "Grace Period"
        DUE_DATE_CHANGE = "due_date_change", "Due Date Change"
        INSTALLMENT = "installment", "Installment Conversion"
        BNPL = "bnpl", "BNPL"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        DENIED = "denied", "Denied"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="interventions")
    risk_alert = models.ForeignKey(RiskAlert, on_delete=models.SET_NULL, null=True, blank=True)
    creditor = models.ForeignKey(Creditor, on_delete=models.SET_NULL, null=True, blank=True, related_name="interventions")
    strategy = models.CharField(max_length=30, choices=Strategy.choices, db_index=True)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    creditor_reference = models.CharField(max_length=255, blank=True)
    requested_payload = models.JSONField(default=dict, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    executed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CreditorCommunicationLog(models.Model):
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE, related_name="communications")
    request_id = models.CharField(max_length=255, db_index=True)
    endpoint = models.CharField(max_length=255)
    http_status = models.PositiveSmallIntegerField(null=True, blank=True)
    request_body = models.JSONField(default=dict, blank=True)
    response_body = models.JSONField(default=dict, blank=True)
    latency_ms = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
