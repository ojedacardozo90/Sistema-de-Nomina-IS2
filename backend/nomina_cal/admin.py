# ============================================================
# 🧭 ADMINISTRACIÓN DEL MÓDULO NÓMINA (TP IS2 – Ingeniería de Software II)
# Cumple Sprint 2–5: Gestión, cálculo IPS, bonificaciones, reportes y autocompletado dinámico
# ============================================================

from django.contrib import admin, messages
from django.utils.html import format_html
from django.http import HttpResponse
from django.contrib.admin import SimpleListFilter
from datetime import date
import io, openpyxl
from reportlab.pdfgen import canvas
from django.db.models import Sum

# Modelos
from .models import Concepto, SalarioMinimo, Liquidacion, DetalleLiquidacion
#from .utils_email import enviar_recibo_email

from .models_descuento import Descuento

#from .utils import calcular_liquidacion

# ============================================================
# 🔹 ADMIN: CONCEPTO SALARIAL
# ============================================================
@admin.register(Concepto)
class ConceptoAdmin(admin.ModelAdmin):
    list_display = (
        "descripcion",
        "es_debito",
        "es_recurrente",
        "afecta_ips",
        "para_aguinaldo",
        "created_at",
    )
    list_filter = ("es_debito", "es_recurrente", "afecta_ips", "para_aguinaldo")
    search_fields = ("descripcion",)
    ordering = ("descripcion",)
    readonly_fields = ("created_at", "updated_at")


# ============================================================
# 🔹 ADMIN: SALARIO MÍNIMO LEGAL
# ============================================================
@admin.register(SalarioMinimo)
class SalarioMinimoAdmin(admin.ModelAdmin):
    list_display = ("monto", "vigente_desde", "vigente")
    list_filter = ("vigente_desde", "vigente")
    ordering = ("-vigente_desde",)
    search_fields = ("vigente_desde",)


# ============================================================
# 🔹 ADMIN: DESCUENTOS
# ============================================================
@admin.register(Descuento)
class DescuentoAdmin(admin.ModelAdmin):
    list_display = (
        "empleado",
        "tipo",
        "descripcion",
        "monto",
        "fecha_inicio",
        "fecha_fin",
        "recurrente",
        "activo",
    )
    list_filter = ("tipo", "recurrente", "activo")
    search_fields = ("empleado__nombre", "empleado__cedula", "descripcion")
    ordering = ("-fecha_inicio",)
    date_hierarchy = "fecha_inicio"


# ============================================================
# 🔹 ADMIN: DETALLE DE LIQUIDACIÓN
# ============================================================
@admin.register(DetalleLiquidacion)
class DetalleLiquidacionAdmin(admin.ModelAdmin):
    list_display = ("liquidacion", "concepto", "monto", "created_at")
    list_filter = ("concepto__descripcion",)
    search_fields = ("liquidacion__empleado__nombre", "concepto__descripcion")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


# ============================================================
# 🔹 INLINE: Detalles dentro de Liquidación
# ============================================================
class DetalleInline(admin.TabularInline):
    model = DetalleLiquidacion
    extra = 0
    readonly_fields = ("concepto", "monto", "created_at", "updated_at")


# ============================================================
# 🔹 FILTRO PERSONALIZADO: IPS aplicado
# ============================================================
class IPSFilter(SimpleListFilter):
    title = "Con IPS aplicado"
    parameter_name = "con_ips"

    def lookups(self, request, model_admin):
        return (("si", "✅ Con IPS"), ("no", "❌ Sin IPS"))

    def queryset(self, request, queryset):
        if self.value() == "si":
            return queryset.filter(detalles__concepto__descripcion__icontains="IPS").distinct()
        if self.value() == "no":
            return queryset.exclude(detalles__concepto__descripcion__icontains="IPS").distinct()
        return queryset


