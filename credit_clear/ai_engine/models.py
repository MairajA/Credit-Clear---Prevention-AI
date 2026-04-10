from django.conf import settings
from django.db import models


class CreditReportPull(models.Model):
    class Bureau(models.TextChoices):
        EXPERIAN = "experian", "Experian"
        EQUIFAX = "equifax", "Equifax"
        TRANSUNION = "transunion", "TransUnion"

    class PullStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        SUCCESS = "success", "Success"
        FAILED = "failed", "Failed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="credit_report_pulls")
    bureau = models.CharField(max_length=20, choices=Bureau.choices, db_index=True)
    status = models.CharField(max_length=20, choices=PullStatus.choices, default=PullStatus.PENDING, db_index=True)
    raw_report = models.JSONField(default=dict, blank=True)
    score_at_pull = models.PositiveSmallIntegerField(null=True, blank=True)
    total_accounts = models.PositiveIntegerField(default=0)
    total_debt = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    open_collections = models.PositiveIntegerField(default=0)
    derogatory_marks = models.PositiveIntegerField(default=0)
    hard_inquiries = models.PositiveIntegerField(default=0)
    credit_utilization = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    oldest_account_date = models.DateField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    pulled_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [models.Index(fields=["user", "bureau", "pulled_at"])]


class CreditAnalysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="credit_analyses")
    report_pull = models.ForeignKey(CreditReportPull, on_delete=models.SET_NULL, null=True, blank=True, related_name="analyses")
    bureau_source = models.CharField(max_length=50)
    credit_score = models.PositiveSmallIntegerField(null=True, blank=True)
    risk_summary = models.TextField(blank=True)
    detected_errors = models.JSONField(default=list, blank=True)
    improvement_opportunities = models.JSONField(default=list, blank=True)
    estimated_score_gain = models.PositiveSmallIntegerField(default=0)
    model_version = models.CharField(max_length=50, db_index=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user", "generated_at"])]


class RecoveryPlan(models.Model):
    class PlanStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        ARCHIVED = "archived", "Archived"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recovery_plans")
    analysis = models.ForeignKey(CreditAnalysis, on_delete=models.SET_NULL, null=True, blank=True)
    duration_days = models.PositiveIntegerField(default=90)
    status = models.CharField(max_length=20, choices=PlanStatus.choices, default=PlanStatus.ACTIVE, db_index=True)
    plan_data = models.JSONField(default=dict, blank=True)
    generated_by_model = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
