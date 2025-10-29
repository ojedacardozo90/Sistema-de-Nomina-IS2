# ============================================================
# ⚙️ Configuración del panel de administración para Usuarios
# ============================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Columnas visibles en la tabla de usuarios
    list_display = ("username", "email", "first_name", "last_name", "rol", "is_active", "is_staff", "is_superuser")
    list_filter = ("rol", "is_active", "is_staff")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("rol", "username")

    # Campos mostrados al editar un usuario
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Información personal", {"fields": ("first_name", "last_name", "email", "rol")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )

    # Campos al crear un nuevo usuario
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "password1",
                    "password2",
                    "rol",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
