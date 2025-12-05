from django.urls import path
from . import views
from .views import PaginatedAssignedUnit, PaginatedUnit, get_assigned_units, get_units

urlpatterns = [
    # Crud operations for units
    path('units', get_units.as_view(), name='get_units'),
    path('units/paginated', PaginatedUnit.as_view(), name='get_paginated_units'),
    path('unit/', views.create_unit, name='create_unit'),
    path('unit/<int:pk>/', views.get_unit_by_id, name='get_unit_by_id'),
    path('unit/<int:pk>/update/', views.update_unit_by_id, name='update_unit_by_id'),
    path('unit/<int:pk>/delete/', views.delete_unit_by_id, name='delete_unit_by_id'),
    path('unit/<int:pk>/delete-permanently/', views.delete_unit_by_id_permanently, name='delete_unit_by_id_permanently'),
    path('unit/<int:pk>/restore/', views.restore_unit, name='restore_unit'),

    # Crud operations for assigned units
    path('assigned_units', get_assigned_units.as_view(), name='get_assigned_units'),
    path('assigned_units/paginated', PaginatedAssignedUnit.as_view(), name='PaginatedAssignedUnit'),
    path('assigned_unit/', views.create_assigned_unit, name='create_assigned_unit'),
    path('assigned_unit/<int:pk>/', views.get_assigned_unit_by_id, name='get_assigned_unit_by_id'),
    path('assigned_unit/<int:pk>/details', views.get_assigned_unit_detail_by_id, name='get_assigned_unit_by_id'),
    path('assigned_unit/<int:pk>/update/', views.update_assigned_unit_by_id, name='update_assigned_unit_by_id'),
    path('assigned_unit/<int:pk>/delete/', views.delete_assigned_unit_by_id, name='update_assigned_unit_by_id'),
    path('assigned_unit/<int:pk>/restore/', views.restore_assigned_unit_by_id, name='restore_assigned_unit_by_id'),
    path('assigned_unit/<int:pk>/permanently-delete/', views.delete_permanently_assigned_unit_by_id, name='update_assigned_unit_by_id'),
]