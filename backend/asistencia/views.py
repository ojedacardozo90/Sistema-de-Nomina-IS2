from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from django.utils.timezone import localtime, localdate
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from datetime import datetime
import io
import openpyxl
from reportlab.pdfgen import canvas

from usuarios.permissions import IsAdmin, IsGerenteRRHH, IsAsistenteRRHH
from .models import Fichada, RegistroAsistencia
from .serializers import FichadaSerializer, RegistroAsistenciaSerializer

# Permiso unificado para roles administrativos de RRHH
class IsRRHH(BasePermission):
    """Permite acceso a roles RRHH: Admin, Gerente o Asistente."""
    def has_permission(self, request, view):
        rol = getattr(request.user, "rol", None)
        return rol in ["admin", "gerente_rrhh", "asistente_rrhh"]
# Clase base de permisos para ViewSets
class BasePerm(viewsets.ModelViewSet):
    """Controla permisos según tipo de operación."""
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsRRHH()]
        return [IsAuthenticated()]
# ViewSet de Fichadas (Entradas/Salidas)
class FichadaViewSet(BasePerm):
    queryset = Fichada.objects.all().select_related("empleado")
    serializer_class = FichadaSerializer

    @action(detail=False, methods=["post"], url_path="marcar")
    def marcar(self, request):
        """
        Marca entrada o salida del empleado autenticado.
        Body esperado: { "tipo": "entrada" | "salida" }
        """
        tipo = request.data.get("tipo")
        empleado = getattr(request.user, "empleado", None)

        if not empleado:
            return Response({"detail": "El usuario no está vinculado a un empleado."}, status=400)
        if tipo not in ["entrada", "salida"]:
            return Response({"detail": "Tipo inválido."}, status=400)

        # Crear registro de fichada
        f = Fichada.objects.create(empleado=empleado, tipo=tipo, origen="web")

        # Crear o actualizar registro de asistencia diario
        reg, _ = RegistroAsistencia.objects.get_or_create(empleado=empleado, fecha=localdate())
        if tipo == "entrada":
            reg.hora_entrada = localtime(f.timestamp).time()
        else:
            reg.hora_salida = localtime(f.timestamp).time()

        reg.recalcular()
        return Response(FichadaSerializer(f).data, status=201)
# ViewSet de RegistroAsistencia
class RegistroAsistenciaViewSet(BasePerm):
    queryset = RegistroAsistencia.objects.all().select_related("empleado")
    serializer_class = RegistroAsistenciaSerializer

    @action(detail=False, methods=["post"], url_path="recalcular-dia")
    def recalcular_dia(self, request):
        """
        Recalcula manualmente un registro específico.
        Body esperado: { "empleado_id": 1, "fecha": "2025-10-22" }
        """
        emp_id = request.data.get("empleado_id")
        fecha = request.data.get("fecha")
        reg = get_object_or_404(RegistroAsistencia, empleado_id=emp_id, fecha=fecha)
        reg.recalcular()
        return Response(RegistroAsistenciaSerializer(reg).data)
# Reporte mensual de asistencia (JSON)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsRRHH])
def reporte_mensual_asistencia(request):
    """
    Endpoint GET: /api/asistencia/asistencias/reporte-mensual/?mes=10&anio=2025[&empleado_id=1]
    Retorna resumen mensual de asistencia por empleado.
    """
    try:
        mes = int(request.GET.get("mes", datetime.now().month))
        anio = int(request.GET.get("anio", datetime.now().year))
    except ValueError:
        return Response({"error": "Parámetros 'mes' o 'anio' inválidos."}, status=400)

    empleado_id = request.GET.get("empleado_id")
    filtros = Q(fecha__month=mes, fecha__year=anio)
    if empleado_id:
        filtros &= Q(empleado_id=empleado_id)

    registros = (
        RegistroAsistencia.objects
        .filter(filtros)
        .select_related("empleado")
        .values("empleado__nombre", "empleado__cedula")
        .annotate(
            presentes=Count("id", filter=Q(estado="presente")),
            tardanzas=Count("id", filter=Q(estado="tardanza")),
            ausencias=Count("id", filter=Q(estado="ausencia")),
            incompletos=Count("id", filter=Q(estado="incompleto")),
            minutos_trabajados=Sum("minutos_trabajados"),
        )
        .order_by("empleado__nombre")
    )

    total = RegistroAsistencia.objects.filter(filtros).count()

    return Response({
        "mes": mes,
        "anio": anio,
        "total_registros": total,
        "resumen": list(registros),
    }, status=200)
