import os
import django

# Configura el entorno de Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_nomina.settings")
django.setup()

print("Django está inicializado correctamente")
