from rest_framework import serializers

from credit_clear.ai_engine.models import CreditAnalysis
from credit_clear.ai_engine.models import CreditReportPull
from credit_clear.ai_engine.models import RecoveryPlan


# ---------------------------------------------------------------------------
# Credit Report Pull
# ---------------------------------------------------------------------------

class CreditReportPullSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditReportPull
        fields = [
            "id",
            "bureau",
            "status",
            "score_at_pull",
            "total_accounts",
            "total_debt",
            "open_collections",
            "derogatory_marks",
            "hard_inquiries",
            "credit_utilization",
            "oldest_account_date",
            "error_message",
            "pulled_at",
        ]
        read_only_fields = fields


class CreditReportPullDetailSerializer(CreditReportPullSerializer):
    """Includes raw_report for detail view."""

    class Meta(CreditReportPullSerializer.Meta):
        fields = [*CreditReportPullSerializer.Meta.fields, "raw_report"]


class CreditReportPullRequestSerializer(serializers.Serializer):
    bureau = serializers.ChoiceField(choices=CreditReportPull.Bureau.choices)


# ---------------------------------------------------------------------------
# Credit Analysis
# ---------------------------------------------------------------------------

class CreditAnalysisSerializer(serializers.ModelSerializer):
    report_pull_id = serializers.IntegerField(source="report_pull.id", read_only=True, default=None)

    class Meta:
        model = CreditAnalysis
        fields = [
            "id",
            "report_pull_id",
            "bureau_source",
            "credit_score",
            "risk_summary",
            "detected_errors",
            "improvement_opportunities",
            "estimated_score_gain",
            "model_version",
            "generated_at",
        ]
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Recovery Plan
# ---------------------------------------------------------------------------

class RecoveryPlanSerializer(serializers.ModelSerializer):
    analysis_id = serializers.IntegerField(source="analysis.id", read_only=True, default=None)

    class Meta:
        model = RecoveryPlan
        fields = [
            "id",
            "analysis_id",
            "duration_days",
            "status",
            "plan_data",
            "generated_by_model",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class RecoveryPlanGenerateSerializer(serializers.Serializer):
    analysis_id = serializers.IntegerField(
        required=False,
        help_text="Optional: ID of a CreditAnalysis to base the plan on. Defaults to latest.",
    )


class RecoveryPlanUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=RecoveryPlan.PlanStatus.choices)
