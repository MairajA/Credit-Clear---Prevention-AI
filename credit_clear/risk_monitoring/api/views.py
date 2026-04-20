from __future__ import annotations

import logging
from datetime import timedelta

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from credit_clear.risk_monitoring.models import RiskAlert
from credit_clear.risk_monitoring.models import RiskScoreSnapshot
from credit_clear.utils.auth import bearer_auth
from credit_clear.utils.response import not_found
from credit_clear.utils.response import success
from credit_clear.utils.response import validation_error

from .serializers import RiskAlertSerializer
from .serializers import RiskDashboardSerializer
from .serializers import RiskScoreSnapshotSerializer

logger = logging.getLogger(__name__)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  RISK SCORES                                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝


class RiskScoreListView(APIView):
    """
    GET /api/v1/risk-monitoring/scores/
    List risk score history.

    Query params:
        account: filter by account ID
        days: number of days of history (default 30)
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        days = int(request.query_params.get("days", 30))
        since = timezone.now() - timedelta(days=days)

        qs = (
            RiskScoreSnapshot.objects
            .filter(user=user, evaluated_at__gte=since)
            .select_related("account")
            .order_by("-evaluated_at")
        )

        account_id = request.query_params.get("account")
        if account_id:
            qs = qs.filter(account_id=account_id)

        serializer = RiskScoreSnapshotSerializer(qs[:100], many=True)
        return success(serializer.data)


class RiskScoreLatestView(APIView):
    """
    GET /api/v1/risk-monitoring/scores/latest/
    Get the most recent risk score.
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        score = (
            RiskScoreSnapshot.objects
            .filter(user=user)
            .select_related("account")
            .order_by("-evaluated_at")
            .first()
        )
        if not score:
            return not_found("No risk score available yet.")

        serializer = RiskScoreSnapshotSerializer(score)
        return success(serializer.data)


class RiskScoreDetailView(APIView):
    """
    GET /api/v1/risk-monitoring/scores/{id}/
    """

    def get(self, request, pk: int):
        user, err = bearer_auth(request)
        if err:
            return err

        try:
            score = RiskScoreSnapshot.objects.select_related("account").get(pk=pk, user=user)
        except RiskScoreSnapshot.DoesNotExist:
            return not_found("Risk score snapshot not found.")

        serializer = RiskScoreSnapshotSerializer(score)
        return success(serializer.data)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  RISK ALERTS                                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝


class RiskAlertListView(APIView):
    """
    GET /api/v1/risk-monitoring/alerts/
    List risk alerts.

    Query params:
        status: open | acknowledged | resolved
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        qs = (
            RiskAlert.objects
            .filter(user=user)
            .select_related("risk_score")
            .order_by("-triggered_at")
        )

        alert_status = request.query_params.get("status")
        if alert_status:
            qs = qs.filter(status=alert_status)

        serializer = RiskAlertSerializer(qs[:50], many=True)
        return success(serializer.data)


class RiskAlertDetailView(APIView):
    """
    GET /api/v1/risk-monitoring/alerts/{id}/
    """

    def get(self, request, pk: int):
        user, err = bearer_auth(request)
        if err:
            return err

        try:
            alert = RiskAlert.objects.select_related("risk_score").get(pk=pk, user=user)
        except RiskAlert.DoesNotExist:
            return not_found("Risk alert not found.")

        serializer = RiskAlertSerializer(alert)
        return success(serializer.data)


@method_decorator(csrf_exempt, name="dispatch")
class RiskAlertAcknowledgeView(APIView):
    """
    PATCH /api/v1/risk-monitoring/alerts/{id}/acknowledge/
    Mark alert as acknowledged by the user.
    """

    def patch(self, request, pk: int):
        user, err = bearer_auth(request)
        if err:
            return err

        try:
            alert = RiskAlert.objects.select_related("risk_score").get(pk=pk, user=user)
        except RiskAlert.DoesNotExist:
            return not_found("Risk alert not found.")

        if alert.status != RiskAlert.AlertStatus.OPEN:
            from credit_clear.utils.response import error, CONFLICT
            return error(
                f"Alert is already {alert.status}.",
                code=CONFLICT,
                status=409,
            )

        alert.status = RiskAlert.AlertStatus.ACKNOWLEDGED
        alert.save(update_fields=["status"])

        serializer = RiskAlertSerializer(alert)
        return success(serializer.data)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  RISK DASHBOARD                                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝


class RiskDashboardView(APIView):
    """
    GET /api/v1/risk-monitoring/dashboard/
    Aggregated risk overview for the user's dashboard.
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        # Latest score
        latest_score = (
            RiskScoreSnapshot.objects
            .filter(user=user)
            .select_related("account")
            .order_by("-evaluated_at")
            .first()
        )

        # Score trend (compare last 2 scores)
        trend = "stable"
        if latest_score:
            previous = (
                RiskScoreSnapshot.objects
                .filter(user=user, evaluated_at__lt=latest_score.evaluated_at)
                .order_by("-evaluated_at")
                .first()
            )
            if previous:
                diff = latest_score.missed_payment_probability - previous.missed_payment_probability
                if diff > 5:
                    trend = "declining"
                elif diff < -5:
                    trend = "improving"

        # Alert counts
        open_count = RiskAlert.objects.filter(user=user, status=RiskAlert.AlertStatus.OPEN).count()
        resolved_count = RiskAlert.objects.filter(user=user, status=RiskAlert.AlertStatus.RESOLVED).count()

        # Highest risk account
        highest_risk = None
        if latest_score and latest_score.account:
            highest_risk = {
                "account_id": latest_score.account.id,
                "display_name": latest_score.account.display_name,
                "probability": float(latest_score.missed_payment_probability),
            }

        data = {
            "current_score": float(latest_score.missed_payment_probability) if latest_score else None,
            "score_trend": trend,
            "open_alerts_count": open_count,
            "resolved_alerts_count": resolved_count,
            "highest_risk_account": highest_risk,
            "last_evaluated_at": latest_score.evaluated_at if latest_score else None,
        }
        serializer = RiskDashboardSerializer(data)
        return success(serializer.data)
