// frontend/src/AppRouter.jsx
// ============================================================
// 🚦 Rutas principales del Sistema de Nómina (React Router v6)
// Incluye:
// - Login
// - Recuperar contraseña
// - Dashboard según rol
// - Módulos: Empleados, Nóminas, Reportes, Retenciones
// - Rutas privadas protegidas por token
// ============================================================

import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";

// 🔹 Layout y utilidades
import Layout from "./components/Layout";
import { getToken } from "./utils/auth";

// 🔹 Páginas
import Login from "./pages/Login";
import ForgotPassword from "./pages/ForgotPassword";
import Dashboard from "./pages/Dashboard";
import DashboardAdmin from "./pages/DashboardAdmin";
import DashboardGerente from "./pages/DashboardGerente";
import DashboardAsistente from "./pages/DashboardAsistente";
import DashboardEmpleado from "./pages/DashboardEmpleado";

import Empleados from "./pages/Empleados";
import Nominas from "./pages/Nominas";
import Reportes from "./pages/Reportes";
import ReporteGeneral from "./pages/ReporteGeneral";
import Retenciones from "./pages/Retenciones";
import Automatizacion from "./pages/Automatizacion";
import CalculoNominaPage from "./pages/CalculoNominaPage";
import CalcularTodasNominas from "./pages/CalcularTodasNominas";

// ============================================================
// 🔐 Componente de ruta privada
// ============================================================
function PrivateRoute({ children }) {
  const token = getToken();
  return token ? children : <Navigate to="/login" />;
}

// ============================================================
// 🚀 Definición de rutas
// ============================================================
export default function AppRouter() {
  return (
    <Router>
      <Routes>
        {/* 🔹 Rutas públicas */}
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />

        {/* 🔹 Rutas privadas dentro del Layout */}
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          {/* Dashboard general */}
          <Route path="dashboard" element={<Dashboard />} />

          {/* Dashboards específicos por rol */}
          <Route path="dashboard/admin" element={<DashboardAdmin />} />
          <Route path="dashboard/gerente" element={<DashboardGerente />} />
          <Route path="dashboard/asistente" element={<DashboardAsistente />} />
          <Route path="dashboard/empleado" element={<DashboardEmpleado />} />

          {/* Módulos */}
          <Route path="empleados" element={<Empleados />} />
          <Route path="nominas" element={<Nominas />} />
          <Route path="retenciones" element={<Retenciones />} />
          <Route path="reportes" element={<Reportes />} />
          <Route path="reporte-general" element={<ReporteGeneral />} />
          <Route path="automatizacion" element={<Automatizacion />} />
          <Route path="calculo-nomina" element={<CalculoNominaPage />} />
          <Route path="calcular-todas" element={<CalcularTodasNominas />} />
        </Route>

        {/* 🔹 Cualquier ruta inválida redirige al login */}
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </Router>
  );
}
