from django.urls import path
from . import views
from .views import PaginatedUsers, UserListView, password_reset_request, password_reset_confirm, change_password



urlpatterns = [
    path('register/', views.register_user, name='register'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),

    # Crud operations for users
    path('users-paginated/', PaginatedUsers.as_view(), name='get_paginated_users'),
    path('users/', UserListView.as_view(), name='get_users'),
    path('user/<int:pk>/', views.get_user_by_id, name='get_user'),
    path('user/update/<int:pk>/', views.update_user_by_id, name='update_user'),
    path('user/delete/<int:pk>/', views.delete_user_by_id, name='delete_user'),
    path('user/restore/<int:pk>/', views.restore_deleted_user,name='restore_user' ),

    # Users Summary
    path('users/summary/', views.user_summary_stats, name='user-summary'),
    # Statistics for Charts Data
    path('users/stats/', views.user_stats_monthly, name='user-stats'),

    path('password-reset/', password_reset_request, name='password-reset'),
    path('password-reset/confirm/', password_reset_confirm, name='password-reset-confirm'),
    path('change-password/', change_password, name='change-password'),
]
