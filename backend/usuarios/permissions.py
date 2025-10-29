# ============================================================
# 🔐 Permisos personalizados según rol del usuario (Sistema Nómina IS2)
# ============================================================

from rest_framework.permissions import BasePermission, SAFE_METHODS


# ============================================================
# 🔹 Función auxiliar
# ============================================================
def get_user_role(user):
    """Obtiene el rol de un usuario, retornando 'admin' si es superusuario."""
    if not user or not user.is_authenticated:
        return None
    if getattr(user, "is_superuser", False):
        return "admin"
    return getattr(user, "rol", None)


# ============================================================
# 🔹 Permisos individuales
# ============================================================
class IsAdmin(BasePermission):
    """Permite acceso solo a usuarios con rol ADMIN."""
    def has_permission(self, request, view):
        return get_user_role(request.user) == "admin"


class IsGerenteRRHH(BasePermission):
    """Permite acceso solo a usuarios con rol GERENTE RRHH."""
    def has_permission(self, request, view):
        return get_user_role(request.user) == "gerente_rrhh"


class IsAsistenteRRHH(BasePermission):
    """Permite acceso solo a usuarios con rol ASISTENTE RRHH."""
    def has_permission(self, request, view):
        return get_user_role(request.user) == "asistente_rrhh"


class IsEmpleado(BasePermission):
    """Permite acceso solo a usuarios con rol EMPLEADO."""
    def has_permission(self, request, view):
        return get_user_role(request.user) == "empleado"


class ReadOnly(BasePermission):
    """Permite acceso de solo lectura (GET, HEAD, OPTIONS)."""
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


# ============================================================
# 🔹 Permisos combinados (OR lógico)
# ============================================================
class IsAdminOrAsistente(BasePermission):
    """Permite acceso a ADMIN o ASISTENTE RRHH."""
    def has_permission(self, request, view):
        rol = get_user_role(request.user)
        return rol in ["admin", "asistente_rrhh"]


class IsAdminOrGerente(BasePermission):
    """Permite acceso a ADMIN o GERENTE RRHH."""
    def has_permission(self, request, view):
        rol = get_user_role(request.user)
        return rol in ["admin", "gerente_rrhh"]


class IsGerenteOrAsistente(BasePermission):
    """Permite acceso a GERENTE RRHH o ASISTENTE RRHH."""
    def has_permission(self, request, view):
        rol = get_user_role(request.user)
        return rol in ["gerente_rrhh", "asistente_rrhh"]
