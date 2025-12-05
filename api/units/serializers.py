from rest_framework import serializers
from .models import Unit, AssignedUnit
from users.serializers import UserSerializer
from django.contrib.auth import get_user_model
from users.models import CustomUser
from units.models import Unit

User = get_user_model()

class UnitSerializer(serializers.ModelSerializer):

    class Meta:
        model=Unit
        fields=['id', 'unit_name','rent_amount', 'building', 'floor_area', 'bedrooms', 'isAvailable' , 'created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_at', 'deleted_by']
    
    def validate(self, data):
        """
        ✅ Check if a unit with this name already exists in the same building
        """
        unit_name = data.get('unit_name', '').strip()
        building = data.get('building', '')
        
        if not unit_name or not building:
            return data
            
        # Get the instance if it exists (for updates)
        instance = self.instance
        
        # Check for existing unit with same name in same building
        query = Unit.objects.filter(
            unit_name__iexact=unit_name,
            building__iexact=building
        )
        
        # If updating, exclude current instance from the check
        if instance:
            query = query.exclude(id=instance.id)
        
        if query.exists():
            raise serializers.ValidationError({
                'unit_name': f'A unit with name "{unit_name}" already exists in building {building}.'
            })
        
        return data

    def create(self, validated_data):
        created_by = self.context.get('created_by')

        unit = Unit(**validated_data)
        if created_by and created_by.is_authenticated:
            unit.created_by = created_by
        
        unit.save()
        return unit
    

class UpdateUnitSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Unit
        fields=['unit_name','rent_amount', 'building', 'floor_area', 'bedrooms', 'isAvailable', 'created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_at', 'deleted_by']

    def update(self, instance, validated_data):
        updated_by = self.context.get('updated_by')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if updated_by and updated_by.is_authenticated:
            instance.updated_by = updated_by

        instance.save()
        return instance


class PaginateAssignedUnitSerializer(serializers.ModelSerializer):
    unit_id = UnitSerializer()
    assigned_by = UserSerializer()
    class Meta:
        model = AssignedUnit
        fields = ['id', 'unit_id', 'assigned_by', 'building', 'unit_status', 'move_in_date', 'security', 'maintenance', 'amenities', 'created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_at', 'deleted_by']


class AssignedUnitSerializer(serializers.ModelSerializer):
    assigned_by = UserSerializer(read_only=True)
    unit_id = UnitSerializer(read_only=True)

    user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        source="assigned_by",
        write_only=True,
        required=False
    )

    unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.all(),
        source="unit_id",
        write_only=True,
        required=False
    )

    class Meta:
        model = AssignedUnit
        fields = [
            'id', 'unit_id', 'assigned_by', 'building', 'move_in_date', 'user_id', 'unit',
            'unit_status', 'security', 'maintenance', 'amenities',
            'created_at', 'created_by', 'updated_at', 'updated_by',
            'deleted_at', 'deleted_by'
        ]

    def validate(self, data):
        unit = data.get('unit_id') or self.initial_data.get('unit')
        user = data.get('assigned_by') or self.initial_data.get('user_id')

        instance = getattr(self, 'instance', None)

        # 🧩 Check if this unit is already assigned to someone else
        if AssignedUnit.objects.filter(unit_id=unit).exclude(id=getattr(instance, 'id', None)).exists():
            raise serializers.ValidationError({
                "unit_id": "This unit is already assigned to someone."
            })

        # 🧩 Check if this user is already assigned to this unit
        if AssignedUnit.objects.filter(unit_id=unit, assigned_by=user).exclude(id=getattr(instance, 'id', None)).exists():
            raise serializers.ValidationError({
                "detail": "This user is already assigned to this unit."
            })

        return data

    def create(self, validated_data):
        created_by = self.context.get('created_by')
        assigned_unit = AssignedUnit(**validated_data)
        if created_by and created_by.is_authenticated:
            assigned_unit.created_by = created_by
        assigned_unit.save()
        return assigned_unit

    def update(self, instance, validated_data):
        updated_by = self.context.get('updated_by')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if updated_by and updated_by.is_authenticated:
            instance.updated_by = updated_by
        instance.save()
        return instance
    
class AssignedUnitDetailSerializer(serializers.ModelSerializer):
    unit_id = UnitSerializer()
    assigned_by = serializers.StringRelatedField()  # Assuming you want to display the username or string representation of the user
    class Meta:
        model = AssignedUnit
        fields = ['id', 'unit_id', 'assigned_by', 'created_at', 'created_by', 'updated_at', 'updated_by', 'deleted_at', 'deleted_by']
