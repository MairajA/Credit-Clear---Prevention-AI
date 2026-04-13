from __future__ import annotations

import logging

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from credit_clear.accounts.models import FinancialInstitution
from credit_clear.accounts.models import LinkedAccount
from credit_clear.accounts.models import PaymentDue
from credit_clear.accounts.models import Transaction
from credit_clear.users.api.views import _json_body
from credit_clear.utils.auth import bearer_auth
from credit_clear.utils.response import created
from credit_clear.utils.response import no_content
from credit_clear.utils.response import not_found
from credit_clear.utils.response import success
from credit_clear.utils.response import validation_error

from .serializers import AnalysisStatusSerializer
from .serializers import FinancialInstitutionSerializer
from .serializers import LinkedAccountCreateSerializer
from .serializers import LinkedAccountSerializer
from .serializers import ManualAccountSerializer
from .serializers import ManualBillSerializer
from .serializers import PaymentDueSerializer
from .serializers import ScanResultSerializer
from .serializers import TransactionSerializer

logger = logging.getLogger(__name__)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FINANCIAL INSTITUTIONS                                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝


class InstitutionListView(APIView):
    """
    GET /api/v1/accounts/institutions/
    GET /api/v1/accounts/institutions/?q=chase

    Search supported financial institutions.
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        qs = FinancialInstitution.objects.filter(is_active=True)
        query = request.query_params.get("q", "").strip()
        if query:
            qs = qs.filter(name__icontains=query)
        qs = qs[:50]

        serializer = FinancialInstitutionSerializer(qs, many=True)
        return success(serializer.data)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  ACCOUNT LINKING (Plaid flow)                                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝


@method_decorator(csrf_exempt, name="dispatch")
class AccountLinkInitiateView(APIView):
    """
    POST /api/v1/accounts/link/initiate/
    Generate a Plaid link_token for the frontend.

    Request: { "institution_id": 1 }
    """

    def post(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        serializer = LinkedAccountCreateSerializer(data=_json_body(request))
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        institution_id = serializer.validated_data["institution_id"]
        try:
            FinancialInstitution.objects.get(pk=institution_id, is_active=True)
        except FinancialInstitution.DoesNotExist:
            return not_found("Institution not found.")

        # In production: call Plaid API to generate link_token
        return success({
            "link_token": "link-sandbox-placeholder-token",
            "expiration": (timezone.now() + timezone.timedelta(hours=4)).isoformat(),
            "institution_id": institution_id,
        })


@method_decorator(csrf_exempt, name="dispatch")
class AccountLinkCompleteView(APIView):
    """
    POST /api/v1/accounts/link/complete/
    Exchange Plaid public_token after user completes Link.

    Request: { "public_token": "...", "institution_id": 1 }
    """

    def post(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        body = _json_body(request)
        public_token = body.get("public_token")
        institution_id = body.get("institution_id")

        if not public_token or not institution_id:
            return validation_error({"public_token": ["Required."], "institution_id": ["Required."]})

        try:
            institution = FinancialInstitution.objects.get(pk=institution_id, is_active=True)
        except FinancialInstitution.DoesNotExist:
            return not_found("Institution not found.")

        # In production: exchange public_token via Plaid
        account = LinkedAccount.objects.create(
            user=user,
            institution=institution,
            account_type=LinkedAccount.AccountType.BANK,
            external_account_id=f"plaid_{public_token[:12]}",
            display_name=f"{institution.name} Account",
            masked_number="",
            status=LinkedAccount.LinkStatus.ACTIVE,
        )

        if user.onboarding_step in (
            user.OnboardingStep.REGISTERED,
            user.OnboardingStep.PHONE_VERIFIED,
        ):
            user.onboarding_step = user.OnboardingStep.ACCOUNTS_CONNECTED
            user.save(update_fields=["onboarding_step"])

        serializer = LinkedAccountSerializer(account)
        return created({
            "detail": f"{institution.name} connected successfully.",
            "account": serializer.data,
        })


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  LINKED ACCOUNTS                                                        ║
# ╚══════════════════════════════════════════════════════════════════════════╝


class LinkedAccountListView(APIView):
    """
    GET /api/v1/accounts/linked/
    GET /api/v1/accounts/linked/?account_type=card
    GET /api/v1/accounts/linked/?status=active
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        qs = LinkedAccount.objects.filter(user=user).select_related("institution")

        account_type = request.query_params.get("account_type")
        if account_type:
            qs = qs.filter(account_type=account_type)

        acct_status = request.query_params.get("status")
        if acct_status:
            qs = qs.filter(status=acct_status)

        serializer = LinkedAccountSerializer(qs, many=True)
        return success(serializer.data)


