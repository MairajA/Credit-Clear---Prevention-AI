from django.conf import settings
from django.db import models

from credit_clear.ai_engine.models import RecoveryPlan


class RoadmapMilestone(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        SKIPPED = "skipped", "Skipped"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="roadmap_milestones")
    recovery_plan = models.ForeignKey(RecoveryPlan, on_delete=models.SET_NULL, null=True, blank=True)
    month_index = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("user", "month_index", "title")]


class RoadmapAction(models.Model):
    class ActionType(models.TextChoices):
        DISPUTE = "dispute", "File Dispute"
        REDUCE_UTILIZATION = "reduce_utilization", "Reduce Utilization"
        OPEN_BUILDER = "open_builder", "Open Builder Account"
        NEGOTIATE_DEBT = "negotiate_debt", "Negotiate Debt"
        PAY_BILL = "pay_bill", "Pay Bill"
        APPLY_CARD = "apply_card", "Apply for Card"
        MONITOR = "monitor", "Monitor Report"
        CUSTOM = "custom", "Custom Action"

    class ActionStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        SKIPPED = "skipped", "Skipped"

    milestone = models.ForeignKey(RoadmapMilestone, on_delete=models.CASCADE, related_name="actions")
    action_type = models.CharField(max_length=30, choices=ActionType.choices, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=ActionStatus.choices, default=ActionStatus.PENDING, db_index=True)
    estimated_score_impact = models.SmallIntegerField(default=0)
    target_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    linked_case_id = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["milestone", "order"]
