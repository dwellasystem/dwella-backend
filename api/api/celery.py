import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

app = Celery("api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Redis config
# app.conf.broker_url = "redis://localhost:6379/0"
# app.conf.result_backend = "redis://localhost:6379/0"

# Beat schedule
app.conf.beat_schedule = {
    "generate-monthly-bill": {
        "task": "bills.tasks.generate_monthly_bill",
        # "schedule": crontab(hour=0, minute=0, day_of_month="1"),  # Every 1st of month
        "schedule": crontab(minute="*"),  # every minute
    },
    "update-bill-status": {
        "task": "bills.tasks.update_bill_status",
        # "schedule": crontab(hour=1, minute=0),  # Every day at 1 AM
        "schedule": crontab(minute="*"),  # every minute
    },
}