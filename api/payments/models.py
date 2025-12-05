from django.db import models
from django.conf import settings
from units.models import Unit
from bills.models import MonthlyBill
from units.models import AssignedUnit

# Create your models here.

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)
    account_name = models.CharField(max_length=100, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class PaymentRecord(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        COMPLETED = 'paid', 'Paid'
        REJECTED = 'rejected', 'Rejected'

    class PaymentType(models.TextChoices):
        REGULAR = 'regular', 'Regular Payment'
        ADVANCE = 'advance', 'Advance Payment'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        default=PaymentType.REGULAR,
    )
    unit = models.ForeignKey(Unit, on_delete=models.PROTECT, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    proof_of_payment = models.ImageField(upload_to='proofs/', blank=True, null=True)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT)
    bill = models.ForeignKey(MonthlyBill, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    
    # Advance payment fields
    advance_start_date = models.DateField(null=True, blank=True)
    advance_end_date = models.DateField(null=True, blank=True)
    advance_months_paid = models.IntegerField(default=0)  # Number of months covered
    is_advance_allocated = models.BooleanField(default=False)  # Track if advance has been allocated to bills

    def __str__(self):
        return f"PaymentRecord(user_id={self.user_id}, amount={self.amount}, status={self.status})"

    def allocate_advance_payment(self):
        """Allocate advance payment to future bills"""
        if (self.payment_type != self.PaymentType.ADVANCE or 
            self.status != self.PaymentStatus.COMPLETED or 
            self.is_advance_allocated or
            not self.advance_start_date or 
            not self.advance_end_date):
            return

        from dateutil.relativedelta import relativedelta
        from django.utils.timezone import now
        
        current_date = self.advance_start_date
        monthly_rent = float(self.unit.rent_amount) if self.unit else 0
        
        # Calculate additional charges
        additional_charges = 0
        try:
            assigned_unit = AssignedUnit.objects.get(
                unit_id=self.unit, 
                assigned_by=self.user, 
                deleted_at__isnull=True
            )
            if assigned_unit.amenities:
                additional_charges += 2500
            if assigned_unit.security:
                additional_charges += 2000
            if assigned_unit.maintenance:
                additional_charges += 1500
        except AssignedUnit.DoesNotExist:
            pass

        total_monthly_amount = monthly_rent + additional_charges
        
        # Create bills for each month in the advance period
        bills_created = 0
        while current_date <= self.advance_end_date:
            # Calculate due date (same day as advance start date)
            due_date = current_date.replace(day=self.advance_start_date.day)
            
            # Check if bill already exists
            if not MonthlyBill.objects.filter(
                user=self.user, 
                unit=self.unit,
                due_date=due_date
            ).exists():
                
                MonthlyBill.objects.create(
                    user=self.user,
                    unit=self.unit,
                    amount_due=total_monthly_amount,
                    due_date=due_date,
                    payment_status=MonthlyBill.PaymentStatus.PAID,  # Mark as paid in advance
                    due_status=MonthlyBill.DueStatus.DONE,
                )
                bills_created += 1
            
            # Move to next month
            current_date = current_date + relativedelta(months=1)
        
        self.advance_months_paid = bills_created
        self.is_advance_allocated = True
        self.save()
        
        return bills_created


