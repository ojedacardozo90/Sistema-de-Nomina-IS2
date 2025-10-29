# ============================================================
# 📊 views_dashboard.py — Dashboards IS2 Grupo 1
# ------------------------------------------------------------
# Sprint 6–7: Paneles dinámicos por rol (Admin, Gerente, Asistente, Empleado)
# ============================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg, Count
from django.utils.timezone import now
from datetime import timedelta
from empleados.models import Empleado
from nomina_cal.models import Liquidacion, DetalleLiquidacion
from usuarios.models import Usuario

# ============================================================
# 🧩 PERMISO SIMPLE PARA ADMIN O GERENTE RRHH
# ============================================================
class IsAdminOrRRHH(IsAuthenticated):
    def has_permission(self, request, view):
        user = request.user
        return (
            super().has_permission(request, view)
            and (
                user.is_staff
                or getattr(user, "rol", "") in ["ADMIN", "GERENTE", "RRHH"]
            )
        )

# ============================================================
# 📊 DASHBOARD ADMINISTRADOR GENERAL
# ============================================================
class ReporteGeneralAdminView(APIView):
    permission_classes = [IsAdminOrRRHH]

    def get(self, request):
        try:
            # ------------------------------------------------------------
            # 🧮 Totales básicos
            # ------------------------------------------------------------
            total_empleados = Empleado.objects.filter(activo=True).count()
            total_liquidaciones = Liquidacion.objects.count()

            total_monto = (
                Liquidacion.objects.aggregate(Sum("neto_cobrar"))["neto_cobrar__sum"]
                or 0
            )
            promedio_neto = (
                Liquidacion.objects.aggregate(Avg("neto_cobrar"))["neto_cobrar__avg"]
                or 0
            )

            # ------------------------------------------------------------
            # 📈 Evolución últimos 6 meses
            # ------------------------------------------------------------
            hoy = now().date()
            meses_data = []
            for i in range(5, -1, -1):
                fecha = hoy - timedelta(days=30 * i)
                mes = fecha.month
                anio = fecha.year
                monto = (
                    Liquidacion.objects.filter(mes=mes, anio=anio)
                    .aggregate(Sum("neto_cobrar"))["neto_cobrar__sum"]
                    or 0
                )
                meses_data.append(
                    {
                        "mes": f"{mes}/{anio}",
                        "total": monto,
                    }
                )

            # ------------------------------------------------------------
            # 🧾 Top empleados con mayor salario neto
            # ------------------------------------------------------------
            top_empleados = (
                Liquidacion.objects.values("empleado__nombre")
                .annotate(total=Sum("neto_cobrar"))
                .order_by("-total")[:5]
            )

            # ------------------------------------------------------------
            # 📊 Respuesta JSON estructurada
            # ------------------------------------------------------------
            data = {
                "ok": True,
                "kpis": {
                    "total_empleados": total_empleados,
                    "total_liquidaciones": total_liquidaciones,
                    "total_monto": f"{total_monto:,.0f}",
                    "promedio_neto": f"{promedio_neto:,.0f}",
                },
                "evolucion_mensual": meses_data,
                "top_empleados": list(top_empleados),
            }

            return Response(data, status=200)

        except Exception as e:
            print("⚠️ Error Dashboard Admin:", e)
            return Response(
                {"ok": False, "error": str(e)}, status=500
            )

# ============================================================
# 📊 DASHBOARD GERENTE RRHH — Sprint 6–7 (versión React)
# ============================================================


class DashboardGerenteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Totales generales
            total_empleados = Empleado.objects.filter(activo=True).count()
            total_liquidaciones = Liquidacion.objects.count()
            promedio_nomina = (
                Liquidacion.objects.aggregate(Avg("neto_cobrar"))["neto_cobrar__avg"]
                or 0
            )

            # Evolución últimos 6 meses (mismo formato que el frontend)
            hoy = now().date()
            evolucion = []
            for i in range(5, -1, -1):
                fecha = hoy - timedelta(days=30 * i)
                mes = fecha.month
                anio = fecha.year
                total_mes = (
                    Liquidacion.objects.filter(mes=mes, anio=anio)
                    .aggregate(Sum("neto_cobrar"))["neto_cobrar__sum"]
                    or 0
                )
                evolucion.append(
                    {"mes": mes, "anio": anio, "total_mes": round(total_mes, 2)}
                )

            data = {
                "total_empleados": total_empleados,
                "total_liquidaciones": total_liquidaciones,
                "promedio_nomina": promedio_nomina,
                "evolucion": evolucion,
            }
            return Response(data, status=200)

        except Exception as e:
            print("⚠️ Error Dashboard Gerente:", e)
            return Response(
                {"error": f"Error interno del servidor: {str(e)}"},
                status=500,
            )


# ============================================================
# 📊 DASHBOARD ASISTENTE RRHH — Sprint 7
# ============================================================

class DashboardAsistenteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            total_nominas = Liquidacion.objects.count()
            monto_total = (
                Liquidacion.objects.aggregate(Sum("neto_cobrar"))["neto_cobrar__sum"]
                or 0
            )
            promedio_nomina = (
                Liquidacion.objects.aggregate(Avg("neto_cobrar"))["neto_cobrar__avg"]
                or 0
            )

            ultimas_nominas = list(
                Liquidacion.objects.values(
                    "id", "empleado__nombre", "mes", "anio", "neto_cobrar"
                )
                .order_by("-anio", "-mes")[:6]
            )

            data = {
                "total_nominas": total_nominas,
                "monto_total": monto_total,
                "promedio_nomina": promedio_nomina,
                "ultimas_nominas": ultimas_nominas,
            }
            return Response(data, status=200)

        except Exception as e:
            print("⚠️ Error Dashboard Asistente:", e)
            return Response({"error": str(e)}, status=500)


# ============================================================
# 📊 DASHBOARD EMPLEADO (Individual)
# ============================================================
class DashboardEmpleadoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        empleado = getattr(request.user, "empleado", None)
        if not empleado:
            return Response({"ok": False, "error": "No asociado a empleado"}, status=400)

        liquidaciones = (
            Liquidacion.objects.filter(empleado=empleado)
            .values("mes", "anio", "neto_cobrar")
            .order_by("-anio", "-mes")[:6]
        )

        data = {
            "empleado": empleado.nombre,
            "ultimas_liquidaciones": list(liquidaciones),
        }
        return Response(data)
# ============================================================
# 📊 Reporte General de Nómina (Panel Admin)
# ------------------------------------------------------------
# Devuelve totales, empleados y detalle mensual de nóminas
# para alimentar el Dashboard del frontend.
# ============================================================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from nomina_cal.models import Liquidacion
from empleados.models import Empleado
from datetime import datetime
from django.db.models import Sum

class ReporteGeneralView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        mes = request.query_params.get("mes")
        qs = Liquidacion.objects.all()

        if mes:
            try:
                año, mes_num = mes.split("-")
                qs = qs.filter(fecha__year=año, fecha__month=mes_num)
            except Exception:
                pass

        # Totales
        total_general = qs.aggregate(total=Sum("total"))["total"] or 0
        total_empleados = qs.values("empleado").distinct().count()

        # Detalle
        detalle = []
        for liq in qs.select_related("empleado"):
            detalle.append({
                "empleado": f"{liq.empleado.nombre} {liq.empleado.apellido}",
                "total": float(liq.total or 0),
                "fecha": liq.fecha.strftime("%Y-%m-%d") if liq.fecha else "",
            })

        data = {
            "total_general": total_general,
            "total_empleados": total_empleados,
            "detalle": detalle,
        }
        return Response(data)
