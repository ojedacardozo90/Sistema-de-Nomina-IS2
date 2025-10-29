# backend/conftest.py
import pytest
from rest_framework.test import APIClient
from usuarios.models import Usuario

@pytest.fixture
def api_client():
    """Cliente API para pruebas."""
    return APIClient()

@pytest.fixture
def admin_user(db):
    """Usuario administrador para pruebas."""
    return Usuario.objects.create_user(username="admin", password="admin123", rol="admin")

@pytest.fixture
def empleado_user(db):
    """Usuario empleado para pruebas."""
    return Usuario.objects.create_user(username="empleado", password="empleado123", rol="empleado")

