from django.urls import path
from . import views
from .views import PaginatedPayments

urlpatterns = [
    path('payment-methods', views.get_payment_methods, name='get_payment_methods'),
    path('payment-method/', views.create_payment_method, name='create_payment_method'),
    path('payment-method/<int:pk>/', views.get_payment_method_by_id, name='get_payment_method_by_id'),
    path('payment-method/<int:pk>/update/', views.update_payment_method_by_id, name='update_payment_method_by_id'),
    path('payment-method/<int:pk>/delete/', views.delete_payment_method_by_id, name='delete_payment_method_by_id'),

    path('payments', PaginatedPayments.as_view(), name='paginated-payments' ),
    # path('payments', views.get_payments, name='get_payments'),
    path('payment/', views.create_payment, name='create_payment'),
    path('payment/<int:pk>/', views.get_payment_by_id, name='get_payment_by_id'),
    path('payment/<int:pk>/update/', views.update_payment_by_id, name='update_payment_by_id'),
    path('payment/<int:pk>/delete/', views.delete_payment_by_id, name='delete_payment_by_id'),

    path('payment/pendings', views.get_total_pendings),

    path('calculate-advance/', views.calculate_advance_payment, name='calculate-advance'),
    path('advance-payments/<int:user_id>/', views.get_advance_payments, name='get-advance-payments'),
]