# ============================================================
# 🌐 URLs globales del backend (TP IS2 - Sistema de Nómina)
# ------------------------------------------------------------
# Enrutamiento principal del sistema, conectando todos los módulos:
#   • Usuarios (autenticación, JWT, panel admin, recuperación de contraseña)
#   • Empleados e Hijos
#   • Nómina (conceptos, salarios, liquidaciones)
#   • Asistencia (fichadas, registros)
#   • Auditoría
# ------------------------------------------------------------
# Incluye compatibilidad con:
#   - SimpleJWT (login + refresh)
#   - Archivos estáticos/media
# ============================================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# JWT de SimpleJWT (renovación de token)
from rest_framework_simplejwt.views import TokenRefreshView


# ============================================================
# 🔗 URLPATTERNS — Mapeo de rutas del sistema
# ============================================================
urlpatterns = [

    # --------------------------------------------------------
    # 🛡️ Panel administrativo API (con permisos por rol)
    # --------------------------------------------------------
    path("api/admin-panel/", include("usuarios.urls_admin_api")),

    # --------------------------------------------------------
    # 🔐 Usuarios (autenticación, login JWT, perfil, reset password)
    # --------------------------------------------------------
    path("api/usuarios/", include("usuarios.urls")),

    # 🔑 Token refresh (JWT)
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # --------------------------------------------------------
    # 👥 Empleados e Hijos (Gestión de RRHH)
    # --------------------------------------------------------
    path("api/empleados/", include("empleados.urls")),

    # --------------------------------------------------------
    # 💰 Nómina (conceptos, salarios, reportes, liquidaciones)
    # --------------------------------------------------------
    path("api/nomina_cal/", include("nomina_cal.urls")),

    # --------------------------------------------------------
    # 🕒 Asistencia (fichadas, registros diarios)
    # --------------------------------------------------------
    path("api/asistencia/", include("asistencia.urls")),

    # --------------------------------------------------------
    # 🧾 Auditoría (movimientos, registros y logs)
    # --------------------------------------------------------
    path("api/auditoria/", include("auditoria.urls")),

    # --------------------------------------------------------
    # ⚙️ Administración Django (interfaz nativa)
    # --------------------------------------------------------
    path("admin/", admin.site.urls),

    # --------------------------------------------------------
    # 🔒 API interna de usuarios para superadministradores
    # --------------------------------------------------------
    path("api/admin/", include("usuarios.urls_admin")),
]


# ============================================================
# 📁 Archivos estáticos y media (modo DEBUG)
# ------------------------------------------------------------
# Esto asegura que las imágenes, PDFs y recursos del sistema
# estén accesibles en entorno local de desarrollo.
# ============================================================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
