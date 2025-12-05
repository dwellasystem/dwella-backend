from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from units.models import Unit

from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def get_queryset(self):
        # Return only users that are not soft-deleted
        return super().get_queryset().filter(deleted_at__isnull=True)

class CustomUser(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        EMPLOYEE = 'employee', 'Employee'
        RESIDENT = 'resident', 'Resident'

    class AccountStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
   
    # your custom fields:
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField()
    phone_number = models.CharField(max_length=20)
    date_of_birth = models.DateField(blank=True, null=True)
    move_in_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='created_users'
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='updated_users'
    )
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='deleted_users'
    )
    account_status = models.CharField(
        max_length=20,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.RESIDENT
    )
    profile = models.ImageField(upload_to='profiles/', blank=True, null=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    unit = models.ForeignKey(
        Unit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="residents"
    )

    objects = CustomUserManager()          # Default: excludes soft-deleted users
    all_objects = models.Manager()         # Includes soft-deleted users
    
    def __str__(self):
        return self.username
    
    def soft_delete(self, by_user=None):
        self.deleted_at = timezone.now()
        self.deleted_by = by_user
        self.is_active = False  # optional: also disable login
        self.save()

    def restore(self):
        self.deleted_at = None
        self.deleted_by = None
        self.is_active = True  # optional: reactivate
        self.save()
    

