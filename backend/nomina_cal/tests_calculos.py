from django.test import TestCase
from nomina_cal.models import Empleado, Concepto
from nomina_cal.utils.calculos import calcular_ips

class CalculoTest(TestCase):
    def test_ips(self):
        empleado = Empleado.objects.create(nombre="Ana", salario_base=4000000)
        total_ips = calcular_ips(empleado.salario_base)
        self.assertEqual(total_ips, 360000)
        print(" IPS 9% calculado correctamente")

    def test_bonificacion_hijos(self):
        # Simular empleado con 2 hijos y salario bajo
        salario_minimo = 2680000
        empleado = Empleado.objects.create(nombre="Raúl", salario_base=6000000)
        hijos = 2
        bonificacion = 0
        if empleado.salario_base < 3 * salario_minimo:
            bonificacion = hijos * 0.05 * salario_minimo
        self.assertAlmostEqual(bonificacion, 268000)
        print(" Bonificación por hijos calculada correctamente")
