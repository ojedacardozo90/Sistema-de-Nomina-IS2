# backend/usuarios/urls_reset.py
# ============================================================
# 🔐 Rutas para recuperación de contraseña
# ============================================================

from django.urls import path
from . import views

urlpatterns = [
    path("request/", views.reset_password_request, name="reset_password_request"),
    path("confirm/<str:token>/", views.reset_password_confirm, name="reset_password_confirm"),
]
