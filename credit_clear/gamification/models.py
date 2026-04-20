from django.conf import settings
from django.db import models


class Badge(models.Model):
    key = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    points_reward = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)


class UserPointsBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="points_balance")
    total_points = models.PositiveIntegerField(default=0)
    level = models.PositiveSmallIntegerField(default=1)
    streak_days = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_activity_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserReward(models.Model):
    class RewardSource(models.TextChoices):
        DISPUTE_FILED = "dispute_filed", "Dispute Filed"
        PAYMENT_ON_TIME = "payment_on_time", "Payment On Time"
        SCORE_IMPROVED = "score_improved", "Score Improved"
        COURSE_COMPLETED = "course_completed", "Course Completed"
        ACCOUNT_LINKED = "account_linked", "Account Linked"
        STREAK_BONUS = "streak_bonus", "Streak Bonus"
        REFERRAL = "referral", "Referral"
        MILESTONE = "milestone", "Milestone Reached"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rewards")
    badge = models.ForeignKey(Badge, on_delete=models.SET_NULL, null=True, blank=True)
    points_delta = models.IntegerField(default=0)
    source = models.CharField(max_length=30, choices=RewardSource.choices, blank=True, db_index=True)
    reason = models.CharField(max_length=255)
    awarded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["user", "awarded_at"])]
