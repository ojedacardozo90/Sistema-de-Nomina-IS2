#
# email_api.py — Envío de correos usando SendGrid API HTTP
# Sistema de Nómina IS2 —  / 

# Permite enviar correos desde cualquier parte de Django
# sin depender del backend SMTP.
#

import os
from pathlib import Path
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


# # Cargar .env (por si no está cargado aún)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def enviar_correo_api(asunto, mensaje, destinatarios, remitente=None):
    """
    Envía un correo usando la API HTTP de SendGrid.
    :param asunto: Asunto del mensaje.
    :param mensaje: Contenido de texto plano.
    :param destinatarios: Lista de emails destino.
    :param remitente: Email remitente (por defecto el verificado).
    :return: Código de respuesta HTTP (202 = éxito).
    """
    api_key = os.getenv("EMAIL_HOST_PASSWORD")
    from_email = remitente or os.getenv("DEFAULT_FROM_EMAIL", "ojeda.cardozo90@gmail.com")

    if not api_key:
        print(" No se encontró la API Key de SendGrid.")
        return None

    try:
        sg = SendGridAPIClient(api_key)
        msg = Mail(
            from_email=from_email,
            to_emails=destinatarios,
            subject=asunto,
            plain_text_content=mensaje,
        )
        response = sg.send(msg)
        print(f" Correo enviado correctamente ({response.status_code})")
        return response.status_code
    except Exception as e:
        print(f" Error al enviar correo: {e}")
        return None
