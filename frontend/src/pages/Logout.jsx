
// 🚪 Logout.jsx — Cierre de sesión del Sistema de Nómina IS2
// Limpia tokens JWT y redirige al login


import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function Logout() {
  const navigate = useNavigate();

  useEffect(() => {
    //  Borrar todo lo relacionado al usuario
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("rol");
    localStorage.removeItem("usuario");

    //  Redirigir al login
    navigate("/login");
  }, [navigate]);

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <div className="text-center bg-white shadow-md rounded-2xl p-8">
        <h2 className="text-xl font-semibold mb-2 text-gray-700">
          Cerrando sesión…
        </h2>
        <p className="text-gray-500 text-sm">Serás redirigido al inicio de sesión.</p>
      </div>
    </div>
  );
}
