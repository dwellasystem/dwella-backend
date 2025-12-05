# hoa/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from payments.models import PaymentMethod  # Import your existing PaymentMethod model

User = get_user_model()

class HoaInformation(models.Model):
    """Model to store HOA-related information"""
    # Instead of duplicating bank info, reference existing PaymentMethod
    # We'll store the primary payment method
    primary_payment_method = models.ForeignKey(
        PaymentMethod, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_for_hoa',
        help_text="Primary payment method for HOA"
    )
    
    # For additional payment methods (many-to-many)
    additional_payment_methods = models.ManyToManyField(
        PaymentMethod,
        blank=True,
        related_name='additional_for_hoa',
        help_text="Additional accepted payment methods"
    )
    
    reference_format = models.TextField(blank=True, help_text="Format for payment references (e.g., Unit No. + Month)")
    
    # Emergency contacts
    emergency_hotline = models.CharField(max_length=20, blank=True, help_text="Main emergency hotline")
    security_guard_contact = models.CharField(max_length=20, blank=True, help_text="Security guard contact number")
    fire_department = models.CharField(max_length=20, blank=True, help_text="Fire department contact")
    police_station = models.CharField(max_length=20, blank=True, help_text="Local police station contact")
    hospital = models.CharField(max_length=20, blank=True, help_text="Nearest hospital contact")
    
    # HOA Office
    hoa_office_phone = models.CharField(max_length=20, blank=True, help_text="HOA office phone number")
    hoa_email = models.EmailField(blank=True, help_text="HOA office email address")
    office_hours = models.CharField(max_length=100, blank=True, help_text="Office operating hours")
    office_address = models.TextField(blank=True, help_text="HOA office physical address")
    
    # Maintenance contacts
    maintenance_contact = models.CharField(max_length=20, blank=True, help_text="Maintenance department contact")
    electrician_contact = models.CharField(max_length=20, blank=True, help_text="Electrician contact")
    plumber_contact = models.CharField(max_length=20, blank=True, help_text="Plumber contact")
    
    # Important notices
    important_notices = models.TextField(blank=True, help_text="Important notices or announcements")
    
    # Timestamps and tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='created_hoa_info'
    )
    updated_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='updated_hoa_info'
    )
    
    class Meta:
        verbose_name = "HOA Information"
        verbose_name_plural = "HOA Information"
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"HOA Information (Last updated: {self.updated_at})"
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and HoaInformation.objects.exists():
            raise ValidationError("Only one HOA Information instance is allowed")
        super().save(*args, **kwargs)
    
    @property
    def all_payment_methods(self):
        """Returns all payment methods associated with HOA"""
        methods = []
        if self.primary_payment_method:
            methods.append({
                'id': self.primary_payment_method.id,
                'name': self.primary_payment_method.name,
                'account_name': self.primary_payment_method.account_name,
                'account_number': self.primary_payment_method.account_number,
                'instructions': self.primary_payment_method.instructions,
                'is_primary': True,
                'is_active': self.primary_payment_method.is_active
            })
        
        for method in self.additional_payment_methods.filter(is_active=True):
            methods.append({
                'id': method.id,
                'name': method.name,
                'account_name': method.account_name,
                'account_number': method.account_number,
                'instructions': method.instructions,
                'is_primary': False,
                'is_active': method.is_active
            })
        
        return methods
    
    @property
    def active_payment_methods(self):
        """Returns only active payment methods"""
        return [method for method in self.all_payment_methods if method['is_active']]