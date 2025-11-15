# backend/nomina_cal/urls.py
#
#  Rutas completas del módulo Nómina / Liquidaciones (TP IS2 / FP-UNA)

# Cumple Sprints 3–6:
#   • CRUD completo de conceptos, salarios mínimos, descuentos y liquidaciones
#   • Cálculos automáticos individuales y globales
#   • Dashboards dinámicos por rol (Admin, Gerente, Asistente, Empleado)
#   • Reportes descargables (Excel, PDF)
#   • Panel visual del empleado (HTML + AJAX)
#   • Endpoints de análisis (KPI, series temporales, top descuentos, distribución)
#

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_importacion import importar_empleados, importar_liquidaciones
from rest_framework import routers

from .views_dashboard import ReporteGeneralView
from .views import CierreNominaView, NominaPDFView

# # Vistas base (funcionales y API REST)
from . import views
from .views import EnviarReciboView, calcular_todas
from . import views_export
from .views_export import ExportPDFView, ExportExcelView

# # Vistas especializadas
from .views_export import ExportPDFView, ExportExcelView
from .views_analytics import (
    kpis_resumen,
    serie_nomina_ultimos_6,
    top_descuentos_por_concepto,
    distribucion_por_area,
    distribucion_por_tipo_contrato,
)
from .views_dashboard import (
    ReporteGeneralAdminView,
    DashboardGerenteView,
    DashboardAsistenteView,
    DashboardEmpleadoView,
)

#
# ROUTER PRINCIPAL PARA API REST CRUD
#
router = DefaultRouter()
router.register(r"conceptos", views.ConceptoViewSet, basename="conceptos")
router.register(r"salarios_minimos", views.SalarioMinimoViewSet, basename="salarios_minimos")
router.register(r"liquidaciones", views.LiquidacionViewSet, basename="liquidaciones")
router.register(r"detalles", views.DetalleLiquidacionViewSet, basename="detalles")
router.register(r"descuentos", views.DescuentoViewSet, basename="descuentos")

#
#  URLPATTERNS — Endpoints adicionales fuera del router
#
urlpatterns = [
    
    #  RUTAS REST CRUD BASE
    
    path("", include(router.urls)),

    
    #  CÁLCULOS AUTOMÁTICOS / MASIVOS (Sprint 3)
    
    path("liquidaciones/calcular_todas/", views.calcular_todas, name="calcular_todas"),
    path("liquidaciones/calcular-periodo/", views.recalcular_liquidaciones_periodo_view, name="recalcular_liquidaciones_periodo"),
    path("calcular-todas/", calcular_todas, name="calcular_todas_alias"),  # alias opcional interno

    
    #  REPORTES Y EXPORTACIONES (Sprint 4)
    
    path("reportes/general/", views.reporte_general_detallado, name="reporte_general_detallado"),
    path("reportes/simple/", views.reporte_general, name="reporte_general"),
    path("reportes/excel/", views.exportar_reporte_excel, name="exportar_reporte_excel"),
    path("reportes/pdf/", views.exportar_reporte_pdf, name="exportar_reporte_pdf"),

    # # Versiones CBV de exportaciones (para interoperabilidad futura)
    path("export/pdf/", ExportPDFView.as_view(), name="export_pdf_cbv"),
    path("export/excel/", ExportExcelView.as_view(), name="export_excel_cbv"),

    
    # ENVÍO DE RECIBO (APIView)
    
    path("liquidaciones/<int:pk>/enviar-recibo/", EnviarReciboView.as_view(), name="enviar_recibo"),
    path("liquidaciones/<int:pk>/pdf/", views_export.ReciboPDFView.as_view(), name="recibo_pdf"),

    
    #  DASHBOARDS INTERACTIVOS (Sprint 5 — CBV y FBV)
    
    path("dashboard/admin/", ReporteGeneralAdminView.as_view(), name="dashboard_admin_cbv"),
    path("dashboard/gerente/", DashboardGerenteView.as_view(), name="dashboard_gerente_cbv"),
    path("dashboard/asistente/", DashboardAsistenteView.as_view(), name="dashboard_asistente_cbv"),
    path("dashboard/empleado/", DashboardEmpleadoView.as_view(), name="dashboard_empleado_cbv"),

    # # Alternativas FBV (de views.py) para compatibilidad con el frontend React
    path("dashboard/admin/json/", views.dashboard_admin, name="dashboard_admin_json"),
    path("dashboard/gerente/json/", views.dashboard_gerente, name="dashboard_gerente_json"),
    path("dashboard/asistente/json/", views.dashboard_asistente, name="dashboard_asistente_json"),
    path("dashboard/empleado/json/", views.dashboard_empleado, name="dashboard_empleado_json"),

    
    #  PANEL HTML DEL EMPLEADO (interfaz visual Django)
    
    path("panel/empleado/", views.panel_empleado, name="panel_empleado"),

    
    # # AJAX — Servicios complementarios
    
    path("ajax/obtener-salario/", views.obtener_salario_empleado, name="obtener_salario_empleado"),

    
    # RESUMEN VISUAL GENERAL (Sprint 4 — vista HTML)
    
    path("resumen-visual/", views.resumen_visual, name="resumen_visual"),
    path("importar/empleados/", importar_empleados, name="importar_empleados"),
    path("importar/liquidaciones/", importar_liquidaciones, name="importar_liquidaciones"),
    
    #  ANALYTICS / KPI (Sprint 5–6 — ampliado)
    
    path("analytics/kpis/", kpis_resumen, name="analytics_kpis"),
    path("analytics/serie6/", serie_nomina_ultimos_6, name="analytics_serie6"),
    path("analytics/top-descuentos/", top_descuentos_por_concepto, name="analytics_top_descuentos"),
    path("analytics/distribucion-area/", distribucion_por_area, name="analytics_distribucion_area"),
    path("analytics/distribucion-contrato/", distribucion_por_tipo_contrato, name="analytics_distribucion_contrato"),
    path("reporte-general/", ReporteGeneralView.as_view(), name="reporte_general"),

    
    #  Alias directo para compatibilidad con frontend React
    

    path("cierres/", CierreNominaView.as_view(), name="nomina-cierres"),
    path("pdf/<int:pk>/", NominaPDFView.as_view(), name="nomina-pdf"),
    path("reporte-general/", ReporteGeneralAdminView.as_view(), name="reporte_general_alias"),
]

#
#  NOTAS TÉCNICAS PROFESIONALES
#
# • Este módulo integra DRF + Django clásico.
# • Compatible con:
#     - DSpace-like endpoints REST
#     - Frontend React (axios / fetch)
#     - Panel HTML SSR (server-side rendered)
# • Los endpoints CBV se usan para dashboards con vistas extendidas y datos agregados.
# • Los FBV (views.py) sirven para JSON consumido por React.
# • Analytics ofrece datos agregados de nómina para gráficos estadísticos (Chart.js / Recharts).
# • Mantené sincronizado este archivo con:
#     - backend/nomina_cal/views.py
#     - backend/nomina_cal/views_dashboard.py
#     - backend/nomina_cal/views_export.py
#     - backend/nomina_cal/views_analytics.py
#
