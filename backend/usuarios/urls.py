#
#  Rutas para Usuarios y Autenticación (TP IS2 - NóminaPro)
#

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


# Importación de vistas y serializadores

from .views import (
    CustomTokenObtainPairView,
    ForgotPasswordView,
    ResetPasswordView,        #  Unificada (acepta uid/token vía URL o body)
    ValidateResetTokenView,   #  Para ValidateToken.jsx
    CheckServerView,
)
from .views_users import UsuarioViewSet
from .serializers import CustomTokenObtainPairSerializer  #  necesario para el endpoint estándar


# Router CRUD de Usuarios (API tipo admin)

router = DefaultRouter()
router.register(r"usuarios", UsuarioViewSet, basename="usuarios")


#  Definición de rutas

urlpatterns = [
    # ==
    #  Autenticación JWT (estandarizada y personalizada)
    # ==

    # # Endpoint estándar con CustomToken
    path(
        "token/",
        TokenObtainPairView.as_view(serializer_class=CustomTokenObtainPairSerializer),
        name="token_obtain_pair",
    ),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # # Alias adicional (login personalizado)
    path("login/", CustomTokenObtainPairView.as_view(), name="login_usuario"),

    # ==
    #  Recuperación y restablecimiento de contraseña
    # ==
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password_body"),  # vía body
    path("reset-password/<uidb64>/<token>/", ResetPasswordView.as_view(), name="reset_password_url"),  # vía URL
    path("password-reset/validate/<uidb64>/<token>/", ValidateResetTokenView.as_view(), name="validate_reset_token"),

    # ==
    # 🩺 Diagnóstico rápido del servidor backend
    # ==
    path("check-server/", CheckServerView.as_view(), name="check_server"),

    # ==
    #  CRUD completo de usuarios (Panel Admin interno)
    # ==
    path("", include(router.urls)),
]
