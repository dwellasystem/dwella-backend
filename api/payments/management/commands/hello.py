from django.core.management.base import BaseCommand
from datetime import datetime

class Command(BaseCommand):
    help = "Test command that prints 'Hello testing'"

    def handle(self, *args, **kwargs):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.stdout.write(self.style.SUCCESS(f"[{now}] Hello testing"))
