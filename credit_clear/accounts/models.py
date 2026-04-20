from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class FinancialInstitution(TimeStampedModel):
    name = models.CharField(max_length=255)
    provider_key = models.CharField(max_length=100, unique=True)
    website = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]


class LinkedAccount(TimeStampedModel):
    class AccountType(models.TextChoices):
        BANK = "bank", "Bank"
        CARD = "card", "Card"
        LOAN = "loan", "Loan"
        BILLER = "biller", "Biller"

    class LinkStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        ACTIVE = "active", "Active"
        FAILED = "failed", "Failed"
        DISCONNECTED = "disconnected", "Disconnected"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="linked_accounts",
    )
    institution = models.ForeignKey(
        FinancialInstitution,
        on_delete=models.PROTECT,
        related_name="accounts",
    )
    account_type = models.CharField(max_length=20, choices=AccountType.choices)
    external_account_id = models.CharField(max_length=255, db_index=True)
    display_name = models.CharField(max_length=255)
    masked_number = models.CharField(max_length=8, blank=True)
    currency = models.CharField(max_length=8, default="USD")
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    available_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=LinkStatus.choices, default=LinkStatus.PENDING, db_index=True)
    oauth_access_expires_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = [("user", "external_account_id")]
        indexes = [
            models.Index(fields=["user", "account_type"]),
            models.Index(fields=["status", "updated_at"]),
        ]


class Transaction(TimeStampedModel):
    class TransactionType(models.TextChoices):
        DEBIT = "debit", "Debit"
        CREDIT = "credit", "Credit"
        PAYMENT = "payment", "Payment"
        FEE = "fee", "Fee"
        INTEREST = "interest", "Interest"
        TRANSFER = "transfer", "Transfer"

    class TransactionStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        POSTED = "posted", "Posted"
        CANCELLED = "cancelled", "Cancelled"

    account = models.ForeignKey(LinkedAccount, on_delete=models.CASCADE, related_name="transactions")
    external_transaction_id = models.CharField(max_length=255, db_index=True)
    transaction_type = models.CharField(max_length=20, choices=TransactionType.choices, db_index=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    currency = models.CharField(max_length=8, default="USD")
    description = models.CharField(max_length=500, blank=True)
    merchant_name = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=TransactionStatus.choices, default=TransactionStatus.POSTED, db_index=True)
    transaction_date = models.DateField(db_index=True)
    posted_date = models.DateField(null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = [("account", "external_transaction_id")]
        indexes = [
            models.Index(fields=["account", "transaction_date"]),
            models.Index(fields=["account", "transaction_type", "transaction_date"]),
        ]


class PaymentDue(TimeStampedModel):
    class DueStatus(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"
        MISSED = "missed", "Missed"

    account = models.ForeignKey(LinkedAccount, on_delete=models.CASCADE, related_name="payment_dues")
    creditor_name = models.CharField(max_length=255)
    amount_due = models.DecimalField(max_digits=14, decimal_places=2)
    minimum_due = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    due_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=DueStatus.choices, default=DueStatus.UPCOMING, db_index=True)
    auto_pay_enabled = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["account", "due_date"]),
            models.Index(fields=["status", "due_date"]),
        ]
