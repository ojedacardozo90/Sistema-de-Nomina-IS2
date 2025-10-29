# backend/usuarios/serializers.py
# ============================================================
# 🎯 Serializadores de Usuarios (TP IS2 - Nómina con JWT)
# ============================================================

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

# ============================================================
# 🔐 Custom Token Serializer (JWT extendido)
# ============================================================

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

Usuario = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para el inicio de sesión JWT.
    Incluye datos adicionales del usuario dentro del token.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Agregamos información personalizada
        token["email"] = user.email
        token["rol"] = user.rol
        token["nombre_completo"] = user.get_full_name()
        token["username"] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["usuario"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "rol": self.user.rol,
            "nombre_completo": self.user.get_full_name(),
        }
        return data


User = get_user_model()


# ============================================================
# 🔹 SERIALIZER: Usuario
# ============================================================
class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializador principal para el modelo de Usuario.
    Incluye validación de contraseña y manejo de roles.
    """

    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)
    rol_display = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "rol",              # rol interno (ej: admin, gerente, asistente, empleado)
            "rol_display",      # descripción legible del rol
            "is_active",
            "password",
            "password2",
        ]
        read_only_fields = ["id"]

    # --------------------------------------------------------
    # 🔹 Validaciones
    # --------------------------------------------------------
    def validate_email(self, value):
        """El email debe ser único."""
        if User.objects.filter(email=value).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise serializers.ValidationError("Ya existe un usuario con este email.")
        return value

    def validate(self, data):
        """Valida que las contraseñas coincidan."""
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Las contraseñas no coinciden."})

        # Validación de seguridad de contraseña (mínimo 8 caracteres, etc.)
        validate_password(data["password"])
        return data

    def get_rol_display(self, obj):
        """Traduce el rol en un nombre legible."""
        roles_map = {
            "admin": "Administrador",
            "gerente": "Gerente de RRHH",
            "asistente": "Asistente de RRHH",
            "empleado": "Empleado",
        }
        return roles_map.get(obj.rol, "Desconocido")

    # --------------------------------------------------------
    # 🔹 Creación y actualización
    # --------------------------------------------------------
    def create(self, validated_data):
        """Crea un usuario con contraseña encriptada."""
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Actualiza usuario y re-encripta contraseña si es necesario."""
        validated_data.pop("password2", None)
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)
        instance.save()
        return instance
