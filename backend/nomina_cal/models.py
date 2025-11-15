#
# MODELOS DE NÓMINA (TP IS2 - Ingeniería de Software II)
# Cumple los requisitos de los Sprint 2–5 y la rúbrica final
#

from django.db import models
from django.conf import settings
from empleados.models import Empleado, Hijo
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum
from .models_descuento import Descuento
from .utils_email import generar_recibo_pdf




#
# # MODELO BASE DE AUDITORÍA
#
class AuditoriaModel(models.Model):
    
    """Registra trazabilidad de creación y modificación."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        related_name="%(class)s_created",
        on_delete=models.SET_NULL
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        related_name="%(class)s_updated",
        on_delete=models.SET_NULL
    )

    class Meta:
        abstract = True


#
# # SALARIO MÍNIMO HISTÓRICO
#
class SalarioMinimo(models.Model):
    """Registro histórico del salario mínimo vigente."""
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    vigente_desde = models.DateField(help_text="Fecha desde la cual rige este salario mínimo")
    vigente = models.BooleanField(default=True, help_text="Marca si es el salario actual vigente")

    class Meta:
        ordering = ["-vigente_desde"]

    def __str__(self):
        return f"{self.monto} Gs - vigente desde {self.vigente_desde}"

    @staticmethod
    def get_vigente(fecha=None):
        """
        Obtiene el salario mínimo vigente para una fecha dada.
        Se prioriza el registro con 'vigente=True' para evitar duplicidades.
        """
        if not fecha:
            fecha = date.today()
        vigente = (
            SalarioMinimo.objects
            .filter(vigente_desde__lte=fecha, vigente=True)
            .order_by("-vigente_desde")
            .first()
        )
        return vigente


#
# # CONCEPTO SALARIAL
#
class Concepto(AuditoriaModel):
    """Define un concepto salarial: crédito o débito."""
    descripcion = models.CharField(max_length=150, unique=True)
    es_debito = models.BooleanField(default=False, help_text="True = descuento, False = ingreso")
    es_recurrente = models.BooleanField(default=True)
    afecta_ips = models.BooleanField(default=True)
    para_aguinaldo = models.BooleanField(default=True)

    def __str__(self):
        tipo = "Débito" if self.es_debito else "Crédito"
        return f"{self.descripcion} ({tipo})"


#
# # LIQUIDACIÓN DE NÓMINA
#
class Liquidacion(AuditoriaModel):
    """
    Representa la liquidación mensual de un empleado.
    Incluye sueldo base, bonificación, IPS, descuentos y totales.
    """
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="liquidaciones")
    mes = models.IntegerField()  # 1–12
    anio = models.IntegerField()
    sueldo_base = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_ingresos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_descuentos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    neto_cobrar = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    cerrada = models.BooleanField(default=False)
    enviado_email = models.BooleanField(default=False, help_text="Indica si el recibo ya fue enviado por correo")
    fecha_envio = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("empleado", "mes", "anio")
        ordering = ["-anio", "-mes"]
        ordering = ["-anio", "-mes"]
        verbose_name = "Liquidación"
        verbose_name_plural = "Liquidaciones"

        
    def __str__(self):
        return f"Liquidación {self.mes}/{self.anio} - {self.empleado}"

    #
    # MÉTODO SAVE: validaciones automáticas
    #
    def save(self, *args, **kwargs):
        """
        Completa automáticamente el sueldo base al crear.
        Bloquea edición si la liquidación está cerrada.
        """
        if self.pk and self.cerrada:
            raise ValueError("No se puede modificar una liquidación cerrada.")
        if not (1 <= self.mes <= 12):
            raise ValueError("El campo 'mes' debe estar entre 1 y 12.")
        # calcular_totales():
        if self.enviado_email and not kwargs.get("force_update"):
            raise ValueError("No se puede recalcular una liquidación ya enviada.")
    
        if not self.sueldo_base or self.sueldo_base == 0:
            self.sueldo_base = self.empleado.salario_base or Decimal("0.00")
        super().save(*args, **kwargs)

    #
    #  BONIFICACIÓN FAMILIAR (Cumple MTESS)
    #
    def calcular_bonificacion_hijos(self):
        """
        Bonificación familiar conforme al MTESS (Código Laboral):
        - 5% del salario mínimo vigente por hijo menor de 18 años.
        - Hasta 4 hijos.
        - Solo si gana ≤ 3 salarios mínimos.
        - Solo hijos residentes en Paraguay con residencia vigente.
        """
        salario_minimo = SalarioMinimo.get_vigente(date(self.anio, self.mes, 1))
        
        if not salario_minimo:
            return Decimal("0.00")

        # # Tope legal: hasta 2 salarios mínimos (ajustado según MTESS)
        if self.sueldo_base > salario_minimo.monto * Decimal("3"):
            return Decimal("0.00")

        # # Filtrar hijos válidos según requisitos legales
        hijos_validos = [
            h for h in self.empleado.hijos.all()
            if h.es_menor() and h.residente and hasattr(h, "residencia_valida") and h.residencia_valida() and h.activo
        ][:4]  # Máximo 4 hijos

        bonificacion = salario_minimo.monto * Decimal("0.05") * Decimal(len(hijos_validos))
        return bonificacion.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    #
    #  CÁLCULO DE IPS Y TOTALES
    #
    def calcular_ips(self, imponible):
        """Calcula el aporte IPS del empleado (9%)."""
        return (imponible * Decimal("0.09")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calcular_totales(self):
        """
        Recalcula todos los totales de la liquidación:
        Sueldo, bonificación, IPS y descuentos adicionales.
        Aplica reglas del MTESS y bloquea recalculo si fue enviado.
        """
        if self.cerrada:
            raise ValueError("No se puede recalcular una liquidación cerrada.")
        if self.enviado_email:
            raise ValueError("No se puede recalcular una liquidación ya enviada por correo.")

        # Eliminar detalles previos para regenerar el cálculo
        self.detalles.all().delete()

        ingresos = Decimal(self.sueldo_base)
        descuentos = Decimal("0.00")

        
        #  Sueldo Base
        
        concepto_base, _ = Concepto.objects.get_or_create(
            descripcion="Sueldo Base",
            defaults={"es_debito": False, "afecta_ips": True, "para_aguinaldo": True},
        )
        DetalleLiquidacion.objects.create(liquidacion=self, concepto=concepto_base, monto=self.sueldo_base)

        
        #  Bonificación Familiar (MTESS)
        
        bonificacion = self.calcular_bonificacion_hijos()
        if bonificacion > 0:
            concepto_bono, _ = Concepto.objects.get_or_create(
                descripcion="Bonificación Familiar",
                defaults={"es_debito": False, "afecta_ips": False, "para_aguinaldo": False},
            )
            DetalleLiquidacion.objects.create(liquidacion=self, concepto=concepto_bono, monto=bonificacion)
            ingresos += bonificacion

        
        #  Descuento IPS (9%)
        
        descuento_ips = self.calcular_ips(self.sueldo_base)
        concepto_ips, _ = Concepto.objects.get_or_create(
            descripcion="Descuento IPS 9%",
            defaults={"es_debito": True, "afecta_ips": False, "para_aguinaldo": False},
        )
        DetalleLiquidacion.objects.create(liquidacion=self, concepto=concepto_ips, monto=descuento_ips)
        descuentos += descuento_ips

        
        #  Descuentos adicionales (Préstamos, embargos, etc.)
        
        descuentos_extra = Descuento.objects.filter(empleado=self.empleado, activo=True)
        for d in descuentos_extra:
            if d.es_vigente(self.mes, self.anio):
                concepto_extra, _ = Concepto.objects.get_or_create(
                    descripcion=f"Descuento: {d.tipo.title()}",
                    defaults={"es_debito": True, "afecta_ips": False, "para_aguinaldo": False},
                )
                DetalleLiquidacion.objects.create(liquidacion=self, concepto=concepto_extra, monto=d.monto)
                descuentos += d.monto

        
        #  Totales finales
        
        self.total_ingresos = ingresos
        self.total_descuentos = descuentos
        self.neto_cobrar = ingresos - descuentos
        self.save(update_fields=["total_ingresos", "total_descuentos", "neto_cobrar"])

        # Log informativo
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[OK] Liquidación recalculada {self.mes}/{self.anio} → Neto: {self.neto_cobrar} Gs")

        return self.neto_cobrar

    def cerrar(self):
        """Bloquea la edición de la liquidación.
        (El envío del recibo ahora se realiza vía EnviarReciboView por API.)
        """
        self.cerrada = True
        self.save(update_fields=["cerrada"])

            

    @property
    def neto(self):
        """Acceso rápido al neto."""
        return self.neto_cobrar
#
# # DETALLE DE LIQUIDACIÓN
#
class DetalleLiquidacion(AuditoriaModel):
    """Cada concepto aplicado en una liquidación."""
    liquidacion = models.ForeignKey(
        'Liquidacion',
        on_delete=models.CASCADE,
        related_name="detalles"
    )
    concepto = models.ForeignKey(
        'Concepto',
        on_delete=models.PROTECT
    )
    monto = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.liquidacion} - {self.concepto.descripcion}: {self.monto:,.0f} Gs"
