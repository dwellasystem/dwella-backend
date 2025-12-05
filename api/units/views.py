from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status, filters
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .serializers import UnitSerializer, PaginateAssignedUnitSerializer, UpdateUnitSerializer, AssignedUnitSerializer, AssignedUnitDetailSerializer
from .models import Unit, AssignedUnit

# Create your views here.

######################################################################
######################## Units Views #################################
######################################################################

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_unit(request):
    serializer = UnitSerializer(data=request.data, context={'created_by': request.user})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_units(request):
#     units = Unit.objects.all()
#     serializer = UnitSerializer(units, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)


class get_units(ListAPIView):
    queryset = Unit.objects.all().order_by('building', 'unit_name')
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['isAvailable']
    pagination_class = None


class PaginatedUnit(ListAPIView):
    queryset = Unit.objects.all().order_by('building', 'unit_name')
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['unit_name', 'rent_amount', 'isAvailable']
    search_fields = ['unit_name', 'rent_amount', 'isAvailable']
    ordering_fields = ['building', 'rent_amount']


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unit_by_id(request, pk):
    try:
        unit = Unit.objects.get(pk=pk)
    except Unit.DoesNotExist:
        return Response({"error": "Payment method not found."}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = UnitSerializer(unit)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
def update_unit_by_id(request, pk):
    try:
        unit = Unit.objects.get(pk=pk)
    except Unit.DoesNotExist:
        return Response({"error": "Payment method not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateUnitSerializer(unit, data=request.data, context={'updated_by': request.user}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_unit_by_id(request, pk):
    try:
        unit = Unit.objects.get(pk=pk)
    except Unit.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    unit.soft_delete(by_user=request.user)
    return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_unit_by_id_permanently(request, pk):
    try:
        unit = Unit.all_objects.get(pk=pk)
        unit.delete()
        return Response({'message':'User permanently deleted'})
    except Unit.DoesNotExist:
        return Response({'error':'Unit not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_unit(request, pk):
    try:
        unit = Unit.all_objects.get(pk=pk)
        unit.restore()
        return Response({'message': 'User restored successfully.'})
    except Unit.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


######################################################################
######################## Assigned Unit Views #########################
######################################################################

class get_assigned_units(ListAPIView):
    queryset = AssignedUnit.objects.all()
    serializer_class = AssignedUnitSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['assigned_by']
    pagination_class = None

class PaginatedAssignedUnit(ListAPIView):
    queryset = AssignedUnit.objects.all().order_by('-move_in_date')
    serializer_class = PaginateAssignedUnitSerializer
    # permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['assigned_by', 'unit_id']
    search_fields = ['unit_status', 'building', 'assigned_by__first_name', 'assigned_by__last_name', 'assigned_by__middle_name']
    ordering_fields = ['unit_id__building', 'move_in_date']
    # ordering = ['-move_in_date']

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_assigned_unit(request):
    # 1️⃣ Get the unit ID from the request
    unit_id = request.data.get('unit')
    print(unit_id)

    try:
        unit = Unit.objects.get(pk=unit_id)
    except Unit.DoesNotExist:
        return Response({'error': 'Unit not found'}, status=status.HTTP_404_NOT_FOUND)

    # 2️⃣ Update the unit availability
    serializer_unit = UnitSerializer(unit, data={'isAvailable': False}, partial=True)
    if serializer_unit.is_valid():
        serializer_unit.save()
        print("✅ Unit updated:", serializer_unit.data)
    else:
        print("❌ Unit update errors:", serializer_unit.errors)
        return Response(serializer_unit.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer = AssignedUnitSerializer(data=request.data, context={'created_by': request.user})
    if serializer.is_valid():
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assigned_unit_by_id(request, pk):
    try:
        assigned_unit = AssignedUnit.objects.get(assigned_by=pk)
    except AssignedUnit.DoesNotExist:
        return Response({"error": "No assigned unit not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = AssignedUnitSerializer(assigned_unit)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_assigned_unit_by_id(request, pk):
    try:
        assigned_unit = AssignedUnit.objects.get(pk=pk)
    except AssignedUnit.DoesNotExist:
        return Response({"error": "No assigned unit not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = AssignedUnitSerializer(assigned_unit, data=request.data, context={'updated_by': request.user}, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_assigned_unit_by_id(request, pk):
    try:
        assigned_unit = AssignedUnit.objects.get(pk=pk)
    except AssignedUnit.DoesNotExist:
        return Response({"error": "No assigned unit not found."}, status=status.HTTP_404_NOT_FOUND)
    
    assigned_unit.soft_delete(by_user=request.user)
    return Response({'message': f'Assigned unit {assigned_unit.id} successfully deleted.'})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_permanently_assigned_unit_by_id(request, pk):
    try:
        assigned_unit = AssignedUnit.all_objects.get(pk=pk)
    except AssignedUnit.DoesNotExist:
        return Response({"error": "No assigned unit not found."}, status=status.HTTP_404_NOT_FOUND)
    
    assigned_unit.delete()
    print(f'The assigned unit {assigned_unit.id} deleted permanently.')
    return Response({'message': 'The assigned unit permanently deleted'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def restore_assigned_unit_by_id(request, pk):
    try:
        assigned_unit = AssignedUnit.all_objects.get(pk=pk)
    except AssignedUnit.DoesNotExist:
        return Response({"error": "No assigned unit not found."}, status=status.HTTP_404_NOT_FOUND)
    
    assigned_unit.restore()
    return Response({"error": f"Successfully restore user {assigned_unit.id}"}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_assigned_unit_detail_by_id(request, pk):
    try:
        assigned_unit = AssignedUnit.objects.get(pk=pk)
    except AssignedUnit.DoesNotExist:
        return Response({"error": "No assigned unit not found."}, status=status.HTTP_404_NOT_FOUND)
    serializer = AssignedUnitDetailSerializer(assigned_unit)
    return Response(serializer.data, status=status.HTTP_200_OK)