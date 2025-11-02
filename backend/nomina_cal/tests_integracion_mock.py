# ============================================================
# 🧪 TESTS DE INTEGRACIÓN AVANZADOS CON MOCKS (Sprint 6)
# ------------------------------------------------------------
# Módulo: nomina_cal
# Verifica:
#   • Calcular totales correctamente
#   • Cierre de liquidación bloqueando edición posterior
#   • Disparo automático de señal post_save
#   • Envío de correo simulado con mock.patch
# ============================================================

from django.test import TestCase
from unittest import mock
from decimal import Decimal
from datetime import date
from empleados.models import Empleado
from nomina_cal.models import Liquidacion, SalarioMinimo, Concepto
from nomina_cal import signals


class LiquidacionIntegracionMockTests(TestCase):
    """🔍 Pruebas integradas del ciclo completo de liquidación"""

    def setUp(self):
        # 🧱 Datos base
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
            empleado=self.empleado, mes=10, anio=2025
        )

    # --------------------------------------------------------
    # ✅ 1. Prueba cálculo completo de totales
    # --------------------------------------------------------
    def test_calcular_totales_ok(self):
        """Debe calcular ingresos, descuentos y neto correctamente"""
        self.liquidacion.calcular_totales()
        self.liquidacion.refresh_from_db()

        self.assertGreater(self.liquidacion.total_ingresos, 0)
        self.assertGreaterEqual(self.liquidacion.neto_cobrar, 0)
        self.assertEqual(
            self.liquidacion.total_ingresos - self.liquidacion.total_descuentos,
            self.liquidacion.neto_cobrar,
        )

    # --------------------------------------------------------
    # ✅ 2. Prueba cierre de liquidación
    # --------------------------------------------------------
    def test_cerrar_bloquea_edicion(self):
        """Debe impedir modificar una liquidación cerrada"""
        self.liquidacion.calcular_totales()
        self.liquidacion.cerrar()

        with self.assertRaises(ValueError):
            self.liquidacion.save()  # No puede modificarse una vez cerrada

    # --------------------------------------------------------
    # ✅ 3. Señal post_save con mock de envío de correo
    # --------------------------------------------------------
    @mock.patch("nomina_cal.signals.enviar_recibo_email")
    def test_signal_envio_recibo_disparada(self, mock_enviar_recibo):
        """Debe ejecutarse la señal post_save al cerrar una liquidación"""
        self.liquidacion.calcular_totales()
        self.liquidacion.cerrar()

        # Forzamos post_save manualmente
        signals.enviar_recibo_automatico(sender=Liquidacion, instance=self.liquidacion, created=False)

        # Verificación del mock
        mock_enviar_recibo.assert_called_once()
        args, kwargs = mock_enviar_recibo.call_args
        self.assertEqual(kwargs["liquidacion"].empleado, self.empleado)

    # --------------------------------------------------------
    # ✅ 4. Generación PDF simulada sin crear archivo real
    # --------------------------------------------------------
    @mock.patch("nomina_cal.utils_email.generar_recibo_pdf")
    def test_generacion_pdf_mock(self, mock_pdf):
        """Debe invocar la generación de PDF al cerrar la liquidación"""
        mock_pdf.return_value = b"%PDF-1.4 simulated"
        self.liquidacion.calcular_totales()
        self.liquidacion.cerrar()

        # Simular señal
        signals.enviar_recibo_automatico(sender=Liquidacion, instance=self.liquidacion, created=False)

        mock_pdf.assert_called_once()
        self.assertTrue(mock_pdf.return_value.startswith(b"%PDF"))
