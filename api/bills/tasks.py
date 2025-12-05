from datetime import date, timedelta
from calendar import monthrange
from celery import shared_task
from django.utils.timezone import now
from dateutil.relativedelta import relativedelta
from users.models import CustomUser
from bills.models import MonthlyBill
from units.models import AssignedUnit

# @shared_task
# def generate_monthly_bill():
#     """
#     Generate bills for residents 7 days before their due date.
#     Example: move_in_date=Oct 1 -> bill is generated on Sep 25.
#     Prevents duplicate bills.
#     """
#     today = now().date()
#     print(f"[{today}] Running generate_monthly_bills task")  # ✅ debug
#     residents = CustomUser.objects.filter(
#         role="resident",
#         is_active=True,
#         account_status="active",
#         move_in_date__isnull=False,
#         unit__isnull=False
#     ).select_related("unit")

#     count = 0
#     for user in residents:
#         rent_amount = getattr(user.unit, "rent_amount", None)
#         if rent_amount is None:
#             continue

#         due_day = user.move_in_date.day

#         # Step 1: find the upcoming due date
#         if today.day <= due_day:
#             target_month = today.month
#             target_year = today.year
#         else:
#             next_month = today + relativedelta(months=1)
#             target_month = next_month.month
#             target_year = next_month.year

#         # Adjust for short months (e.g. Feb 30 -> Feb 28/29)
#         last_day = monthrange(target_year, target_month)[1]
#         due_day = min(due_day, last_day)
#         next_due_date = date(target_year, target_month, due_day)

#         # Step 2: check if today == due_date - 7 days
#         generate_date = next_due_date - timedelta(days=7)
#         if today == generate_date:
#             if not MonthlyBill.objects.filter(user=user, due_date=next_due_date).exists():
#                 MonthlyBill.objects.create(
#                     user=user,
#                     amount_due=rent_amount,
#                     due_date=next_due_date
#                 )
#                 count += 1
#     print(f"✅ Generated {count} bills (7 days before due date)")
#     return f"✅ Generated {count} bills (7 days before due date)"


# @shared_task
# def update_bill_status():
#     """
#     Refresh all bill statuses.
#     Assumes MonthlyBill.save() updates status (e.g., paid, overdue, pending).
#     """
#     bills = MonthlyBill.objects.all()
#     count = 0
#     for bill in bills:
#         bill.save()  # triggers update_due_status logic
#         count += 1
#     print(f"🔄 Updated {count} bills")
#     return f"🔄 Updated {count} bills"


@shared_task
def generate_monthly_bill():
    """
    Generate monthly bills for active assigned units (7 days before due date).
    ✅ Skips:
        - Inactive or deleted users
        - Units without rent amount
        - Soft-deleted assigned units
        - Duplicate bills for the same due date
    """
    today = now().date()
    print(f"[{today}] Running generate_monthly_bill task")

    # ✅ Fetch active assigned units (not soft deleted)
    assigned_units = AssignedUnit.objects.filter(
        deleted_at__isnull=True,
        unit_id__isnull=False,
        assigned_by__isnull=False,
    ).select_related("unit_id", "assigned_by")

    count = 0
    for assigned in assigned_units:
        user = assigned.assigned_by
        unit = assigned.unit_id

        # ✅ Skip if user is inactive or account_status != 'active'
        if not user.is_active or getattr(user, "account_status", None) != "active":
            continue

        if not unit or not unit.rent_amount:
            continue

        # 💰 Base rent
        total_amount_due = float(unit.rent_amount)

        # ➕ Additional charges
        if assigned.amenities:
            total_amount_due += 2500
        if assigned.security:
            total_amount_due += 2000
        if assigned.maintenance:
            total_amount_due += 1500

        # Assume bill is due monthly on the same day as assignment date
        move_in_date = assigned.move_in_date.date()
        due_day = move_in_date.day

        # Step 1: Compute next due date (this or next month)
        if today.day <= due_day:
            target_month = today.month
            target_year = today.year
        else:
            next_month = today + relativedelta(months=1)
            target_month = next_month.month
            target_year = next_month.year

        # Step 2: Handle months shorter than move-in day (e.g., Feb 30 → Feb 28/29)
        last_day = monthrange(target_year, target_month)[1]
        due_day = min(due_day, last_day)
        next_due_date = date(target_year, target_month, due_day)

        # Step 3: Generate bill 7 days before due date
        generate_date = next_due_date - timedelta(days=7)

        if today == generate_date:
            if not MonthlyBill.objects.filter(user=user, due_date=next_due_date).exists():
                MonthlyBill.objects.create(
                    user=user,
                    unit=unit,
                    amount_due=total_amount_due,
                    due_date=next_due_date,
                )
                count += 1

    print(f"✅ Generated {count} bills (7 days before due date)")
    return f"✅ Generated {count} bills (7 days before due date)"


@shared_task
def update_bill_status():
    """
    Refresh all bill statuses (e.g., upcoming, overdue, done).
    """
    bills = MonthlyBill.objects.all()
    count = 0
    for bill in bills:
        bill.save()  # triggers update_due_status()
        count += 1

    print(f"🔄 Updated {count} bills")
    return f"🔄 Updated {count} bills"

