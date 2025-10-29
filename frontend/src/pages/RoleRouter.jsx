// src/pages/RoleRouter.jsx
import { Navigate } from "react-router-dom";
import { getUser, fetchProfile, clearSession } from "../utils/auth";
import { useEffect, useState } from "react";

/**
 * ============================================================
 * 🚦 RoleRouter (versión estable)
 * - Redirige al dashboard correcto según el rol
 * - Usa datos locales del JWT y consulta /usuarios/me/
 * ============================================================
 */
export default function RoleRouter() {
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const run = async () => {
      try {
        let user = getUser();

        // Si no hay usuario guardado, intenta obtenerlo del backend
        if (!user) {
          const perfil = await fetchProfile();
          if (!perfil) throw new Error("Sin perfil o token inválido");
          user = perfil;
        }

        if (!user?.rol) {
          console.warn("⚠️ Usuario sin rol definido");
          setRole("EMPLEADO");
        } else {
          setRole(user.rol.toUpperCase());
        }
      } catch (e) {
        console.error("RoleRouter error:", e);
        clearSession();
        setRole("LOGIN");
      } finally {
        setLoading(false);
      }
    };

    run();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen text-gray-600">
        <h2 className="text-xl font-semibold animate-pulse">
          Verificando credenciales...
        </h2>
      </div>
    );
  }

  // ✅ Redirección según rol
  if (role === "LOGIN") return <Navigate to="/login" replace />;
  if (role === "ADMIN") return <Navigate to="/dashboard/admin" replace />;
  if (role === "GERENTE" || role === "GERENTE_RRHH")
    return <Navigate to="/dashboard/gerente" replace />;
  if (role === "ASISTENTE" || role === "ASISTENTE_RRHH")
    return <Navigate to="/dashboard/asistente" replace />;
  if (role === "EMPLEADO") return <Navigate to="/dashboard/empleado" replace />;

  // Por defecto
  return <Navigate to="/dashboard/empleado" replace />;
}
