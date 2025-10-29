# backend/nomina_cal/models_envio.py
from django.db import models
from empleados.models import Empleado

class EnvioCorreo(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="envios_correo")
    asunto = models.CharField(max_length=200)
    destinatario = models.EmailField()
    estado = models.CharField(max_length=20, choices=[("enviado","enviado"),("error","error")])
    detalle_error = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.empleado} -> {self.destinatario} ({self.estado})"
