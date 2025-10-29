import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_nomina.settings")

app = Celery("sistema_nomina")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
