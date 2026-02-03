"""
URL Configuration for Equipment API
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuthViewSet, DatasetViewSet, EquipmentViewSet

router = DefaultRouter()
router.register(r'auth', AuthViewSet, basename='auth')
router.register(r'datasets', DatasetViewSet, basename='dataset')
router.register(r'equipment', EquipmentViewSet, basename='equipment')

urlpatterns = [
    path('', include(router.urls)),
]