#  Exportar reporte mensual de asistencia a Excel
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsRRHH])
def exportar_reporte_excel_asistencia(request):
    """
    Endpoint: /api/asistencia/asistencias/reporte-excel/?mes=10&anio=2025
    Exporta el reporte mensual de asistencia en formato .xlsx
    """
    try:
        mes = int(request.GET.get("mes", datetime.now().month))
        anio = int(request.GET.get("anio", datetime.now().year))
    except ValueError:
        return Response({"error": "Parámetros 'mes' o 'anio' inválidos."}, status=400)

    registros = (
        RegistroAsistencia.objects
        .filter(fecha__month=mes, fecha__year=anio)
        .select_related("empleado")
        .values("empleado__nombre", "empleado__cedula")
        .annotate(
            presentes=Count("id", filter=Q(estado="presente")),
            tardanzas=Count("id", filter=Q(estado="tardanza")),
            ausencias=Count("id", filter=Q(estado="ausencia")),
            incompletos=Count("id", filter=Q(estado="incompleto")),
            minutos_trabajados=Sum("minutos_trabajados"),
        )
        .order_by("empleado__nombre")
    )

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Asistencia Mensual"
    ws.append(["Empleado", "Cédula", "Presentes", "Tardanzas", "Ausencias", "Incompletos", "Minutos Trabajados"])

    for r in registros:
        ws.append([
            r["empleado__nombre"], r["empleado__cedula"],
            r["presentes"], r["tardanzas"], r["ausencias"], r["incompletos"],
            r["minutos_trabajados"] or 0,
        ])

    total_empleados = registros.count()
    total_minutos = sum(r["minutos_trabajados"] or 0 for r in registros)
    ws.append(["", "", "", "", "Total Empleados", total_empleados])
    ws.append(["", "", "", "", "Total Minutos", total_minutos])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = f'attachment; filename="reporte_asistencia_{mes}-{anio}.xlsx"'
    return response

# Exportar reporte mensual de asistencia a PDF

@api_view(["GET"])
@permission_classes([IsAuthenticated, IsRRHH])
def exportar_reporte_pdf_asistencia(request):
    """
    Endpoint: /api/asistencia/asistencias/reporte-pdf/?mes=10&anio=2025
    Exporta el reporte mensual de asistencia en formato PDF.
    """
    try:
        mes = int(request.GET.get("mes", datetime.now().month))
        anio = int(request.GET.get("anio", datetime.now().year))
    except ValueError:
        return Response({"error": "Parámetros 'mes' o 'anio' inválidos."}, status=400)

    registros = (
        RegistroAsistencia.objects
        .filter(fecha__month=mes, fecha__year=anio)
        .select_related("empleado")
        .values("empleado__nombre", "empleado__cedula", "estado")
        .annotate(minutos_trabajados=Sum("minutos_trabajados"))
        .order_by("empleado__nombre")
    )

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(150, 800, f"Reporte de Asistencia - {mes}/{anio}")

    y = 770
    p.setFont("Helvetica", 10)
    for r in registros:
        linea = f"{r['empleado__nombre']} ({r['empleado__cedula']}) - {r['estado'].capitalize()} - {r['minutos_trabajados'] or 0} min"
        p.drawString(50, y, linea)
        y -= 20
        if y < 50:
            p.showPage()
            y = 770

    p.setFont("Helvetica", 9)
    p.drawString(50, 40, f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    p.save()

    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")
# Resumen visual HTML (Dashboard)
def resumen_visual_asistencia(request):
    """
    Vista HTML: /api/asistencia/asistencias/resumen-visual/?mes=10&anio=2025
    Muestra resumen mensual con totales por empleado.
    """
    try:
        mes = int(request.GET.get("mes", datetime.now().month))
        anio = int(request.GET.get("anio", datetime.now().year))
    except ValueError:
        mes, anio = datetime.now().month, datetime.now().year

    registros = (
        RegistroAsistencia.objects
        .filter(fecha__month=mes, fecha__year=anio)
        .select_related("empleado")
        .values("empleado__nombre", "empleado__cedula")
        .annotate(
            presentes=Count("id", filter=Q(estado="presente")),
            tardanzas=Count("id", filter=Q(estado="tardanza")),
            ausencias=Count("id", filter=Q(estado="ausencia")),
            incompletos=Count("id", filter=Q(estado="incompleto")),
            minutos_trabajados=Sum("minutos_trabajados"),
        )
        .order_by("empleado__nombre")
    )

    totales = {
        "presentes": sum(r["presentes"] for r in registros),
        "tardanzas": sum(r["tardanzas"] for r in registros),
        "ausencias": sum(r["ausencias"] for r in registros),
        "incompletos": sum(r["incompletos"] for r in registros),
        "minutos_trabajados": sum((r["minutos_trabajados"] or 0) for r in registros),
    }

    contexto = {"mes": mes, "anio": anio, "registros": registros, "totales": totales}
    return render(request, "asistencia/resumen_asistencia.html", contexto)
