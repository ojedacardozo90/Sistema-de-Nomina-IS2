// frontend/src/Layout/AppLayout.jsx
//  Plantilla Base - Sistema de Nómina (TP IS2)
// Incluye:
// - Sidebar (izquierda)
// - Navbar (superior)
// - Contenedor central con fondo gris
// - Colores según Figma: 
//    Sidebar = negro, Navbar = negro, 
//    Botones = verde agua (#1ABC9C), rojo suave (#E74C3C)

import { useState } from "react";
import { Link, Outlet } from "react-router-dom";
import { LogOut } from "lucide-react"; // iconos bonitos
import clsx from "clsx";

export default function AppLayout() {
  const [open, setOpen] = useState(true);

  return (
    <div className="flex h-screen bg-gray-100">
      {/* ===== SIDEBAR ===== */}
      <aside
        className={clsx(
          "bg-black text-white w-64 transition-all duration-300",
          !open && "w-20"
        )}
      >
        <div className="flex items-center justify-between px-4 py-3">
          <span className="text-lg font-bold">IS2 Nómina</span>
          <button
            onClick={() => setOpen(!open)}
            className="text-gray-400 hover:text-white"
          >
            {open ? "«" : "»"}
          </button>
        </div>

        <nav className="mt-6">
          <ul className="space-y-2">
            <li>
              <Link
                to="/dashboard"
                className="block px-4 py-2 rounded hover:bg-gray-700"
              >
                Dashboard
              </Link>
            </li>
            <li>
              <Link
                to="/empleados"
                className="block px-4 py-2 rounded hover:bg-gray-700"
              >
                Empleados
              </Link>
            </li>
            <li>
              <Link
                to="/nominas"
                className="block px-4 py-2 rounded hover:bg-gray-700"
              >
                Nóminas
              </Link>
            </li>
            <li>
              <Link
                to="/reportes"
                className="block px-4 py-2 rounded hover:bg-gray-700"
              >
                Reportes
              </Link>
            </li>
          </ul>
        </nav>
      </aside>

      {/* ===== CONTENEDOR PRINCIPAL ===== */}
      <div className="flex-1 flex flex-col">
        {/* ===== NAVBAR SUPERIOR ===== */}
        <header className="bg-black text-white flex items-center justify-between px-6 py-3 shadow-md">
          <h1 className="text-xl font-bold">Sistema de Nómina</h1>
          <button className="flex items-center bg-red-500 hover:bg-red-600 px-3 py-1 rounded text-white">
            <LogOut className="w-5 h-5 mr-1" />
            Cerrar Sesión
          </button>
        </header>

        {/* ===== CONTENIDO ===== */}
        <main className="flex-1 p-6 overflow-y-auto">
          <Outlet /> {/* Aquí se cargan las páginas según ruta */}
        </main>
      </div>
    </div>
  );
}
