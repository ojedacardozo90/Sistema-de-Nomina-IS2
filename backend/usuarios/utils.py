#
# Funciones auxiliares para envío de correos
# - Reset password
# - Notificaciones generales
#
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.timezone import now
import logging

logger = logging.getLogger(__name__)


def enviar_email_reset(user, token):
    """
    Envía un correo de restablecimiento de contraseña al usuario.
    """
    frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
    reset_url = f"{frontend_url}/reset-password/{token}"

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
    except Exception as e:
        logger.error(f" Error al enviar correo de reset a {user.email}: {e}")


def enviar_email_generico(user, subject, template_txt, template_html, context_extra=None):
    """
    Envía un correo genérico al usuario con soporte para HTML.
    Se puede usar para notificaciones, bienvenida, etc.
    """
    context = {
        "user": user,
        "year": now().year,
    }
    if context_extra:
        context.update(context_extra)

    try:
        text_message = render_to_string(template_txt, context)
        html_message = render_to_string(template_html, context)

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@sistema-nomina.com"),
            to=[user.email],
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
    except Exception as e:
        logger.error(f" Error al enviar correo a {user.email}: {e}")
