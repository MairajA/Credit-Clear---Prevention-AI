from __future__ import annotations

import logging

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from credit_clear.ai_engine.models import CreditAnalysis
from credit_clear.ai_engine.models import CreditReportPull
from credit_clear.ai_engine.models import RecoveryPlan
from credit_clear.utils.auth import bearer_auth
from credit_clear.utils.response import created
from credit_clear.utils.response import not_found
from credit_clear.utils.response import success
from credit_clear.utils.response import validation_error

from .serializers import CreditAnalysisSerializer
from .serializers import CreditReportPullDetailSerializer
from .serializers import CreditReportPullRequestSerializer
from .serializers import CreditReportPullSerializer
from .serializers import RecoveryPlanGenerateSerializer
from .serializers import RecoveryPlanSerializer
from .serializers import RecoveryPlanUpdateSerializer

logger = logging.getLogger(__name__)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  CREDIT REPORT PULLS                                                    ║
# ╚══════════════════════════════════════════════════════════════════════════╝


class ReportPullListView(APIView):
    """
    GET /api/v1/ai-engine/report-pulls/
    List all credit report pulls for the authenticated user.

    Query params:
        bureau: experian | equifax | transunion
        status: pending | success | failed
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        qs = CreditReportPull.objects.filter(user=user).order_by("-pulled_at")

        bureau = request.query_params.get("bureau")
        if bureau:
            qs = qs.filter(bureau=bureau)

        pull_status = request.query_params.get("status")
        if pull_status:
            qs = qs.filter(status=pull_status)

        serializer = CreditReportPullSerializer(qs[:50], many=True)
        return success(serializer.data)


class ReportPullDetailView(APIView):
    """
    GET /api/v1/ai-engine/report-pulls/{id}/
    Get a single report pull with full details including raw_report.
    """

    def get(self, request, pk: int):
        user, err = bearer_auth(request)
        if err:
            return err

        try:
            pull = CreditReportPull.objects.get(pk=pk, user=user)
        except CreditReportPull.DoesNotExist:
            return not_found("Credit report pull not found.")

        serializer = CreditReportPullDetailSerializer(pull)
        return success(serializer.data)


@method_decorator(csrf_exempt, name="dispatch")
class ReportPullCreateView(APIView):
    """
    POST /api/v1/ai-engine/report-pulls/
    Initiate a new credit report pull from a bureau.

    Request body:
        { "bureau": "experian" }

    In production this dispatches a Celery task to pull from the bureau API.
    For now it creates a pending record.
    """

    def post(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        serializer = CreditReportPullRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        bureau = serializer.validated_data["bureau"]

        # Rate limit: max 3 pulls per day per user
        from django.utils import timezone
        from datetime import timedelta
        today_start = timezone.now() - timedelta(days=1)
        recent_count = CreditReportPull.objects.filter(
            user=user, bureau=bureau, pulled_at__gte=today_start,
        ).count()
        if recent_count >= 3:
            from credit_clear.utils.response import rate_limited
            return rate_limited("Maximum 3 bureau pulls per day. Please try again tomorrow.")

        pull = CreditReportPull.objects.create(
            user=user,
            bureau=bureau,
            status=CreditReportPull.PullStatus.PENDING,
        )

        # In production: dispatch Celery task
        # tasks.pull_credit_report.delay(pull.id)
        logger.info("Credit report pull initiated: user=%s bureau=%s pull_id=%s", user.id, bureau, pull.id)

        result = CreditReportPullSerializer(pull)
        return created(result.data)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  CREDIT ANALYSIS                                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝


class AnalysisListView(APIView):
    """
    GET /api/v1/ai-engine/analyses/
    List all credit analyses for the authenticated user.

    Query params:
        bureau_source: experian | equifax | transunion
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        qs = CreditAnalysis.objects.filter(user=user).select_related("report_pull").order_by("-generated_at")

        bureau = request.query_params.get("bureau_source")
        if bureau:
            qs = qs.filter(bureau_source=bureau)

        serializer = CreditAnalysisSerializer(qs[:50], many=True)
        return success(serializer.data)


class AnalysisDetailView(APIView):
    """
    GET /api/v1/ai-engine/analyses/{id}/
    Get a single analysis with detected errors and improvement opportunities.
    """

    def get(self, request, pk: int):
        user, err = bearer_auth(request)
        if err:
            return err

        try:
            analysis = CreditAnalysis.objects.select_related("report_pull").get(pk=pk, user=user)
        except CreditAnalysis.DoesNotExist:
            return not_found("Credit analysis not found.")

        serializer = CreditAnalysisSerializer(analysis)
        return success(serializer.data)


