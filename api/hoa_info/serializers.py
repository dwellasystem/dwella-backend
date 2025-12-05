# hoa/serializers.py
from rest_framework import serializers
from .models import HoaInformation
from payments.models import PaymentMethod
from payments.serializers import CreatePaymentMethodSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class PaymentMethodSimpleSerializer(serializers.ModelSerializer):
    """Simple serializer for PaymentMethod display"""
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'account_name', 'account_number', 'instructions', 'is_active']


class HoaInformationSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    updated_by_name = serializers.CharField(source='updated_by.get_full_name', read_only=True)
    
    # Nested serializers for payment methods
    primary_payment_method = PaymentMethodSimpleSerializer(read_only=True)
    primary_payment_method_id = serializers.PrimaryKeyRelatedField(
        queryset=PaymentMethod.objects.filter(is_active=True),
        source='primary_payment_method',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    additional_payment_methods = PaymentMethodSimpleSerializer(many=True, read_only=True)
    additional_payment_method_ids = serializers.PrimaryKeyRelatedField(
        queryset=PaymentMethod.objects.filter(is_active=True),
        source='additional_payment_methods',
        write_only=True,
        many=True,
        required=False
    )
    
    # Computed properties
    all_payment_methods = serializers.SerializerMethodField(read_only=True)
    active_payment_methods = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = HoaInformation
        fields = [
            'id',
            
            # Payment method references
            'primary_payment_method',
            'primary_payment_method_id',
            'additional_payment_methods',
            'additional_payment_method_ids',
            'all_payment_methods',
            'active_payment_methods',
            
            'reference_format',
            
            # Emergency contacts
            'emergency_hotline',
            'security_guard_contact',
            'fire_department',
            'police_station',
            'hospital',
            
            # HOA Office
            'hoa_office_phone',
            'hoa_email',
            'office_hours',
            'office_address',
            
            # Maintenance contacts
            'maintenance_contact',
            'electrician_contact',
            'plumber_contact',
            
            # Important notices
            'important_notices',
            
            # Audit fields
            'created_at',
            'updated_at',
            'created_by',
            'updated_by',
            'created_by_name',
            'updated_by_name',
        ]
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at', 
            'created_by', 
            'updated_by',
            'all_payment_methods',
            'active_payment_methods'
        ]
    
    def get_all_payment_methods(self, obj):
        return obj.all_payment_methods
    
    def get_active_payment_methods(self, obj):
        return obj.active_payment_methods
    
    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        
        # Check if HOA information already exists
        if HoaInformation.objects.exists():
            raise serializers.ValidationError("HOA Information already exists. Use update instead.")
        
        # Extract payment method data
        additional_payment_methods = validated_data.pop('additional_payment_methods', [])
        primary_payment_method = validated_data.get('primary_payment_method')
        
        # Create the instance
        instance = HoaInformation.objects.create(
            **validated_data,
            created_by=user,
            updated_by=user
        )
        
        # Add additional payment methods
        if additional_payment_methods:
            instance.additional_payment_methods.set(additional_payment_methods)
        
        return instance
    
    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user if request else None
        
        # Extract payment method data
        additional_payment_methods = validated_data.pop('additional_payment_methods', None)
        
        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Update additional payment methods if provided
        if additional_payment_methods is not None:
            instance.additional_payment_methods.set(additional_payment_methods)
        
        instance.updated_by = user
        instance.save()
        return instance


class HoaInformationPublicSerializer(serializers.ModelSerializer):
    """Serializer for public/non-admin users (read-only)"""
    primary_payment_method = PaymentMethodSimpleSerializer(read_only=True)
    additional_payment_methods = PaymentMethodSimpleSerializer(many=True, read_only=True)
    active_payment_methods = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = HoaInformation
        fields = [
            'id',
            
            # Payment methods
            'primary_payment_method',
            'additional_payment_methods',
            'active_payment_methods',
            
            'reference_format',
            
            # Emergency contacts
            'emergency_hotline',
            'security_guard_contact',
            'fire_department',
            'police_station',
            'hospital',
            
            # HOA Office
            'hoa_office_phone',
            'hoa_email',
            'office_hours',
            'office_address',
            
            # Maintenance contacts
            'maintenance_contact',
            'electrician_contact',
            'plumber_contact',
            
            # Important notices
            'important_notices',
            
            'updated_at',
        ]
        read_only_fields = fields
    
    def get_active_payment_methods(self, obj):
        return obj.active_payment_methods