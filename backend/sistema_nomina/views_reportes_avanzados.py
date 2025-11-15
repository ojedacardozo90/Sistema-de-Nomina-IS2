#
#  Reportes Avanzados: filtros + exportaciones (Excel/PDF)
#
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Sum, Q
from django.http import HttpResponse
from datetime import date
import io
import openpyxl
from reportlab.pdfgen import canvas

from empleados.models import Empleado
from .models import Liquidacion

class ReporteAvanzadoView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self, request):
        qs = Liquidacion.objects.select_related("empleado").all()

        # filtros
        mes = request.GET.get("mes")         # 1-12
        anio = request.GET.get("anio")       # yyyy
        empleado_id = request.GET.get("empleado_id")
        area = request.GET.get("area")
        contrato = request.GET.get("contrato")  # tipo_contrato del empleado
        min_total = request.GET.get("min_total")
        max_total = request.GET.get("max_total")

        if mes: qs = qs.filter(mes=mes)
        if anio: qs = qs.filter(anio=anio)
        if empleado_id: qs = qs.filter(empleado_id=empleado_id)
        if area: qs = qs.filter(empleado__area__icontains=area)
        if contrato: qs = qs.filter(empleado__tipo_contrato__icontains=contrato)
        if min_total: qs = qs.filter(neto_cobrar__gte=min_total)
        if max_total: qs = qs.filter(neto_cobrar__lte=max_total)

        # búsqueda rápida
        q = request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(empleado__nombre__icontains=q)
                | Q(empleado__cedula__icontains=q)
            )
        return qs.order_by("-anio", "-mes", "empleado__nombre")

    def get(self, request):
        qs = self.get_queryset(request)
        payload = [
            {
                "id": l.id,
                "empleado": l.empleado.nombre,
                "cedula": l.empleado.cedula,
                "mes": l.mes,
                "anio": l.anio,
                "area": getattr(l.empleado, "area", ""),
                "contrato": getattr(l.empleado, "tipo_contrato", ""),
                "neto": float(l.neto_cobrar),
            }
            for l in qs
        ]
        total = qs.aggregate(s=Sum("neto_cobrar"))["s"] or 0
        return Response({"total": float(total), "items": payload})


class ReporteAvanzadoExcel(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = ReporteAvanzadoView().get_queryset(request)

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Reporte Avanzado"
        ws.append(["Empleado", "Cédula", "Mes", "Año", "Área", "Contrato", "Neto (Gs)"])

        for l in qs:
            ws.append([
                l.empleado.nombre, l.empleado.cedula, l.mes, l.anio,
                getattr(l.empleado, "area", ""), getattr(l.empleado, "tipo_contrato", ""),
                float(l.neto_cobrar)
            ])

        ws.append(["", "", "", "", "", "TOTAL", float(qs.aggregate(s=Sum("neto_cobrar"))["s"] or 0)])

        buf = io.BytesIO()
        wb.save(buf); buf.seek(0)
        res = HttpResponse(
            buf.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        res["Content-Disposition"] = 'attachment; filename="reporte_avanzado.xlsx"'
        return res


class ReporteAvanzadoPDF(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = ReporteAvanzadoView().get_queryset(request)

        buf = io.BytesIO()
        p = canvas.Canvas(buf)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(160, 800, "Reporte Avanzado de Liquidaciones")

        y = 770
        p.setFont("Helvetica", 10)
        for l in qs:
            p.drawString(40, y, f"{l.empleado.nombre} ({l.empleado.cedula}) {l.mes}/{l.anio} — {l.neto_cobrar:,.0f} Gs")
            y -= 18
            if y < 50:
                p.showPage(); y = 770; p.setFont("Helvetica", 10)

        total = qs.aggregate(s=Sum("neto_cobrar"))["s"] or 0
        p.setFont("Helvetica-Bold", 11)
        p.drawString(40, 40, f"TOTAL: {total:,.0f} Gs — Generado {date.today():%d/%m/%Y}")
        p.save()
        pdf = buf.getvalue(); buf.close()
        return HttpResponse(pdf, content_type="application/pdf")
