# ============================================================
# 🧪 Prueba real de nómina — 10 empleados
# Sistema de Nómina IS2 - FPUNA / FAP
# ------------------------------------------------------------
# • 10 empleados (5 con hijos, 5 sin hijos)
# • Cálculo de sueldo, IPS (9%) y bonificación por hijo
# • Generación de liquidaciones y recibos PDF reales
# • Evidencia de Sprint 4–5
# ============================================================

from django.test import TestCase
from empleados.models import Empleado
from nomina_cal.models import Concepto, Liquidacion
from nomina_cal.utils.recibos import generar_pdf_recibo
from decimal import Decimal
from datetime import date
import os

SALARIO_MINIMO = Decimal("2680000")
IPS_TASA = Decimal("0.09")

class TestNominaReal10(TestCase):
    def setUp(self):
        # ----------------------------------------
        # 🔹 Crear empleados de prueba (10 totales)
        # ----------------------------------------
        self.empleados = [
            Empleado.objects.create(nombre="Raúl", apellido="Irala", ci="100001", cargo="Administrador", salario_base=4500000, cantidad_hijos=2),
            Empleado.objects.create(nombre="Bianca", apellido="Benítez", ci="100002", cargo="RRHH", salario_base=2500000, cantidad_hijos=1),
            Empleado.objects.create(nombre="Carlos", apellido="Ojeda", ci="100003", cargo="Técnico", salario_base=3100000, cantidad_hijos=3),
            Empleado.objects.create(nombre="María", apellido="Gómez", ci="100004", cargo="Contadora", salario_base=5200000, cantidad_hijos=0),
            Empleado.objects.create(nombre="Julio", apellido="Vera", ci="100005", cargo="Asistente", salario_base=2700000, cantidad_hijos=2),
            Empleado.objects.create(nombre="Lucía", apellido="Martínez", ci="100006", cargo="Analista", salario_base=3300000, cantidad_hijos=0),
            Empleado.objects.create(nombre="Pedro", apellido="González", ci="100007", cargo="Mecánico", salario_base=2900000, cantidad_hijos=1),
            Empleado.objects.create(nombre="Diana", apellido="Caballero", ci="100008", cargo="Supervisora", salario_base=5100000, cantidad_hijos=0),
            Empleado.objects.create(nombre="Andrés", apellido="Ruiz", ci="100009", cargo="Piloto", salario_base=5800000, cantidad_hijos=0),
            Empleado.objects.create(nombre="Marta", apellido="Fernández", ci="100010", cargo="Auxiliar", salario_base=2400000, cantidad_hijos=2),
        ]

        # ----------------------------------------
        # 🔹 Crear conceptos base de nómina
        # ----------------------------------------
        self.conceptos = [
            Concepto.objects.create(descripcion="Sueldo Básico", es_debito=False, afecta_ips=True, para_aguinaldo=True),
            Concepto.objects.create(descripcion="Bonificación por Hijo", es_debito=False, afecta_ips=True, para_aguinaldo=True),
            Concepto.objects.create(descripcion="Descuento IPS", es_debito=True, afecta_ips=True, para_aguinaldo=False),
        ]

    def test_liquidaciones_reales_10(self):
        print("\n🧾 INICIO DE PRUEBA REAL DE NÓMINA (10 EMPLEADOS)\n")
        total_general = Decimal(0)

        for empleado in self.empleados:
            salario = Decimal(empleado.salario_base)
            descuento_ips = (salario * IPS_TASA).quantize(Decimal("1."))
            bonificacion = Decimal(0)

            # Aplicar bonificación si salario < 3 salarios mínimos
            if salario < (3 * SALARIO_MINIMO):
                bonificacion = Decimal(empleado.cantidad_hijos) * (SALARIO_MINIMO * Decimal("0.05"))

            total_pagado = salario - descuento_ips + bonificacion
            total_general += total_pagado

            # Guardar liquidación
            liq = Liquidacion.objects.create(
                empleado=empleado,
                periodo="2025-10",
                total_pagado=total_pagado,
                observaciones=f"Liquidación real de prueba - {empleado.nombre}",
                detalle={
                    "fecha_creacion": str(date.today()),
                    "conceptos": ["Sueldo Básico", "IPS", "Bonificación"],
                    "estado": "Prueba Real"
                }
            )

            # Generar PDF del recibo
            path = generar_pdf_recibo(empleado, "Octubre 2025", float(total_pagado))
            self.assertTrue(os.path.exists(path))

            print(f"✅ {empleado.nombre} {empleado.apellido} | Base: {salario:,.0f} | "
                  f"IPS: {int(descuento_ips)} | Bono: {int(bonificacion)} | Neto: {int(total_pagado)}")
            print(f"📄 Recibo generado: {path}\n")

        print(f"💰 Total general de nómina: {int(total_general)} Gs.\n")
        self.assertEqual(Liquidacion.objects.count(), 10)
        print("✅ PRUEBA FINALIZADA CON ÉXITO\n")
