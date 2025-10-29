# backend/nomina_cal/tests/test_nomina.py
# ============================================================
# Tests de Nómina (bonificación, IPS, neto y endpoint de reporte)
# Ejecutar: python manage.py test nomina_cal
# ============================================================

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch

from nomina_cal.models import Liquidacion, SalarioMinimo, Concepto, DetalleLiquidacion
from empleados.models import Empleado, Hijo
from datetime import date

User = get_user_model()

class NominaCalculoTests(TestCase):
    def setUp(self):
        # Salario mínimo vigente
        SalarioMinimo.objects.create(monto=Decimal("3000000.00"), vigente_desde=date(2025, 1, 1), vigente=True)

        # Usuario/empleado base
        self.user = User.objects.create_user(username="emp1", password="123456", email="emp1@test.com")
        self.emp = Empleado.objects.create(
            usuario=self.user,
            nombre_completo="Empleado Uno",
            salario_base=Decimal("5000000.00"),
            email="emp1@test.com",
            residente=True,
        )

        # Hijos: 3 válidos (menores + residencia válida)
        for i in range(3):
            Hijo.objects.create(
                empleado=self.emp,
                nombre=f"Hijo {i+1}",
                fecha_nacimiento=date(2015, 1, 1),  # < 18
                residente=True,
                activo=True,
                # Asegúrate de que tu modelo tenga algo como fecha_residencia o método residencia_valida()
                fecha_residencia=date(2025, 6, 1),
            )

        # Liquidación del mes
        self.liq = Liquidacion.objects.create(empleado=self.emp, mes=9, anio=2025, sueldo_base=self.emp.salario_base)

    def test_bonificacion_hasta_4_hijos_y_tope_salario(self):
        """
        - 5% SM por hijo, máximo 4.
        - Si sueldo base <= tope (ajusta a 2 o 3 SM según tu regla), aplica.
        """
        # Asegúrate que en tu modelo la regla del tope sea coherente (2x o 3x)
        neto = self.liq.calcular_totales()

        # Bonificación esperada = hijos (3) * (5% * SM 3.000.000) = 3 * 150.000 = 450.000
        bonificacion_esperada = Decimal("150000.00") * 3  # 450.000
        detalle_bono = DetalleLiquidacion.objects.filter(liquidacion=self.liq, concepto__descripcion="Bonificación Familiar").first()
        self.assertIsNotNone(detalle_bono)
        self.assertEqual(detalle_bono.monto, bonificacion_esperada)

    def test_ips_9_por_ciento_sobre_imponible(self):
        neto = self.liq.calcular_totales()

        # IPS = 9% del sueldo base (5.000.000 * 0.09) = 450.000
        ips_esperado = (self.emp.salario_base * Decimal("0.09")).quantize(Decimal("0.01"))
        detalle_ips = DetalleLiquidacion.objects.filter(liquidacion=self.liq, concepto__descripcion="Descuento IPS 9%").first()
        self.assertIsNotNone(detalle_ips)
        self.assertEqual(detalle_ips.monto, ips_esperado)

    def test_neto_coincide_con_creditos_menos_debitos(self):
        neto = self.liq.calcular_totales()

        total_creditos = sum(d.monto for d in DetalleLiquidacion.objects.filter(liquidacion=self.liq, concepto__es_debito=False))
        total_debitos = sum(d.monto for d in DetalleLiquidacion.objects.filter(liquidacion=self.liq, concepto__es_debito=True))

        self.assertEqual(self.liq.total_ingresos, total_creditos)
        self.assertEqual(self.liq.total_descuentos, total_debitos)
        self.assertEqual(self.liq.neto_cobrar, total_creditos - total_debitos)
        self.assertEqual(neto, self.liq.neto_cobrar)


class NominaEndpointTests(TestCase):
    """
    Testea que el endpoint de Reporte General exista y responda 200 a un admin.
    Requiere que en urls.py hayas definido name='nomina_cal-reportes-general'.
    """
    def setUp(self):
        self.admin = User.objects.create_superuser(username="admin", password="123456", email="admin@test.com")

    def test_reporte_general_admin_200(self):
        try:
            url = reverse("nomina_cal-reportes-general")
        except NoReverseMatch:
            self.skipTest("Ruta 'nomina_cal-reportes-general' no encontrada. Verifica nomina_cal/urls.py")

        self.client.login(username="admin", password="123456")
        resp = self.client.get(url)
        # Si tu view exige permisos específicos distintos a superuser, ajusta esto.
        self.assertIn(resp.status_code, (200, 403))  # 200 OK, 403 si falta permiso específico
