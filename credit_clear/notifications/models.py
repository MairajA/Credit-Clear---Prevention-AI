from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Channel(models.TextChoices):
        IN_APP = "in_app", "In App"
        EMAIL = "email", "Email"
        SMS = "sms", "SMS"
        PUSH = "push", "Push"

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed"
        READ = "read", "Read"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    channel = models.CharField(max_length=20, choices=Channel.choices, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.QUEUED, db_index=True)
    title = models.CharField(max_length=255)
    message = models.TextField()
    payload = models.JSONField(default=dict, blank=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user", "status", "created_at"])]


class NotificationPreference(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_preferences")
    channel = models.CharField(max_length=20, choices=Notification.Channel.choices)
    risk_alerts = models.BooleanField(default=True)
    intervention_updates = models.BooleanField(default=True)
    payment_reminders = models.BooleanField(default=True)
    score_changes = models.BooleanField(default=True)
    fraud_alerts = models.BooleanField(default=True)
    marketing = models.BooleanField(default=False)
    weekly_summary = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    is_enabled = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("user", "channel")]
