# hoa/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HoaInformationViewSet

router = DefaultRouter()
router.register(r'hoa-information', HoaInformationViewSet, basename='hoa-information')

urlpatterns = [
    path('', include(router.urls)),
]