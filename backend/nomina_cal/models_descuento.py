# backend/nomina_cal/models_descuento.py
#
#  MODELO DE DESCUENTOS Y DÉBITOS (TP IS2 - Ingeniería de Software II)
#

from django.db import models
from django.conf import settings
from datetime import date
from decimal import Decimal
from empleados.models import Empleado


#
# # MODELO: Descuento
#
class Descuento(models.Model):
    """
    Representa un descuento aplicado a un empleado:
    - Puede ser puntual o recurrente.
    - Aplica en un rango de fechas (fecha_inicio, fecha_fin).
    - Se usa durante el cálculo de la liquidación mensual.
    """

    TIPOS_DESCUENTO = [
        ("prestamo", "Préstamo"),
        ("embargo", "Embargo Judicial"),
        ("ausencia", "Ausencia"),
        ("retencion", "Retención Sindical"),
        ("otro", "Otro Descuento"),
    ]

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name="descuentos",
        help_text="Empleado al que se aplica el descuento",
    )
    tipo = models.CharField(max_length=50, choices=TIPOS_DESCUENTO, default="otro")
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    monto = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    recurrente = models.BooleanField(default=False, help_text="Se aplica automáticamente cada mes")
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="descuentos_creados"
    )

    class Meta:
        ordering = ["-fecha_inicio"]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.empleado.nombre} ({self.monto} Gs)"

    
    #  MÉTODOS DE LÓGICA DE NEGOCIO
    
    def es_vigente(self, mes, anio):
        """
        Determina si el descuento aplica para el mes/año actual.
        Tiene en cuenta la fecha de inicio y fin, y si está activo.
        """
        if not self.activo:
            return False

        # Calcular primer y último día del mes de la liquidación
        fecha_ini_liq = date(anio, mes, 1)
        if mes == 12:
            fecha_fin_liq = date(anio + 1, 1, 1)
        else:
            fecha_fin_liq = date(anio, mes + 1, 1)

        # Descuento puntual
        if not self.recurrente:
            return self.fecha_inicio >= fecha_ini_liq and (
                not self.fecha_fin or self.fecha_fin < fecha_fin_liq
            )

        # Descuento recurrente
        if self.recurrente:
            if self.fecha_fin:
                return self.fecha_inicio <= fecha_fin_liq and self.fecha_fin >= fecha_ini_liq
            else:
                return self.fecha_inicio <= fecha_fin_liq

        return False

    def aplicar(self, liquidacion):
        """
        Aplica el descuento a una liquidación si está vigente.
        """
        from .models import Concepto, DetalleLiquidacion

        if not self.es_vigente(liquidacion.mes, liquidacion.anio):
            return

        concepto_extra, _ = Concepto.objects.get_or_create(
            descripcion=f"Descuento: {self.get_tipo_display()}",
            defaults={
                "es_debito": True,
                "es_recurrente": self.recurrente,
                "afecta_ips": False,
                "para_aguinaldo": False,
            },
        )

        DetalleLiquidacion.objects.create(
            liquidacion=liquidacion,
            concepto=concepto_extra,
            monto=self.monto,
        )

    def desactivar(self):
        """Desactiva manualmente el descuento."""
        self.activo = False
        self.save(update_fields=["activo"])

    def reactivar(self):
        """Reactiva el descuento."""
        self.activo = True
        self.save(update_fields=["activo"])
