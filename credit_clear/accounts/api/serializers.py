from rest_framework import serializers

from credit_clear.accounts.models import FinancialInstitution
from credit_clear.accounts.models import LinkedAccount
from credit_clear.accounts.models import PaymentDue
from credit_clear.accounts.models import Transaction


# ---------------------------------------------------------------------------
# Financial Institution
# ---------------------------------------------------------------------------

class FinancialInstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialInstitution
        fields = ["id", "name", "provider_key", "website", "is_active"]
        read_only_fields = fields


class InstitutionSearchSerializer(serializers.Serializer):
    q = serializers.CharField(max_length=100, required=False, help_text="Search query for bank name")


# ---------------------------------------------------------------------------
# Linked Account
# ---------------------------------------------------------------------------

class LinkedAccountSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source="institution.name", read_only=True)

    class Meta:
        model = LinkedAccount
        fields = [
            "id",
            "institution",
            "institution_name",
            "account_type",
            "display_name",
            "masked_number",
            "currency",
            "balance",
            "available_balance",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "institution_name", "balance", "available_balance",
            "status", "created_at", "updated_at",
        ]


class LinkedAccountCreateSerializer(serializers.Serializer):
    """Initiate account linking via Plaid."""

    institution_id = serializers.IntegerField(help_text="ID of the FinancialInstitution to link")


class PlaidLinkTokenSerializer(serializers.Serializer):
    """Response for Plaid Link token generation."""

    link_token = serializers.CharField()
    expiration = serializers.DateTimeField()


class PlaidPublicTokenSerializer(serializers.Serializer):
    """Exchange Plaid public token after Link completes."""

    public_token = serializers.CharField()
    institution_id = serializers.IntegerField()


class ManualAccountSerializer(serializers.Serializer):
    """Manually add a card."""

    institution_id = serializers.IntegerField()
    account_type = serializers.ChoiceField(choices=LinkedAccount.AccountType.choices)
    display_name = serializers.CharField(max_length=255)
    masked_number = serializers.CharField(max_length=8, required=False, allow_blank=True)
    balance = serializers.DecimalField(max_digits=14, decimal_places=2, required=False)


class ManualBillSerializer(serializers.Serializer):
    """Add a bill or loan — Vehicle Loans, Student Loan, etc."""

    class BillCategory(serializers.ChoiceField):
        pass

    category = serializers.ChoiceField(choices=[
        ("vehicle_loan", "Vehicle Loans"),
        ("student_loan", "Student Loan"),
        ("mortgage", "Mortgage"),
        ("phone_utilities", "Phone & Utilities"),
        ("medical", "Medical Bills"),
    ])
    creditor_name = serializers.CharField(max_length=255)
    amount_due = serializers.DecimalField(max_digits=14, decimal_places=2)
    due_date = serializers.DateField()
    is_recurring = serializers.BooleanField(default=True)


# ---------------------------------------------------------------------------
# Transaction
# ---------------------------------------------------------------------------

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "account",
            "transaction_type",
            "amount",
            "currency",
            "description",
            "merchant_name",
            "category",
            "status",
            "transaction_date",
            "posted_date",
            "is_recurring",
            "created_at",
        ]
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Payment Due
# ---------------------------------------------------------------------------

class PaymentDueSerializer(serializers.ModelSerializer):
    account_display_name = serializers.CharField(source="account.display_name", read_only=True)
    account_masked_number = serializers.CharField(source="account.masked_number", read_only=True)

    class Meta:
        model = PaymentDue
        fields = [
            "id",
            "account",
            "account_display_name",
            "account_masked_number",
            "creditor_name",
            "amount_due",
            "minimum_due",
            "due_date",
            "status",
            "auto_pay_enabled",
            "paid_at",
            "created_at",
        ]
        read_only_fields = fields


# ---------------------------------------------------------------------------
# Analysis progress + Scan results
# ---------------------------------------------------------------------------

class AnalysisStatusSerializer(serializers.Serializer):
    bank_accounts_linked = serializers.BooleanField()
    credit_cards_synced = serializers.BooleanField()
    payment_due_dates_mapped = serializers.BooleanField()
    transactions_analyzed = serializers.BooleanField()
    risk_score_calculated = serializers.BooleanField()
    recovery_plan_generated = serializers.BooleanField()
    is_complete = serializers.BooleanField()


class ScanResultSerializer(serializers.Serializer):
    payments_at_risk = serializers.IntegerField()
    credit_errors_detected = serializers.IntegerField()
    estimated_score_boost_min = serializers.IntegerField()
    estimated_score_boost_max = serializers.IntegerField()
