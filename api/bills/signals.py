from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import MonthlyBill

# @receiver(post_save, sender=MonthlyBill)
# def notify_overdue_bills(sender, instance, created, **kwargs):
#     user = instance.user
#     # Send notification either on creation OR if the due_status changed to overdue
#     if created or instance.due_status == "overdue":
#         unseen_count = MonthlyBill.objects.filter(user=user, due_status="overdue").count()
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             f"user_{user.id}",
#             {
#                 "type": "send_request_notification",
#                 "count": unseen_count
#             }
#         )


@receiver(post_save, sender=MonthlyBill)
def notify_overdue_bills(sender, instance, **kwargs):
    user = instance.user
    unseen_count = 5  # or your actual logic
    channel_layer = get_channel_layer()

    try:
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {"type": "send_request_notification", "count": unseen_count}
        )
    except ConnectionError:
        # Just log the error and skip notifications
        print("⚠️ Redis not available, skipping notifications")