# ============================================================
# 🚀 test_sendgrid.py — Prueba independiente de SendGrid API
# ------------------------------------------------------------
# Este script verifica que tu API Key y remitente verificado
# funcionen correctamente, sin pasar por SMTP.
# ============================================================
import os
from pathlib import Path
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Cargar el archivo .env del backend
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


...

# Cargar la API Key directamente del entorno (.env)
API_KEY = os.getenv("EMAIL_HOST_PASSWORD")

# Cambiá los correos si querés probar con otros
FROM_EMAIL = "ojeda.cardozo90@gmail.com"
TO_EMAIL = "ojeda.cardozo90@gmail.com"

# Crear mensaje
message = Mail(
    from_email=FROM_EMAIL,
    to_emails=TO_EMAIL,
    subject="✅ Prueba directa vía API HTTP - Sistema de Nómina IS2",
    plain_text_content="Hola Raúl, este mensaje fue enviado correctamente usando la API HTTP de SendGrid.",
)

print("🔹 Usando API Key:", API_KEY[:10] + "..." if API_KEY else "No encontrada")

try:
    sg = SendGridAPIClient(API_KEY)
    response = sg.send(message)
    print("✅ Enviado correctamente")
    print("🔸 Código de respuesta:", response.status_code)
    print("🔸 Detalles:", response.body)
    print("🔸 Headers:", response.headers)
except Exception as e:
    print("❌ Error al enviar:", e)
