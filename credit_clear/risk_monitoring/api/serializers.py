from rest_framework import serializers

from credit_clear.risk_monitoring.models import RiskAlert
from credit_clear.risk_monitoring.models import RiskScoreSnapshot


class RiskScoreSnapshotSerializer(serializers.ModelSerializer):
    account_display_name = serializers.CharField(
        source="account.display_name", read_only=True, default=None,
    )

    class Meta:
        model = RiskScoreSnapshot
        fields = [
            "id",
            "account",
            "account_display_name",
            "missed_payment_probability",
            "threshold",
            "score_factors",
            "evaluated_at",
        ]
        read_only_fields = fields


class RiskAlertSerializer(serializers.ModelSerializer):
    risk_score_id = serializers.IntegerField(source="risk_score.id", read_only=True)
    missed_payment_probability = serializers.DecimalField(
        source="risk_score.missed_payment_probability",
        max_digits=5, decimal_places=2, read_only=True,
    )

    class Meta:
        model = RiskAlert
        fields = [
            "id",
            "risk_score_id",
            "missed_payment_probability",
            "title",
            "message",
            "status",
            "triggered_at",
            "resolved_at",
        ]
        read_only_fields = fields


class RiskDashboardSerializer(serializers.Serializer):
    current_score = serializers.DecimalField(max_digits=5, decimal_places=2, allow_null=True)
    score_trend = serializers.CharField()  # "improving" | "stable" | "declining"
    open_alerts_count = serializers.IntegerField()
    resolved_alerts_count = serializers.IntegerField()
    highest_risk_account = serializers.DictField(allow_null=True)
    last_evaluated_at = serializers.DateTimeField(allow_null=True)
