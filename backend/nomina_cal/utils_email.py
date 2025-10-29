# ============================================================
# 📧 utils_email.py — Generación y envío de Recibos (IS2 Grupo 1)
# Sistema de Nómina — Ingeniería de Software II
# ============================================================

import io
from datetime import date
from decimal import Decimal
from django.core.mail import EmailMessage
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from django.conf import settings

# ============================================================
# 🧾 GENERADOR DE PDF PROFESIONAL (membrete IS2 Grupo 1)
# ============================================================
def generar_recibo_pdf(liquidacion):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=30, leftMargin=30,
                            topMargin=40, bottomMargin=30)

    styles = getSampleStyleSheet()
    elements = []

    # ------------------------------------------------------------
    # 🟦 Encabezado
    # ------------------------------------------------------------
    encabezado = """
    <para align=center>
    <b><font size=14 color="#0b5394">SISTEMA DE NÓMINA — IS2 GRUPO 1</font></b><br/>
    <font size=11 color="#555555">Departamento de RRHH — Gestión de Salarios</font><br/>
    <font size=10 color="#777777">Fecha de emisión: {}</font>
    </para>
    """.format(date.today().strftime("%d/%m/%Y"))
    elements.append(Paragraph(encabezado, styles["Normal"]))
    elements.append(Spacer(1, 12))

    # ------------------------------------------------------------
    # 👤 Datos del empleado
    # ------------------------------------------------------------
    empleado = liquidacion.empleado
    info = [
        ["Empleado:", f"{empleado.nombre}"],
        ["Cédula:", f"{empleado.cedula}"],
        ["Cargo:", f"{empleado.cargo or '-'}"],
        ["Periodo:", f"{liquidacion.mes}/{liquidacion.anio}"],
    ]

    tabla_info = Table(info, colWidths=[90 * mm, 90 * mm])
    tabla_info.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dae3f3")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.gray),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.gray),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    elements.append(tabla_info)
    elements.append(Spacer(1, 14))

    # ------------------------------------------------------------
    # 💵 Detalle de conceptos
    # ------------------------------------------------------------
    data = [["Concepto", "Monto (Gs)"]]
    for det in liquidacion.detalles.all():
        data.append([det.concepto.descripcion, f"{det.monto:,.0f}"])

    tabla = Table(data, colWidths=[110 * mm, 50 * mm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b5394")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.gray),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.gray),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
    ]))
    elements.append(tabla)
    elements.append(Spacer(1, 14))

    # ------------------------------------------------------------
    # 📊 Totales
    # ------------------------------------------------------------
    total_ing = f"{liquidacion.total_ingresos:,.0f}"
    total_desc = f"{liquidacion.total_descuentos:,.0f}"
    neto = f"{liquidacion.neto_cobrar:,.0f}"

    totales = [
        ["Total Ingresos:", total_ing],
        ["Total Descuentos:", total_desc],
        ["Neto a Cobrar:", neto],
    ]

    tabla_tot = Table(totales, colWidths=[100 * mm, 60 * mm])
    tabla_tot.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("TEXTCOLOR", (0, 2), (-1, 2), colors.HexColor("#0b5394")),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    elements.append(tabla_tot)
    elements.append(Spacer(1, 20))

    # ------------------------------------------------------------
    # ✍️ Pie de página
    # ------------------------------------------------------------
    pie = """
    <para align=center>
    <font size=9 color="#777777">
    Sistema desarrollado por <b>IS2 Grupo 1</b> — Ingeniería de Software II<br/>
    Universidad Nacional de Asunción — Facultad Politécnica<br/>
    </font>
    </para>
    """
    elements.append(Paragraph(pie, styles["Normal"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer

# ============================================================
# ✉️ FUNCIÓN DE ENVÍO DE CORREO
# ============================================================
def enviar_recibo_email(liquidacion):
    empleado = liquidacion.empleado
    email = getattr(empleado, "email", None)
    if not email:
        return False

    pdf_buffer = generar_recibo_pdf(liquidacion)
    pdf_bytes = pdf_buffer.getvalue()

    subject = f"Recibo de Salario — {liquidacion.mes}/{liquidacion.anio}"
    body = (
        f"Estimado/a {empleado.nombre},\n\n"
        f"Adjuntamos su recibo de salario correspondiente al periodo "
        f"{liquidacion.mes}/{liquidacion.anio}.\n\n"
        "Atentamente,\nDepartamento de RRHH — IS2 Grupo 1\n"
    )

    msg = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    msg.attach(filename=f"recibo_{liquidacion.id}.pdf",
               content=pdf_bytes,
               mimetype="application/pdf")
    msg.send(fail_silently=False)
    return True
