from rest_framework import serializers
from .models import PaymentRecord, PaymentMethod
from users.serializers import UserSerializer
from bills.serializers import MonthlyBillSerializer
from django.utils.timezone import now
# Serializer for creating a payment method
class CreatePaymentMethodSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = PaymentMethod
        fields = '__all__'
        read_only_fields = ['id']


# Serializer for creating a payment record
class CreatePaymentSerializer(serializers.ModelSerializer):
    advance_start_date = serializers.DateField(required=False, allow_null=True)
    advance_end_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = PaymentRecord
        fields = ['user',
                  'amount', 
                  'status',
                  'payment_method', 
                  'payment_date', 
                  'proof_of_payment', 
                  'reference_number', 
                  'unit', 
                  'bill',
                  'payment_type',
                  'advance_start_date',
                  'advance_end_date'
                ]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be a positive number.")
        return value
    
    def validate(self, data):
        payment_type = data.get('payment_type', PaymentRecord.PaymentType.REGULAR)
        advance_start_date = data.get('advance_start_date')
        advance_end_date = data.get('advance_end_date')
        user = data.get('user')
        bill = data.get('bill')
        
        # Check for duplicate payment (user + bill combination)
        if user and bill:
            # Check if a payment already exists for this user and bill
            existing_payment = PaymentRecord.objects.filter(
                user=user,
                bill=bill
            ).exists()
            
            if existing_payment:
                raise serializers.ValidationError(
                    f"Your payment for bill of {bill.due_date.strftime("%B %d, %Y")} has already been processed..."
                )
        
        if payment_type == PaymentRecord.PaymentType.ADVANCE:
            if not advance_start_date or not advance_end_date:
                raise serializers.ValidationError(
                    "Advance payment requires both start date and end date."
                )
            
            if advance_start_date < now().date():
                raise serializers.ValidationError(
                    "Advance start date must be today or in the future."
                )
            
            if advance_start_date >= advance_end_date:
                raise serializers.ValidationError(
                    "Advance start date must be before end date."
                )
        
        return data
    
class GetPaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    unit = serializers.StringRelatedField()
    payment_method = serializers.StringRelatedField()
    bill = MonthlyBillSerializer(read_only=True)

    class Meta:
        model = PaymentRecord
        fields = ['id', 
                  'user', 
                  'amount', 
                  'status', 
                  'created_at', 
                  'updated_at', 
                  'payment_method', 
                  'reference_number', 
                  'proof_of_payment', 
                  'payment_date' , 
                  'unit', 
                  'bill',
                  'payment_type',
                  'advance_start_date',
                  'advance_end_date'
                ]
        read_only_fields = ['id', 'created_at', 'updated_at']