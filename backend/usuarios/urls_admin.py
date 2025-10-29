# backend/usuarios/urls_admin.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_admin import UsuarioAdminViewSet

router = DefaultRouter()
router.register(r"usuarios", UsuarioAdminViewSet, basename="usuarios_admin")

urlpatterns = [
    path("", include(router.urls)),
]
