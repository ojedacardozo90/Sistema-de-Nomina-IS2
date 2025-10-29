# backend/empleados/serializers.py
# ============================================================
# 🎯 Serializadores de Empleados e Hijos (TP IS2 - Nómina)
# ============================================================

from rest_framework import serializers
from .models import Empleado, Hijo


# ============================================================
# 🔹 SERIALIZER: Hijo
# ============================================================
class HijoSerializer(serializers.ModelSerializer):
    edad = serializers.SerializerMethodField()
    es_menor = serializers.SerializerMethodField()

    class Meta:
        model = Hijo
        fields = [
            "id",
            "empleado",
            "nombre",
            "fecha_nacimiento",
            "residente",
            "certificado_nacimiento",
            "activo",
            "edad",
            "es_menor",
        ]
        read_only_fields = ["edad", "es_menor"]

    def get_edad(self, obj):
        return obj.edad()

    def get_es_menor(self, obj):
        return obj.es_menor()


# ============================================================
# 🔹 SERIALIZER: Empleado
# ============================================================
class EmpleadoSerializer(serializers.ModelSerializer):
    hijos = HijoSerializer(many=True, read_only=True)
    antiguedad = serializers.SerializerMethodField()

    class Meta:
        model = Empleado
        fields = [
            "id",
            "usuario",
            "nombre",
            "apellido",
            "cedula",
            "fecha_ingreso",
            "cargo",
            "salario_base",
            "telefono",
            "email",
            "direccion",
            "activo",
            "antiguedad",
            "hijos",
        ]
        read_only_fields = ["antiguedad", "hijos"]

    def get_antiguedad(self, obj):
        return obj.antiguedad

    def validate_salario_base(self, value):
        if value < 0:
            raise serializers.ValidationError("El salario base no puede ser negativo.")
        return value
