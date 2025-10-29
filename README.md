Archivo: README.md

# 💼 Sistema de Nómina – TP Ingeniería de Software II

Proyecto desarrollado para la asignatura **Ingeniería de Software II**, cuyo objetivo es implementar un sistema modular y escalable de **gestión de nómina y cálculo de salarios** para la empresa ficticia **INGESOFT**.  
El sistema está compuesto por un **backend en Django (Python)** y un **frontend en React**, con base de datos **PostgreSQL**.

---

## 🧩 1. Estructura del Proyecto



Is2-payroll-app/
│
├── backend/
│ ├── manage.py
│ ├── sistema_nomina/ # Configuración principal de Django
│ ├── usuarios/ # Módulo de usuarios y roles
│ ├── empleados/ # Gestión de empleados e hijos
│ ├── nomina_cal/ # Cálculo de nómina, conceptos, descuentos
│ ├── requirements.txt # Dependencias Python
│ └── db.sqlite3 / PostgreSQL # Base de datos local o remota
│
├── frontend/
│ ├── src/
│ │ ├── pages/ # Páginas principales (login, dashboard, etc.)
│ │ ├── components/ # Componentes reutilizables
│ │ └── utils/api.js # Conexión al backend Django
│ └── package.json # Dependencias React


---

## ⚙️ 2. Requisitos Previos

- **Python 3.12+**
- **Node.js 18+**
- **PostgreSQL 14+**
- **Git**
- **pip / venv**

---

## 🐍 3. Configuración del Backend (Django)

### 3.1 Clonar el repositorio o copiar el proyecto
```bash
git clone https://github.com/usuario/Is2-payroll-app.git
cd Is2-payroll-app/backend

3.2 Crear y activar el entorno virtual
python -m venv venv
venv\Scripts\activate    # Windows

3.3 Instalar dependencias
pip install -r requirements.txt

3.4 Configurar la base de datos (PostgreSQL)

Editá el archivo:

# backend/sistema_nomina/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nomina_db',
        'USER': 'is2',
        'PASSWORD': 'teamis2',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


⚠️ El usuario y contraseña deben existir previamente en tu PostgreSQL.

3.5 Crear la base de datos y migraciones
python manage.py makemigrations
python manage.py migrate

3.6 Crear un superusuario
python manage.py createsuperuser

3.7 Ejecutar el servidor
python manage.py runserver


El backend estará disponible en:
👉 http://127.0.0.1:8000/api/

⚛️ 4. Configuración del Frontend (React)
4.1 Ingresar al directorio del frontend
cd ../frontend

4.2 Instalar dependencias
npm install

4.3 Configurar conexión al backend

Verificá que el archivo src/utils/api.js tenga la siguiente línea:

baseURL: "http://127.0.0.1:8000/api",

4.4 Ejecutar el frontend
npm run dev


El sistema estará disponible en:
👉 http://localhost:5173

👥 5. Roles del Sistema
Rol	Descripción principal
Administrador	Crea usuarios, gestiona empleados y liquidaciones
Gerente RRHH	Supervisa reportes, genera estadísticas
Asistente RRHH	Carga empleados, conceptos y descuentos
Empleado	Visualiza su liquidación mensual
📊 6. Funcionalidades Principales

✅ Autenticación JWT

✅ Gestión de empleados e hijos

✅ Conceptos salariales (créditos/débitos)

✅ Liquidaciones mensuales automáticas

✅ Cálculo IPS, aguinaldo, vacaciones, bonificaciones

✅ Descuentos adicionales

✅ Reportes en Excel y PDF

✅ Dashboards dinámicos por rol