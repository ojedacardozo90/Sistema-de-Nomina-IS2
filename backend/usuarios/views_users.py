from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UsuarioSerializer

User = get_user_model()

class IsAdminOrRRHH(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        rol = getattr(request.user, "rol", "").lower()
        return request.user.is_staff or rol in ["admin", "gerente_rrhh", "asistente_rrhh"]

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrRRHH]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            # 204 no lleva body, pero por conveniencia devolvemos 200 con mensaje
            return Response({"detail": "Usuario eliminado correctamente."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
