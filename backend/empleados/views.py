
#  Vistas de Empleados e Hijos - Sistema de Nómina IS2
# API REST:
#   • CRUD de empleados e hijos
#   • Filtros por rol de usuario
#   • Exportaciones (Excel / PDF)
#   • Historial de cargos/salarios


from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import openpyxl
from reportlab.pdfgen import canvas

from usuarios.permissions import (
    IsAdmin,
    IsGerenteRRHH,
    IsAsistenteRRHH,
    IsEmpleado,
    ReadOnly,
)
from .models import Empleado, Hijo
from .serializers import EmpleadoSerializer, HijoSerializer
#  ViewSet: Empleado
class EmpleadoViewSet(viewsets.ModelViewSet):
    """
    CRUD de empleados.
    Reglas de acceso:
      • Admin / Gerente → CRUD completo
      • Asistente RRHH → lectura
      • Empleado → solo su propio perfil
    """
    queryset = Empleado.objects.all().order_by("apellido", "nombre")
    serializer_class = EmpleadoSerializer

    def get_permissions(self):
        action = getattr(self, "action", None)

        if action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdmin() or IsGerenteRRHH()]
        elif action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [ReadOnly()]

    def get_queryset(self):
        """Filtra empleados según el rol."""
        user = self.request.user
        if getattr(user, "rol", None) == "empleado":
            return Empleado.objects.filter(usuario=user)
        return super().get_queryset()

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def historial(self, request, pk=None):
        """Devuelve el historial de cargos y salarios del empleado."""
        empleado = get_object_or_404(Empleado, pk=pk)
        historial = empleado.historial_cargos.all().values(
            "cargo", "salario", "fecha_inicio", "fecha_fin"
        )
        return Response(list(historial))


#  ViewSet: Hijo / Dependiente
class HijoViewSet(viewsets.ModelViewSet):
    """
    CRUD de dependientes (hijos).
    Reglas:
      • Admin / Gerente → CRUD total
      • Asistente RRHH → solo lectura
      • Empleado → solo ver o editar sus hijos
    """
    queryset = Hijo.objects.all().order_by("nombre")
    serializer_class = HijoSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdmin() or IsGerenteRRHH()]
        elif self.action in ["list", "retrieve"]:
            return [IsAuthenticated()]
        return [ReadOnly()]

    def get_queryset(self):
        """Restringe acceso de empleados a sus propios hijos."""
        user = self.request.user
        if getattr(user, "rol", None) == "empleado" and hasattr(user, "empleado"):
            return Hijo.objects.filter(empleado=user.empleado)
        return super().get_queryset()



# Exportaciones (Excel / PDF)

@api_view(["GET"])
@permission_classes([IsAdminUser])
def exportar_empleados_excel(request):
    """
    Exporta la lista completa de empleados en formato Excel (.xlsx)
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Empleados"
    ws.append(["Nombre", "Apellido", "Cédula", "Cargo", "Salario", "Área"])

    for e in Empleado.objects.all():
        ws.append([e.nombre, e.apellido, e.cedula, e.cargo, e.salario_base, e.area])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="empleados.xlsx"'
    wb.save(response)
    return response


@api_view(["GET"])
@permission_classes([IsAdminUser])
def exportar_empleados_pdf(request):
    """
    Exporta la lista completa de empleados en formato PDF.
    """
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="empleados.pdf"'

    p = canvas.Canvas(response)
    p.setTitle("Listado de Empleados")
    y = 800
    p.setFont("Helvetica", 10)
    p.drawString(100, y, "Listado general de empleados — Sistema Nómina IS2")
    y -= 30

    for e in Empleado.objects.all():
        texto = f"{e.nombre} {e.apellido} and {e.cargo or '-'} and Gs. {e.salario_base:,}"
        p.drawString(100, y, texto)
        y -= 18
        if y < 100:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    return response
