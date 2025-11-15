#
#  Serializador administrativo de Usuarios
# Sistema de Nómina IS2 (FP-UNA / )

# Este serializer se utiliza exclusivamente desde el panel
# React tipo Admin Django (ruta: /api/admin-panel/usuarios/),
# permitiendo crear, editar y visualizar usuarios con todos
# sus atributos (rol, permisos, fechas, etc.).
#

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()


class UsuarioAdminSerializer(serializers.ModelSerializer):
    """
    Serializer completo para CRUD de usuarios desde el panel administrativo.
    Incluye:
      - Hash automático de contraseñas en create/update.
      - Campo adicional `rol_display` para mostrar el nombre legible del rol.
      - Campos de control (is_active, is_staff, is_superuser).
    """

    
    #  Configuración de campos especiales
    
    password = serializers.CharField(write_only=True, required=False)
    rol_display = serializers.CharField(source="get_rol_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "rol",
            "rol_display",
            "is_active",
            "is_staff",
            "is_superuser",
            "date_joined",
            "last_login",
            "password",
        ]
        read_only_fields = ["date_joined", "last_login"]

    
    #  Creación de usuario (con encriptado de contraseña)
    
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.password = make_password(password)
        user.save()
        return user

    
    # ✏️ Actualización de usuario (con hash si cambia contraseña)
    
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.password = make_password(password)
        instance.save()
        return instance
