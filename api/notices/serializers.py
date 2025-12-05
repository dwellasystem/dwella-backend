from rest_framework import serializers
from .models import Notice, NoticeType
from units.models import Unit
from units.serializers import AssignedUnitSerializer

class NoticeTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = NoticeType
        fields = ['id', 'name']

class CreateNoticeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notice
        fields = ['id', 'title', 'content', 'target_audience', 'created_at', 'updated_at', 'notice_type']
        read_only_fields = ['created_at', 'updated_at']  # Make these fields read-only

class UpdateCreateNoticeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notice
        fields = ['id', 'title', 'content', 'target_audience', 'notice_type']
        extra_kwargs = {
            'title': {'required': False},
            'content': {'required': False},
            'target_audience': {'required': False},
            'notice_type': {'required': False}  # Required false for update any single fields
        }
        read_only_fields = ['created_at', 'updated_at']  # Make these fields read-only


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'unit_name', 'created_at', 'updated_at']

class NoticeSerializer(serializers.ModelSerializer):

    notice_type = NoticeTypeSerializer(read_only=True)
    target_audience = AssignedUnitSerializer(many=True, read_only=True)
    class Meta:
        model = Notice
        fields = ['id', 'title', 'content', 'target_audience', 'created_at', 'updated_at', 'notice_type']
        read_only_fields = ['created_at', 'updated_at']  # Make these fields read-only