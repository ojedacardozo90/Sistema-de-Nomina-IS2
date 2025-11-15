#
# Envío de correos relacionados con usuarios
#
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)


def enviar_reset_password_email(user, token_link):
    """
    Envía un correo de restablecimiento de contraseña.
    - user: instancia del usuario
    - token_link: parte de la URL con uid/token
    """
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    reset_url = f"{frontend_url}/reset-password/{token_link}"

    context = {
        "user": user,
        "reset_url": reset_url,
        "year": now().year,
    }

    subject = " Restablecer tu contraseña - Sistema de Nómina IS2"
    text_message = render_to_string("emails/reset_password.txt", context)
    html_message = render_to_string("emails/reset_password.html", context)

    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@sistema-nomina.com"),
            to=[user.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        logger.info(f"Correo de reset enviado a {user.email}")
    except Exception as e:
        logger.error(f" Error al enviar correo de reset a {user.email}: {e}")
