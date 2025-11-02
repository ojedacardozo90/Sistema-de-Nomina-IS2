# backend/nomina_cal/views_analytics.py
# ============================================================
# 📊 MÓDULO: Vistas de Análisis y KPI (IS2 - Sistema de Nómina)
# ------------------------------------------------------------
# Este módulo provee indicadores estadísticos y analíticos
# para los dashboards de RRHH:
#   • KPI globales por mes/año (kpis_resumen)
#   • Serie temporal de nómina (serie_nomina_ultimos_6)
#   • Ranking de descuentos por concepto (top_descuentos_por_concepto)
#   • Distribución por área y tipo de contrato (Sprint 6)
# ------------------------------------------------------------
# Sprint 5–6 — FP-UNA / Fuerza Aérea Paraguaya
# ============================================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from datetime import date

# 🔹 Modelos base
from empleados.models import Empleado
from .models import Liquidacion, DetalleLiquidacion, Concepto


# ============================================================
# 📈 FUNCIÓN: KPIs Resumen general
# ------------------------------------------------------------
# Endpoint: /nomina_cal/analytics/kpis/
# Método:   GET
# Descripción:
#   Devuelve indicadores cuantitativos principales:
#     - Total de empleados activos
#     - Total de nómina mensual
#     - Total de descuentos del mes
#     - Total de aportes IPS
# ============================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def kpis_resumen(request):
    # 🗓️ Determinar mes y año a consultar (por defecto, mes actual)
    hoy = date.today()
    mes = int(request.GET.get("mes", hoy.month))
    anio = int(request.GET.get("anio", hoy.year))

    # 👥 Total de empleados activos
    empleados_activos = Empleado.objects.filter(activo=True).count()

    # 💵 Totales generales del mes
    liqs_mes = Liquidacion.objects.filter(mes=mes, anio=anio)
    total_nomina_mes = liqs_mes.aggregate(s=Sum("neto_cobrar")).get("s", 0) or 0
    total_descuentos_mes = liqs_mes.aggregate(s=Sum("total_descuentos")).get("s", 0) or 0

    # 🧮 Cálculo de IPS — búsqueda por nombre o código del concepto
    total_ips_mes = (
        DetalleLiquidacion.objects.filter(
            liquidacion__mes=mes,
            liquidacion__anio=anio
        )
        .filter(
            Q(concepto__descripcion__icontains="IPS")
            # | Q(concepto__codigo__icontains="IPS")  # ⚠️ activar si existe 'codigo' en Concepto
        )
        .aggregate(s=Sum("monto"))
        .get("s", 0)
        or 0
    )

    # 📤 Respuesta final (JSON)
    return Response({
        "empleados_activos": empleados_activos,
        "total_nomina_mes": float(total_nomina_mes),
        "total_descuentos_mes": float(total_descuentos_mes),
        "total_ips_mes": float(total_ips_mes),
        "mes": mes,
        "anio": anio,
    })


# ============================================================
# 📉 FUNCIÓN: Serie temporal (últimos 6 meses)
# ------------------------------------------------------------
# Endpoint: /nomina_cal/analytics/serie6/
# Método:   GET
# Descripción:
#   Devuelve la evolución del neto total pagado
#   en los últimos seis meses consecutivos.
# ============================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def serie_nomina_ultimos_6(request):
    hoy = date.today()
    datos = []
    m = hoy.month
    a = hoy.year

    # 🔄 Recorremos los 6 meses hacia atrás
    for _ in range(6):
        total = (
            Liquidacion.objects.filter(mes=m, anio=a)
            .aggregate(s=Sum("neto_cobrar"))
            .get("s", 0) or 0
        )

        datos.append({
            "mes": m,
            "anio": a,
            "neto_total": float(total)
        })

        # Retroceder un mes en el calendario
        m -= 1
        if m == 0:
            m = 12
            a -= 1

    # 🔁 Invertir la lista para orden ascendente (más antiguo → reciente)
    datos.reverse()
    return Response(datos)


