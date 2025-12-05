from django.core.management.base import BaseCommand
from users.models import CustomUser as User
from calendar import monthrange
from dateutil.relativedelta import relativedelta  # to handle month rollover
from datetime import date
from django.utils.timezone import now
from datetime import date

class Command(BaseCommand):
    help = "Generate monthly bills for users whose move_in_date matches today (batch-optimized)"

    def handle(self, *args, **kwargs):
        today = now().date();  # Example date for testing; replace with now().date() in production
        next_month_date = today + relativedelta(months=1)
        testDate = relativedelta(months=1)

        self.stdout.write(self.style.SUCCESS(
           f"relativedelta(months=1): {testDate} \n"
        ))
        # Adjust day if next month doesn't have this day (e.g., Feb 30 → Feb 28)
        # while True:
        #     try:
        #         next_month_date = date(next_month_date.year, next_month_date.month, today.day)
        #         self.stdout.write(self.style.SUCCESS(
        #             f"🔄 next_month_date: {next_month_date} \n"
        #         ))
        #         break
        #     except ValueError:
        #         self.stdout.write(self.style.WARNING(
        #             f"❌ Invalid date: {today}. Adjusting..."
        #         ))
        #         today = today - relativedelta(days=1)
        
        # self.stdout.write(self.style.SUCCESS(
        #     f"today: {next_month_date} \n"
        #     f"and next month: {next_month_date.month} \n"
        #     f"and next day: {next_month_date.day}"
        # ))


        # next_month_date = today + relativedelta(months=1)

        # self.stdout.write(self.style.SUCCESS(
        #     f"🔄 Generating monthly bills for users with move_in_date matching today: {today} \n"
        #     f"and next month: {next_month_date.month} \n"
        #     f"and next day: {next_month_date.day}"
        # ))

        # users_qs = User.objects.filter(
        #     move_in_date__lt=today,
        # ).only("id").iterator(chunk_size=100)

        # count = 0
        # for user in users_qs:
        #     count += 1
        #     self.stdout.write(f"[{count}] ID: {user.id}, Username: {user.username}, "
        #                       f"Email: {user.email}, Move-in Date: {user.move_in_date}, Day: {user.move_in_date.day}, Month: {user.move_in_date.month}")
        #     # You can add logic here, e.g. create bills, print, etc.

        # self.stdout.write(self.style.SUCCESS(
        #     f"✅ Finished! Total bills created:"
        # ))
