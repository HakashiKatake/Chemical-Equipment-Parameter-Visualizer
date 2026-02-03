"""
URL Configuration for Equipment API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, DatasetViewSet, EquipmentViewSet, health_check

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'datasets', DatasetViewSet, basename='dataset')
router.register(r'equipment', EquipmentViewSet, basename='equipment')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', health_check, name='health-check'),
]
