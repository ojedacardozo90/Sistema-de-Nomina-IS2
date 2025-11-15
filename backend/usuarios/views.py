#
#  Gestión de Usuarios - Sistema de Nómina IS2 (FP-UNA / )

# Autenticación, recuperación y reseteo de contraseñas,
# CRUD administrativo, y endpoints de diagnóstico / dashboard.
#

import csv
import io
import logging
from typing import List

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
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
from .permissions import ReadOnly
from .serializers import UsuarioSerializer, CustomTokenObtainPairSerializer
from nomina_cal.utils.notificaciones import notificar_pago
# notificar_pago(empleado, periodo)

logger = logging.getLogger(__name__)
Usuario = get_user_model()
token_generator = PasswordResetTokenGenerator()

def generar_recibo(request, id_empleado):
    empleado = Empleado.objects.get(pk=id_empleado)
    periodo = "Octubre 2025"
    notificar_pago(empleado, periodo)
    return Response({"ok": True, "msg": "Notificación enviada"})

#
#  Autenticación JWT Personalizada
#
class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Retorna access + refresh tokens y datos del usuario autenticado.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response(
                {"error": "Credenciales inválidas o usuario inactivo."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        tokens = serializer.validated_data
        user = serializer.user
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
            "mensaje": f"Bienvenido {user.first_name or user.username} ",
        }, status=200)


#
# Forgot Password — envío de enlace de recuperación
#
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
            f"Recibimos una solicitud para restablecer tu contraseña.\n"
            f"Para continuar, hacé clic en el siguiente enlace:\n\n"
            f"{reset_link}\n\n"
            f"Si no solicitaste esto, ignorá este mensaje.\n\n"
            f"— Sistema de Nómina IS2"
        )
        try:
            send_mail(
                subject,
                message,
                getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@nomina.local"),
                [email],
                fail_silently=False,
            )
            logger.info(f"[ForgotPassword] Enlace enviado a {email}")
            return Response({"mensaje": "Correo de recuperación enviado correctamente."}, status=200)
        except Exception as e:
            logger.exception(f"[ForgotPassword] Fallo de envío: {e}")
            return Response({"error": "No se pudo enviar el correo."}, status=500)


#
#  Validar token (para ValidateToken.jsx)
#
class ValidateResetTokenView(APIView):
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


#
#  Reset Password (acepta UID/token vía body o URL)
#
class ResetPasswordView(APIView):
    """
    Restablece la contraseña de dos formas:
       POST /api/usuarios/reset-password/<uid>/<token>/
       POST /api/usuarios/reset-password/ (con body {uid, token, password})
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


#
#  ViewSet de Usuarios — Panel Administrativo Interno
#
class UsuarioViewSet(viewsets.ModelViewSet):
    """
    Replica del admin de Django (CRUD completo con roles).
    """
    queryset = Usuario.objects.all().order_by("-date_joined")
    serializer_class = UsuarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["username", "email", "first_name", "last_name", "rol"]
    ordering_fields = ["id", "username", "email", "first_name", "last_name", "is_active", "date_joined"]
    ordering = ["id"]

    def get_queryset(self):
        user = self.request.user
        rol = getattr(user, "rol", None)
        if rol == "admin" or getattr(user, "is_superuser", False):
            return Usuario.objects.all()
        elif rol == "gerente_rrhh":
            return Usuario.objects.exclude(rol="admin")
        elif rol == "asistente_rrhh":
            return Usuario.objects.filter(rol="empleado")
        elif rol == "empleado":
            return Usuario.objects.filter(id=user.id)
        return Usuario.objects.none()

    def perform_create(self, serializer):
        password = serializer.validated_data.get("password")
        if password:
            serializer.save(password=make_password(password))
        else:
            serializer.save()

    def perform_update(self, serializer):
        password = self.request.data.get("password")
        if password:
            serializer.save(password=make_password(password))
        else:
            serializer.save()

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data, status=200)

    @action(detail=True, methods=["post"], url_path="set-password")
    def set_password(self, request, pk=None):
        if getattr(request.user, "rol", None) != "admin" and not request.user.is_superuser:
            return Response({"error": "No autorizado."}, status=403)
        user = self.get_object()
        nueva = request.data.get("password")
        if not nueva:
            return Response({"error": "Debe proporcionar una nueva contraseña."}, status=400)
        user.password = make_password(nueva)
        user.save(update_fields=["password"])
        return Response({"mensaje": "Contraseña actualizada correctamente."}, status=200)

    @action(detail=True, methods=["post"], url_path="toggle-active")
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        return Response({"id": user.id, "is_active": user.is_active}, status=200)

    @action(detail=False, methods=["get"], url_path="export-csv")
    def export_csv(self, request):
        qs = self.filter_queryset(self.get_queryset())
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["id", "username", "email", "first_name", "last_name", "rol", "is_active"])
        for u in qs:
            writer.writerow([u.id, u.username, u.email, u.first_name, u.last_name, getattr(u, "rol", ""), u.is_active])
        resp = HttpResponse(buffer.getvalue(), content_type="text/csv")
        resp["Content-Disposition"] = "attachment; filename=usuarios.csv"
        return resp


#
#  Dashboard y perfil de empleado
#
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def dashboard_usuarios(request):
    data = list(Usuario.objects.values("rol").annotate(total=Count("id")).order_by("rol"))
    activos = Usuario.objects.filter(is_active=True).count()
    total = Usuario.objects.count()
    return Response({
        "total_usuarios": total,
        "activos": activos,
        "por_rol": data,
        "porcentaje_activos": f"{(activos / total * 100):.2f}%" if total else "0%",
    }, status=200)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def perfil_empleado(request):
    try:
        emp = Empleado.objects.get(usuario=request.user)
    except Empleado.DoesNotExist:
        return Response({"error": "No existe empleado asociado."}, status=404)
    return Response({
        "nombre": emp.nombre,
        "cedula": emp.cedula,
        "cargo": emp.cargo,
        "salario_base": float(emp.salario_base),
        "hijos": emp.hijos,
        "activo": emp.activo,
    }, status=200)


#
# 🩺 Check Server (diagnóstico)
#
class CheckServerView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        now = timezone.localtime()
        return Response({
            "status": "ok",
            "mensaje": "Servidor operativo y listo ",
            "hora": now.strftime("%Y-%m-%d %H:%M:%S"),
        }, status=200)
