from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    ACCION_CHOICES = (
        ("create", "CREATE"),
        ("update", "UPDATE"),
        ("delete", "DELETE"),
    )

    modelo = models.CharField(max_length=120)             # e.g. "Empleado", "Liquidacion"
    objeto_id = models.CharField(max_length=64)           # pk como string para uniformidad
    accion = models.CharField(max_length=10, choices=ACCION_CHOICES)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                on_delete=models.SET_NULL, related_name="audits")
    cambios = models.JSONField(default=dict, blank=True)  # diff o snapshot
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

class Meta:
        ordering = ["-fecha"]
        indexes = [
            models.Index(fields=["modelo", "accion", "fecha"]),
        ]

def __str__(self):
        return f"[{self.fecha:%Y-%m-%d %H:%M}] {self.modelo}({self.objeto_id}) {self.accion}"
