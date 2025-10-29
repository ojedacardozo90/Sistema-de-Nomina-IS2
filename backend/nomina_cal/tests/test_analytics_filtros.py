from rest_framework.test import APITestCase
from empleados.models import Empleado
from nomina_cal.models import Liquidacion

class AnalyticsTest(APITestCase):
    def setUp(self):
        e1 = Empleado.objects.create(
            nombre="Juan",
            apellido="Lopez",
            area="RRHH",
            tipo_contrato="INDEFINIDO",
            fecha_ingreso="2020-01-01"
        )
        e2 = Empleado.objects.create(
            nombre="Lucia",
            apellido="Benitez",
            area="IT",
            tipo_contrato="TEMPORAL",
            fecha_ingreso="2021-01-01"
        )
        Liquidacion.objects.create(empleado=e1, mes=10, anio=2025, neto_cobrar=2500000)
        Liquidacion.objects.create(empleado=e2, mes=10, anio=2025, neto_cobrar=3000000)

    def test_kpis_endpoint(self):
        resp = self.client.get("/api/nomina_cal/analytics/kpis/?mes=10&anio=2025")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("empleados_activos", resp.json())

    def test_distribucion_area(self):
        resp = self.client.get("/api/nomina_cal/analytics/distribucion-area/?mes=10&anio=2025")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("series", resp.json())

    def test_distribucion_contrato(self):
        resp = self.client.get("/api/nomina_cal/analytics/distribucion-contrato/?mes=10&anio=2025")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("series", resp.json())
