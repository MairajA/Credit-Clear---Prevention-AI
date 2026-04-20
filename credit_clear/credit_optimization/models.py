from django.conf import settings
from django.db import models

from credit_clear.interventions.models import Creditor


class OptimizationCase(models.Model):
    class CaseType(models.TextChoices):
        CREDIT_REPAIR = "credit_repair", "Credit Repair"
        DEBT_NEGOTIATION = "debt_negotiation", "Debt Negotiation"
        CREDIT_BUILDING = "credit_building", "Credit Building"
        FRAUD_MONITORING = "fraud_monitoring", "Fraud Monitoring"
        BILL_NEGOTIATION = "bill_negotiation", "Bill Negotiation"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        BLOCKED = "blocked", "Blocked"
        COMPLETED = "completed", "Completed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="optimization_cases")
    case_type = models.CharField(max_length=30, choices=CaseType.choices, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN, db_index=True)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    achieved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BureauDispute(models.Model):
    class Bureau(models.TextChoices):
        EXPERIAN = "experian", "Experian"
        EQUIFAX = "equifax", "Equifax"
        TRANSUNION = "transunion", "TransUnion"

    class DisputeStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        SUBMITTED = "submitted", "Submitted"
        RESPONDED = "responded", "Responded"
        ESCALATED = "escalated", "Escalated"
        RESOLVED = "resolved", "Resolved"

    case = models.ForeignKey(OptimizationCase, on_delete=models.CASCADE, related_name="bureau_disputes")
    bureau = models.CharField(max_length=20, choices=Bureau.choices, db_index=True)
    dispute_reason = models.TextField()
    account_name = models.CharField(max_length=255, blank=True)
    account_number_masked = models.CharField(max_length=20, blank=True)
    dispute_letter = models.TextField(blank=True)
    evidence_urls = models.JSONField(default=list, blank=True)
    bureau_reference_number = models.CharField(max_length=100, blank=True)
    cfpb_complaint_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=DisputeStatus.choices, default=DisputeStatus.DRAFT, db_index=True)
    bureau_response = models.TextField(blank=True)
    resolution_details = models.JSONField(default=dict, blank=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)


class NegotiationOffer(models.Model):
    class OfferType(models.TextChoices):
        SETTLEMENT = "settlement", "Settlement"
        PAYMENT_PLAN = "payment_plan", "Payment Plan"
        INTEREST_REDUCTION = "interest_reduction", "Interest Reduction"
        BALANCE_REDUCTION = "balance_reduction", "Balance Reduction"
        PAY_FOR_DELETE = "pay_for_delete", "Pay for Delete"

    class OfferStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        SENT = "sent", "Sent"
        COUNTER_RECEIVED = "counter_received", "Counter Received"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        EXPIRED = "expired", "Expired"

    case = models.ForeignKey(OptimizationCase, on_delete=models.CASCADE, related_name="negotiation_offers")
    creditor = models.ForeignKey(Creditor, on_delete=models.SET_NULL, null=True, blank=True)
    offer_type = models.CharField(max_length=30, choices=OfferType.choices, db_index=True)
    original_balance = models.DecimalField(max_digits=12, decimal_places=2)
    offered_amount = models.DecimalField(max_digits=12, decimal_places=2)
    counter_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    final_agreed_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    savings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    proposed_monthly_payment = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    proposed_term_months = models.PositiveSmallIntegerField(null=True, blank=True)
    proposed_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=OfferStatus.choices, default=OfferStatus.DRAFT, db_index=True)
    communication_log = models.JSONField(default=list, blank=True)
    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["case", "status"])]


