from django.conf import settings
from django.db import models


class EventLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    event_name = models.CharField(max_length=120, db_index=True)
    event_source = models.CharField(max_length=120, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    occurred_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [models.Index(fields=["event_name", "occurred_at"])]


class ModelPerformanceMetric(models.Model):
    metric_name = models.CharField(max_length=120, db_index=True)
    model_version = models.CharField(max_length=50, db_index=True)
    metric_value = models.DecimalField(max_digits=10, decimal_places=4)
    evaluated_at = models.DateTimeField(auto_now_add=True, db_index=True)
    context = models.JSONField(default=dict, blank=True)
