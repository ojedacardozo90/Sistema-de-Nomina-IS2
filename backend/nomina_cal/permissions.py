from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == "admin"


class IsGerenteRRHH(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == "gerente"


class IsAsistenteRRHH(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == "asistente"


class IsEmpleado(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == "empleado"
