from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# =========================================================
# 👤 MODELO USUARIO PERSONALIZADO
# =========================================================
class Usuario(AbstractUser):
    """
    Modelo de Usuario extendido para el sistema de nómina.
    - Basado en AbstractUser de Django.
    - Login por email (USERNAME_FIELD = "email").
    - Incluye campo de rol con choices para control de permisos.
    """

    # ----------------------------
    # Constantes de Roles
    # ----------------------------
    ADMIN = "admin"
    GERENTE = "gerente_rrhh"
    ASISTENTE = "asistente_rrhh"
    EMPLEADO = "empleado"

    ROLES = [
        (ADMIN, "Administrador"),
        (GERENTE, "Gerente RRHH"),
        (ASISTENTE, "Asistente RRHH"),
        (EMPLEADO, "Empleado"),
    ]

    # ----------------------------
    # Campos personalizados
    # ----------------------------
    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default=EMPLEADO,
        db_index=True,  # 👈 mejora: más rápido para búsquedas por rol
        help_text="Rol asignado al usuario dentro del sistema"
    )

    email = models.EmailField(
        unique=True,
        blank=False,
        help_text="Correo electrónico único para cada usuario (login preferido)"
    
    
    )

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    # ----------------------------
    # Configuración de autenticación
    # ----------------------------
    USERNAME_FIELD = "email"   # 👈 login con email
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    # ----------------------------
    # Métodos útiles
    # ----------------------------
    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"

    def is_admin(self):
        return self.rol == self.ADMIN

    def is_gerente(self):
        return self.rol == self.GERENTE

    def is_asistente(self):
        return self.rol == self.ASISTENTE

    def is_empleado(self):
        return self.rol == self.EMPLEADO

    # ----------------------------
    # Configuración Meta
    # ----------------------------
    class Meta:
        ordering = ["username"]
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"