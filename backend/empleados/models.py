# Modelos de Empleados y Familiares (TP IS2 - Nómina)
# Cumple con la legislación MTESS sobre bonificación familiar.

from django.db import models
from django.conf import settings
from datetime import date
from django.utils import timezone


# MODELO EMPLEADO
class Empleado(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="empleado",
        null=True,
        blank=True,
        help_text="Usuario asociado al empleado (autenticación en el sistema)."
    )
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150)
    cedula = models.CharField(max_length=20, unique=True)
    fecha_ingreso = models.DateField()
    cargo = models.CharField(max_length=100, blank=True, null=True)
    salario_base = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    # # Campos adicionales sugeridos
    fecha_nacimiento = models.DateField(null=True, blank=True)
    estado_civil = models.CharField(max_length=50, blank=True)

    # Datos adicionales
    telefono = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)

class Meta:
    ordering = ["apellido", "nombre"]
    verbose_name = "Empleado"
    verbose_name_plural = "Empleados"

    # NUEVOS CAMPOS Sprint 6 (para dashboards y reportes)
    AREA_CHOICES = [
        ("ADMIN", "Administración"),
        ("RRHH", "Recursos Humanos"),
        ("IT", "Tecnología"),
        ("VENTAS", "Ventas"),
        ("OTROS", "Otros"),
    ]
    TIPO_CONTRATO_CHOICES = [
        ("INDEFINIDO", "Indefinido"),
        ("PLAZO_FIJO", "Plazo fijo"),
        ("TEMPORAL", "Temporal"),
    ]

    area = models.CharField(
        max_length=20,
        choices=AREA_CHOICES,
        default="OTROS",
        blank=True,
        help_text="Departamento o área donde trabaja el empleado."
    )
    tipo_contrato = models.CharField(
        max_length=20,
        choices=TIPO_CONTRATO_CHOICES,
        default="INDEFINIDO",
        blank=True,
        help_text="Tipo de contrato laboral (indefinido, temporal, etc.)."
    )

    
    # Métodos existentes
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cedula}"

    @property
    def antiguedad(self) -> int:
        """Retorna la antigüedad en años del empleado."""
        return (date.today().year - self.fecha_ingreso.year) if self.fecha_ingreso else 0

   
    #  Meta para orden y nombre legible
    class Meta:
        ordering = ["apellido", "nombre"]
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"



#  MODELO HIJO / DEPENDIENTE

class Hijo(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="hijos")
    nombre = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField()

    #  Campos actualizados según requisitos legales
    residente = models.BooleanField(default=True, help_text="Reside en Paraguay")
    certificado_nacimiento = models.FileField(
        upload_to="certificados/", null=True, blank=True,
        help_text="Archivo escaneado del certificado de nacimiento"
    )
    vida_residencia = models.FileField(
        upload_to="residencias/", null=True, blank=True,
        help_text="Comprobante de vida y residencia"
    )
    fecha_vencimiento_residencia = models.DateField(
        null=True, blank=True, help_text="Fecha de vencimiento del comprobante de residencia"
    )

    activo = models.BooleanField(default=True)
class Meta:
    ordering = ["nombre"]
    verbose_name = "Hijo"
    verbose_name_plural = "Hijos"

    def __str__(self):
        
        return f"{self.nombre} ({self.empleado.nombre})"

    
    #  Validaciones automáticas
    
    def edad(self) -> int:
        """Calcula la edad actual del hijo."""
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def es_menor(self) -> bool:
        """Determina si el hijo es menor de 18 años."""
        return self.edad() < 18

    def residencia_valida(self) -> bool:
        """Verifica si el certificado de residencia está vigente."""
        if not self.residente:
            return False
        if self.fecha_vencimiento_residencia:
            return self.fecha_vencimiento_residencia >= timezone.now().date()
        return True  # si no tiene vencimiento cargado, se asume válida

    
    # Propiedades para usar fuera del serializer
    
    @property
    def edad_actual(self):
        """Edad actual (propiedad accesible sin llamar al método)."""
        return self.edad()

    @property
    def es_menor_edad(self):
        """Propiedad booleana que indica si el hijo es menor de edad."""
        return self.es_menor()

        #  Meta para orden y nombre legible
    
    class Meta:
        ordering = ["nombre"]
        verbose_name = "Hijo"
        verbose_name_plural = "Hijos"


#  HISTORIAL DE CARGOS/SALARIOS (para auditoría de cambios)

class HistorialCargoSalario(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name="historial_cargos")
    cargo = models.CharField(max_length=100)
    salario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-fecha_inicio"]
        verbose_name = "Historial de Cargo y Salario"
        verbose_name_plural = "Historiales de Cargos y Salarios"

    def __str__(self):
        return f"{self.empleado} | {self.cargo} | {self.salario} | {self.fecha_inicio} - {self.fecha_fin or 'Actual'}"
