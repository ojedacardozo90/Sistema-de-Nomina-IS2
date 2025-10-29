# ============================================================
# ✅ PRUEBA REAL DE NÓMINA (10 EMPLEADOS)
# Sistema de Nómina IS2 - FPUNA / FAP
# ------------------------------------------------------------
# Genera 10 empleados, calcula IPS, bonificación por hijo
# y genera PDF de recibos.
# ============================================================

from django.test import TestCase
from empleados.models import Empleado
from nomina_cal.models import Concepto
from nomina_cal.utils.recibos import generar_pdf_recibo

class NominaReal10Test(TestCase):

    def setUp(self):
        """Crea datos iniciales"""
        print("\n🧾 INICIO DE PRUEBA REAL DE NÓMINA (10 EMPLEADOS)")

        self.salario_minimo = 2681266  # Gs

        # Crear conceptos base
        Concepto.objects.create(
            descripcion="Salario Base", es_debito=False, afecta_ips=True, para_aguinaldo=True
        )
        Concepto.objects.create(
            descripcion="IPS", es_debito=True, afecta_ips=False, para_aguinaldo=False
        )
        Concepto.objects.create(
            descripcion="Bonificación por hijo", es_debito=False, afecta_ips=False, para_aguinaldo=False
        )

        # Crear 10 empleados (5 con hijos)
        self.empleados = []
        for i in range(1, 11):
            tiene_hijos = i <= 5
            emp = Empleado.objects.create(
                nombre=f"Empleado{i}",
                apellido="Test",
                ci=f"123456{i}",
                cargo="Técnico",
                salario_base=2500000 + i * 250000,
                cantidad_hijos=2 if tiene_hijos else 0,
            )
            self.empleados.append(emp)

    def test_calculo_nomina(self):
        """Calcula IPS, bonificación e imprime resultados"""
        total_general = 0
        periodo = "Octubre 2025"

        for e in self.empleados:
            # IPS 9% sobre salario imponible
            ips = e.salario_base * 0.09

            # Bonificación por hijo (5% SMO por cada hijo si gana < 3 SMO)
            bono = 0
            if e.salario_base < self.salario_minimo * 3:
                bono = e.cantidad_hijos * (self.salario_minimo * 0.05)

            total = e.salario_base - ips + bono
            total_general += total

            # Mostrar resultado
            print(f"✅ {e.nombre} | Base: {e.salario_base:,} | IPS: {int(ips):,} | Bono: {int(bono):,} | Neto: {int(total):,}")

            # Generar recibo PDF
            path = generar_pdf_recibo(e, periodo, total)
            print(f"📄 Recibo generado: {path}")

        print(f"\n💰 Total general de nómina: {int(total_general):,} Gs.")
        print("✅ PRUEBA FINALIZADA CON ÉXITO\n")
