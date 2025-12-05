# hoa/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import HoaInformation
from .serializers import HoaInformationSerializer, HoaInformationPublicSerializer

class IsAdminUser(permissions.BasePermission):
    """Custom permission to only allow admin users"""
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'

class HoaInformationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for HOA Information with role-based permissions.
    
    - Admin users can perform all CRUD operations
    - Non-admin users can only read (list, retrieve, current)
    """
    queryset = HoaInformation.objects.all()
    
    def get_serializer_class(self):
        # Use public serializer for non-admin users for read operations
        if self.request.user and self.request.user.role != 'admin':
            # For GET requests, use public serializer
            if self.request.method in permissions.SAFE_METHODS:
                return HoaInformationPublicSerializer
            # Non-admin users shouldn't be able to modify, but just in case
            return HoaInformationPublicSerializer
        # Admin users use full serializer
        return HoaInformationSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve', 'current']:
            # All authenticated users can read
            permission_classes = [permissions.IsAuthenticated]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only admin users can write
            permission_classes = [permissions.IsAuthenticated, IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        """
        GET /api/hoa-information/
        Returns the single HOA Information instance or empty response
        """
        queryset = self.get_queryset()
        
        if queryset.exists():
            instance = queryset.first()
            serializer = self.get_serializer(instance)
            return Response([serializer.data])  # Return as list for consistency
        else:
            return Response([])
    
    def retrieve(self, request, pk=None, *args, **kwargs):
        """
        GET /api/hoa-information/{id}/
        Get specific HOA Information
        """
        queryset = self.get_queryset()
        
        if queryset.exists():
            instance = queryset.first()
            # If trying to access a specific ID, check if it matches
            if pk and str(instance.id) != pk:
                return Response(
                    {"detail": "Not found."}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response(
                {"detail": "No HOA information found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    def create(self, request, *args, **kwargs):
        """
        POST /api/hoa-information/
        Create HOA Information (only if it doesn't exist)
        """
        # Check if HOA information already exists
        if HoaInformation.objects.exists():
            return Response(
                {"detail": "HOA Information already exists. Use update instead."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, pk=None, *args, **kwargs):
        """
        PUT /api/hoa-information/{id}/
        Update entire HOA Information
        """
        instance = get_object_or_404(HoaInformation, pk=pk)
        
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)
    
    def partial_update(self, request, pk=None, *args, **kwargs):
        """
        PATCH /api/hoa-information/{id}/
        Partial update of HOA Information
        """
        instance = get_object_or_404(HoaInformation, pk=pk)
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)
    
    def destroy(self, request, pk=None, *args, **kwargs):
        """
        DELETE /api/hoa-information/{id}/
        Delete HOA Information (admin only)
        """
        instance = get_object_or_404(HoaInformation, pk=pk)
        instance.delete()
        
        return Response(
            {"detail": "HOA Information deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """
        GET /api/hoa-information/current/
        Get the current HOA Information (convenience endpoint)
        """
        queryset = self.get_queryset()
        
        if queryset.exists():
            instance = queryset.first()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response(
                {"detail": "No HOA information found."}, 
                status=status.HTTP_404_NOT_FOUND
            )