#  URLs de Asistencia y Reportes
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    FichadaViewSet,
    RegistroAsistenciaViewSet,
    reporte_mensual_asistencia,
    exportar_reporte_excel_asistencia,
    exportar_reporte_pdf_asistencia,
    resumen_visual_asistencia,
)
# Router para los ViewSets
router = DefaultRouter()
router.register(r"fichadas", FichadaViewSet, basename="fichada")
router.register(r"asistencias", RegistroAsistenciaViewSet, basename="asistencia")
# URLs específicas del módulo de Asistencia
urlpatterns = [
    # CRUD y endpoints automáticos
    path("", include(router.urls)),

    # Reporte mensual (JSON)
    path("asistencias/reporte-mensual/", reporte_mensual_asistencia, name="reporte_mensual_asistencia"),

    # Exportaciones (Excel / PDF)
    path("asistencias/reporte-excel/", exportar_reporte_excel_asistencia, name="reporte_excel_asistencia"),
    path("asistencias/reporte-pdf/", exportar_reporte_pdf_asistencia, name="reporte_pdf_asistencia"),

    # Resumen visual HTML
    path("asistencias/resumen-visual/", resumen_visual_asistencia, name="resumen_visual_asistencia"),
]
