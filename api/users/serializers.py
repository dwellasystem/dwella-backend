from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.password_validation import validate_password
from units.models import Unit  # adjust if your Unit model is in another app

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    address = serializers.CharField(write_only=True, required=False)
    role = serializers.CharField(write_only=True, required=False, default='resident')
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "password", "first_name", "last_name",
            "middle_name", "profile", "account_status", "move_in_date", "phone_number", "role", "created_by", "created_at", "address", "unit"
        ]

        read_only_fields = ["created_by", "created_at"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        created_by = self.context.get('created_by')

        # Create user instance without password
        user = User(**validated_data)
        user.set_password(password)   # This hashes the password
        if created_by and created_by.is_authenticated:
            user.created_by = created_by
        
        user.save()
        return user
    
class UpdateUserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "middle_name", "profile", "is_staff", "account_status", "date_joined", "phone_number", "password", "role", "address", "unit"
        ]
        extra_kwargs = {
            "username": {"required": False},
            "phone_number": {"required": False},
            "is_staff": {"write_only": True},
            "role": {"required": False},
            "address": {"required": False},
        }

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        updated_by = self.context.get('updated_by')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        if updated_by and updated_by.is_authenticated:
            instance.updated_by = updated_by

        instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    unit_name = serializers.CharField(source="unit.unit_name", read_only=True)
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'middle_name', 'address', 'phone_number', 'date_of_birth',
            'move_in_date', 'created_at', 'created_by', 'updated_at', 'updated_by','deleted_at',
            'deleted_by', 'account_status', 'role', 'profile', 'is_active', 'unit', 'unit_name'
        ]

        read_only_fields = ['created_at', 'updated_at', 'deleted_at', 'deleted_by', 'created_by', 'updated_by']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token["username"] = user.username
        token["role"] = user.role
        return token
    

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        User = get_user_model()
        data = super().validate(attrs)

        old_refresh = RefreshToken(attrs["refresh"])
        user_id = old_refresh["user_id"]
        
        user = User.objects.get(pk=user_id)

        new_refresh = RefreshToken.for_user(user)

        data["refresh"] = str(new_refresh)

        return data
    

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.lower().strip()

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        
        try:
            validate_password(data['new_password'])
        except Exception as e:
            raise serializers.ValidationError({"new_password": list(e.messages)})
        
        return data

    def validate_uid(self, value):
        """Validate that UID can be decoded"""
        try:
            from django.utils.encoding import force_str
            from django.utils.http import urlsafe_base64_decode
            force_str(urlsafe_base64_decode(value))
            return value
        except (TypeError, ValueError, OverflowError):
            raise serializers.ValidationError("Invalid user ID format.")