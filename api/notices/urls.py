from django.urls import path
from . import views
from .views import PaginatedNotices

urlpatterns = [
    ######################### NoticeType Crud API URLs #########################
    path('notice-types', views.get_notice_types, name='get_notice_types'),
    path('notice-type/', views.create_notice_type, name='create_notice_type'),
    path('notice-type/<int:pk>/', views.get_notice_type_by_id, name='get_notice_type_by_id'),
    path('notice-type/<int:pk>/update/', views.update_notice_type_by_id, name='update_notice_type_by_id'),
    path('notice-type/<int:pk>/delete/', views.delete_notice_type, name='delete_notice_type'),

    ######################### Notices Crud API URLs ############################
    path('notices', PaginatedNotices.as_view(), name='get_notices'),
    # path('notices', views.get_notices, name='get_notices'),
    path('notice/', views.create_notice, name='create_notice'),
    path('notice/<int:pk>/', views.get_notice_by_id, name='get_notice_by_id'),
    path('notice/<int:pk>/update/', views.update_notice_by_id, name='update_notice_by_id'),
    path('notice/<int:pk>/delete/', views.delete_notice, name='delete_notice')
]