# backend/nomina_cal/utils.py
from .models import Liquidacion

def calcular_liquidacion(liquidacion_id):
    liquidacion = Liquidacion.objects.get(id=liquidacion_id)
    liquidacion.calcular_totales()
    return liquidacion
