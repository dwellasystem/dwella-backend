# serializers.py
from rest_framework import serializers
from .models import Inquiry, InquiryType
from units.models import Unit
from django.contrib.auth import get_user_model

User = get_user_model()

class InquiryTypeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = InquiryType
        fields = ['id', 'name']

class CreateInquirySerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Inquiry
        fields = ['id', 'unit', 'title', 'description', 'status', 'created_at', 'updated_at', 'type', 'resident', 'photo']
        read_only_fields = ['id', 'inquiry_type', 'created_at', 'updated_at', 'status']

    def create(self, validated_data):
        # Handle the photo field properly
        photo = validated_data.pop('photo', None)
        inquiry = Inquiry.objects.create(**validated_data)
        
        if photo:
            inquiry.photo = photo
            inquiry.save()
            
        return inquiry

class UpdateInquirySerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Inquiry
        fields = ['id', 'unit', 'title', 'description', 'status', 'inquiry_type', 'resident', 'type', 'photo']
        extra_kwargs = {
            'resident': {'required': False},  # Optional for update
            'unit': {'required': False},
            'title': {'required': False},
            'description': {'required': False},
            'status': {'required': False},
            'inquiry_type': {'required': False},  # Required false for update any single fields
            'photo': {'required': False}  # Optional for update
        }
        read_only_fields = ['created_at', 'updated_at']  # Make these fields read-only

    def update(self, instance, validated_data):
        # Handle photo update
        photo = validated_data.pop('photo', None)
        
        if photo is not None:
            # If photo is explicitly set to null, clear it
            if photo is None:
                instance.photo = None
            else:
                instance.photo = photo
        
        return super().update(instance, validated_data)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'middle_name', 'last_name']

class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'unit_name', 'building']

class InquirySerializer(serializers.ModelSerializer):
    resident = UserSerializer()
    unit = UnitSerializer()
    photo = serializers.ImageField(read_only=True)  # Make photo read-only in listing
    
    class Meta:
        model = Inquiry
        fields = ['id', 'unit', 'title', 'description', 'status', 'resident', 'type', 'created_at', 'photo']
        read_only_fields = ['id', 'created_at', 'updated_at', 'resident']  # Make these fields read-only