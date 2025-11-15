#
# Vistas de Nómina (TP IS2 - Sistema de Nómina con PostgreSQL)
# Cumple Sprints 2–5: Cálculo completo, roles, reportes, dashboards y auditoría
#

# DRF core
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Concepto, Liquidacion
from .serializers import ConceptoSerializer, LiquidacionSerializer
from usuarios.permissions import IsAdmin, IsGerenteRRHH, IsAsistenteRRHH, ReadOnly
from rest_framework import filters
# Django core
from django.db.models import Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from usuarios.permissions import IsAdminOrGerente

# Utilidades / estándar
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
import io
import openpyxl
import logging
from reportlab.pdfgen import canvas

#  IMPORT DEL SERVICIO ALIAS: evitamos chocar con tu función local
#from nomina_cal.services.calculo_individual import calcular_liquidacion as calcular_liquidacion_individual
from nomina_cal.services.calculo_nomina import calcular_liquidaciones_periodo

#
# # Importaciones internas (modelo de negocio)
#
from empleados.models import Empleado
from .models import Concepto, SalarioMinimo, Liquidacion, DetalleLiquidacion
from .models_descuento import Descuento
from .serializers import (
    ConceptoSerializer,
    SalarioMinimoSerializer,
    LiquidacionSerializer,
    DetalleLiquidacionSerializer,
    DescuentoSerializer,
    
)
from usuarios.permissions import (
    IsAdmin,
    IsGerenteRRHH,
    IsAsistenteRRHH,
    IsEmpleado,
    IsAdminOrAsistente,
)

#
#  LOGGING DE OPERACIONES (para auditoría interna)
#
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename="logs_nomina.txt",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

#
#  Resumen general simple (conteos)
#
@api_view(["GET"])
def reporte_general(request):
    total_empleados = Empleado.objects.count()
    total_liquidaciones = Liquidacion.objects.count()
    #  campo correcto en tu modelo: neto_cobrar
    total_nomina = (
        Liquidacion.objects.aggregate(s=Sum("neto_cobrar"))["s"] or Decimal("0.00")
    )
    return Response(
        {
            "total_empleados": total_empleados,
            "total_liquidaciones": total_liquidaciones,
            "total_nomina": str(total_nomina),
        }
    )

# Import tolerante del servicio de envío de recibos
#try:
#    from .models import enviar_recibo_email  # si está en models.py
#except Exception:
#    try:
#        from .emails import enviar_recibo_email  # si está en emails.py
#    except Exception:
#        from .utils import enviar_recibo_email  # fallback utils.py