# ============================================================
# 🔹 ADMIN: LIQUIDACIÓN
# ============================================================
@admin.register(Liquidacion)
class LiquidacionAdmin(admin.ModelAdmin):
    list_display = (
        "empleado",
        "mes",
        "anio",
        "sueldo_base",
        "mostrar_total_ingresos",
        "mostrar_total_descuentos",
        "mostrar_neto_coloreado",
        "estado_ips",
        "estado_bonificacion",
        "resumen_mes",
        "cerrada",
        "enviado_email",  # 👈 nuevo campo
        "fecha_envio",    # 👈 nuevo campo
        
    )
    list_filter = ("anio", "mes", "cerrada", IPSFilter)
    search_fields = ("empleado__nombre", "empleado__apellido", "empleado__cedula")
    readonly_fields = (
        "total_ingresos",
        "total_descuentos",
        "neto_cobrar",
        "created_at",
        "updated_at",
    )
    inlines = [DetalleInline]
    actions = [
        "calcular_ahora",
        "cerrar_liquidacion",
        "exportar_excel_seleccionadas",
        "exportar_pdf_seleccionadas",
        
    ]
    ordering = ("-anio", "-mes")
    

        # ============================================================
    # 📧 ENVIAR RECIBOS POR CORREO (PDF)
    # ============================================================
    @admin.action(description="📤 Enviar recibos seleccionados por correo")
    def enviar_recibos_email(self, request, queryset):
        """Envía los recibos PDF por correo a los empleados seleccionados."""
        enviados = 0
        sin_correo = 0
        errores = 0

        for liq in queryset:
            try:
                if getattr(liq, "enviado_email", False):
                    continue  # ya enviado antes

                if not getattr(liq.empleado, "email", None):
                    sin_correo += 1
                    continue

                enviado = enviar_recibo_email(liq)
                if enviado:
                    enviados += 1
            except Exception as e:
                errores += 1
                self.message_user(request, f"⚠️ Error al enviar a {liq}: {e}", level=messages.ERROR)

        msg = f"✅ {enviados} recibos enviados correctamente."
        if sin_correo:
            msg += f" ⚠️ {sin_correo} empleados sin correo."
        if errores:
            msg += f" ❌ {errores} errores de envío."
        self.message_user(request, msg, level=messages.SUCCESS)



    # ============================================================
    # 🧩 NUEVO MÉTODO PARA AUTOCOMPLETAR SUELDO BASE
    # ============================================================
    def save_model(self, request, obj, form, change):
        if not change or obj.sueldo_base == 0:
            obj.sueldo_base = obj.empleado.salario_base or 0
        super().save_model(request, obj, form, change)

    # ============================================================
    # ⚙️ ACCIONES PERSONALIZADAS
    # ============================================================
    @admin.action(description="🧮 Calcular ahora")
    def calcular_ahora(self, request, queryset):
        contador = 0
        for liq in queryset:
            try:
                calcular_liquidacion(liq)
                contador += 1
            except Exception as e:
                self.message_user(request, f"⚠️ Error en {liq}: {e}", level=messages.ERROR)
        self.message_user(
            request,
            f"✅ {contador} liquidaciones recalculadas correctamente.",
            level=messages.SUCCESS,
        )

    @admin.action(description="🔒 Cerrar liquidación seleccionada")
    def cerrar_liquidacion(self, request, queryset):
        for liq in queryset:
            liq.cerrada = True
            liq.save()
        self.message_user(request, "🔒 Liquidación cerrada correctamente.", level=messages.SUCCESS)

    # ============================================================
    # 📤 EXPORTAR SELECCIONADAS (Excel / PDF)
    # ============================================================
    @admin.action(description="📊 Exportar seleccionadas a Excel")
    def exportar_excel_seleccionadas(self, request, queryset):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Liquidaciones"
        ws.append(["Empleado", "Cédula", "Mes/Año", "Neto a Cobrar"])
        for l in queryset:
            ws.append([l.empleado.nombre, l.empleado.cedula, f"{l.mes}/{l.anio}", float(l.neto_cobrar)])
        total_general = sum([l.neto_cobrar for l in queryset])
        ws.append(["", "", "TOTAL", float(total_general)])
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        response = HttpResponse(
            buffer,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="liquidaciones_seleccionadas.xlsx"'
        return response

    @admin.action(description="📄 Exportar seleccionadas a PDF")
    def exportar_pdf_seleccionadas(self, request, queryset):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(180, 800, "Reporte de Liquidaciones Seleccionadas")
        y = 770
        for l in queryset:
            p.setFont("Helvetica", 10)
            p.drawString(
                50,
                y,
                f"{l.empleado.nombre} ({l.empleado.cedula}) - {l.mes}/{l.anio} - {l.neto_cobrar} Gs",
            )
            y -= 20
            if y < 50:
                p.showPage()
                y = 770
        p.drawString(50, 40, f"Generado el {date.today().strftime('%d/%m/%Y')}")
        p.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type="application/pdf")

    # ============================================================
    # 🔎 INDICADORES VISUALES Y FORMATOS
    # ============================================================
    def estado_ips(self, obj):
        detalle = obj.detalles.filter(concepto__descripcion__icontains="IPS").exists()
        icono = "✅" if detalle else "❌"
        texto = "Sí" if detalle else "No"
        return format_html("{} <b>{}</b>", icono, texto)
    estado_ips.short_description = "IPS 9% Aplicado"

    def estado_bonificacion(self, obj):
        detalle = obj.detalles.filter(concepto__descripcion__icontains="hijo").exists()
        icono = "✅" if detalle else "❌"
        texto = "Sí" if detalle else "No"
        return format_html("{} <b>{}</b>", icono, texto)
    estado_bonificacion.short_description = "Bonif. por Hijos"

    def mostrar_total_ingresos(self, obj):
        return f"{float(obj.total_ingresos):,.0f} Gs"
    mostrar_total_ingresos.short_description = "Total Ingresos"

    def mostrar_total_descuentos(self, obj):
        return f"{float(obj.total_descuentos):,.0f} Gs"
    mostrar_total_descuentos.short_description = "Total Descuentos"

    def mostrar_neto_coloreado(self, obj):
        color = "#16a085" if obj.neto_cobrar > 0 else "#e74c3c"
        valor = f"{float(obj.neto_cobrar):,.0f} Gs"
        return format_html('<b><span style="color:{};">💰 {}</span></b>', color, valor)
    mostrar_neto_coloreado.short_description = "Neto a Cobrar"

    # ============================================================
    # 🧮 RESUMEN POR MES Y GENERAL
    # ============================================================
    def resumen_mes(self, obj):
        total_mes = (
            Liquidacion.objects.filter(mes=obj.mes, anio=obj.anio)
            .aggregate(total=Sum("neto_cobrar"))["total"]
            or 0
        )
        total_formateado = "{:,.0f}".format(float(total_mes))
        return format_html('<span style="color:#2c3e50;"><b>{} Gs</b></span>', total_formateado)
    resumen_mes.short_description = "💼 Total del Mes"

    # ============================================================
    # 📊 RESUMEN GLOBAL EN PANTALLA (QUERYSET FILTRADO)
    # ============================================================
    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            qs = response.context_data["cl"].queryset
            resumen = qs.aggregate(
                total_general=Sum("neto_cobrar"),
                total_ingresos=Sum("total_ingresos"),
                total_descuentos=Sum("total_descuentos"),
            )
            extra_context = response.context_data
            extra_context["summary"] = {
                "total_ingresos": resumen["total_ingresos"] or 0,
                "total_descuentos": resumen["total_descuentos"] or 0,
                "total_general": resumen["total_general"] or 0,
            }
        except Exception:
            pass
        return response

    # ============================================================
    # 🧠 NUEVO: CARGAR SCRIPT JS DE AUTOCOMPLETADO DINÁMICO
    # ============================================================
    class Media:
        js = ("nomina_cal/js/autocompletar_sueldo.js",)
