# backend/empleados/views.py
# ============================================================
# 📦 Vistas de Empleados e Hijos (TP IS2 - Nómina)
# ============================================================

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
import openpyxl
from reportlab.pdfgen import canvas

from usuarios.permissions import IsAdmin, IsGerenteRRHH, IsAsistenteRRHH
from .models import Empleado, Hijo
from .serializers import EmpleadoSerializer, HijoSerializer



from .models import Empleado
from .serializers import EmpleadoSerializer
from usuarios.permissions import IsAdmin, IsGerenteRRHH, IsAsistenteRRHH, IsEmpleado, ReadOnly

class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer

    def get_permissions(self):
        rol = getattr(self.request.user, "rol", None)
        if rol in ["admin", "gerente_rrhh", "asistente_rrhh"]:
            return [IsAuthenticated()]
        elif rol == "empleado":
            return [IsAuthenticated(), ReadOnly()]
        return [ReadOnly()]


# ============================================================
# 🔹 ViewSet: Empleado
# ============================================================
class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.all().order_by("apellido", "nombre")
    serializer_class = EmpleadoSerializer

    def get_permissions(self):
        """
        Reglas de acceso:
        - Admin y Gerente → CRUD completo
        - Asistente RRHH → solo lectura
        - Empleado → solo puede ver su perfil
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdmin(), IsGerenteRRHH()]
        elif self.action in ["list", "retrieve"]:
            return [IsAdmin(), IsGerenteRRHH(), IsAsistenteRRHH(), IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        # Si el usuario es empleado común, que solo pueda ver su perfil
        if hasattr(user, "empleado"):
            return Empleado.objects.filter(usuario=user)
        return super().get_queryset()


# ============================================================
# 🔹 ViewSet: Hijo
# ============================================================
class HijoViewSet(viewsets.ModelViewSet):
    queryset = Hijo.objects.all().order_by("nombre")
    serializer_class = HijoSerializer

    def get_permissions(self):
        """
        Reglas de acceso:
        - Admin y Gerente → CRUD completo
        - Asistente RRHH → solo lectura
        - Empleado → solo puede ver/editar sus propios hijos
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdmin(), IsGerenteRRHH()]
        elif self.action in ["list", "retrieve"]:
            return [IsAdmin(), IsGerenteRRHH(), IsAsistenteRRHH(), IsAuthenticated()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        # Si es empleado común → solo sus hijos
        if hasattr(user, "empleado"):
            return Hijo.objects.filter(empleado=user.empleado)
        return super().get_queryset()


# ============================================================
# 📊 Funciones adicionales: historial y reportes
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def historial_cargos(request, pk):
    """
    Devuelve el historial de cargos y salarios de un empleado
    """
    empleado = get_object_or_404(Empleado, pk=pk)
    historial = empleado.historial_cargos.all().values(
        "cargo", "salario", "fecha_inicio", "fecha_fin"
    )
    return Response(historial)


@api_view(["GET"])
@permission_classes([IsAdminUser])
def exportar_empleados_excel(request):
    """
    Exporta listado de empleados a Excel
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Empleados"
    ws.append(["Nombre", "Apellido", "Cédula", "Cargo", "Salario"])
    for e in Empleado.objects.all():
        ws.append([e.nombre, e.apellido, e.cedula, e.cargo, e.salario_base])

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
    Exporta listado de empleados a PDF
    """
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="empleados.pdf"'
    p = canvas.Canvas(response)
    y = 800
    for e in Empleado.objects.all():
        p.drawString(100, y, f"{e.nombre} {e.apellido} - {e.cargo} - {e.salario_base}")
        y -= 20
    p.showPage()
    p.save()
    return response
