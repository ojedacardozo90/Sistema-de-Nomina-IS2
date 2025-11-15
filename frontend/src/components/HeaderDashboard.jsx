
// HeaderDashboard.jsx — Encabezado global de los dashboards

// Muestra:
//   • Título del sistema
//   • Rol actual del usuario
//   • Botón de cierre de sesión

// Usado por: todos los dashboards (Admin, Gerente, etc.)


import { LogOut } from "lucide-react";
import { getUser, clearSession } from "../utils/auth";
import { useNavigate } from "react-router-dom";

export default function HeaderDashboard({ titulo = "Panel de Control" }) {
  const user = getUser();
  const navigate = useNavigate();

  const handleLogout = () => {
    clearSession();
    navigate("/login");
  };

  return (
    <header className="flex justify-between items-center bg-white shadow-sm border-b px-6 py-3 mb-4">
      <h1 className="text-xl font-bold text-emerald-700">{titulo}</h1>

      <div className="flex items-center gap-6">
        <span className="text-sm font-semibold text-gray-700">
          Rol:{" "}
          <span className="uppercase text-emerald-600">
            {user?.rol || "Invitado"}
          </span>
        </span>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-1.5 rounded-lg transition"
        >
          <LogOut size={16} />
          Cerrar sesión
        </button>
      </div>
    </header>
  );
}
