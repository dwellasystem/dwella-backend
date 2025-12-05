from django.db import models
from units.models import AssignedUnit, Unit

# Create your models here.

class NoticeType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Notice(models.Model):
    
    # class TargetAudience(models.TextChoices):
    #     ALL = 'all', 'All Users',
    #     RESIDENTS = 'residents', 'Residents',
    title = models.CharField(max_length=255)
    content = models.TextField()
    target_audience = models.ManyToManyField(AssignedUnit, blank=True, related_name='notices')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notice_type = models.ForeignKey(NoticeType, on_delete=models.CASCADE, related_name='notices')

    def __str__(self):
        return self.title