#
# # FUNCIÓN CENTRAL DE CÁLCULO (INDIVIDUAL, sobre una Liquidación)
#    Mantengo tu lógica tal cual, solo comentarios y guardado.
#
def calcular_liquidacion(liquidacion: Liquidacion):
    """
    Recalcula una liquidación individual del empleado asociado,
    generando/actualizando los DetalleLiquidacion conforme a:
    - Sueldo base (imponible, siempre)
    - Bonificación por hijos (no imponible, excluye IPS/aguinaldo)
    - IPS 9% sobre imponibles
    - Descuentos adicionales (préstamos, embargos, etc.)
    - Aguinaldo/Vacaciones proporcionales (según política)
    """
    empleado = liquidacion.empleado
    salario_base = empleado.salario_base or Decimal("0.00")

    # Validaciones de consistencia
    if salario_base <= 0:
        raise ValueError(f"El empleado {empleado} no tiene salario base asignado.")

    salario_minimo = SalarioMinimo.get_vigente(
        date(liquidacion.anio, liquidacion.mes, 1)
    )
    if not salario_minimo:
        raise ValueError("No existe salario mínimo vigente para la fecha indicada.")

    # Reinicia detalles previos de la liquidación para un recálculo limpio
    liquidacion.detalles.all().delete()
    total_ingresos = Decimal("0.00")
    total_descuentos = Decimal("0.00")

    
    # 1) Sueldo base (imponible)
    
    concepto_base, _ = Concepto.objects.get_or_create(
        descripcion="Sueldo Base",
        defaults={
            "es_debito": False,
            "es_recurrente": True,
            "afecta_ips": True,
            "para_aguinaldo": True,
        },
    )
    DetalleLiquidacion.objects.create(
        liquidacion=liquidacion, concepto=concepto_base, monto=salario_base
    )
    total_ingresos += salario_base

    
    # 2) Bonificación familiar (usa tu método en el modelo)
    #    * Debe excluirse del IPS y del Aguinaldo.
    
    bonificacion = liquidacion.calcular_bonificacion_hijos()
    if bonificacion > 0:
        concepto_bono, _ = Concepto.objects.get_or_create(
            descripcion="Bonificación Familiar por Hijo",
            defaults={
                "es_debito": False,
                "es_recurrente": True,
                "afecta_ips": False,
                "para_aguinaldo": False,
            },
        )
        DetalleLiquidacion.objects.create(
            liquidacion=liquidacion, concepto=concepto_bono, monto=bonificacion
        )
        total_ingresos += bonificacion

    
    # 3) Descuento IPS (9% sobre imponibles)
    
    ips = liquidacion.calcular_ips(salario_base).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    concepto_ips, _ = Concepto.objects.get_or_create(
        descripcion="Descuento IPS 9%",
        defaults={
            "es_debito": True,
            "es_recurrente": True,
            "afecta_ips": True,
            "para_aguinaldo": False,
        },
    )
    DetalleLiquidacion.objects.create(
        liquidacion=liquidacion, concepto=concepto_ips, monto=ips
    )
    total_descuentos += ips

    
    # 4) Descuentos adicionales (préstamos, embargos, etc.)
    
    descuentos_extra = Descuento.objects.filter(empleado=empleado, activo=True)
    for d in descuentos_extra:
        if d.es_vigente(liquidacion.mes, liquidacion.anio):
            concepto_extra, _ = Concepto.objects.get_or_create(
                descripcion=f"Descuento: {d.tipo.title()}",
                defaults={
                    "es_debito": True,
                    "es_recurrente": d.recurrente,
                    "afecta_ips": False,
                    "para_aguinaldo": False,
                },
            )
            DetalleLiquidacion.objects.create(
                liquidacion=liquidacion, concepto=concepto_extra, monto=d.monto
            )
            total_descuentos += d.monto

    
    # 5) Aguinaldo + Vacaciones proporcionales (evidencia sprint)
    
    aguinaldo = (salario_base / Decimal("12")).quantize(Decimal("0.01"))
    vacaciones = (salario_base * Decimal("0.04")).quantize(Decimal("0.01"))

    for descripcion, monto in [
        ("Aguinaldo Proporcional", aguinaldo),
        ("Vacaciones Proporcionales", vacaciones),
    ]:
        if monto > 0:
            concepto, _ = Concepto.objects.get_or_create(
                descripcion=descripcion,
                defaults={
                    "es_debito": False,
                    "es_recurrente": True,
                    "afecta_ips": False,
                    "para_aguinaldo": (descripcion == "Aguinaldo Proporcional"),
                },
            )
            DetalleLiquidacion.objects.create(
                liquidacion=liquidacion, concepto=concepto, monto=monto
            )
            total_ingresos += monto

    
    # 6) Persistencia de totales y auditoría
    
    liquidacion.total_ingresos = total_ingresos
    liquidacion.total_descuentos = total_descuentos
    liquidacion.neto_cobrar = total_ingresos - total_descuentos
    liquidacion.updated_at = datetime.now()
    liquidacion.save()
    liquidacion.refresh_from_db()

    logger.info(
        f"Liquidación recalculada: Empleado={empleado.cedula} | Ingresos={total_ingresos} | Descuentos={total_descuentos} | Neto={liquidacion.neto_cobrar}"
    )

    return liquidacion

#
# # AUDITORÍA AUTOMÁTICA (para crear/actualizar)
#
class AuditoriaMixin:
    """Mixin reutilizable para registrar quién crea o actualiza registros."""

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

#
# # CRUD VIEWSETS (API REST) — Conceptos / Salario Mínimo
#
class ConceptoViewSet(viewsets.ModelViewSet):
    queryset = Concepto.objects.all()
    serializer_class = ConceptoSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "destroy"]:
            return [IsAdmin() or IsGerenteRRHH()]
        return [IsAuthenticated(), ReadOnly()]


class LiquidacionViewSet(viewsets.ModelViewSet):
    queryset = Liquidacion.objects.all()
    serializer_class = LiquidacionSerializer

    def get_permissions(self):
        rol = getattr(self.request.user, "rol", None)
        if rol in ["admin", "gerente_rrhh", "asistente_rrhh"]:
            return [IsAuthenticated()]
        return [IsAuthenticated(), ReadOnly()]


