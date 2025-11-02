# ============================================================
# 🧩 Administración de Usuarios - Sistema de Nómina IS2
# ------------------------------------------------------------
# Vistas para panel de administración interno:
#   • Listado, creación y edición de usuarios
#   • Exportación CSV
#   • Resumen de roles y estadísticas
# ============================================================

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers_admin import UsuarioAdminSerializer
from .permissions import IsAdmin, IsAdminOrGerente

Usuario = get_user_model()

# ============================================================
# 🔹 1️⃣ Vista principal (CRUD completo)
# ============================================================
class UsuarioAdminViewSet(viewsets.ModelViewSet):
    """
    Gestiona usuarios desde el panel de administración (solo roles con permisos altos).
    - Admin puede crear, listar y eliminar usuarios.
    - Gerente puede listar, pero no eliminar.
    """
    queryset = Usuario.objects.all().order_by("username")
    serializer_class = UsuarioAdminSerializer
    permission_classes = [IsAdminOrGerente]

    def create(self, request, *args, **kwargs):
        """Crea usuarios nuevos con rol asignado."""
        data = request.data.copy()
        email = data.get("email", "").lower().strip()
        if Usuario.objects.filter(email=email).exists():
            return Response({"error": "Ya existe un usuario con este correo."}, status=400)
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """Elimina usuarios solo si el rol actual es admin."""
        user = request.user
        if getattr(user, "rol", "") != "admin":
            return Response({"error": "Solo los administradores pueden eliminar usuarios."}, status=403)
        return super().destroy(request, *args, **kwargs)

# ============================================================
# 📊 2️⃣ Endpoint de estadísticas
# ============================================================
    @action(detail=False, methods=["get"], permission_classes=[IsAdmin])
    def resumen_roles(self, request):
        """
        Devuelve un resumen con el conteo de usuarios por rol.
        Ejemplo: {"admin": 2, "gerente": 3, "asistente": 4, "empleado": 10}
        """
        data = Usuario.objects.values("rol").annotate(total=Count("id"))
        resumen = {d["rol"]: d["total"] for d in data}
        return Response(resumen)

# ============================================================
# 📤 3️⃣ Exportación CSV
# ============================================================
    @action(detail=False, methods=["get"], permission_classes=[IsAdmin])
    def exportar_csv(self, request):
        """Exporta todos los usuarios a un archivo CSV descargable."""
        usuarios = Usuario.objects.all().values("id", "username", "email", "rol", "is_active")
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="usuarios_export.csv"'

        columnas = ["ID", "Usuario", "Correo", "Rol", "Activo"]
        import csv
        writer = csv.writer(response)
        writer.writerow(columnas)
        for u in usuarios:
            writer.writerow([u["id"], u["username"], u["email"], u["rol"], "Sí" if u["is_active"] else "No"])
        return response

# ============================================================
# 🔍 4️⃣ Diagnóstico rápido
# ============================================================
    @action(detail=False, methods=["get"], permission_classes=[IsAdmin])
    def diagnostico(self, request):
        """
        Endpoint de prueba para verificar conexión y modelo.
        """
        total = Usuario.objects.count()
        activos = Usuario.objects.filter(is_active=True).count()
        return Response({
            "total_usuarios": total,
            "activos": activos,
            "modo_debug": settings.DEBUG,
            "base_datos": settings.DATABASES["default"]["NAME"],
        })
