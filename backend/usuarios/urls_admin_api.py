# ============================================================
# urls_admin_api.py — API interna para el Panel Administrativo
# ------------------------------------------------------------
# Replica el panel de administración de Django dentro del
# frontend React, exponiendo todos los modelos principales
# mediante endpoints REST genéricos.
# ============================================================

from django.urls import path, include
from rest_framework import routers

# 🧩 Importación de ViewSets principales (con alias si es necesario)
from usuarios.views import UsuarioViewSet as UserViewSet
from empleados.views import EmpleadoViewSet
from nomina_cal.views import ConceptoViewSet, LiquidacionViewSet
from asistencia.views import FichadaViewSet, RegistroAsistenciaViewSet

# ============================================================
# 📡 Definición del router central
# ============================================================
router = routers.DefaultRouter()

# --- Usuarios / Empleados / Nómina ---
router.register(r'usuarios', UserViewSet)
router.register(r'empleados', EmpleadoViewSet)
router.register(r'conceptos', ConceptoViewSet)
router.register(r'liquidaciones', LiquidacionViewSet)

# --- Asistencia ---
# Incluye tanto fichadas como registros de asistencia diarios
router.register(r'fichadas', FichadaViewSet)
router.register(r'registros-asistencia', RegistroAsistenciaViewSet)

# ============================================================
# 🔗 URL patterns
# ============================================================
urlpatterns = [
    path('', include(router.urls)),
]
