# backend/nomina_cal/tasks.py
# ============================================================
# 🚀 Tareas asíncronas con Celery (TP IS2 - Nómina)
# Incluye:
# - Debug de prueba con logger
# - Generación automática de nóminas
# - Envío de recibos de sueldo por email (PDF + HTML)
# - Tarea combinada (generar + enviar)
# ============================================================

from celery import shared_task
from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import date, datetime
from empleados.models import Empleado
from .models import Nomina
from .views import calcular_nomina_internal
import io
from reportlab.pdfgen import canvas
import logging

# Configuración de logger
logger = logging.getLogger(__name__)

# ============================================================
# 🔹 Helper: Generar PDF de recibo
# ============================================================
def generar_pdf_nomina(nomina, empleado):
    """
    Genera un PDF simple en memoria con datos de la nómina.
    Retorna un buffer listo para adjuntar en email.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, 800, "Recibo de Pago")
    p.setFont("Helvetica", 12)
    p.drawString(50, 770, f"Empleado: {empleado.nombre} {empleado.apellido}")
    p.drawString(50, 750, f"Fecha: {nomina.fecha}")
    p.drawString(50, 730, f"Total Neto: {float(nomina.total):,.0f} Gs")
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

# ============================================================
# 🔹 Tarea de prueba
# ============================================================
@shared_task
def debug_task():
    """
    Verifica que Celery está funcionando correctamente.
    """
    mensaje = f"✅ Debug Task ejecutada a las {datetime.now()}"
    logger.info(mensaje)
    return mensaje

# ============================================================
# 🔹 Generar Nóminas Automáticamente
# ============================================================
@shared_task
def generar_nominas_mensuales():
    """
    Genera todas las nóminas de empleados automáticamente.
    👉 Ejecutar a fin de mes con Celery Beat.
    """
    empleados = Empleado.objects.all()
    generadas = []

    for emp in empleados:
        nomina = calcular_nomina_internal(emp)  # ✅ usamos la lógica central
        generadas.append(nomina.id)

    mensaje = f"📊 {len(generadas)} nóminas generadas automáticamente el {date.today()}"
    logger.info(mensaje)
    return mensaje

# ============================================================
# 🔹 Enviar Recibos por Correo (PDF + HTML)
# ============================================================
@shared_task
def enviar_recibos_email():
    """
    Envía un PDF por correo a cada empleado con su último recibo de sueldo.
    - PDF en memoria adjunto.
    - Soporte HTML en cuerpo de email.
    - Envía resumen al administrador.
    """
    enviados = 0

    for empleado in Empleado.objects.all():
        nomina = Nomina.objects.filter(empleado=empleado).last()
        if not nomina or not empleado.usuario.email:  # ✅ validación extra
            continue

        # Generar PDF
        pdf_buffer = generar_pdf_nomina(nomina, empleado)

        # Renderizar cuerpo en HTML
        cuerpo_html = render_to_string(
            "emails/recibo_nomina.html",  # 📄 plantilla HTML en templates/emails/
            {"empleado": empleado, "nomina": nomina}
        )

        # Crear y enviar email
        asunto = f"📩 Recibo de Sueldo - {nomina.fecha}"
        email = EmailMessage(asunto, cuerpo_html, to=[empleado.usuario.email])
        email.content_subtype = "html"  # 👉 especificamos que es HTML
        email.attach("recibo.pdf", pdf_buffer.read(), "application/pdf")
        email.send()

        enviados += 1

    # Notificación al admin con resumen
    if enviados > 0 and hasattr(settings, "EMAIL_HOST_USER"):
        send_mail(
            subject="📊 Resumen de Recibos Enviados",
            message=f"Se enviaron {enviados} recibos correctamente el {date.today()}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=True,
        )

    mensaje = f"📤 {enviados} recibos enviados correctamente"
    logger.info(mensaje)
    return mensaje

# ============================================================
# 🔹 Tarea Combinada (Generar + Enviar)
# ============================================================
@shared_task
def generar_y_enviar_nominas():
    """
    Genera las nóminas del mes y luego envía los recibos.
    👉 Ideal para programar con Celery Beat (ej: 28 de cada mes).
    """
    generar_nominas_mensuales()
    enviar_recibos_email()
    mensaje = f"✅ Nóminas generadas y recibos enviados el {date.today()}"
    logger.info(mensaje)
    return mensaje