class ConceptoViewSet(AuditoriaMixin, viewsets.ModelViewSet):
    queryset = Concepto.objects.all().order_by("descripcion")
    serializer_class = ConceptoSerializer
    permission_classes = [IsAuthenticated]

class SalarioMinimoViewSet(AuditoriaMixin, viewsets.ModelViewSet):
    queryset = SalarioMinimo.objects.all().order_by("-vigente_desde")
    serializer_class = SalarioMinimoSerializer
    permission_classes = [IsAuthenticated]

class LiquidacionView(APIView):
    """
    Endpoint utilitario que calcula conceptos en base a un empleado y
    un set de conceptos. Usa la FUNCIÓN DEL SERVICIO (no la local).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        empleado_id = request.data.get("empleado_id")
        empleado = get_object_or_404(Empleado, pk=empleado_id)

        conceptos = [
            {
                "nombre": "Sueldo Base",
                "tipo": "Crédito",
                "monto": empleado.salario_base,
                "afecta_ips": True,
                "afecta_aguinaldo": True,
            }
        ]

        #  Usa la función importada del servicio (alias)
        resultado = calcular_liquidacion_individual(empleado, conceptos)
        return Response(resultado, status=200)

#
# # VIEWSET PRINCIPAL: LIQUIDACIÓN (CRUD + acciones)
#
class LiquidacionViewSet(AuditoriaMixin, viewsets.ModelViewSet):
    """
    ViewSet principal que gestiona todas las liquidaciones.
    Incluye acciones personalizadas: calcular, cerrar, enviar-recibo.
    """
    queryset = Liquidacion.objects.all().order_by("-anio", "-mes")
    serializer_class = LiquidacionSerializer
    permission_classes = [IsAdminOrGerente]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["empleado__nombre", "empleado__apellido", "empleado__cedula"]
    ordering_fields = ["anio", "mes", "neto_cobrar"]
    ordering = ["-anio", "-mes"]  # orden por defecto

    def get_queryset(self):
        """
        Regla de visibilidad:
        - Si el usuario es 'empleado', solo ve sus propias liquidaciones.
        - RRHH/Admin ven todas.
        """
        user = self.request.user
        if hasattr(user, "rol") and user.rol == "empleado":
            return Liquidacion.objects.filter(empleado__usuario=user)
        return super().get_queryset()

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def calcular(self, request, pk=None):
        """
        Recalcula totales, bonificaciones, IPS y descuentos de UNA liquidación.
        Endpoint: POST /api/nomina_cal/liquidaciones/{id}/calcular/
        """
        liquidacion = self.get_object()
        if liquidacion.cerrada:
            return Response({"error": "La liquidación ya está cerrada."}, status=400)

        try:
            liquidacion = calcular_liquidacion(liquidacion)
        except Exception as e:
            logger.error(f"Error en cálculo de liquidación {pk}: {e}")
            return Response({"error": str(e)}, status=400)

        return Response(LiquidacionSerializer(liquidacion).data, status=200)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def cerrar(self, request, pk=None):
        """
        Cierra una liquidación para impedir modificaciones posteriores.
        Endpoint: POST /api/nomina_cal/liquidaciones/{id}/cerrar/
        """
        liquidacion = self.get_object()
        liquidacion.cerrar()
        logger.info(f"Liquidación {pk} cerrada por {request.user}")
        return Response({"status": "Liquidación cerrada correctamente"})

    @action(
        detail=True,
        methods=["post"],
        url_path="enviar-recibo",
        permission_classes=[IsAuthenticated],
    )
    def enviar_recibo(self, request, pk=None):
        """
        Genera el PDF del recibo y lo envía al correo del empleado.
        Marca 'enviado_email=True' en caso de éxito.
        Endpoint: POST /api/nomina_cal/liquidaciones/{id}/enviar-recibo/
        """
        liquidacion = self.get_object()

        # Idempotencia básica
        if getattr(liquidacion, "enviado_email", False):
            return Response(
                {"mensaje": "El recibo ya fue enviado anteriormente."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            enviado = enviar_recibo_email(liquidacion)
            if enviado:
                return Response(
                    {"mensaje": " Recibo enviado correctamente por correo."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "El empleado no tiene correo registrado."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            logger.error(f"Error al enviar recibo: {e}")
            return Response(
                {"error": f"Error al enviar el correo: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

#
# # DETALLE LIQUIDACIÓN (CRUD)
#
class DetalleLiquidacionViewSet(AuditoriaMixin, viewsets.ModelViewSet):
    queryset = DetalleLiquidacion.objects.select_related("concepto", "liquidacion")
    serializer_class = DetalleLiquidacionSerializer
    permission_classes = [IsAuthenticated]

#
# # DESCUENTOS (CRUD)
#   * Permisos: autenticado + (Admin OR AsistenteRRHH)
#   * DRF soporta OR bit a bit: IsAdmin | IsAsistenteRRHH
#
class DescuentoViewSet(viewsets.ModelViewSet):
    queryset = Descuento.objects.all().select_related("empleado")
    serializer_class = DescuentoSerializer
    permission_classes = [IsAuthenticated, (IsAdmin | IsAsistenteRRHH)]

    def perform_create(self, serializer):
        """
        Guarda los usuarios responsables al crear un descuento.
        Soporta tanto created_by/updated_by como creado_por (fallback).
        """
        try:
            serializer.save(created_by=self.request.user, updated_by=self.request.user)
        except TypeError:
            serializer.save(creado_por=self.request.user)

#
# # REPORTES BÁSICOS (JSON) — evidencia sprints
#
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def reporte_general_detallado(request):
    """
    Devuelve un resumen JSON de liquidaciones (total general + detalle).
    Soporta filtros por mes, año y empleado_id vía querystring.
    """
    qs = Liquidacion.objects.all()
    mes, anio, empleado_id = (
        request.GET.get("mes"),
        request.GET.get("anio"),
        request.GET.get("empleado_id"),
    )
    if mes:
        qs = qs.filter(mes=mes)
    if anio:
        qs = qs.filter(anio=anio)
    if empleado_id:
        qs = qs.filter(empleado_id=empleado_id)

    total_general = qs.aggregate(total=Sum("neto_cobrar"))["total"] or 0
    detalle = [
        {
            "empleado": l.empleado.nombre,
            "cedula": l.empleado.cedula,
            "mes": l.mes,
            "anio": l.anio,
            "total": str(l.neto_cobrar),
        }
        for l in qs
    ]
    return Response({"total_general": str(total_general), "detalle": detalle})

#
# # EXPORTACIÓN: EXCEL & PDF (descargables)
#
@api_view(["GET"])
@permission_classes([IsAdmin])
def exportar_reporte_excel(request):
    """
    Exporta todas las liquidaciones en formato Excel (.xlsx).
    Devuelve un archivo binario con Content-Disposition: attachment.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Liquidaciones"
    ws.append(["Empleado", "Cédula", "Mes/Año", "Neto a Cobrar"])

    for l in Liquidacion.objects.all():
        ws.append(
            [l.empleado.nombre, l.empleado.cedula, f"{l.mes}/{l.anio}", float(l.neto_cobrar)]
        )

    total_general = Liquidacion.objects.aggregate(total=Sum("neto_cobrar"))["total"] or 0
    ws.append(["", "", "TOTAL GENERAL", float(total_general)])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(
        buffer,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="reporte_liquidaciones.xlsx"'
    return response

@api_view(["GET"])
@permission_classes([IsAdmin])
def exportar_reporte_pdf(request):
    """
    Exporta todas las liquidaciones en formato PDF usando ReportLab.
    Devuelve un PDF con Content-Disposition por defecto (inline).
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(180, 800, "Reporte General de Liquidaciones")

    y = 770
    for l in Liquidacion.objects.all():
        p.setFont("Helvetica", 10)
        p.drawString(
            50,
            y,
            f"{l.empleado.nombre} ({l.empleado.cedula}) - {l.mes}/{l.anio} - {l.neto_cobrar} Gs",
        )
        y -= 20
        if y < 50:
            p.showPage()
            y = 770

    p.drawString(50, 40, f"Generado el {date.today().strftime('%d/%m/%Y')}")
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type="application/pdf")

#
# # CÁLCULO MASIVO: Recalcular TODAS las liquidaciones abiertas
#
@api_view(["POST"])
@permission_classes([IsAuthenticated, (IsAdmin | IsAsistenteRRHH)])
def calcular_todas(request):
    """
    Recalcula todas las liquidaciones con estado 'abierta' (cerrada=False).
    Útil para cierres mensuales o recalcular masivamente.
    """
    liquidaciones = Liquidacion.objects.filter(cerrada=False)
    if not liquidaciones.exists():
        return Response(
            {"mensaje": "No hay liquidaciones abiertas para calcular."}, status=200
        )

    for liq in liquidaciones:
        calcular_liquidacion(liq)

    logger.info(
        f"Recalculo masivo: {liquidaciones.count()} liquidaciones recalculadas."
    )
    return Response(
        {"mensaje": f"Se recalcularon {liquidaciones.count()} liquidaciones correctamente."},
        status=200,
    )

#
# # ENDPOINT MASIVO POR PERÍODO (mes/año)
#
@api_view(["POST"])
@permission_classes([IsAdminUser])
def recalcular_liquidaciones_periodo_view(request):
    """
    Recalcula TODAS las liquidaciones de un período (mes y año) utilizando
    la función del servicio nomina_cal.services.calculo_nomina.calcular_liquidaciones_periodo
    Body esperado: { "anio": 2025, "mes": 10 }
    """
    from nomina_cal.models import Periodo

    try:
        anio = int(request.data.get("anio"))
        mes = int(request.data.get("mes"))
    except (TypeError, ValueError):
        return Response({"error": "Datos de año o mes inválidos."}, status=400)

    try:
        periodo = Periodo.objects.get(anio=anio, mes=mes)
    except Periodo.DoesNotExist:
        return Response({"error": "El período especificado no existe."}, status=404)

    count = calcular_liquidaciones_periodo(periodo)
    logger.info(f" Recalculadas {count} liquidaciones para {mes}/{anio}")

    return Response(
        {"message": "Liquidaciones recalculadas correctamente.", "count": count},
        status=200,
    )

#
#  DASHBOARDS (ADMIN, GERENTE, ASISTENTE, EMPLEADO)
#
@api_view(["GET"])
@permission_classes([IsAdmin])
def dashboard_admin(request):
    total_empleados = Empleado.objects.count()
    total_liquidaciones = Liquidacion.objects.count()
    total_general = Liquidacion.objects.aggregate(total=Sum("neto_cobrar"))["total"] or 0
    promedio_general = (
        Liquidacion.objects.aggregate(promedio=Avg("neto_cobrar"))["promedio"] or 0
    )
    total_descuentos = (
        Liquidacion.objects.aggregate(desc=Sum("total_descuentos"))["desc"] or 0
    )
    promedio_por_cargo = (
        Empleado.objects.values("cargo")
        .annotate(promedio=Avg("salario_base"))
        .order_by("cargo")
    )
    porcentaje_cubierto = (
        f"{(total_liquidaciones / total_empleados * 100):.2f}%"
        if total_empleados
        else "0%"
    )
    return Response(
        {
            "rol": "Administrador",
            "total_empleados": total_empleados,
            "total_liquidaciones": total_liquidaciones,
            "total_general": str(total_general),
            "total_descuentos": str(total_descuentos),
            "promedio_general": str(round(promedio_general, 2)),
            "porcentaje_cubierto": porcentaje_cubierto,
            "promedio_por_cargo": list(promedio_por_cargo),
        }
    )

@api_view(["GET"])
@permission_classes([IsGerenteRRHH])
def dashboard_gerente(request):
    total_empleados = Empleado.objects.count()
    total_liquidaciones = Liquidacion.objects.count()
    promedio = (
        Liquidacion.objects.aggregate(promedio=Avg("neto_cobrar"))["promedio"] or 0
    )
    datos_mes = (
        Liquidacion.objects.values("mes", "anio")
        .annotate(total_mes=Sum("neto_cobrar"))
        .order_by("-anio", "-mes")[:6]
    )
    return Response(
        {
            "rol": "Gerente RRHH",
            "promedio_nomina": str(round(promedio, 2)),
            "total_empleados": total_empleados,
            "total_liquidaciones": total_liquidaciones,
            "evolucion": list(datos_mes),
        }
    )

@api_view(["GET"])
@permission_classes([IsAsistenteRRHH])
def dashboard_asistente(request):
    ultimas = Liquidacion.objects.all().order_by("-anio", "-mes")[:5]
    if not ultimas.exists():
        return Response(
            {
                "rol": "Asistente RRHH",
                "mensaje": "Aún no hay nóminas registradas.",
                "ultimas_liquidaciones": [],
            }
        )
    return Response(
        {
            "rol": "Asistente RRHH",
            "ultimas_liquidaciones": [
                {
                    "empleado": l.empleado.nombre,
                    "cedula": l.empleado.cedula,
                    "mes": l.mes,
                    "anio": l.anio,
                    "total": str(l.neto_cobrar),
                }
                for l in ultimas
            ],
        }
    )

@api_view(["GET"])
@permission_classes([IsEmpleado])
def dashboard_empleado(request):
    try:
        empleado = Empleado.objects.get(usuario=request.user)
    except Empleado.DoesNotExist:
        return Response({"error": "Empleado no encontrado"}, status=404)

    liquidaciones = Liquidacion.objects.filter(empleado=empleado).order_by(
        "-anio", "-mes"
    )
    if not liquidaciones.exists():
        return Response(
            {
                "rol": "Empleado",
                "mensaje": "No tienes liquidaciones registradas aún.",
                "mis_liquidaciones": [],
            }
        )
    return Response(
        {
            "rol": "Empleado",
            "mis_liquidaciones": [
                {
                    "mes": l.mes,
                    "anio": l.anio,
                    "neto": str(l.neto_cobrar),
                    "detalle": [
                        {"concepto": d.concepto.descripcion, "monto": str(d.monto)}
                        for d in l.detalles.all()
                    ],
                }
                for l in liquidaciones
            ],
        }
    )

#
# # VISTAS HTML (panel empleado / resumen visual) — evidencia UI
#
@login_required
def panel_empleado(request):
    """
    Renderiza el panel del empleado autenticado (vistas HTML server-side).
    Incluye banderas para indicar si hay IPS o Bonificación en sus detalles.
    """
    try:
        empleado = Empleado.objects.get(usuario=request.user)
    except Empleado.DoesNotExist:
        return render(
            request,
            "nomina_cal/panel_empleado.html",
            {"empleado": None, "liquidaciones": []},
        )

    liquidaciones = (
        Liquidacion.objects.filter(empleado=empleado)
        .order_by("-anio", "-mes")
        .prefetch_related("detalles")
    )
    # Enriquecer con banderas de IPS y bonificación
    for liq in liquidaciones:
        liq.detalles_ips = liq.detalles.filter(
            concepto__descripcion__icontains="IPS"
        ).exists()
        liq.detalles_bonificacion = liq.detalles.filter(
            concepto__descripcion__icontains="hijo"
        ).exists()

    contexto = {"empleado": empleado, "liquidaciones": liquidaciones}
    return render(request, "nomina_cal/panel_empleado.html", contexto)

def obtener_salario_empleado(request):
    """
    AJAX: devuelve el salario base del empleado en JSON.
    Usado para autocompletar en el admin.
    """
    empleado_id = request.GET.get("empleado_id")
    salario = 0
    if empleado_id:
        try:
            empleado = Empleado.objects.get(id=empleado_id)
            salario = float(empleado.salario_base)
        except Empleado.DoesNotExist:
            pass
    return JsonResponse({"salario": salario})

#
#  ENVÍO DE RECIBO INDIVIDUAL (por correo electrónico)
#
from django.core.mail import EmailMessage
from nomina_cal.utils_email import generar_recibo_pdf
from nomina_cal.models_envio import EnvioCorreo
from nomina_cal.models import Liquidacion


class EnviarReciboView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrAsistente]

    def post(self, request, pk):
        liq = get_object_or_404(Liquidacion, pk=pk)
        emp = liq.empleado
        to_email = getattr(emp, "email", None)

        if not to_email:
            return Response(
                {"ok": False, "error": "Empleado sin email registrado."}, status=400
            )

        #  Generar PDF profesional (nuevo utils_email.py)
        pdf_bytes = generar_recibo_pdf(liq)

        msg = EmailMessage(
            subject=f"Recibo de salario {liq.mes}/{liq.anio}",
            body=(
                f"Estimado/a {emp.nombre}, adjuntamos su recibo correspondiente "
                f"al periodo {liq.mes}/{liq.anio}.\n\n"
                f"Atentamente,\nRRHH - INGESOFT"
            ),
            to=[to_email],
        )
        msg.attach(
            filename=f"recibo_{liq.id}.pdf",
            content=pdf_bytes,
            mimetype="application/pdf",
        )

        try:
            msg.send()
            liq.enviado_email = True
            liq.save(update_fields=["enviado_email"])

            EnvioCorreo.objects.create(
                empleado=emp,
                asunto=msg.subject,
                destinatario=to_email,
                estado="ENVIADO",
                detalle_error=""
            )
            return Response({"ok": True, "mensaje": " Recibo enviado y registrado."})

        except Exception as e:
            EnvioCorreo.objects.create(
                empleado=emp,
                asunto=msg.subject,
                destinatario=to_email,
                estado="ERROR",
                detalle_error=str(e)[:400]
            )
            return Response(
                {"ok": False, "error": "Fallo al enviar correo."},
                status=500
            )


def resumen_visual(request):
    """
    Render HTML con un resumen de totales (ingresos, descuentos, neto).
    Evidencia Sprint 4 — reporte visual simple.
    """
    resumen = Liquidacion.objects.aggregate(
        total_ingresos=Sum("total_ingresos"),
        total_descuentos=Sum("total_descuentos"),
        total_general=Sum("neto_cobrar"),
    )
    contexto = {
        "total_ingresos": resumen["total_ingresos"] or 0,
        "total_descuentos": resumen["total_descuentos"] or 0,
        "total_general": resumen["total_general"] or 0,
    }
    return render(request, "nomina_cal/resumen_visual.html", contexto)


#
#  CierreNominaView — Cierre mensual de la nómina
#

from django.db import transaction
from .models import Liquidacion
from nomina_cal.utils_email import generar_recibo_pdf  # o de donde venga tu función
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class CierreNominaView(APIView):
    """
    Cierra todas las liquidaciones abiertas del mes y año indicados,
    marcándolas como cerradas y generando los recibos PDF.
    """

    def post(self, request, *args, **kwargs):
        mes = request.data.get("mes")
        anio = request.data.get("anio")

        if not mes or not anio:
            return Response(
                {"error": "Debe especificar el mes y el año."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            liquidaciones = Liquidacion.objects.filter(mes=mes, anio=anio, cerrada=False)
            count = liquidaciones.count()

            for liq in liquidaciones:
                liq.cerrada = True
                liq.save()
                try:
                    generar_recibo_pdf(liq)
                except Exception as e:
                    print(f" Error generando recibo: {e}")

        return Response(
            {"mensaje": f"Cierre completado. {count} liquidaciones cerradas."},
            status=status.HTTP_200_OK,
        )

#
#  NominaPDFView — Genera PDF individual de una liquidación
#

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import io
from .models import Liquidacion


class NominaPDFView(APIView):
    """
    Genera el PDF del recibo de salario para una liquidación específica.
    Endpoint: GET /api/nomina_cal/pdf/<id>/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            liq = Liquidacion.objects.get(pk=pk)
        except Liquidacion.DoesNotExist:
            return Response({"error": "Liquidación no encontrada."}, status=404)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(200, 800, "Recibo de Salario")

        y = 760
        p.setFont("Helvetica", 11)
        p.drawString(50, y, f"Empleado: {liq.empleado.nombre}")
        y -= 20
        p.drawString(50, y, f"Cédula: {liq.empleado.cedula}")
        y -= 20
        p.drawString(50, y, f"Periodo: {liq.mes}/{liq.anio}")
        y -= 20
        p.drawString(50, y, f"Sueldo Base: {liq.empleado.salario_base} Gs")
        y -= 20
        p.drawString(50, y, f"Total Ingresos: {liq.total_ingresos} Gs")
        y -= 20
        p.drawString(50, y, f"Total Descuentos: {liq.total_descuentos} Gs")
        y -= 20
        p.drawString(50, y, f"Neto a Cobrar: {liq.neto_cobrar} Gs")

        p.line(50, y - 10, 550, y - 10)
        y -= 40
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y, "Detalle de Conceptos:")

        y -= 20
        p.setFont("Helvetica", 10)
        for detalle in liq.detalles.all():
            if y < 80:
                p.showPage()
                y = 780
                p.setFont("Helvetica", 10)
            p.drawString(
                60,
                y,
                f"{detalle.concepto.descripcion}: {detalle.monto} Gs",
            )
            y -= 18

        p.showPage()
        p.save()
        buffer.seek(0)

        response = HttpResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="recibo_{liq.id}.pdf"'
        return response
