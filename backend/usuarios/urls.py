# ============================================================
# 🌐 Rutas para Usuarios y Autenticación (TP IS2 - NóminaPro)
# ============================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

# ------------------------------------------------------------
# 📦 Importación de vistas principales
# ------------------------------------------------------------
from .views import (
    CustomTokenObtainPairView,
    ForgotPasswordView,
    ResetPasswordView,        # ✅ Unificada (acepta uid/token vía URL o body)
    ValidateResetTokenView,   # ✅ Para ValidateToken.jsx
    CheckServerView,
)
from .views_users import UsuarioViewSet

# ------------------------------------------------------------
# 📦 Router CRUD de Usuarios (API tipo admin)
# ------------------------------------------------------------
router = DefaultRouter()
router.register(r"usuarios", UsuarioViewSet, basename="usuarios")

# ------------------------------------------------------------
# 🌐 Definición de rutas
# ------------------------------------------------------------
urlpatterns = [
    # 🔐 Autenticación JWT
    path("login/", CustomTokenObtainPairView.as_view(), name="login_usuario"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify/", TokenVerifyView.as_view(), name="token_verify"),

    # 🔒 Recuperación y restablecimiento de contraseña
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password_body"),  # vía body
    path("reset-password/<uidb64>/<token>/", ResetPasswordView.as_view(), name="reset_password_url"),  # vía URL
    path("password-reset/validate/<uidb64>/<token>/", ValidateResetTokenView.as_view(), name="validate_reset_token"),

    # 🩺 Diagnóstico rápido del servidor backend
    path("check-server/", CheckServerView.as_view(), name="check_server"),

    # 👥 CRUD completo de usuarios (Panel Admin interno)
    path("", include(router.urls)),
]
