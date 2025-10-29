# backend/nomina_cal/tests/test_liquidaciones.py
import pytest
from django.urls import reverse
from rest_framework import status
from empleados.models import Empleado, Hijo
from nomina_cal.models import SalarioMinimo, Liquidacion

@pytest.mark.django_db
class TestLiquidaciones:
    def setup_method(self):
        """Inicialización antes de cada test."""
        from usuarios.models import Usuario
        from rest_framework.test import APIClient

        self.client = APIClient()

        # Crear admin y autenticar
        self.admin = Usuario.objects.create_user(
            username="admin_test", password="admin123", rol="admin"
        )
        self.client.force_authenticate(user=self.admin)

        # Crear empleado
        self.empleado = Empleado.objects.create(
            nombre="Juan Pérez",
            cedula="1234567",
            salario_base=3000000,
            usuario=Usuario.objects.create_user(username="empleado_test", password="123", rol="empleado")
        )

        # Salario mínimo vigente
        SalarioMinimo.objects.create(monto=2500000)

    def test_crear_y_calcular_liquidacion(self):
        """Debe crear y calcular una liquidación."""
        liquidacion = Liquidacion.objects.create(empleado=self.empleado, mes=1, anio=2025)
        url = reverse("liquidaciones-calcular", args=[liquidacion.id])
        response = self.client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert "neto_cobrar" in response.json()

    def test_bonificacion_por_hijo(self):
        """Aplica bonificación si cumple condiciones legales."""
        hijo = Hijo.objects.create(
            empleado=self.empleado,
            nombre="Pedro",
            fecha_nacimiento="2015-05-10",  # < 18 años
            residencia="Paraguay"
        )
        liquidacion = Liquidacion.objects.create(empleado=self.empleado, mes=2, anio=2025)
        url = reverse("liquidaciones-calcular", args=[liquidacion.id])
        response = self.client.post(url)
        data = response.json()
        assert any(d["concepto"]["descripcion"] == "Bonificación Familiar por Hijo" for d in data["detalles"])

    def test_dashboard_admin(self):
        """Admin recibe métricas generales."""
        url = reverse("dashboard_admin")
        response = self.client.get(url)
        assert response.status_code == 200
        body = response.json()
        assert "total_empleados" in body
        assert "total_liquidaciones" in body

    def test_empleado_solo_ve_sus_liquidaciones(self):
        """Empleado autenticado solo accede a sus liquidaciones."""
        empleado_user = self.empleado.usuario
        self.client.force_authenticate(user=empleado_user)
        url = reverse("dashboard_empleado")
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.json()["rol"] == "empleado"
