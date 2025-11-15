from django.test import TestCase
from empleados.models import Empleado
from nomina_cal.utils.recibos import generar_pdf_recibo

class PdfTest(TestCase):
    def test_generar_recibo_pdf(self):
        empleado = Empleado.objects.create(nombre="Bianca", salario_base=3000000)
        path = generar_pdf_recibo(empleado, "Octubre 2025", 2700000)
        self.assertTrue(path.endswith(".pdf"))
        print(" Recibo PDF generado correctamente:", path)
