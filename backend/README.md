 backend/README.md
# Sistema de Gestión de Nómina – Backend

Este es el **backend** del sistema de nómina desarrollado en **Django REST Framework** con PostgreSQL.  
Incluye autenticación JWT, gestión de empleados, cálculo de nómina, reportes PDF y Excel.

---

##  Tecnologías

- Django 5.2.6  
- Django REST Framework 3.16.1  
- JWT (SimpleJWT)  
- PostgreSQL  
- ReportLab (PDF)  
- OpenPyXL (Excel)  

---

##  Instalación

1. Crear entorno virtual
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   source venv/bin/activate # Linux/Mac


Instalar dependencias

pip install -r requirements.txt


Migraciones

python manage.py makemigrations
python manage.py migrate


Cargar datos iniciales

python manage.py loaddata fixtures/usuarios.json
python manage.py loaddata fixtures/empleados.json
python manage.py loaddata fixtures/conceptos.json
python manage.py loaddata fixtures/salario_minimo.json


Crear superusuario

python manage.py createsuperuser


Levantar servidor

python manage.py runserver

 Autenticación

Login:

POST http://localhost:8000/api/usuarios/token/
{
  "username": "admin",
  "password": "12345"
}


Devuelve access y refresh.

Usar token:

Authorization: Bearer <access_token>

 Endpoints principales
Usuarios

POST /api/usuarios/token/

POST /api/usuarios/token/refresh/

Empleados

GET /api/empleados/

POST /api/empleados/

Nómina

POST /api/nomina/calcular-nomina/

POST /api/nomina/calcular-todas/

GET /api/nomina/reporte-general/

GET /api/nomina/exportar-reporte-pdf/

GET /api/nomina/exportar-reporte-excel/

 Pruebas con Thunder Client

Crear colección Nómina API.

Hacer login con:

{ "username": "admin", "password": "12345" }


Guardar access como variable token.

Usar en headers:

Authorization: Bearer {{token}}

 Estado

Sprint 1 → Login JWT

Sprint 2 → CRUD empleados

Sprint 3 → Cálculo nómina

Sprint 4 → Reportes PDF/Excel

Sprint 5 → Integración completa