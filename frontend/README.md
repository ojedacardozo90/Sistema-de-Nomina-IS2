---

## 📂 frontend/README.md

```markdown
# Sistema de Gestión de Nómina – Frontend

Este es el **frontend** del sistema de nómina desarrollado con **React, Vite y TailwindCSS**.  
Incluye dashboards por rol (Administrador, RRHH, Asistente, Empleado), login JWT y visualización de reportes.

---

##  Tecnologías

- React 18  
- Vite 5  
- TailwindCSS 3  
- Axios  
- React Router DOM 6  

---

##  Instalación

1. Instalar dependencias
   ```bash
   npm install
Levantar servidor

bash
Copiar código
npm run dev
Acceder en: http://localhost:5173/

 Diseño
Paleta:

Azul #1ABC9C

Gris oscuro #121826

Blanco #FFFFFF

Layout minimalista con Tailwind

Sidebar + Navbar adaptados al rol del usuario

 Autenticación
El login se conecta al endpoint del backend:

bash
Copiar código
POST http://localhost:8000/api/usuarios/token/
El token se guarda en localStorage y se agrega automáticamente en los headers con Axios.

 Funcionalidades
Login/logout con JWT

Dashboard de administrador

CRUD de empleados

Cálculo de nómina

Reportes PDF/Excel descargables

 Estado
Sprint 1 → Login funcionando

Sprint 2 → Dashboards por rol

Sprint 3 → Integración con cálculo nómina

Sprint 4 → Reportes Excel/PDF

Sprint 5 → Sistema completo

yaml
Copiar código
