#
#  recibos.py — Generador de Recibos de Pago en PDF
# Sistema de Nómina IS2 -  

# • Genera recibos PDF simples y legibles
# • Guarda automáticamente en media/recibos/
#

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import os

def generar_pdf_recibo(empleado, periodo, total):
    """Genera un recibo de pago PDF simple"""
    carpeta = "media/recibos"
    os.makedirs(carpeta, exist_ok=True)
    nombre_archivo = f"recibo_{empleado.nombre}_{empleado.apellido}_{periodo}.pdf"
    path = os.path.join(carpeta, nombre_archivo)

    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(30 * mm, 280 * mm, "FUERZA AÉREA PARAGUAYA")
    c.setFont("Helvetica", 11)
    c.drawString(30 * mm, 270 * mm, f"Recibo de Pago — {periodo}")
    c.line(30 * mm, 268 * mm, 180 * mm, 268 * mm)

    c.setFont("Helvetica", 10)
    c.drawString(30 * mm, 255 * mm, f"Empleado: {empleado.nombre} {empleado.apellido}")
    c.drawString(30 * mm, 248 * mm, f"CI: {empleado.ci}")
    c.drawString(30 * mm, 241 * mm, f"Cargo: {empleado.cargo}")
    c.drawString(30 * mm, 234 * mm, f"Hijos: {empleado.cantidad_hijos}")
    c.drawString(30 * mm, 227 * mm, f"Salario Base: {int(empleado.salario_base):,} Gs.")
    c.drawString(30 * mm, 220 * mm, f"Total Neto a Cobrar: {int(total):,} Gs.")

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(30 * mm, 40 * mm, "Generado automáticamente por el Sistema de Nómina IS2 - ")

    c.showPage()
    c.save()
    return path
