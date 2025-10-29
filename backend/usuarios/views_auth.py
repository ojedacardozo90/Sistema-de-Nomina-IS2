# ============================================================
# 🔐 Vistas de Autenticación y Roles (TP IS2 - Sistema de Nómina FAP)
# ------------------------------------------------------------
# Incluye:
#   • Inicio / cierre de sesión con JWT (SimpleJWT)
#   • Recuperación y restablecimiento de contraseña
#   • Perfil del usuario autenticado
#   • Control de roles para enrutamiento React
# ============================================================

from django.contrib.auth.models import update_last_login
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# ============================================================
# 🧩 LOGIN - JWT Authentication
# ============================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    Recibe credenciales (username, password)
    y devuelve tokens JWT (access + refresh) + rol del usuario.
    """
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({"error": "Credenciales inválidas."}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    update_last_login(None, user)

    rol = getattr(user, "rol", "empleado")  # fallback
    return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "rol": rol,
        }
    })


# ============================================================
# 🚪 LOGOUT (token blacklist opcional)
# ============================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Invalida el token de refresh (opcional).
    """
    try:
        token = RefreshToken(request.data.get("refresh"))
        token.blacklist()
        return Response({"message": "Sesión cerrada correctamente."}, status=200)
    except Exception:
        return Response({"message": "Token inválido o expirado."}, status=400)


# ============================================================
# 👤 PERFIL DEL USUARIO ACTUAL
# ============================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    return Response({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "rol": getattr(user, "rol", "empleado"),
    })


# ============================================================
# 📧 SOLICITUD DE RESETEO DE CONTRASEÑA
# ============================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Envia un correo con enlace de restablecimiento de contraseña.
    """
    email = request.data.get("email")
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({"error": "No existe un usuario con ese correo."}, status=404)

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    reset_link = f"http://localhost:5173/reset-password/{uid}/{token}"

    send_mail(
        subject="Recuperación de contraseña - Sistema de Nómina",
        message=f"Hola {user.username},\n\nPara restablecer tu contraseña hacé clic en el siguiente enlace:\n{reset_link}\n\nSi no solicitaste este correo, ignoralo.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )

    return Response({"message": "Correo de restablecimiento enviado correctamente."})


# ============================================================
# 🔁 RESETEO DE CONTRASEÑA (desde el link del correo)
# ============================================================
@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request, uidb64, token):
    """
    Cambia la contraseña del usuario si el token es válido.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        return Response({"error": "Enlace inválido o expirado."}, status=400)

    if not default_token_generator.check_token(user, token):
        return Response({"error": "Token inválido o expirado."}, status=400)

    new_password = request.data.get("password")
    if not new_password or len(new_password) < 4:
        return Response({"error": "Contraseña no válida o demasiado corta."}, status=400)

    user.set_password(new_password)
    user.save()
    return Response({"message": "Contraseña restablecida correctamente."})
