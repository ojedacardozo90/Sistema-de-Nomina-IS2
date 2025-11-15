# backend/nomina_cal/serializers.py
#
#  Serializadores del módulo Nómina (TP IS2 - Ingeniería de Software II)
#

from rest_framework import serializers
from .models import Concepto, SalarioMinimo, Liquidacion, DetalleLiquidacion
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

from .models import Liquidacion, DetalleLiquidacion

Usuario = get_user_model()

#
#  Custom Token Serializer (para autenticación JWT extendida)
#

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personalizado para el inicio de sesión JWT.
    Añade datos adicionales del usuario al token (rol, nombre, email).
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Campos adicionales en el token
        token["email"] = user.email
        token["rol"] = user.rol
        token["nombre"] = user.get_full_name()
        token["username"] = user.username
        return token

    def validate(self, attrs):
        data = super().validate




#
# # SERIALIZER: Concepto Salarial
#
class ConceptoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Concepto
        fields = [
            "id",
            "descripcion",
            "es_debito",
            "es_recurrente",
            "afecta_ips",
            "para_aguinaldo",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def validate(self, data):
        """
        Reglas de validación:
        - La descripción debe ser única (sin distinción de mayúsculas/minúsculas).
        """
        descripcion = data.get("descripcion")
        if Concepto.objects.filter(descripcion__iexact=descripcion).exclude(
            pk=self.instance.pk if self.instance else None
        ).exists():
            raise serializers.ValidationError(
                {"descripcion": "Ya existe un concepto con esta descripción."}
            )
        return data


#
# # SERIALIZER: Salario Mínimo Legal Vigente
#
class SalarioMinimoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalarioMinimo
        fields = ["id", "monto", "vigente_desde"]

    def validate_monto(self, value):
        if value <= 0:
            raise serializers.ValidationError("El monto debe ser mayor que cero.")
        return value


#
# # SERIALIZER: Detalle de Liquidación
#
#
#  LiquidacionSerializer — Serializador principal de nómina

# Incluye:
#   • Datos básicos del empleado (nombre, cédula, salario base)
#   • Totales automáticos (ingresos, descuentos, neto a cobrar)
#   • Detalles de liquidación anidados
#



class DetalleLiquidacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleLiquidacion
        fields = ["id", "concepto", "monto", "tipo"]


class LiquidacionSerializer(serializers.ModelSerializer):
    # # Campos relacionados del empleado
    empleado_nombre = serializers.CharField(source="empleado.nombre", read_only=True)
    empleado_cedula = serializers.CharField(source="empleado.cedula", read_only=True)
    empleado_salario_base = serializers.ReadOnlyField(source="empleado.salario_base")

    # # Campos calculados
    total_descuentos = serializers.SerializerMethodField()
    total_neto = serializers.SerializerMethodField()

    # # Detalles anidados
    detalles = DetalleLiquidacionSerializer(many=True, read_only=True)

    
    #  Métodos de cálculo
    
    def get_total_descuentos(self, obj):
        """Suma los descuentos asociados a la liquidación"""
        return sum([d.monto for d in obj.descuentos.all()]) if hasattr(obj, "descuentos") else 0

    def get_total_neto(self, obj):
        """Calcula el total neto (ingresos - descuentos)"""
        total_desc = self.get_total_descuentos(obj)
        return float(obj.total_ingresos or 0) - float(total_desc)

    
    #  Configuración del serializador
    
    class Meta:
        model = Liquidacion
        fields = [
            "id",
            "empleado",
            "empleado_nombre",
            "empleado_cedula",
            "empleado_salario_base",
            "mes",
            "anio",
            "total_ingresos",
            "total_descuentos",
            "total_neto",
            "neto_cobrar",
            "cerrada",
            "detalles",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "total_ingresos",
            "total_descuentos",
            "total_neto",
            "neto_cobrar",
            "created_at",
            "updated_at",
        ]

    
    #  Validaciones personalizadas
    
    def validate(self, data):
        mes = data.get("mes")
        anio = data.get("anio")
        empleado = data.get("empleado")

        # Validar mes válido
        if mes and (mes < 1 or mes > 12):
            raise serializers.ValidationError({"mes": "El mes debe estar entre 1 y 12."})

        # Evitar duplicados (mismo empleado, mes y año)
        if empleado and mes and anio:
            existe = Liquidacion.objects.filter(
                empleado=empleado, mes=mes, anio=anio
            ).exclude(pk=self.instance.pk if self.instance else None)
            if existe.exists():
                raise serializers.ValidationError(
                    "Ya existe una liquidación para este empleado en ese periodo."
                )
        return data

    
    # Representación extendida
    
    def to_representation(self, instance):
        """
        Amplía la salida para que el frontend reciba
        todos los valores calculados correctamente.
        """
        rep = super().to_representation(instance)
        rep["total_ingresos"] = float(instance.total_ingresos or 0)
        rep["total_descuentos"] = float(instance.total_descuentos or 0)
        rep["neto_cobrar"] = float(instance.neto_cobrar or 0)
        rep["empleado_salario_base"] = float(instance.empleado.salario_base or 0)
        return rep


#
# # SERIALIZER: Descuento
#
from .models_descuento import Descuento


class DescuentoSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source="empleado.nombre", read_only=True)

    class Meta:
        model = Descuento
        fields = [
            "id",
            "empleado",
            "empleado_nombre",
            "tipo",
            "descripcion",
            "monto",
            "fecha_inicio",
            "fecha_fin",
            "recurrente",
            "activo",
            "creado_en",
        ]
        read_only_fields = ["creado_en"]
