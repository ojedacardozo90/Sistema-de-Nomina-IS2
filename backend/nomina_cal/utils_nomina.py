#
#  UTILIDADES DE CÁLCULO DE NÓMINA
# Proyecto: Sistema de Nómina (IS2 - FP-UNA)
# Autor: Raúl Catalino Irala Benítez
# Cumple con el Código Laboral Paraguayo y requisitos MTESS
#

from decimal import Decimal, ROUND_HALF_UP
from datetime import date

#
# # BONIFICACIÓN FAMILIAR (MTESS)
#
def calcular_bonificacion_familiar(empleado, mes, anio):
    """
    Calcula la bonificación familiar conforme a las normativas vigentes:
    - 5 % del salario mínimo legal por cada hijo menor de 18 años.
    - Hasta un máximo de 4 hijos válidos.
    - Solo si el empleado percibe hasta 2 salarios mínimos.
    - Solo hijos residentes en Paraguay con vida y residencia vigentes.
    """
    from nomina_cal.models import SalarioMinimo  # Import local (evita circular import)

    salario_minimo = SalarioMinimo.get_vigente(date(anio, mes, 1))
    if not salario_minimo:
        return Decimal("0.00")

    # Límite de 2 salarios mínimos
    if empleado.salario_base > salario_minimo.monto * Decimal("2"):
        return Decimal("0.00")

    # Selección de hijos válidos
    hijos_validos = [
        h for h in empleado.hijos.all()
        if h.es_menor() and h.residente and h.residencia_valida() and h.activo
    ][:4]

    bonificacion = salario_minimo.monto * Decimal("0.05") * Decimal(len(hijos_validos))
    return bonificacion.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


#
# # CÁLCULO DE APORTES AL IPS (9 %)
#
def calcular_ips(monto_imponible):
    """Calcula el aporte del 9 % al IPS sobre el total imponible."""
    return (monto_imponible * Decimal("0.09")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


#
# # RECÁLCULO TOTAL DE LIQUIDACIÓN
#
def recalcular_totales(liquidacion):
    """
    Recalcula todos los totales de la liquidación:
    - Sueldo base
    - Bonificación familiar
    - Aportes al IPS
    - Descuentos adicionales
    """
    from nomina_cal.models import Concepto, DetalleLiquidacion
    from nomina_cal.models_descuento import Descuento  # Import local

    if liquidacion.cerrada:
        raise ValueError("No se puede recalcular una liquidación cerrada.")

    # Limpia los detalles anteriores
    DetalleLiquidacion.objects.filter(liquidacion=liquidacion).delete()

    ingresos = Decimal(liquidacion.sueldo_base)
    descuentos = Decimal("0.00")

    # --- Sueldo Base ---
    concepto_base, _ = Concepto.objects.get_or_create(
        descripcion="Sueldo Base",
        defaults={"es_debito": False, "afecta_ips": True, "para_aguinaldo": True},
    )
    DetalleLiquidacion.objects.create(liquidacion=liquidacion, concepto=concepto_base, monto=liquidacion.sueldo_base)

    # --- Bonificación Familiar ---
    bonificacion = calcular_bonificacion_familiar(liquidacion.empleado, liquidacion.mes, liquidacion.anio)
    if bonificacion > 0:
        concepto_bono, _ = Concepto.objects.get_or_create(
            descripcion="Bonificación Familiar",
            defaults={"es_debito": False, "afecta_ips": False, "para_aguinaldo": False},
        )
        DetalleLiquidacion.objects.create(liquidacion=liquidacion, concepto=concepto_bono, monto=bonificacion)
        ingresos += bonificacion

    # --- Aporte IPS (9 %) ---
    descuento_ips = calcular_ips(liquidacion.sueldo_base)
    concepto_ips, _ = Concepto.objects.get_or_create(
        descripcion="Descuento IPS 9%",
        defaults={"es_debito": True, "afecta_ips": True, "para_aguinaldo": False},
    )
    DetalleLiquidacion.objects.create(liquidacion=liquidacion, concepto=concepto_ips, monto=descuento_ips)
    descuentos += descuento_ips

    # --- Descuentos adicionales (embargos, préstamos, etc.) ---
    descuentos_extra = Descuento.objects.filter(empleado=liquidacion.empleado, activo=True)
    for d in descuentos_extra:
        if d.es_vigente(liquidacion.mes, liquidacion.anio):
            concepto_extra, _ = Concepto.objects.get_or_create(
                descripcion=f"Descuento: {d.tipo.title()}",
                defaults={"es_debito": True, "afecta_ips": False, "para_aguinaldo": False},
            )
            DetalleLiquidacion.objects.create(liquidacion=liquidacion, concepto=concepto_extra, monto=d.monto)
            descuentos += d.monto

    # --- Totales finales ---
    liquidacion.total_ingresos = ingresos
    liquidacion.total_descuentos = descuentos
    liquidacion.neto_cobrar = ingresos - descuentos
    liquidacion.save(update_fields=["total_ingresos", "total_descuentos", "neto_cobrar"])

    return liquidacion.neto_cobrar
