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
