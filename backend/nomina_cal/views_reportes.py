# backend/nomina_cal/views_reportes.py
# ============================================================
# 📊 Reportes de Nómina — Sistema de Nómina IS2
# JSON (general), PDF y Excel
# ============================================================
from datetime import date
from decimal import Decimal
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import io, openpyxl
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

from .models import Liquidacion
from empleados.models import Empleado

# -----------------------------
# Utilidades
# -----------------------------
def _to_dec(x):
    try:
        return Decimal(x or 0)
    except Exception:
        return Decimal("0.00")

def _periodo_param(request):
    mes = int(request.GET.get("mes", date.today().month))
    anio = int(request.GET.get("anio", date.today().year))
    return mes, anio

# -----------------------------
# JSON: /api/nomina_cal/reportes/general/
# -----------------------------
@login_required
def reporte_general(request):
    mes, anio = _periodo_param(request)

    qs = Liquidacion.objects.filter(mes=mes, anio=anio)
    resumen = {
        "periodo": f"{mes}/{anio}",
        "total_empleados": Empleado.objects.filter(activo=True).count(),
        "total_neto": float(_to_dec(qs.aggregate(v=Sum("neto_cobrar"))["v"])),
        "total_descuentos": float(_to_dec(qs.aggregate(v=Sum("total_descuentos"))["v"])),
        "aporte_ips": float(_to_dec(
            qs.filter(detalles__concepto__descripcion__icontains="IPS")
              .aggregate(v=Sum("detalles__monto"))["v"]
        )),
    }

    # detalle básico para gráficos (puedes adaptar campos a tu frontend)
    detalle = list(
        qs.values("empleado__nombre", "empleado__apellido")
          .annotate(total_neto=Sum("neto_cobrar"))
          .order_by("-total_neto")
    )
    detalle = [
        {
            "empleado": f'{d["empleado__nombre"]} {d["empleado__apellido"]}',
            "total_neto": float(_to_dec(d["total_neto"])),
            "mes": mes,
        }
        for d in detalle
    ]

    return JsonResponse({"resumen": resumen, "detalle": detalle}, status=200)

# -----------------------------
# PDF: /api/nomina_cal/reportes/pdf/
# -----------------------------
@login_required
def reporte_pdf(request):
    mes, anio = _periodo_param(request)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    # Encabezado institucional
    titulo = "Sistema de Nómina IS2"
    subtitulo = f"Reporte de Liquidaciones — {mes}/{anio}"

    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, h - 50, titulo)
    p.setFont("Helvetica", 11)
    p.drawString(40, h - 70, subtitulo)
    p.line(40, h - 80, w - 40, h - 80)

    y = h - 110
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "Empleado")
    p.drawString(280, y, "Cédula")
    p.drawString(380, y, "Total Ingresos")
    p.drawString(480, y, "Descuentos")
    p.drawString(540, y, "Neto")
    y -= 18
    p.setFont("Helvetica", 10)

    qs = Liquidacion.objects.filter(mes=mes, anio=anio).select_related("empleado")
    total_neto = Decimal("0.00")
    for liq in qs:
        if y < 60:
            p.showPage()
            y = h - 50
        p.drawString(40, y, f"{liq.empleado.nombre} {liq.empleado.apellido}")
        p.drawString(280, y, f"{liq.empleado.cedula}")
        p.drawRightString(440, y, f"{float(liq.total_ingresos):,.0f} Gs")
        p.drawRightString(520, y, f"{float(liq.total_descuentos):,.0f} Gs")
        p.drawRightString(580, y, f"{float(liq.neto_cobrar):,.0f} Gs")
        total_neto += _to_dec(liq.neto_cobrar)
        y -= 16

    # Pie con total
    y -= 10
    p.line(40, y, w - 40, y)
    y -= 18
    p.setFont("Helvetica-Bold", 11)
    p.drawRightString(580, y, f"TOTAL NETO: {float(total_neto):,.0f} Gs")

    p.showPage()
    p.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="reporte_{mes}_{anio}.pdf"'
    return response

# -----------------------------
# Excel: /api/nomina_cal/reportes/excel/
# -----------------------------
@login_required
def reporte_excel(request):
    mes, anio = _periodo_param(request)
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"Nomina_{mes}_{anio}"
    ws.append(["Sistema de Nómina IS2"])
    ws.append([f"Reporte de Liquidaciones — {mes}/{anio}"])
    ws.append([])
    ws.append(["Empleado", "Cédula", "Total Ingresos", "Descuentos", "Neto"])

    qs = Liquidacion.objects.filter(mes=mes, anio=anio).select_related("empleado")
    total = Decimal("0.00")
    for liq in qs:
        ws.append([
            f"{liq.empleado.nombre} {liq.empleado.apellido}",
            liq.empleado.cedula,
            float(liq.total_ingresos or 0),
            float(liq.total_descuentos or 0),
            float(liq.neto_cobrar or 0),
        ])
        total += _to_dec(liq.neto_cobrar)

    ws.append([])
    ws.append(["", "", "", "TOTAL NETO", float(total)])

    bio = io.BytesIO()
    wb.save(bio)
    bio.seek(0)
    response = HttpResponse(
        bio.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="reporte_{mes}_{anio}.xlsx"'
    return response
