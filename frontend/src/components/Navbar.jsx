// src/components/Navbar.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import { getUser, clearToken } from "../utils/auth";

const Navbar = () => {
  const navigate = useNavigate();
  const user = getUser(); //  obtenemos usuario desde localStorage

  const handleLogout = () => {
    clearToken(); //  limpiamos tokens + usuario
    navigate("/login"); // redirigimos
  };

  return (
    <nav className="bg-gray-900 text-white p-4 flex justify-between items-center">
      <h1 className="text-lg font-bold"> Sistema de Nómina</h1>

      <div className="flex items-center gap-4">
        {user && (
          <span className="text-sm text-gray-300">
             {user.username} ({user.rol})
          </span>
        )}
        <button
          onClick={handleLogout}
          className="bg-red-600 hover:bg-red-500 px-3 py-1 rounded"
        >
          🚪 Cerrar sesión
        </button>
      </div>
    </nav>
  );
};

export default Navbar;
