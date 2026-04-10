from django.conf import settings
from django.db import models

from credit_clear.interventions.models import Intervention


class FallbackPayment(models.Model):
    class Status(models.TextChoices):
        INITIATED = "initiated", "Initiated"
        SETTLED = "settled", "Settled"
        FAILED = "failed", "Failed"
        REVERSED = "reversed", "Reversed"

    class PaymentMethod(models.TextChoices):
        DIRECT_PAY = "direct_pay", "Direct Pay"
        BNPL = "bnpl", "Buy Now Pay Later"
        INSTALLMENT = "installment", "Installment Plan"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fallback_payments")
    intervention = models.OneToOneField(Intervention, on_delete=models.CASCADE, related_name="fallback_payment")
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.DIRECT_PAY, db_index=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=8, default="USD")
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_installments = models.PositiveSmallIntegerField(default=1)
    bnpl_provider = models.CharField(max_length=100, blank=True)
    bnpl_reference = models.CharField(max_length=255, blank=True)
    repayment_start_date = models.DateField(null=True, blank=True)
    total_repayable = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    payment_provider_reference = models.CharField(max_length=255, blank=True, db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.INITIATED, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    settled_at = models.DateTimeField(null=True, blank=True)


class RepaymentSchedule(models.Model):
    class ScheduleStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        PAID = "paid", "Paid"
        DEFAULTED = "defaulted", "Defaulted"

    fallback_payment = models.ForeignKey(FallbackPayment, on_delete=models.CASCADE, related_name="repayment_schedules")
    installment_number = models.PositiveSmallIntegerField()
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=ScheduleStatus.choices, default=ScheduleStatus.ACTIVE, db_index=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("fallback_payment", "installment_number")]
