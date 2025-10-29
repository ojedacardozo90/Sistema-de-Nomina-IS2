# backend/nomina_cal/services/emailing.py
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from nomina_cal.services.pdf_recibo import pdf_recibo_bytes

def enviar_recibo_liquidacion(liq) -> bool:
    """Genera PDF en memoria y envía por correo al empleado. Marca enviado_email/fecha_envio."""
    email_dest = getattr(getattr(liq.empleado, "usuario", None), "email", None) or getattr(liq.empleado, "email", None)
    if not email_dest:
        return False

    subject = f"Recibo de salario - {liq.mes}/{liq.anio}"
    body = f"Hola {getattr(liq.empleado,'nombre','')}, adjuntamos su recibo de salario."

    msg = EmailMessage(subject=subject, body=body, from_email=settings.DEFAULT_FROM_EMAIL, to=[email_dest])
    pdf = pdf_recibo_bytes(liq)
    filename = f"recibo_{liq.empleado_id}_{liq.mes}_{liq.anio}.pdf"
    msg.attach(filename, pdf, "application/pdf")
    msg.send(fail_silently=False)

    liq.enviado_email = True
    liq.fecha_envio = timezone.now()
    liq.save(update_fields=["enviado_email", "fecha_envio"])
    return True
