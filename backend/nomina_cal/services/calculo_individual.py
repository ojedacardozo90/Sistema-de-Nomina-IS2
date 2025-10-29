from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from nomina_cal.models import Concepto, SalarioMinimo, DetalleLiquidacion
from nomina_cal.models_descuento import Descuento
import logging

logger = logging.getLogger(__name__)

def calcular_liquidacion(liquidacion):
    empleado = liquidacion.empleado
    salario_base = empleado.salario_base or Decimal("0.00")
    if salario_base <= 0:
        raise ValueError(f"El empleado {empleado} no tiene salario base asignado.")

    salario_minimo = SalarioMinimo.get_vigente(date(liquidacion.anio, liquidacion.mes, 1))
    if not salario_minimo:
        raise ValueError("No existe salario mínimo vigente para la fecha indicada.")

    liquidacion.detalles.all().delete()
    total_ingresos = Decimal("0.00")
    total_descuentos = Decimal("0.00")

    concepto_base, _ = Concepto.objects.get_or_create(
        descripcion="Sueldo Base",
        defaults={"es_debito": False, "es_recurrente": True, "afecta_ips": True, "para_aguinaldo": True},
    )
    DetalleLiquidacion.objects.create(liquidacion=liquidacion, concepto=concepto_base, monto=salario_base)
    total_ingresos += salario_base

    bonificacion = liquidacion.calcular_bonificacion_hijos()
    if bonificacion > 0:
        concepto_bono, _ = Concepto.objects.get_or_create(
            descripcion="Bonificación Familiar por Hijo",
            defaults={"es_debito": False, "es_recurrente": True, "afecta_ips": False, "para_aguinaldo": False},
        )
        DetalleLiquidacion.objects.create(liquidacion=liquidacion, concepto=concepto_bono, monto=bonificacion)
        total_ingresos += bonificacion

    ips = liquidacion.calcular_ips(salario_base).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    concepto_ips, _ = Concepto.objects.get_or_create(
        descripcion="Descuento IPS 9%",
        defaults={"es_debito": True, "es_recurrente": True, "afecta_ips": True, "para_aguinaldo": False},
    )
    DetalleLiquidacion.objects.create(liquidacion=liquidacion, concepto=concepto_ips, monto=ips)
    total_descuentos += ips

    descuentos_extra = Descuento.objects.filter(empleado=empleado, activo=True)
    for d in descuentos_extra:
        if d.es_vigente(liquidacion.mes, liquidacion.anio):
            concepto_extra, _ = Concepto.objects.get_or_create(
                descripcion=f"Descuento: {d.tipo.title()}",
                defaults={"es_debito": True, "es_recurrente": d.recurrente, "afecta_ips": False, "para_aguinaldo": False},
            )
            DetalleLiquidacion.objects.create(liquidacion=liquidacion, concepto=concepto_extra, monto=d.monto)
            total_descuentos += d.monto

    aguinaldo = (salario_base / Decimal("12")).quantize(Decimal("0.01"))
    vacaciones = (salario_base * Decimal("0.04")).quantize(Decimal("0.01"))
    for desc, monto in [("Aguinaldo Proporcional", aguinaldo), ("Vacaciones Proporcionales", vacaciones)]:
        if monto > 0:
            concepto, _ = Concepto.objects.get_or_create(
                descripcion=desc,
                defaults={"es_debito": False, "es_recurrente": True, "afecta_ips": False, "para_aguinaldo": (desc == "Aguinaldo Proporcional")},
            )
            DetalleLiquidacion.objects.create(liquidacion=liquidacion, concepto=concepto, monto=monto)
            total_ingresos += monto

    liquidacion.total_ingresos = total_ingresos
    liquidacion.total_descuentos = total_descuentos
    liquidacion.neto_cobrar = total_ingresos - total_descuentos
    liquidacion.updated_at = datetime.now()
    liquidacion.save()
    liquidacion.refresh_from_db()
    logger.info(f"✅ Liquidación recalculada: {empleado} | Neto={liquidacion.neto_cobrar}")
    return liquidacion
