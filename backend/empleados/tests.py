from django.test import TestCase
from rest_framework.test import APIClient
from empleados.models import Empleado

class EmpleadoTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_crear_empleado(self):
        data = {"nombre": "Carlos", "apellido": "Benítez", "ci": "998811", "cargo": "Técnico", "salario_base": 3500000}
        response = self.client.post("/api/empleados/", data, format="json")
        self.assertEqual(response.status_code, 201)
        print(" CRUD Empleado OK — Registro creado correctamente")
