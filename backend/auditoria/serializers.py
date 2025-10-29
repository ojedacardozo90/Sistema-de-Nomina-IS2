from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    usuario_username = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ["id", "modelo", "objeto_id", "accion", "usuario", "usuario_username",
                  "cambios", "ip", "user_agent", "fecha"]

    def get_usuario_username(self, obj):
        return getattr(obj.usuario, "username", None)
