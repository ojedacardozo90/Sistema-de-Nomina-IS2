#
#  notificaciones.py — Módulo de Envío Automático de Recibos
# Sistema de Nómina IS2 — FP-UNA / 

# Usa la API HTTP de SendGrid (vía utils/email_api.py)
# para enviar correos con recibos PDF adjuntos a los empleados.
#

import os
from utils.email_api import enviar_correo_api
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64

#
# Función principal: enviar recibo con PDF adjunto
#

def enviar_recibo_pdf(empleado, periodo, pdf_path):
    """
    Envía un correo con el recibo PDF adjunto al empleado.
    Parámetros:
        empleado: instancia del modelo Empleado (con .nombre y .email)
        periodo: texto del periodo (ej. 'Octubre 2025')
        pdf_path: ruta absoluta o relativa del archivo PDF generado
    """
    try:
        #  Verificar que el archivo existe
        if not os.path.exists(pdf_path):
            print(f" No se encontró el archivo PDF: {pdf_path}")
            return None

        #  Leer PDF y convertirlo a base64
        with open(pdf_path, "rb") as f:
            pdf_data = base64.b64encode(f.read()).decode()

        #  Preparar datos del correo
        asunto = f" Recibo de Pago — {periodo}"
        mensaje = (
            f"Hola {empleado.nombre},\n\n"
            f"Adjunto encontrarás tu recibo de pago correspondiente al periodo {periodo}.\n\n"
            "Saludos cordiales,\n"
            "Sistema de Nómina — FP-UNA / "
        )

        #  Crear mensaje con adjunto
        message = Mail(
            from_email=os.getenv("DEFAULT_FROM_EMAIL", "ojeda.cardozo90@gmail.com"),
            to_emails=empleado.email,
            subject=asunto,
            plain_text_content=mensaje,
        )

        # Adjuntar PDF
        attached_file = Attachment(
            FileContent(pdf_data),
            FileName(os.path.basename(pdf_path)),
            FileType("application/pdf"),
            Disposition("attachment")
        )
        message.attachment = attached_file

        #  Enviar con API Key de SendGrid
        sg = SendGridAPIClient(os.getenv("EMAIL_HOST_PASSWORD"))
        response = sg.send(message)

        print(f" Recibo enviado a {empleado.email} ({response.status_code})")
        return response.status_code

    except Exception as e:
        print(f" Error al enviar correo a {empleado.email}: {e}")
        return None


#
#  Función auxiliar (sin adjunto)
#

def notificar_pago_simple(empleado, periodo):
    """
    Envía una notificación sin adjunto informando que el recibo está disponible.
    """
    asunto = f" Recibo disponible — {periodo}"
    mensaje = (
        f"Hola {empleado.nombre},\n\n"
        f"Tu recibo de pago del periodo {periodo} ya está disponible en el sistema.\n\n"
        "Sistema de Nómina — FP-UNA / "
    )
    enviar_correo_api(asunto, mensaje, [empleado.email])

#
# Notificación básica de pago (usada por vistas/usuarios)
#
from utils.email_api import enviar_correo_api

def notificar_pago(empleado, periodo):
    """
    Envía una notificación simple al empleado informando
    que su recibo de pago está disponible.
    """
    asunto = f" Recibo de Pago - {periodo}"
    mensaje = (
        f"Hola {empleado.nombre},\n\n"
        f"Tu recibo de pago correspondiente al periodo {periodo} "
        f"ya está disponible en el sistema.\n\n"
        f"Atentamente,\nRecursos Humanos - Sistema de Nómina IS2"
    )
    if empleado.email:
        enviar_correo_api(asunto, mensaje, [empleado.email])
        print(f" Notificación enviada a {empleado.email}")
    else:
        print(f" El empleado {empleado.nombre} no tiene email registrado.")