class AnalysisLatestView(APIView):
    """
    GET /api/v1/ai-engine/analyses/latest/
    Get the most recent credit analysis.
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        analysis = (
            CreditAnalysis.objects
            .filter(user=user)
            .select_related("report_pull")
            .order_by("-generated_at")
            .first()
        )
        if not analysis:
            return not_found("No credit analysis found. Initiate a credit report pull first.")

        serializer = CreditAnalysisSerializer(analysis)
        return success(serializer.data)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  RECOVERY PLAN                                                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝


class RecoveryPlanListView(APIView):
    """
    GET /api/v1/ai-engine/recovery-plans/
    List all recovery plans for the authenticated user.

    Query params:
        status: active | completed | archived
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        qs = RecoveryPlan.objects.filter(user=user).select_related("analysis").order_by("-created_at")

        plan_status = request.query_params.get("status")
        if plan_status:
            qs = qs.filter(status=plan_status)

        serializer = RecoveryPlanSerializer(qs[:20], many=True)
        return success(serializer.data)


class RecoveryPlanDetailView(APIView):
    """
    GET  /api/v1/ai-engine/recovery-plans/{id}/
    PATCH /api/v1/ai-engine/recovery-plans/{id}/
    """

    def get(self, request, pk: int):
        user, err = bearer_auth(request)
        if err:
            return err

        try:
            plan = RecoveryPlan.objects.select_related("analysis").get(pk=pk, user=user)
        except RecoveryPlan.DoesNotExist:
            return not_found("Recovery plan not found.")

        serializer = RecoveryPlanSerializer(plan)
        return success(serializer.data)

    def patch(self, request, pk: int):
        user, err = bearer_auth(request)
        if err:
            return err

        try:
            plan = RecoveryPlan.objects.get(pk=pk, user=user)
        except RecoveryPlan.DoesNotExist:
            return not_found("Recovery plan not found.")

        serializer = RecoveryPlanUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        plan.status = serializer.validated_data["status"]
        plan.save(update_fields=["status"])

        result = RecoveryPlanSerializer(plan)
        return success(result.data)


@method_decorator(csrf_exempt, name="dispatch")
class RecoveryPlanGenerateView(APIView):
    """
    POST /api/v1/ai-engine/recovery-plans/generate/
    Generate a new 90-day recovery plan based on the latest (or specified) analysis.

    Request body (optional):
        { "analysis_id": 123 }
    """

    def post(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        serializer = RecoveryPlanGenerateSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        analysis_id = serializer.validated_data.get("analysis_id")

        if analysis_id:
            try:
                analysis = CreditAnalysis.objects.get(pk=analysis_id, user=user)
            except CreditAnalysis.DoesNotExist:
                return not_found("Credit analysis not found.")
        else:
            analysis = CreditAnalysis.objects.filter(user=user).order_by("-generated_at").first()
            if not analysis:
                return not_found("No credit analysis found. Initiate a credit report pull first.")

        # In production: dispatch Celery task to generate plan via AI model
        # tasks.generate_recovery_plan.delay(user.id, analysis.id)
        plan = RecoveryPlan.objects.create(
            user=user,
            analysis=analysis,
            duration_days=90,
            status=RecoveryPlan.PlanStatus.ACTIVE,
            plan_data={
                "month_1": {
                    "title": "Foundation",
                    "actions": [
                        "File disputes for detected errors",
                        "Set up payment reminders",
                        "Link all accounts",
                    ],
                },
                "month_2": {
                    "title": "Build",
                    "actions": [
                        "Pay down highest utilization accounts",
                        "Apply for credit builder if applicable",
                        "Begin debt negotiation",
                    ],
                },
                "month_3": {
                    "title": "Optimize",
                    "actions": [
                        "Follow up on disputes",
                        "Open authorized tradeline if eligible",
                        "Review and optimize recurring bills",
                    ],
                },
            },
            generated_by_model="rpg-v1.0.0",
        )

        logger.info("Recovery plan generated: user=%s plan_id=%s", user.id, plan.id)

        result = RecoveryPlanSerializer(plan)
        return created(result.data)
