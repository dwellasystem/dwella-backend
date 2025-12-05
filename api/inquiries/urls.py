from django.urls import path
from . import views
from .views import PaginatedInquiries

urlpatterns = [
    ############################# Inquiry Type URLs ################################
    path('inquiry-types', views.get_inquiry_types, name='get_inquiry_types'),
    path('inquiry-type/', views.create_inquiry_type, name='create_inquiry_type'),
    path('inquiry-type/<int:pk>/', views.get_inquiry_type_by_id, name='get_inquiry_type_by_id'),
    path('inquiry-type/<int:pk>/update/', views.update_inquiry_type_by_id, name='update_inquiry_type_by_id'),
    path('inquiry-type/<int:pk>/delete/', views.delete_inquiry_type_by_id, name='delete_inquiry_type_by_id'),  

    ############################# Inquiry URLs #####################################
    path("inquiries", PaginatedInquiries.as_view(), name="paginated-inquiries"),
    # path('inquiries', views.get_inquiries, name='get_inquiries'),
    path('inquiry/', views.create_inquiry, name='create_inquiry'),
    path('inquiry/<int:pk>/', views.get_inquiry_by_id, name='get_inquiry_by_id'),
    path('inquiry/<int:pk>/update/', views.update_inquiry_by_id, name='update_inquiry_by_id'),
    path('inquiry/<int:pk>/delete/', views.delete_inquiry_by_id, name='delete_inquiry_by_id'),
    
    path('inquiry/open', views.get_total_open_ionquiries, name='get_total_open_ionquiries')
]