# ============================================================
# 🧮 Servicio de cálculo de nómina (bonificación, IPS, descuentos)
# Mantiene la lógica fuera de views/admin y evita importaciones circulares
# ============================================================

from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from nomina_cal.models import (
    Liquidacion,
    DetalleLiquidacion,
    Concepto,
    SalarioMinimo,
)
from empleados.models import Empleado
from nomina_cal.models_descuento import Descuento


# ============================================================
# 🔹 Funciones auxiliares
# ============================================================

def _edad_menor_18(fnac: date, ref: date) -> bool:
    """Calcula si la persona tiene menos de 18 años al momento de referencia."""
    edad = ref.year - fnac.year - ((ref.month, ref.day) < (fnac.month, fnac.day))
    return edad < 18


def _salario_minimo_vigente(fecha_ref: date) -> Decimal:
    """Obtiene el salario mínimo vigente a la fecha dada."""
    sm = SalarioMinimo.objects.filter(vigente_desde__lte=fecha_ref).order_by("-vigente_desde").first()
    return sm.monto if sm else Decimal("0.00")


# ============================================================
# 🔸 Cálculo principal del período
# ============================================================
@transaction.atomic
def calcular_liquidaciones_periodo(periodo) -> int:
    """
    Calcula TODAS las liquidaciones del período:
    - Sueldo base (imponible)
    - Bonificación por hijos válidos (no imponible, excluida IPS/aguinaldo)
    - IPS 9% sobre imponibles
    - Descuentos adicionales activos y vigentes
    Retorna la cantidad de liquidaciones recalculadas.
    """

    ref = date(periodo.anio, periodo.mes, 1)
    smm = _salario_minimo_vigente(ref)

    # ------------------------------------------------------------
    # Conceptos base del sistema
    # ------------------------------------------------------------
    c_sueldo, _ = Concepto.objects.get_or_create(
        descripcion="Sueldo Base",
        defaults={"es_debito": False, "afecta_ips": True, "para_aguinaldo": True, "es_recurrente": True},
    )
    c_bonif, _ = Concepto.objects.get_or_create(
        descripcion="Bonificación Familiar por Hijo",
        defaults={"es_debito": False, "afecta_ips": False, "para_aguinaldo": False, "es_recurrente": True},
    )
    c_ips, _ = Concepto.objects.get_or_create(
        descripcion="Descuento IPS 9%",
        defaults={"es_debito": True, "afecta_ips": True, "para_aguinaldo": False, "es_recurrente": True},
    )

    # ------------------------------------------------------------
    # Iterar empleados activos
    # ------------------------------------------------------------
    count = 0
    for emp in Empleado.objects.filter(activo=True):
        liq, _ = Liquidacion.objects.get_or_create(empleado=emp, mes=periodo.mes, anio=periodo.anio)

        if liq.cerrada:
            # Si la liquidación está cerrada, no se recalcula
            continue

        # Limpiar detalles anteriores para un recálculo limpio
        liq.detalles.all().delete()

        ingresos = Decimal(emp.salario_base or 0)
        descuentos = Decimal("0.00")

        # --------------------------------------------------------
        # Sueldo base
        # --------------------------------------------------------
        DetalleLiquidacion.objects.create(liquidacion=liq, concepto=c_sueldo, monto=emp.salario_base or 0)

        # --------------------------------------------------------
        # Bonificación familiar (tope 3 SMM; máx 4 hijos)
        # --------------------------------------------------------
        bonif_total = Decimal("0.00")

        if smm > 0 and (emp.salario_base or 0) <= smm * Decimal("3"):
            hijos_validos = []

            for h in emp.hijos.all():
                try:
                    # Compatibilidad con tu modelo Hijo
                    es_menor = h.es_menor() if hasattr(h, "es_menor") else _edad_menor_18(h.fecha_nacimiento, ref)
                    residente_ok = getattr(h, "residente", True)
                    residencia_vig = h.residencia_valida() if hasattr(h, "residencia_valida") else True
                    activo_ok = getattr(h, "activo", True)

                    # 🔧 corrección: condición compuesta con AND
                    if es_menor and residente_ok and residencia_vig and activo_ok:
                        hijos_validos.append(h)

                except Exception:
                    # fallback robusto en caso de errores
                    es_menor = _edad_menor_18(h.fecha_nacimiento, ref)
                    residente_ok = getattr(h, "residente", True)
                    residencia_vig = True
                    activo_ok = getattr(h, "activo", True)
                    if es_menor and residente_ok and residencia_vig and activo_ok:
                        hijos_validos.append(h)

            # máximo 4 hijos válidos
            hijos_validos = hijos_validos[:4]

            bonif_total = (
                smm * Decimal("0.05") * Decimal(len(hijos_validos))
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            if bonif_total > 0:
                DetalleLiquidacion.objects.create(liquidacion=liq, concepto=c_bonif, monto=bonif_total)
                ingresos += bonif_total

        # --------------------------------------------------------
        # IPS (9% del salario base)
        # --------------------------------------------------------
        desc_ips = ((emp.salario_base or 0) * Decimal("0.09")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        if desc_ips > 0:
            DetalleLiquidacion.objects.create(liquidacion=liq, concepto=c_ips, monto=desc_ips)
            descuentos += desc_ips

        # --------------------------------------------------------
        # Descuentos adicionales (vigentes)
        # --------------------------------------------------------
        for d in Descuento.objects.filter(empleado=emp, activo=True):
            if d.es_vigente(periodo.mes, periodo.anio):
                concepto_extra, _ = Concepto.objects.get_or_create(
                    descripcion=f"Descuento: {d.tipo.title()}",
                    defaults={"es_debito": True, "afecta_ips": False, "para_aguinaldo": False},
                )
                DetalleLiquidacion.objects.create(liquidacion=liq, concepto=concepto_extra, monto=d.monto)
                descuentos += d.monto

        # --------------------------------------------------------
        # Totales finales
        # --------------------------------------------------------
        liq.total_ingresos = ingresos
        liq.total_descuentos = descuentos
        liq.neto_cobrar = ingresos - descuentos
        liq.save(update_fields=["total_ingresos", "total_descuentos", "neto_cobrar"])

        count += 1

    return count
