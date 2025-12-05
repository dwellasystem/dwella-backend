# models.py
from django.db import models
from django.conf import settings
from units.models import Unit

# Create your models here.

class InquiryType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    
class Inquiry(models.Model):

    class Category(models.TextChoices):
        COMPLAINT = 'complaint', 'Complaint'
        QUESTION = 'question', 'Question'
        REQUEST = 'request', 'Request'

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        IN_PROGRESS = 'in_progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='inquiries')
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )
    type = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.REQUEST
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    inquiry_type = models.ForeignKey(InquiryType, on_delete=models.CASCADE, related_name='inquiries', null=True, blank=True)
    resident = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inquiries', null=True, blank=True)
    # Add this photo field
    photo = models.ImageField(upload_to='inquiries/', blank=True, null=True, help_text="Optional photo attachment for the inquiry")

    def __str__(self):
        return self.title