import io, csv
import pandas as pd
from decimal import Decimal
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from empleados.models import Empleado
from nomina_cal.models import Liquidacion
from django.db import transaction

# Helpers
def _to_decimal(val):
    if val in (None, "", "NaN"):
        return Decimal("0")
    try:
        return Decimal(str(val)).quantize(Decimal("0.01"))
    except:
        return Decimal("0")

def _read_dataframe(uploaded_file):
    name = (uploaded_file.name or "").lower()
    content = uploaded_file.read()
    if name.endswith(".csv"):
        return pd.read_csv(io.BytesIO(content))
    elif name.endswith(".xlsx") or name.endswith(".xls"):
        return pd.read_excel(io.BytesIO(content))
    else:
        raise ValueError("Formato no soportado. Use .csv o .xlsx")

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def importar_empleados(request):
    """
    Espera columnas (CSV/Excel):
    nombre,apellido,cedula,email,telefono,salario_base,activo(1/0)
    """
    f = request.FILES.get("archivo")
    if not f:
        return Response({"error": "Falta el archivo"}, status=400)

    try:
        df = _read_dataframe(f).fillna("")
        required = {"nombre","apellido","cedula","email","telefono","salario_base","activo"}
        if not required.issubset(set(map(str.lower, df.columns))):
            return Response({"error": "Columnas requeridas: " + ", ".join(sorted(required))}, status=400)

        creados, actualizados = 0, 0
        with transaction.atomic():
            for _, row in df.iterrows():
                cedula = str(row.get("cedula")).strip()
                if not cedula:
                    continue
                defaults = dict(
                    nombre=str(row.get("nombre")).strip(),
                    apellido=str(row.get("apellido")).strip(),
                    email=str(row.get("email")).strip(),
                    telefono=str(row.get("telefono")).strip(),
                    salario_base=_to_decimal(row.get("salario_base")),
                    activo=bool(int(row.get("activo") or 1)),
                )
                emp, created = Empleado.objects.update_or_create(cedula=cedula, defaults=defaults)
                if created: creados += 1
                else: actualizados += 1

        return Response({"ok": True, "creados": creados, "actualizados": actualizados})
    except Exception as e:
        return Response({"error": str(e)}, status=400)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def importar_liquidaciones(request):
    """
    Espera columnas (CSV/Excel):
    cedula,mes,anio,neto_cobrar,total_ingresos,total_descuentos,cerrada(1/0)
    """
    f = request.FILES.get("archivo")
    if not f:
        return Response({"error": "Falta el archivo"}, status=400)

    try:
        df = _read_dataframe(f).fillna("")
        required = {"cedula","mes","anio","neto_cobrar","total_ingresos","total_descuentos","cerrada"}
        if not required.issubset(set(map(str.lower, df.columns))):
            return Response({"error": "Columnas requeridas: " + ", ".join(sorted(required))}, status=400)

        creadas, actualizadas, sin_empleado = 0, 0, 0
        with transaction.atomic():
            for _, row in df.iterrows():
                cedula = str(row.get("cedula")).strip()
                try:
                    emp = Empleado.objects.get(cedula=cedula)
                except Empleado.DoesNotExist:
                    sin_empleado += 1
                    continue

                mes = int(row.get("mes"))
                anio = int(row.get("anio"))
                defaults = dict(
                    empleado=emp,
                    sueldo_base=emp.salario_base,
                    total_ingresos=_to_decimal(row.get("total_ingresos")),
                    total_descuentos=_to_decimal(row.get("total_descuentos")),
                    neto_cobrar=_to_decimal(row.get("neto_cobrar")),
                    cerrada=bool(int(row.get("cerrada") or 0)),
                )
                liq, created = Liquidacion.objects.update_or_create(
                    empleado=emp, mes=mes, anio=anio, defaults=defaults
                )
                if created: creadas += 1
                else: actualizadas += 1

        return Response({"ok": True, "creadas": creadas, "actualizadas": actualizadas, "sin_empleado": sin_empleado})
    except Exception as e:
        return Response({"error": str(e)}, status=400)
