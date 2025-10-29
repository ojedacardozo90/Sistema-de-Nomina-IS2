import os
import django

# 1 Inicializar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_nomina.settings")
django.setup()

# 2 Importar después de inicializar
from nomina_cal.tasks import debug_task

if __name__ == "__main__":
    # Enviar tarea
    result = debug_task.delay()
    print(" Tarea enviada a Celery. ID:", result.id)

    # Esperar respuesta
    print(" Esperando resultado...")
    print(" Resultado:", result.get(timeout=10))
