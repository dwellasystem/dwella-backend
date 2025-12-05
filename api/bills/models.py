from django.db import models
from django.conf import settings
from django.utils.timezone import now
from units.models import Unit, AssignedUnit
from decimal import Decimal


class MonthlyBill(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"

    class DueStatus(models.TextChoices):
        UPCOMING = "upcoming", "Upcoming"
        DUE_TODAY = "due_today", "Due Today"
        OVERDUE = "overdue", "Overdue"
        DONE = "done", "Done"  # when paid

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="monthly_bills"
    )
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)  # Example rent
    due_date = models.DateField()
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    due_status = models.CharField(
        max_length=20,
        choices=DueStatus.choices,
        default=DueStatus.UPCOMING,
    )
    sms_sent = models.BooleanField(default=False)
    unit = models.ForeignKey(Unit, blank=True, null=True, on_delete=models.CASCADE, related_name='bill_unit')
    created_at = models.DateTimeField(auto_now_add=True)

    def update_due_status(self):
        """Update due status based on due_date and payment status"""
        today = now().date()

        if self.payment_status == self.PaymentStatus.PAID:
            self.due_status = self.DueStatus.DONE
        else:
            if self.due_date == today:
                self.due_status = self.DueStatus.DUE_TODAY
            elif self.due_date < today:
                self.due_status = self.DueStatus.OVERDUE
            else:
                self.due_status = self.DueStatus.UPCOMING

    def save(self, *args, **kwargs):
        if not self.amount_due or self.amount_due == 0:
            self.amount_due = self.calculate_total_amount_due()
        self.update_due_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bill(user={self.user.username}, due={self.due_date}, status={self.payment_status}/{self.due_status})"
