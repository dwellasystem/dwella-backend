from celery import shared_task
from django.core.management import call_command

@shared_task
def generate_bills_task():
    call_command("generate_monthly_due")