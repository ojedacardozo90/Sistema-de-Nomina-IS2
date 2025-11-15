# backend/empleados/urls.py

#  Rutas de API para Empleados e Hijos (TP IS2 - Nómina)
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import EmpleadoViewSet, HijoViewSet, exportar_empleados_excel, exportar_empleados_pdf
#  Router principal
router = DefaultRouter()
router.register(r"empleados", EmpleadoViewSet, basename="empleados")
router.register(r"hijos", HijoViewSet, basename="hijos")

# Endpoints adicionales (TP: reportes e historial
urlpatterns = [
    
    path("empleados/exportar/excel/", exportar_empleados_excel, name="exportar_empleados_excel"),
    path("empleados/exportar/pdf/", exportar_empleados_pdf, name="exportar_empleados_pdf"),
]

# Incluir también las rutas del router
urlpatterns += router.urls
