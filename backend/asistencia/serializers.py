from rest_framework import serializers
from .models import Fichada, RegistroAsistencia

class FichadaSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source="empleado.nombre", read_only=True)

    class Meta:
        model = Fichada
        fields = ["id", "empleado", "empleado_nombre", "tipo", "timestamp", "origen"]
        read_only_fields = ["timestamp"]


class RegistroAsistenciaSerializer(serializers.ModelSerializer):
    empleado_nombre = serializers.CharField(source="empleado.nombre", read_only=True)

    class Meta:
        model = RegistroAsistencia
        fields = [
            "id", "empleado", "empleado_nombre", "fecha",
            "hora_entrada", "hora_salida", "minutos_trabajados",
            "estado", "justificacion"
        ]
        read_only_fields = ["minutos_trabajados", "estado"]
