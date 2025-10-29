// ======================================================
// 🌐 App principal - Sistema de Nómina IS2
// Rutas y navegación con React Router DOM v6
// ======================================================
import Logout from "./pages/Logout";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// 🖼️ Layout principal
import Layout from "./components/Layout";
import Sidebar from "./components/Sidebar";

// 🔑 Autenticación
import Login from "./pages/Login";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import RoleRouter from "./pages/RoleRouter";

// 📊 Dashboards
import Dashboard from "./pages/Dashboard";
import DashboardAdmin from "./pages/DashboardAdmin";
import DashboardGerente from "./pages/DashboardGerente";
import DashboardAsistente from "./pages/DashboardAsistente";
import DashboardEmpleado from "./pages/DashboardEmpleado";

// 👥 Empleados
import EmpleadosList from "./pages/EmpleadosList";
import EmpleadoForm from "./pages/EmpleadoForm";

// 💡 Conceptos
import ConceptosList from "./pages/ConceptosList";
import ConceptoForm from "./pages/ConceptoForm";

// 💵 Liquidaciones
import LiquidacionesList from "./pages/LiquidacionesList";
import LiquidacionForm from "./pages/LiquidacionForm";
import CalculoNominaPage from "./pages/CalculoNominaPage";
import CalcularTodasNominas from "./pages/CalcularTodasNominas";

// 🕒 Asistencia
import Asistencia from "./pages/Asistencia";
import NoAutorizado from "./pages/NoAutorizado";

// 🧾 Otros módulos
import ReportesAvanzados from "./pages/ReportesAvanzados";
import Auditoria from "./pages/Auditoria";
import UsuariosList from "./pages/UsuariosList";
import UsuarioForm from "./pages/UsuarioForm";
import ImportarDatos from "./pages/ImportarDatos";


import FichadasList from "./pages/FichadasList";
import DashboardGestion from "./pages/DashboardGestion";
// ======================================================
export default function App() {
  return (
    <Router>
      <Routes>
        {/* 🔑 Login y recuperación */}
        <Route path="/login" element={<Login />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password/:uid/:token" element={<ResetPassword />} />

        {/* 🌐 Rutas protegidas con Layout */}
        <Route element={<Layout sidebar={<Sidebar />} />}>
          {/* Redirección automática por rol */}
          <Route path="/" element={<RoleRouter />} />

          {/* Dashboards */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/dashboard/admin" element={<DashboardAdmin />} />
          <Route path="/dashboard/gerente" element={<DashboardGerente />} />
          <Route path="/dashboard/asistente" element={<DashboardAsistente />} />
          <Route path="/dashboard/empleado" element={<DashboardEmpleado />} />

          {/* Empleados */}
          <Route path="/empleados" element={<EmpleadosList />} />
          <Route path="/empleados/nuevo" element={<EmpleadoForm />} />
          <Route path="/empleados/:id" element={<EmpleadoForm />} />

          {/* Conceptos */}
          <Route path="/conceptos" element={<ConceptosList />} />
          <Route path="/conceptos/nuevo" element={<ConceptoForm />} />
          <Route path="/conceptos/:id" element={<ConceptoForm />} />

          {/* Liquidaciones */}
          <Route path="/liquidaciones" element={<LiquidacionesList />} />
          <Route path="/liquidaciones/nueva" element={<LiquidacionForm />} />
          <Route path="/liquidaciones/:id" element={<LiquidacionForm />} />
          <Route path="/liquidaciones/:id/calcular" element={<CalculoNominaPage />} />
          <Route path="/liquidaciones/calcular-todas" element={<CalcularTodasNominas />} />

          {/* Asistencia */}
          <Route path="/asistencia" element={<Asistencia />} />

          {/* Usuarios */}
          <Route path="/usuarios" element={<UsuariosList />} />
          <Route path="/usuarios/nuevo" element={<UsuarioForm />} />
          <Route path="/usuarios/:id/editar" element={<UsuarioForm />} />

          {/* Auditoría y Reportes */}
          <Route path="/reportes/avanzados" element={<ReportesAvanzados />} />
          <Route path="/auditoria" element={<Auditoria />} />

          {/* Importar datos */}
          <Route path="/importar" element={<ImportarDatos />} />

          {/* Configuración */}
          <Route path="/no-autorizado" element={<NoAutorizado />} />
          <Route path="/logout" element={<Logout />} />
          <Route path="/dashboard/gestion" element={<DashboardGestion />} />
          
          <Route path="/asistencia/fichadas" element={<FichadasList />} />
          
        </Route>

        {/* Fallback a login */}
        <Route path="*" element={<Login />} />
      </Routes>
    </Router>
  );
}