class LinkedAccountDetailView(APIView):
    """
    GET    /api/v1/accounts/linked/{id}/
    DELETE /api/v1/accounts/linked/{id}/
    """

    def get(self, request, pk: int):
        user, err = bearer_auth(request)
        if err:
            return err

        try:
            account = LinkedAccount.objects.select_related("institution").get(pk=pk, user=user)
        except LinkedAccount.DoesNotExist:
            return not_found("Account not found.")

        serializer = LinkedAccountSerializer(account)
        return success(serializer.data)

    def delete(self, request, pk: int):
        user, err = bearer_auth(request)
        if err:
            return err
        try:
            account = LinkedAccount.objects.get(pk=pk, user=user)
        except LinkedAccount.DoesNotExist:
            return not_found("Account not found.")

        account.status = LinkedAccount.LinkStatus.DISCONNECTED
        account.save(update_fields=["status"])
        return no_content()


@method_decorator(csrf_exempt, name="dispatch")
class ManualAccountCreateView(APIView):
    """
    POST /api/v1/accounts/linked/manual/
    Manually add a card.
    """

    def post(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        serializer = ManualAccountSerializer(data=_json_body(request))
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        data = serializer.validated_data
        try:
            institution = FinancialInstitution.objects.get(pk=data["institution_id"], is_active=True)
        except FinancialInstitution.DoesNotExist:
            return not_found("Institution not found.")

        account = LinkedAccount.objects.create(
            user=user,
            institution=institution,
            account_type=data["account_type"],
            external_account_id=f"manual_{user.id}_{timezone.now().timestamp():.0f}",
            display_name=data["display_name"],
            masked_number=data.get("masked_number", ""),
            balance=data.get("balance", 0),
            status=LinkedAccount.LinkStatus.ACTIVE,
        )
        result = LinkedAccountSerializer(account)
        return created(result.data)


@method_decorator(csrf_exempt, name="dispatch")
class AccountRefreshView(APIView):
    """
    POST /api/v1/accounts/linked/{id}/refresh/
    Force re-sync account data from Plaid.
    """

    def post(self, request, pk: int):
        user, err = bearer_auth(request)
        if err:
            return err

        try:
            account = LinkedAccount.objects.get(pk=pk, user=user, status=LinkedAccount.LinkStatus.ACTIVE)
        except LinkedAccount.DoesNotExist:
            return not_found("Account not found.")

        # In production: trigger Celery task
        logger.info("Account refresh requested for account %s", account.id)
        return success({"detail": "Account sync initiated."})


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  CARDS CONFIRMATION                                                      ║
# ╚══════════════════════════════════════════════════════════════════════════╝


@method_decorator(csrf_exempt, name="dispatch")
class ConfirmCardsView(APIView):
    """
    POST /api/v1/accounts/cards/confirm/
    Confirm which detected cards to monitor.

    Request: { "card_ids": [1, 2, 3] }
    """

    def post(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        body = _json_body(request)
        card_ids = body.get("card_ids", [])

        if card_ids:
            LinkedAccount.objects.filter(
                user=user, account_type=LinkedAccount.AccountType.CARD,
            ).exclude(pk__in=card_ids).update(status=LinkedAccount.LinkStatus.DISCONNECTED)

        if user.onboarding_step == user.OnboardingStep.ACCOUNTS_CONNECTED:
            user.onboarding_step = user.OnboardingStep.CARDS_CONFIRMED
            user.save(update_fields=["onboarding_step"])

        return success({"detail": "Cards confirmed.", "onboarding_step": user.onboarding_step})


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  BILLS / LOANS                                                          ║
# ╚══════════════════════════════════════════════════════════════════════════╝


@method_decorator(csrf_exempt, name="dispatch")
class AddBillView(APIView):
    """
    POST /api/v1/accounts/bills/add/
    Add a manual bill/loan (Vehicle Loan, Student Loan, Mortgage, etc.).
    """

    def post(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        serializer = ManualBillSerializer(data=_json_body(request))
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        data = serializer.validated_data
        institution, _ = FinancialInstitution.objects.get_or_create(
            provider_key=f"manual_{data['category']}",
            defaults={"name": data["creditor_name"], "is_active": True},
        )

        account = LinkedAccount.objects.create(
            user=user,
            institution=institution,
            account_type=LinkedAccount.AccountType.BILLER,
            external_account_id=f"bill_{user.id}_{data['category']}_{timezone.now().timestamp():.0f}",
            display_name=data["creditor_name"],
            status=LinkedAccount.LinkStatus.ACTIVE,
        )

        PaymentDue.objects.create(
            account=account,
            creditor_name=data["creditor_name"],
            amount_due=data["amount_due"],
            due_date=data["due_date"],
            status=PaymentDue.DueStatus.UPCOMING,
        )

        return created({
            "detail": f"{data['creditor_name']} added.",
            "account": LinkedAccountSerializer(account).data,
        })


@method_decorator(csrf_exempt, name="dispatch")
class SkipBillsView(APIView):
    """POST /api/v1/accounts/bills/skip/ — Skip the bills step during onboarding."""

    def post(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        if user.onboarding_step == user.OnboardingStep.CARDS_CONFIRMED:
            user.onboarding_step = user.OnboardingStep.BILLS_ADDED
            user.save(update_fields=["onboarding_step"])

        return success({"detail": "Bills step skipped.", "onboarding_step": user.onboarding_step})


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TRANSACTIONS                                                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝


class TransactionListView(APIView):
    """
    GET /api/v1/accounts/transactions/
    GET /api/v1/accounts/transactions/?account=1
    GET /api/v1/accounts/transactions/?type=debit
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        qs = Transaction.objects.filter(account__user=user).select_related("account")

        account_id = request.query_params.get("account")
        if account_id:
            qs = qs.filter(account_id=account_id)

        txn_type = request.query_params.get("type")
        if txn_type:
            qs = qs.filter(transaction_type=txn_type)

        qs = qs.order_by("-transaction_date")[:100]

        serializer = TransactionSerializer(qs, many=True)
        return success(serializer.data)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  PAYMENT DUES                                                           ║
# ╚══════════════════════════════════════════════════════════════════════════╝


class PaymentDueListView(APIView):
    """
    GET /api/v1/accounts/payment-dues/
    GET /api/v1/accounts/payment-dues/?status=upcoming
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        qs = PaymentDue.objects.filter(account__user=user).select_related("account")
        due_status = request.query_params.get("status")
        if due_status:
            qs = qs.filter(status=due_status)
        qs = qs.order_by("due_date")

        serializer = PaymentDueSerializer(qs, many=True)
        return success(serializer.data)


class PaymentDueOverdueView(APIView):
    """GET /api/v1/accounts/payment-dues/overdue/"""

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        qs = PaymentDue.objects.filter(
            account__user=user,
            status__in=[PaymentDue.DueStatus.OVERDUE, PaymentDue.DueStatus.MISSED],
        ).select_related("account").order_by("due_date")

        serializer = PaymentDueSerializer(qs, many=True)
        return success(serializer.data)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  ANALYSIS STATUS & SCAN RESULTS                                         ║
# ╚══════════════════════════════════════════════════════════════════════════╝


class AnalysisStatusView(APIView):
    """
    GET /api/v1/accounts/analysis/status/
    Credit picture analysis progress.
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        has_bank = LinkedAccount.objects.filter(
            user=user, account_type=LinkedAccount.AccountType.BANK,
            status=LinkedAccount.LinkStatus.ACTIVE,
        ).exists()
        has_card = LinkedAccount.objects.filter(
            user=user, account_type=LinkedAccount.AccountType.CARD,
            status=LinkedAccount.LinkStatus.ACTIVE,
        ).exists()
        has_dues = PaymentDue.objects.filter(account__user=user).exists()
        has_transactions = Transaction.objects.filter(account__user=user).exists()

        from credit_clear.risk_monitoring.models import RiskScoreSnapshot
        from credit_clear.recovery_roadmap.models import RoadmapMilestone
        has_risk_score = RiskScoreSnapshot.objects.filter(user=user).exists()
        has_roadmap = RoadmapMilestone.objects.filter(user=user).exists()

        is_complete = all([has_bank, has_dues, has_risk_score, has_roadmap])

        data = {
            "bank_accounts_linked": has_bank,
            "credit_cards_synced": has_card,
            "payment_due_dates_mapped": has_dues,
            "transactions_analyzed": has_transactions,
            "risk_score_calculated": has_risk_score,
            "recovery_plan_generated": has_roadmap,
            "is_complete": is_complete,
        }
        serializer = AnalysisStatusSerializer(data)
        return success(serializer.data)


class ScanResultsView(APIView):
    """
    GET /api/v1/accounts/scan-results/
    Risk summary scan results.
    """

    def get(self, request):
        user, err = bearer_auth(request)
        if err:
            return err

        from datetime import timedelta
        three_days = timezone.now().date() + timedelta(days=3)
        payments_at_risk = PaymentDue.objects.filter(
            account__user=user,
            status__in=[PaymentDue.DueStatus.UPCOMING, PaymentDue.DueStatus.OVERDUE],
            due_date__lte=three_days,
        ).count()

        credit_errors = 0
        estimated_min = 0
        estimated_max = 0
        try:
            from credit_clear.ai_engine.models import CreditAnalysis
            latest = CreditAnalysis.objects.filter(user=user).order_by("-generated_at").first()
            if latest and latest.improvement_opportunities:
                credit_errors = len(latest.improvement_opportunities) if isinstance(latest.improvement_opportunities, list) else 0
                estimated_min = latest.estimated_score_gain or 0
                estimated_max = int(estimated_min * 1.4) if estimated_min else 0
        except Exception:
            pass

        data = {
            "payments_at_risk": payments_at_risk,
            "credit_errors_detected": credit_errors,
            "estimated_score_boost_min": estimated_min,
            "estimated_score_boost_max": estimated_max,
        }
        serializer = ScanResultSerializer(data)
        return success(serializer.data)
