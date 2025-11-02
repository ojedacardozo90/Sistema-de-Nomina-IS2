# ============================================================
# 🔐 Gestión de Usuarios - Sistema de Nómina IS2 (FP-UNA / FAP)
# ------------------------------------------------------------
# Autenticación JWT personalizada, recuperación de contraseña,
# reseteo seguro, CRUD administrativo y endpoints de diagnóstico.
# ============================================================

import csv
import io
import logging
from typing import List

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import permissions, status, viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from empleados.models import Empleado
from .serializers import UsuarioSerializer, CustomTokenObtainPairSerializer
from nomina_cal.utils.notificaciones import notificar_pago

logger = logging.getLogger(__name__)
Usuario = get_user_model()
token_generator = PasswordResetTokenGenerator()

# ============================================================
# 🔑 1️⃣ Autenticación JWT Personalizada
# ============================================================
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Retorna tokens de acceso y datos completos del usuario autenticado.
    Compatible con React (login persistente vía localStorage).
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"error": "Credenciales inválidas o usuario inactivo."},
                            status=status.HTTP_401_UNAUTHORIZED)

        tokens = serializer.validated_data
        user = serializer.user

        # Respuesta personalizada para frontend
        return Response({
            "access": tokens["access"],
            "refresh": tokens["refresh"],
            "usuario": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "nombre": user.get_full_name() or user.username,
                "rol": getattr(user, "rol", None),
                "is_active": user.is_active,
            },
            "mensaje": f"Bienvenido {user.first_name or user.username} ✅",
        }, status=200)


# ============================================================
# 📧 2️⃣ Recuperar contraseña (enviar correo)
# ============================================================
class ForgotPasswordView(APIView):
    """
    Envía al correo del usuario un enlace con UID y token:
      FRONTEND_URL/reset-password?uid=<uidb64>&token=<token>
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip().lower()
        if not email:
            return Response({"error": "Debe proporcionar un correo electrónico."}, status=400)

        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            logger.warning(f"[ForgotPassword] Correo no registrado: {email}")
            return Response({"mensaje": "Si el correo existe, se enviará un enlace de recuperación."}, status=200)

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        frontend = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        reset_link = f"{frontend}/reset-password?uid={uidb64}&token={token}"

        subject = "Recuperación de contraseña - Sistema de Nómina"
        message = (
            f"Hola {user.first_name or user.username},\n\n"
            f"Hacé clic en el siguiente enlace para restablecer tu contraseña:\n\n"
            f"{reset_link}\n\n"
            f"Si no solicitaste esto, ignorá este mensaje.\n\n"
            f"— Sistema de Nómina IS2"
        )

        try:
            send_mail(subject, message,
                      getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@nomina.local"),
                      [email], fail_silently=False)
            logger.info(f"[ForgotPassword] Enlace enviado a {email}")
            return Response({"mensaje": "Correo de recuperación enviado correctamente."}, status=200)
        except Exception as e:
            logger.exception(f"[ForgotPassword] Fallo de envío: {e}")
            return Response({"error": "No se pudo enviar el correo."}, status=500)


# ============================================================
# 🔄 3️⃣ Validar y resetear contraseña
# ============================================================
class ValidateResetTokenView(APIView):
    """Valida UID/token antes del cambio de contraseña."""
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid)
        except Exception:
            return Response({"valido": False, "detalle": "uid inválido."}, status=400)
        if token_generator.check_token(user, token):
            return Response({"valido": True}, status=200)
        return Response({"valido": False, "detalle": "token inválido o expirado."}, status=400)


class ResetPasswordView(APIView):
    """
    Restablece la contraseña desde el enlace de recuperación.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, uid=None, token=None):
        uidb64 = uid or request.data.get("uid")
        token = token or request.data.get("token")
        nueva = request.data.get("password")

        if not (uidb64 and token and nueva):
            return Response({"error": "Debe enviar uid, token y password."}, status=400)
        try:
            uid_decodificado = force_str(urlsafe_base64_decode(uidb64))
            user = Usuario.objects.get(pk=uid_decodificado)
        except Exception:
            return Response({"error": "uid inválido."}, status=400)
        if not token_generator.check_token(user, token):
            return Response({"error": "token inválido o expirado."}, status=400)
        if len(nueva) < 8:
            return Response({"error": "La contraseña debe tener al menos 8 caracteres."}, status=400)

        user.set_password(nueva)
        user.save(update_fields=["password"])
        logger.info(f"[ResetPassword] Contraseña actualizada para {user.email}")
        return Response({"mensaje": "Contraseña actualizada correctamente."}, status=200)
