from rest_framework import serializers
from .models import MonthlyBill
from users.serializers import UserSerializer
from units.serializers import UnitSerializer
from users.models import CustomUser
from units.models import Unit

class MonthlyBillSerializer(serializers.ModelSerializer):
    user_fullname = serializers.CharField(source="user.fullname", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user = UserSerializer(read_only=True)
    unit = UnitSerializer(read_only=True)


     # ✅ Optional user_id for admin/employee to assign bills manually
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source="user",
        write_only=True,
        required=False  
    )

    unit_id = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        source="unit",
        write_only=True,
        required=False
    )

    class Meta:
        model = MonthlyBill
        fields = [
            "id",
            "user",
            "user_id", 
            "unit",
            'construction_bond',
            "unit_id",
            "user_fullname",
            "user_email",
            "amount_due",
            "due_date",
            "payment_status",
            "due_status",
            "sms_sent",
            "created_at"
        ]
        read_only_fields = ["due_status", "created_at"]


class ExpenseReflectionSerializer(serializers.Serializer):
    maintenance = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    security = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    amenities = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    totalExpense = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    totalPaid = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    totalUnpaid = serializers.DecimalField(max_digits=12, decimal_places=2, default=0)
    building_filter = serializers.CharField(required=False, allow_null=True)
    other_expenses = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    total_all_bills = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    filters_applied = serializers.DictField(required=False, allow_null=True)
    summary = serializers.DictField(required=False, allow_null=True)
    chart_data = serializers.DictField(required=False, allow_null=True)
    detailed_breakdown = serializers.DictField(required=False, allow_null=True)
    calculation_note = serializers.CharField(required=False, allow_null=True)
