from django.db import models
from datetime import datetime, time, timedelta
from empleados.models import Empleado

class Fichada(models.Model):
    """Registro de entrada/salida puntual (marca individual)."""
    TIPO = [
        ("entrada", "Entrada"),
        ("salida", "Salida"),
    ]

    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="fichadas")
    tipo = models.CharField(max_length=10, choices=TIPO)
    timestamp = models.DateTimeField(auto_now_add=True)
    origen = models.CharField(max_length=50, default="manual")  # manual, web, reloj, etc.

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.empleado} - {self.tipo} - {self.timestamp:%d/%m/%Y %H:%M}"


class RegistroAsistencia(models.Model):
    """Resumen diario de asistencia del empleado."""
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="asistencias")
    fecha = models.DateField()
    hora_entrada = models.TimeField(null=True, blank=True)
    hora_salida = models.TimeField(null=True, blank=True)
    minutos_trabajados = models.IntegerField(default=0)
    estado = models.CharField(max_length=15, default="presente")  # presente, ausencia, tardanza, incompleto
    justificacion = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        unique_together = ("empleado", "fecha")
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.empleado} - {self.fecha} - {self.estado}"

    def recalcular(self, entrada_esperada=time(8, 0), tolerancia_min=15):
        """
        Recalcula minutos trabajados y estado.
        Jornada 8h (480 min), tolerancia 15 min.
        """
        if self.hora_entrada and self.hora_salida:
            e_dt = datetime.combine(self.fecha, self.hora_entrada)
            s_dt = datetime.combine(self.fecha, self.hora_salida)
            self.minutos_trabajados = max(0, int((s_dt - e_dt).total_seconds() // 60))

            limite_tardanza = (datetime.combine(self.fecha, entrada_esperada)
                               + timedelta(minutes=tolerancia_min)).time()
            self.estado = "tardanza" if self.hora_entrada > limite_tardanza else "presente"
        else:
            if not self.hora_entrada and not self.hora_salida:
                self.estado = "ausencia"
            else:
                self.estado = "incompleto"

        self.save(update_fields=["minutos_trabajados", "estado"])