# ============================================================
# 💸 FUNCIÓN: Top descuentos por concepto
# ------------------------------------------------------------
# Endpoint: /nomina_cal/analytics/top-descuentos/
# Método:   GET
# Descripción:
#   Devuelve los 5 conceptos con mayor monto de descuento
#   del mes/año actual (para gráficos de ranking).
# ============================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def top_descuentos_por_concepto(request):
    hoy = date.today()
    mes = int(request.GET.get("mes", hoy.month))
    anio = int(request.GET.get("anio", hoy.year))

    # 🧾 Agrupar por concepto con totales y cantidad de ítems
    rows = (
        DetalleLiquidacion.objects.filter(
            liquidacion__mes=mes,
            liquidacion__anio=anio,
            concepto__es_debito=True
        )
        .values("concepto__descripcion")
        .annotate(total=Sum("monto"), items=Count("id"))
        .order_by("-total")[:5]
    )

    # 🧩 Transformar resultado a lista JSON
    data = [
        {
            "concepto": r["concepto__descripcion"],
            "total": float(r["total"] or 0),
            "items": r["items"],
        }
        for r in rows
    ]

    return Response(data)


# ============================================================
# 🧭 FUNCIÓN: Distribución por área
# ------------------------------------------------------------
# Endpoint: /nomina_cal/analytics/distribucion-area/
# Método:   GET
# Descripción:
#   Devuelve la distribución de los costos de nómina
#   agrupados por área o departamento.
# ============================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def distribucion_por_area(request):
    mes = int(request.GET.get("mes", 0)) or None
    anio = int(request.GET.get("anio", 0)) or None

    qs = Liquidacion.objects.all()
    if mes:
        qs = qs.filter(mes=mes)
    if anio:
        qs = qs.filter(anio=anio)

    # 🔗 Join con empleado → área
    data = (
        qs.values("empleado__area")
        .annotate(total=Sum("neto_cobrar"))
        .order_by("-total")
    )
    return Response({"series": list(data)})


# ============================================================
# 🧭 FUNCIÓN: Distribución por tipo de contrato
# ------------------------------------------------------------
# Endpoint: /nomina_cal/analytics/distribucion-contrato/
# Método:   GET
# Descripción:
#   Devuelve la distribución de los costos de nómina
#   agrupados por tipo de contrato.
# ============================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def distribucion_por_tipo_contrato(request):
    mes = int(request.GET.get("mes", 0)) or None
    anio = int(request.GET.get("anio", 0)) or None

    qs = Liquidacion.objects.all()
    if mes:
        qs = qs.filter(mes=mes)
    if anio:
        qs = qs.filter(anio=anio)

    data = (
        qs.values("empleado__tipo_contrato")
        .annotate(total=Sum("neto_cobrar"))
        .order_by("-total")
    )
    return Response({"series": list(data)})
# backend/nomina_cal/views_analytics.py
# ============================================================
# 📊 MÓDULO: Vistas de Análisis y KPI (IS2 - Sistema de Nómina)
# ------------------------------------------------------------
# Este módulo provee indicadores estadísticos y analíticos
# para los dashboards de RRHH y Administración:
#   • KPI globales por mes/año (kpis_resumen)
#   • Serie temporal (últimos 6 meses)
#   • Ranking de descuentos
#   • Distribución por área / contrato
#   • Gráfico simple (chart_data) para iframe o frontend directo
# ------------------------------------------------------------
# Sprints 5–6 — FP-UNA / Fuerza Aérea Paraguaya
# ============================================================

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from datetime import date

# 🔹 Modelos base
from empleados.models import Empleado
from .models import Liquidacion, DetalleLiquidacion, Concepto


