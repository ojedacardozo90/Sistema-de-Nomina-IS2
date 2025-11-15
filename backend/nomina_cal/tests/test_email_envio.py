from django.urls import reverse
from rest_framework.test import APITestCase
from empleados.models import Empleado
from nomina_cal.models import Liquidacion
from nomina_cal.models_envio import EnvioCorreo
from django.contrib.auth import get_user_model

User = get_user_model()

class EnvioReciboTest(APITestCase):
    def setUp(self):
        # # Usuario autenticado (simula RRHH)
        user = User.objects.create_user(username="rrhh", password="12345", is_staff=True)
        self.client.force_authenticate(user=user)

        # # Crear empleado y liquidación simulada
        emp = Empleado.objects.create(
            nombre="Ana",
            apellido="Rojas",
            cedula="123",
            email="ana@.mil.py",
            fecha_ingreso="2020-01-01"
        )
        self.liq = Liquidacion.objects.create(
            empleado=emp,
            mes=10,
            anio=2025,
            neto_cobrar=2000000
        )

    def test_envio_recibo_exitoso(self):
        url = reverse("enviar_recibo", args=[self.liq.id])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(Liquidacion.objects.get(id=self.liq.id).enviado_email)
        self.assertEqual(EnvioCorreo.objects.count(), 1)

    def test_envio_recibo_error_sin_email(self):
        self.liq.empleado.email = ""
        self.liq.empleado.save()
        url = reverse("enviar_recibo", args=[self.liq.id])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 400)