class SettlementAgreement(models.Model):
    class AgreementStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        PAYING = "paying", "Paying"
        COMPLETED = "completed", "Completed"
        DEFAULTED = "defaulted", "Defaulted"

    offer = models.OneToOneField(NegotiationOffer, on_delete=models.CASCADE, related_name="settlement")
    agreed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    total_months = models.PositiveSmallIntegerField(default=1)
    first_payment_date = models.DateField()
    agreement_document_url = models.URLField(blank=True)
    status = models.CharField(max_length=20, choices=AgreementStatus.choices, default=AgreementStatus.ACTIVE, db_index=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    next_payment_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CreditBuildingProduct(models.Model):
    class ProductType(models.TextChoices):
        SECURED_CARD = "secured_card", "Secured Credit Card"
        BUILDER_LOAN = "builder_loan", "Credit Builder Loan"
        TRADELINE = "tradeline", "Authorized Tradeline"
        RENT_REPORTING = "rent_reporting", "Rent Reporting"
        DEBIT_BUILDER = "debit_builder", "Debit Card Builder"

    class EnrollmentStatus(models.TextChoices):
        RECOMMENDED = "recommended", "Recommended"
        APPLIED = "applied", "Applied"
        APPROVED = "approved", "Approved"
        ACTIVE = "active", "Active"
        REJECTED = "rejected", "Rejected"
        CANCELLED = "cancelled", "Cancelled"

    case = models.ForeignKey(OptimizationCase, on_delete=models.CASCADE, related_name="building_products")
    product_type = models.CharField(max_length=30, choices=ProductType.choices, db_index=True)
    provider_name = models.CharField(max_length=255)
    product_name = models.CharField(max_length=255)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    deposit_required = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    monthly_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    annual_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    reports_to_bureaus = models.JSONField(default=list, blank=True)
    enrollment_status = models.CharField(max_length=20, choices=EnrollmentStatus.choices, default=EnrollmentStatus.RECOMMENDED, db_index=True)
    applied_at = models.DateTimeField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    estimated_score_impact = models.PositiveSmallIntegerField(default=0)
    referral_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class FraudAlert(models.Model):
    class AlertType(models.TextChoices):
        NEW_ACCOUNT = "new_account", "New Account Opened"
        HARD_INQUIRY = "hard_inquiry", "Hard Inquiry"
        DARK_WEB = "dark_web", "Dark Web Data Found"
        ADDRESS_CHANGE = "address_change", "Address Change"
        SUSPICIOUS_ACTIVITY = "suspicious_activity", "Suspicious Activity"
        IDENTITY_THEFT = "identity_theft", "Identity Theft"

    class AlertSeverity(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    class AlertStatus(models.TextChoices):
        OPEN = "open", "Open"
        INVESTIGATING = "investigating", "Investigating"
        DISPUTED = "disputed", "Disputed"
        RESOLVED = "resolved", "Resolved"
        FALSE_POSITIVE = "false_positive", "False Positive"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fraud_alerts")
    case = models.ForeignKey(OptimizationCase, on_delete=models.SET_NULL, null=True, blank=True, related_name="fraud_alerts")
    alert_type = models.CharField(max_length=30, choices=AlertType.choices, db_index=True)
    severity = models.CharField(max_length=10, choices=AlertSeverity.choices, default=AlertSeverity.MEDIUM, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    source = models.CharField(max_length=100, blank=True)
    affected_account = models.CharField(max_length=255, blank=True)
    exposed_data_types = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=AlertStatus.choices, default=AlertStatus.OPEN, db_index=True)
    auto_dispute_filed = models.BooleanField(default=False)
    dispute_reference = models.CharField(max_length=100, blank=True)
    detected_at = models.DateTimeField(auto_now_add=True, db_index=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "alert_type", "detected_at"]),
            models.Index(fields=["severity", "status"]),
        ]


class BillNegotiationResult(models.Model):
    class BillType(models.TextChoices):
        MEDICAL = "medical", "Medical Bill"
        CREDIT_CARD_INTEREST = "credit_card_interest", "Credit Card Interest"
        COLLECTION = "collection", "Collection Account"
        SUBSCRIPTION = "subscription", "Subscription"
        UTILITY = "utility", "Utility Bill"
        INSURANCE = "insurance", "Insurance"
        OTHER = "other", "Other"

    class NegotiationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        SUCCESS = "success", "Success"
        PARTIAL = "partial", "Partial Success"
        FAILED = "failed", "Failed"

    case = models.ForeignKey(OptimizationCase, on_delete=models.CASCADE, related_name="bill_negotiations")
    creditor = models.ForeignKey(Creditor, on_delete=models.SET_NULL, null=True, blank=True)
    bill_type = models.CharField(max_length=30, choices=BillType.choices, db_index=True)
    provider_name = models.CharField(max_length=255)
    original_amount = models.DecimalField(max_digits=12, decimal_places=2)
    negotiated_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    original_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    negotiated_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    monthly_savings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_savings = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    subscription_cancelled = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=NegotiationStatus.choices, default=NegotiationStatus.PENDING, db_index=True)
    negotiation_notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
