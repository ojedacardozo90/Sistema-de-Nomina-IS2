# backend/nomina_cal/views_pdf.py
from django.http import FileResponse
from utils.email_api import enviar_correo_api  # 👈 agregar import
from nomina_cal.utils.notificaciones import enviar_recibo_pdf


def generar_recibo_pdf(request, empleado_id, periodo):
    # ... tu lógica para generar el PDF ...
    pdf_path = f"media/recibos/{empleado.nombre}_{periodo}.pdf"
    enviar_recibo_pdf(empleado, periodo, pdf_path)  
    # Enviar correo al empleado
    asunto = f"📄 Recibo de Pago - {periodo}"
    mensaje = f"Hola {empleado.nombre}, tu recibo de pago del periodo {periodo} ya está disponible."
    enviar_correo_api(asunto, mensaje, [empleado.email])

    return FileResponse(open(pdf_path, "rb"), content_type="application/pdf")
