# backend/nomina_cal/views_export.py
# ============================================================
# 📤 EXPORTACIONES DE REPORTES (IS2 - Sistema de Nómina)
# ------------------------------------------------------------
# Genera reportes coherentes con los dashboards:
#   • PDF (resumen general de nómina)
#   • Excel (detalles por área y tipo de contrato)
# ============================================================

from django.http import HttpResponse
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from openpyxl import Workbook

from empleados.models import Empleado
from .models import Liquidacion

# ============================================================
# 🧾 EXPORTACIÓN A PDF
# ============================================================
class ExportPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hoy = timezone.now()
        mes = int(request.GET.get("mes", 0)) or hoy.month
        anio = int(request.GET.get("anio", 0)) or hoy.year

        # 🔹 Totales por área
        data = (
            Liquidacion.objects.filter(mes=mes, anio=anio)
            .values("empleado__area")
            .annotate(total=Sum("neto_cobrar"))
            .order_by("empleado__area")
        )

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="reporte_nomina_{mes}_{anio}.pdf"'

        pdf = canvas.Canvas(response, pagesize=A4)
        pdf.setTitle("Reporte de Nómina - FP-UNA / FAP")
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(2 * cm, 28 * cm, "Fuerza Aérea Paraguaya - Sistema de Nómina")
        pdf.setFont("Helvetica", 10)
        pdf.drawString(2 * cm, 27.4 * cm, f"Reporte consolidado de nómina ({mes}/{anio})")

        y = 26 * cm
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(2 * cm, y, "Área")
        pdf.drawString(9 * cm, y, "Total (Gs)")
        y -= 0.4 * cm
        pdf.line(2 * cm, y, 18 * cm, y)
        y -= 0.4 * cm

        pdf.setFont("Helvetica", 10)
        for row in data:
            pdf.drawString(2 * cm, y, row["empleado__area"] or "No especificado")
            pdf.drawRightString(17.5 * cm, y, f"{float(row['total'] or 0):,.2f}")
            y -= 0.4 * cm
            if y < 2 * cm:
                pdf.showPage()
                y = 28 * cm

        pdf.setFont("Helvetica-Oblique", 9)
        pdf.drawString(2 * cm, 1.8 * cm, f"Generado el {hoy.strftime('%d/%m/%Y %H:%M')}")
        pdf.save()
        return response


# ============================================================
# 📊 EXPORTACIÓN A EXCEL
# ============================================================
class ExportExcelView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hoy = timezone.now()
        mes = int(request.GET.get("mes", 0)) or hoy.month
        anio = int(request.GET.get("anio", 0)) or hoy.year

        # 🔹 Query coherente con dashboards
        qs = (
            Liquidacion.objects.filter(mes=mes, anio=anio)
            .values(
                "empleado__nombre",
                "empleado__apellido",
                "empleado__area",
                "empleado__tipo_contrato",
                "neto_cobrar",
            )
            .order_by("empleado__area", "empleado__apellido")
        )

        wb = Workbook()
        ws = wb.active
        ws.title = "Nómina"

        # 🧭 Encabezados
        ws.append(["Nombre", "Apellido", "Área", "Tipo Contrato", "Neto a Cobrar (Gs)"])

        for row in qs:
            ws.append([
                row["empleado__nombre"],
                row["empleado__apellido"],
                row["empleado__area"],
                row["empleado__tipo_contrato"],
                float(row["neto_cobrar"] or 0),
            ])

        filename = f"reporte_nomina_{mes}_{anio}.xlsx"
        response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename={filename}'
        wb.save(response)
        return response
from rest_framework.views import APIView
from rest_framework.response import Response

class ReciboPDFView(APIView):
    def get(self, request, pk):
        return Response({"ok": True, "mensaje": "Vista ReciboPDFView pendiente de implementación"})
# ============================================================
# 📄 VISTA TEMPORAL: ReciboPDFView (placeholder)
# ------------------------------------------------------------
# Esta vista solo evita errores hasta implementar la versión
# completa en utils_email.py con generar_recibo_pdf(liq)
# ============================================================

from rest_framework.views import APIView
from rest_framework.response import Response

class ReciboPDFView(APIView):
    def get(self, request, pk):
        return Response({
            "ok": True,
            "mensaje": f"ReciboPDFView pendiente de implementación (liquidación {pk})"
        })
