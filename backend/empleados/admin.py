from django.contrib import admin
from .models import Empleado, Hijo

# ============================================================
# 👨‍👩‍👧 Inline: permite agregar hijos dentro del formulario del empleado
# ============================================================
class HijoInline(admin.TabularInline):
    model = Hijo
    extra = 1  # muestra una fila vacía para añadir hijo nuevo
    fields = ("nombre", "fecha_nacimiento")  # ✅ quitado 'residente' por ahora
    show_change_link = True

# ============================================================
# 👨‍💼 Panel de administración de Empleados
# ============================================================
@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "cedula", "cargo", "salario_base", "fecha_ingreso")
    search_fields = ("nombre", "cedula")
    list_filter = ("cargo", "fecha_ingreso")
    inlines = [HijoInline]  # 🔹 agrega la sección “Hijos” dentro del empleado

# ============================================================
# 👶 Panel independiente de Hijos (opcional)
# ============================================================
@admin.register(Hijo)
class HijoAdmin(admin.ModelAdmin):
    list_display = ("empleado", "nombre", "fecha_nacimiento")  # ✅ sin 'residente'
    search_fields = ("nombre",)

from .models import Empleado, Hijo, HistorialCargoSalario  # 👈 agrega este import

@admin.register(HistorialCargoSalario)
class HistorialCargoSalarioAdmin(admin.ModelAdmin):
    list_display = ("empleado", "cargo", "salario", "fecha_inicio", "fecha_fin")
    search_fields = ("empleado__nombre", "empleado__cedula", "cargo")
    list_filter = ("cargo",)
