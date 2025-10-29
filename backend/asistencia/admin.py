from django.contrib import admin
from .models import Fichada, RegistroAsistencia

@admin.register(Fichada)
class FichadaAdmin(admin.ModelAdmin):
    list_display = ("empleado", "tipo", "timestamp", "origen")
    list_filter = ("tipo", "origen")
    search_fields = ("empleado__nombre", "empleado__cedula")

@admin.register(RegistroAsistencia)
class RegistroAsistenciaAdmin(admin.ModelAdmin):
    list_display = ("empleado", "fecha", "hora_entrada", "hora_salida", "minutos_trabajados", "estado")
    list_filter = ("estado", "fecha")
    search_fields = ("empleado__nombre", "empleado__cedula")
