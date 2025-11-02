# ============================================================
# ⚙️ apps.py — Configuración de la aplicación Nómina
# ------------------------------------------------------------
# Se encarga de registrar las señales automáticas para el envío
# de recibos PDF al cerrar una liquidación.
# ============================================================

from django.apps import AppConfig

class NominaCalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nomina_cal"
    verbose_name = "Cálculo de Nómina"

    def ready(self):
        # 🧩 Importa las señales al iniciar Django
        

        from . import signals  # noqa

    

