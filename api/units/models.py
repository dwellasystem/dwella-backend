from django.db import models
from django.conf import settings
from django.utils import timezone
# Create your models here.

class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class Unit(models.Model):
    unit_name = models.CharField(max_length=100)
    building = models.CharField(max_length=100)
    bedrooms = models.IntegerField(default=0)
    floor_area = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    isAvailable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL, related_name='units_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL, related_name='units_updated')
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.SET_NULL, related_name='units_deleted')

    objects = ActiveManager()
    all_objects = models.Manager()


    def soft_delete(self, by_user=None):
        self.deleted_at = timezone.now()
        self.deleted_by = by_user
        self.is_active = False
        self.save()


    def restore(self):
        self.deleted_at = None
        self.deleted_by = None
        self.is_active = True
        self.save()


    def __str__(self):
        return self.unit_name or "Unnamed Unit"


class AssignedUnit(models.Model):
    class UnitStatus(models.TextChoices):
        OWNER_OCCUPIED = "owner_occupied", "Owner Occupied"
        RENTED_SHOR_TERM = "rented_short_term", "Rented Short Term"
        AIRBNB = "air_bnb", "Air Bnb"

    
    unit_id = models.ForeignKey(Unit, blank=True, null=True, on_delete=models.CASCADE, related_name='assigned_unit')
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='assigned_unit')
    move_in_date = models.DateTimeField(blank=True, null=True)
    building = models.CharField(max_length=100)
    maintenance = models.BooleanField(default=True)
    security = models.BooleanField(default=True)
    amenities = models.BooleanField(default=True)
    unit_status = models.CharField(max_length=20, choices=UnitStatus.choices, default=UnitStatus.OWNER_OCCUPIED)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='assigned_units_created')
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='assigned_units_updated')
    deleted_at = models.DateTimeField(blank=True, null=True)
    deleted_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='assigned_units_deleted')

    objects = ActiveManager()
    all_objects = models.Manager()


    def soft_delete(self, by_user=None):
        self.deleted_at = timezone.now()
        self.deleted_by = by_user
        self.is_active = False
        self.save()


    def restore(self):
        self.deleted_at = None
        self.deleted_by = None
        self.is_active = True
        self.save()