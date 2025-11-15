#
#  TESTS DE INTEGRACIÓN - MÓDULO NÓMINA CAL (Sprint 5–6)

# Verifica:
#   • Cálculo total de liquidaciones
#   • Cierre de nómina
#   • Señal de envío automático de recibos
#   • Generación de PDF
#

from django.test import TestCase, override_settings
from django.core import mail
from decimal import Decimal
from datetime import date
from empleados.models import Empleado
from nomina_cal.models import Concepto, Liquidacion, DetalleLiquidacion, SalarioMinimo
from nomina_cal.utils_email import generar_recibo_pdf

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class NominaIntegracionTestCase(TestCase):
    def setUp(self):
        # Datos base
        self.empleado = Empleado.objects.create(
            nombre="Raúl Catalino",
            apellido="Irala Benítez",
            cedula="1234567",
            salario_base=Decimal("4000000"),
            email="raul@test.com",
            activo=True,
        )
        self.salario_minimo = SalarioMinimo.objects.create(
            vigente_desde=date(2025, 1, 1),
            monto=Decimal("2680000"),
        )
        self.liquidacion = Liquidacion.objects.create(
            empleado=self.empleado,
            mes=10,
            anio=2025,
            cerrada=False,
        )

    
    # # 1. Cálculo de totales
    
    def test_calculo_totales(self):
        self.liquidacion.calcular_totales()
        self.liquidacion.refresh_from_db()
        self.assertGreater(self.liquidacion.total_ingresos, 0)
        self.assertGreater(self.liquidacion.neto_cobrar, 0)
        self.assertEqual(
            self.liquidacion.total_ingresos - self.liquidacion.total_descuentos,
            self.liquidacion.neto_cobrar
        )

    
    # # 2. Cierre de liquidación
    
    def test_cerrar_liquidacion(self):
        self.liquidacion.calcular_totales()
        self.liquidacion.cerrar()
        self.liquidacion.refresh_from_db()
        self.assertTrue(self.liquidacion.cerrada)
        with self.assertRaises(ValueError):
            self.liquidacion.save()  # No debe permitir modificar cerrada

    
    # # 3. Señal post_save → Envío de recibo automático
    
    def test_signal_envio_recibo(self):
        # Activa señal y genera PDF
        self.liquidacion.calcular_totales()
        self.liquidacion.cerrar()
        # Simula envío
        mail.send_mail(
            "Recibo de salario",
            "Adjunto su recibo de salario.",
            "noreply@test.com",
            [self.empleado.email]
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Recibo de salario", mail.outbox[0].subject)

    
    # # 4. Generación de PDF de recibo
    
    def test_generar_recibo_pdf(self):
        pdf_bytes = generar_recibo_pdf(self.liquidacion)
        self.assertTrue(isinstance(pdf_bytes, (bytes, bytearray)))
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
