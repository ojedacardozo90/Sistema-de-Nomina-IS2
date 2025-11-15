#
#  Reset de Contraseña con Token (TP IS2 - Nómina)
#
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .emails import enviar_reset_password_email

Usuario = get_user_model()

#
#  1) Solicitud de reset (genera token y envía email)
#
@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_request(request):
    email = request.data.get("email")
    if not email:
        return Response({"detail": "Debes indicar un correo."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = Usuario.objects.get(email=email)
    except Usuario.DoesNotExist:
        return Response({"detail": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    # Enviamos el email con enlace único (frontend recibirá uid/token)
    enviar_reset_password_email(user, f"{uid}/{token}")

    return Response({"detail": "Se envió un correo con instrucciones de recuperación."}, status=status.HTTP_200_OK)


#
#  2) Confirmación de reset (valida token y cambia password)
#
@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_confirm(request, token):
    uidb64 = request.data.get("uid")
    new_password = request.data.get("password")
    confirm_password = request.data.get("password2")

    if not uidb64 or not new_password or not confirm_password:
        return Response({"detail": "Datos incompletos."}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != confirm_password:
        return Response({"detail": "Las contraseñas no coinciden."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        return Response({"detail": "Token inválido o usuario no encontrado."}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({"detail": "Token inválido o expirado."}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({"detail": "Contraseña restablecida con éxito."}, status=status.HTTP_200_OK)
