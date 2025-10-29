from django.apps import AppConfig

class NominaCalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "nomina_cal"
   
   
 
    def ready(self):
        # Importa señales al iniciar la app
        from . import signals  # noqa