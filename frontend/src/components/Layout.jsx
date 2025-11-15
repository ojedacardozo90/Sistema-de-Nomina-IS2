import { Outlet, useNavigate } from "react-router-dom";
import { getUser, logout } from "../services/auth";

/**

 *  Layout principal del sistema
 * - Muestra nombre y rol
 * - Botón de logout
 * - Renderiza contenido dinámico (Outlet)

 */
export default function Layout({ sidebar }) {
  const navigate = useNavigate();
  const user = getUser();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Sidebar opcional */}
      {sidebar && <aside className="w-64 bg-white shadow-lg">{sidebar}</aside>}

      {/* Contenido principal */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white shadow px-6 py-3 flex justify-between items-center">
          <div>
            <h1 className="text-xl font-bold text-emerald-700">Sistema de Nómina</h1>
          </div>
          {user && (
            <div className="flex items-center gap-4 text-sm text-gray-700">
              <span>
                 {user.username} ({user.rol})
              </span>
              <button
                onClick={handleLogout}
                className="text-red-600 hover:text-red-800 font-medium"
              >
                Cerrar sesión
              </button>
            </div>
          )}
        </header>

        {/* Main Content */}
        <main className="p-6 flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