# ============================================================
# 📈 FUNCIÓN: KPIs Resumen general
# Endpoint: /nomina_cal/analytics/kpis/
# ============================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def kpis_resumen(request):
    hoy = date.today()
    mes = int(request.GET.get("mes", hoy.month))
    anio = int(request.GET.get("anio", hoy.year))

    empleados_activos = Empleado.objects.filter(activo=True).count()

    liqs_mes = Liquidacion.objects.filter(mes=mes, anio=anio)
    total_nomina_mes = liqs_mes.aggregate(s=Sum("neto_cobrar")).get("s", 0) or 0
    total_descuentos_mes = liqs_mes.aggregate(s=Sum("total_descuentos")).get("s", 0) or 0

    total_ips_mes = (
        DetalleLiquidacion.objects.filter(
            liquidacion__mes=mes,
            liquidacion__anio=anio
        )
        .filter(Q(concepto__descripcion__icontains="IPS"))
        .aggregate(s=Sum("monto"))
        .get("s", 0)
        or 0
    )

    return Response({
        "empleados_activos": empleados_activos,
        "total_nomina_mes": float(total_nomina_mes),
        "total_descuentos_mes": float(total_descuentos_mes),
        "total_ips_mes": float(total_ips_mes),
        "mes": mes,
        "anio": anio,
        "kpis": {  # ✅ para compatibilidad con tu frontend actual
            "total_general": float(total_nomina_mes),
            "promedio_neto": round(total_nomina_mes / empleados_activos, 2) if empleados_activos else 0,
            "total_empleados": empleados_activos,
        },
        "evolucion": list(Liquidacion.objects.values("mes").annotate(total=Sum("neto_cobrar")).order_by("mes")),
    })


# ============================================================
# 📉 FUNCIÓN: Serie temporal (últimos 6 meses)
# Endpoint: /nomina_cal/analytics/serie6/
# ============================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def serie_nomina_ultimos_6(request):
    hoy = date.today()
    datos = []
    m, a = hoy.month, hoy.year

    for _ in range(6):
        total = (
            Liquidacion.objects.filter(mes=m, anio=a)
            .aggregate(s=Sum("neto_cobrar"))
            .get("s", 0) or 0
        )
        datos.append({"mes": m, "anio": a, "neto_total": float(total)})
        m -= 1
        if m == 0:
            m = 12
            a -= 1

    datos.reverse()
    return Response(datos)


# ============================================================
# 💸 FUNCIÓN: Top descuentos por concepto
# Endpoint: /nomina_cal/analytics/top-descuentos/
# ============================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def top_descuentos_por_concepto(request):
    hoy = date.today()
    mes = int(request.GET.get("mes", hoy.month))
    anio = int(request.GET.get("anio", hoy.year))

    rows = (
        DetalleLiquidacion.objects.filter(
            liquidacion__mes=mes,
            liquidacion__anio=anio,
            concepto__es_debito=True
        )
        .values("concepto__descripcion")
        .annotate(total=Sum("monto"), items=Count("id"))
        .order_by("-total")[:5]
    )

    data = [
        {
            "concepto": r["concepto__descripcion"],
            "total": float(r["total"] or 0),
            "items": r["items"],
        }
        for r in rows
    ]
    return Response(data)


# ============================================================
# 🧭 FUNCIÓN: Distribución por área
# Endpoint: /nomina_cal/analytics/distribucion-area/
# ============================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def distribucion_por_area(request):
    mes = int(request.GET.get("mes", 0)) or None
    anio = int(request.GET.get("anio", 0)) or None

    qs = Liquidacion.objects.all()
    if mes:
        qs = qs.filter(mes=mes)
    if anio:
        qs = qs.filter(anio=anio)

    data = (
        qs.values("empleado__area")
        .annotate(total=Sum("neto_cobrar"))
        .order_by("-total")
    )
    return Response({"series": list(data)})


# ============================================================
# 🧭 FUNCIÓN: Distribución por tipo de contrato
# Endpoint: /nomina_cal/analytics/distribucion-contrato/
# ============================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def distribucion_por_tipo_contrato(request):
    mes = int(request.GET.get("mes", 0)) or None
    anio = int(request.GET.get("anio", 0)) or None

    qs = Liquidacion.objects.all()
    if mes:
        qs = qs.filter(mes=mes)
    if anio:
        qs = qs.filter(anio=anio)

    data = (
        qs.values("empleado__tipo_contrato")
        .annotate(total=Sum("neto_cobrar"))
        .order_by("-total")
    )
    return Response({"series": list(data)})


# ============================================================
# 📊 FUNCIÓN: Datos para gráfico embebido (iframe o Chart.js)
# Endpoint: /nomina_cal/analytics/chart/
# ------------------------------------------------------------
# Usado por el Dashboard Admin (iframe o gráfico externo)
# ============================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chart_data(request):
    data = (
        Liquidacion.objects.values("mes")
        .annotate(total=Sum("neto_cobrar"))
        .order_by("mes")
    )
    return Response(list(data))
