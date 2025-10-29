from datetime import date
from decimal import Decimal
from .models import RegistroAsistencia
from nomina_cal.models_descuento import Descuento

def aplicar_descuento_ausencias(empleado, mes, anio, monto_por_ausencia=Decimal("50000")):
    """
    Crea un Descuento acumulado por todas las 'ausencias' del mes.
    Evita crear duplicados si ya existe uno.
    """
    ausencias = RegistroAsistencia.objects.filter(
        empleado=empleado, fecha__year=anio, fecha__month=mes, estado="ausencia"
    ).count()

    if ausencias == 0:
        return 0

    # Evita duplicar descuentos del mismo tipo y mes
    if Descuento.objects.filter(empleado=empleado, tipo="ausencia", fecha_inicio__year=anio, fecha_inicio__month=mes).exists():
        return ausencias

    total = monto_por_ausencia * ausencias
    Descuento.objects.create(
        empleado=empleado,
        tipo="ausencia",
        descripcion=f"Ausencias {mes}/{anio} ({ausencias})",
        monto=total,
        fecha_inicio=date(anio, mes, 1),
        recurrente=False,
        activo=True,
    )
    return ausencias
