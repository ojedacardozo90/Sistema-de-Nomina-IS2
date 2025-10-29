# backend/nomina_cal/services/pdf_recibo.py
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

def pdf_recibo_bytes(liq) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    w, h = A4

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, h-50, "Recibo de Sueldo - Sistema de Nómina")

    c.setFont("Helvetica", 10)
    emp = getattr(liq, "empleado", None)
    nombre = getattr(emp, "nombre_completo", None) or f"{getattr(emp,'nombre', '')} {getattr(emp,'apellido','')}".strip()
    c.drawString(40, h-80, f"Empleado: {nombre}")
    c.drawString(40, h-95, f"Periodo: {liq.mes}/{liq.anio}")

    y = h-125
    c.drawString(40, y, "Concepto"); c.drawString(380, y, "Tipo"); c.drawString(430, y, "Monto")
    y -= 15

    for it in liq.detalles.all():
        tipo = "Débito" if it.concepto.es_debito else "Crédito"
        c.drawString(40, y, it.concepto.descripcion[:42])
        c.drawString(380, y, tipo)
        c.drawRightString(520, y, f"{it.monto:,.2f}")
        y -= 14
        if y < 80:
            c.showPage()
            y = h-50

    y -= 10; c.line(40, y, 520, y); y -= 16
    c.drawString(300, y, "Total ingresos:");  c.drawRightString(520, y, f"{liq.total_ingresos:,.2f}"); y -= 14
    c.drawString(300, y, "Total descuentos:");c.drawRightString(520, y, f"{liq.total_descuentos:,.2f}"); y -= 14
    c.setFont("Helvetica-Bold", 11)
    c.drawString(300, y, "NETO A COBRAR:");  c.drawRightString(520, y, f"{liq.neto_cobrar:,.2f}")
    c.showPage(); c.save()

    pdf = buffer.getvalue()
    buffer.close()
    return pdf
