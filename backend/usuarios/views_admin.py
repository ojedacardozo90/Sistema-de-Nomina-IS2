# backend/usuarios/views_admin.py
from rest_framework import viewsets, permissions
from django.contrib.auth import get_user_model
from .serializers_admin import UsuarioAdminSerializer

User = get_user_model()

class IsAdminOrGerente(permissions.BasePermission):
    """Permite acceso solo a ADMIN o GERENTE RRHH"""
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return getattr(request.user, "rol", "") in ["admin", "gerente_rrhh"]

class UsuarioAdminViewSet(viewsets.ModelViewSet):
    """CRUD completo de usuarios (similar a Django Admin)"""
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UsuarioAdminSerializer
    permission_classes = [IsAdminOrGerente]

    def get_queryset(self):
        user = self.request.user
        # Los gerentes pueden ver todo menos los ADMIN
        if user.rol == "gerente_rrhh":
            return User.objects.exclude(rol="admin")
        return super().get_queryset()
