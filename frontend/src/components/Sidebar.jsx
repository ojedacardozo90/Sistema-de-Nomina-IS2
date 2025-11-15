
// Sidebar — Estilo Admin Django con ícono de proceso (Workflow)
// Sistema de Nómina IS2 -  / 

// • Secciones colapsables tipo admin Django
// • Ícono Workflow simboliza proceso y desarrollo
// • Roles dinámicos (Admin, Gerente, Asistente, Empleado)


import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { getUser, clearSession } from "../utils/auth";
import {
  Workflow,
  LayoutDashboard,
  Users,
  FileText,
  ClipboardList,
  Zap,
  PieChart,
  Upload,
  Settings,
  ShieldCheck,
  UserCog,
  LogOut,
  Database, //  agregado
} from "lucide-react";

export default function Sidebar() {
  const user = getUser() || {};
  const rol = (user.rol || "empleado").toLowerCase();
  const location = useLocation();
  const navigate = useNavigate();

  
  // Secciones colapsables
  
  const [openRRHH, setOpenRRHH] = useState(true);
  const [openAdmin, setOpenAdmin] = useState(true);
  const [openConfig, setOpenConfig] = useState(false);

  const handleLogout = () => {
    clearSession();
    navigate("/login");
  };

  
  //  Render principal
  
  return (
    <aside className="bg-[#111827] text-gray-100 w-64 min-h-screen flex flex-col border-r border-gray-700 shadow-lg">
      {/* Encabezado con ícono Workflow */}
      <div className="px-6 py-5 border-b border-gray-700 flex items-center gap-3">
        <div className="bg-indigo-600 p-2 rounded-lg">
          <Workflow size={20} className="text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-white tracking-wide">
            Nómina<span className="text-green-400">Pro</span>
          </h1>
          <p className="text-xs text-gray-400">Procesos y Desarrollo</p>
        </div>
      </div>
      
      {/* Contenido scrollable */}
      <nav className="flex-1 overflow-y-auto p-3 space-y-2">
        {/* == RRHH == */}
        <div>
          <button
            onClick={() => setOpenRRHH(!openRRHH)}
            className="flex items-center justify-between w-full px-3 py-2 text-sm font-semibold text-gray-300 hover:bg-gray-800 rounded"
          >
            <span>▸ RRHH</span>
            <span
              className={`transform transition ${openRRHH ? "rotate-90" : ""}`}
            >
              ▶
            </span>
          </button>

          {openRRHH && (
            <ul className="ml-4 mt-1 space-y-1 border-l border-gray-700 pl-3">
              <SidebarLink to="/dashboard/admin" label="Dashboard" icon={LayoutDashboard} />
              <SidebarLink to="/dashboard/gestion" label="Panel Admin" icon={LayoutDashboard} />
              <SidebarLink to="/empleados" label="Empleados" icon={Users} />
              <SidebarLink to="/conceptos" label="Conceptos" icon={ClipboardList} />
              <SidebarLink to="/liquidaciones" label="Liquidaciones" icon={FileText} />
              <SidebarLink to="/asistencia" label="Asistencia" icon={Zap} />
              <SidebarLink to="/reportes/avanzados" label="Reportes" icon={PieChart} />
            </ul>
          )}
        </div>

        {/* == ADMINISTRACIÓN == */}
        {["admin", "gerente_rrhh"].includes(rol) && (
          <div>
            <button
              onClick={() => setOpenAdmin(!openAdmin)}
              className="flex items-center justify-between w-full px-3 py-2 text-sm font-semibold text-gray-300 hover:bg-gray-800 rounded"
            >
              <span>▸ Administración</span>
              <span
                className={`transform transition ${openAdmin ? "rotate-90" : ""}`}
              >
                ▶
              </span>
            </button>

            {openAdmin && (
              <ul className="ml-4 mt-1 space-y-1 border-l border-gray-700 pl-3">
                <SidebarLink to="/usuarios" label="Usuarios" icon={UserCog} />
                <SidebarLink to="/auditoria" label="Auditoría" icon={ShieldCheck} />
                <SidebarLink to="/importar" label="Importar Datos" icon={Upload} />

                {/* # NUEVO BLOQUE - Panel Django solo visible para ADMIN */}
                {user?.rol === "ADMIN" && (
                  <li>
                    <Link
                      to="/dashboard/gestion"
                      className="flex items-center gap-2 p-2 hover:bg-emerald-50 rounded text-gray-800 transition"
                    >
                      <Database size={18} />
                      Panel Django
                    </Link>
                  </li>
                )}
              </ul>
            )}
          </div>
        )}

        {/* == CONFIGURACIÓN == */}
        <div>
          <button
            onClick={() => setOpenConfig(!openConfig)}
            className="flex items-center justify-between w-full px-3 py-2 text-sm font-semibold text-gray-300 hover:bg-gray-800 rounded"
          >
            <span>▸ Configuración</span>
            <span
              className={`transform transition ${openConfig ? "rotate-90" : ""}`}
            >
              ▶
            </span>
          </button>

          {openConfig && (
            <ul className="ml-4 mt-1 space-y-1 border-l border-gray-700 pl-3">
              <SidebarLink to="/configuracion" label="Preferencias" icon={Settings} />
              <li>
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-3 px-2 py-1.5 rounded text-sm text-red-500 hover:bg-gray-800 hover:text-red-400 transition w-full text-left"
                >
                  <LogOut size={16} />
                  Cerrar Sesión
                </button>
              </li>
            </ul>
          )}
        </div>
      </nav>

      {/* Pie del menú */}
      <div className="px-4 py-4 border-t border-gray-700 text-center text-xs text-gray-500">
        © 2025 NóminaPro — Masivo
      </div>
    </aside>
  );
}


// # Componente auxiliar para links del menú

function SidebarLink({ to, label, icon: Icon }) {
  const location = useLocation();
  const active = location.pathname === to;

  return (
    <li>
      <Link
        to={to}
        className={`flex items-center gap-3 px-2 py-1.5 rounded text-sm transition ${
          active
            ? "bg-indigo-600 text-white"
            : "text-gray-300 hover:text-white hover:bg-gray-800"
        }`}
      >
        <Icon size={16} />
        {label}
      </Link>
    </li>
  );
}
