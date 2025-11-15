
// 🚦 RoleRouter — Redirección automática por rol de usuario

// Verifica token JWT, obtiene perfil si es necesario,
// y redirige al dashboard correspondiente según el rol.
// Compatible con backend Django 5.2.6 (IS2 Nómina).


import { Navigate } from "react-router-dom";
import { getUser, fetchProfile, clearSession } from "../utils/auth";
import { useEffect, useState } from "react";

export default function RoleRouter() {
  // 
  // # Estados principales
  // 
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(true);

  
  //  Verificar credenciales al cargar
  
  useEffect(() => {
    const run = async () => {
      try {
        let user = getUser();

        // --------------------------------------------------------
        // Si no hay usuario guardado, obtener desde el backend
        // --------------------------------------------------------
        if (!user) {
          const perfil = await fetchProfile();
          if (!perfil) throw new Error("Sin perfil o token inválido");
          user = perfil;
        }

        // --------------------------------------------------------
        //  Normalizar rol
        // --------------------------------------------------------
        if (!user?.rol) {
          console.warn(" Usuario sin rol definido");
          setRole("EMPLEADO");
        } else {
          // Convertimos el rol a mayúsculas por consistencia
          setRole(user.rol.toUpperCase());
        }
      } catch (e) {
        console.error(" Error en RoleRouter:", e);
        clearSession();
        setRole("LOGIN");
      } finally {
        setLoading(false);
      }
    };

    run();
  }, []);

  
  //  Pantalla de carga
  
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen text-gray-600">
        <h2 className="text-xl font-semibold animate-pulse">
          Verificando credenciales...
        </h2>
      </div>
    );
  }

  
  // 🚦 Redirección según rol
  
  if (role === "LOGIN") return <Navigate to="/login" replace />;
  if (role === "ADMIN") return <Navigate to="/dashboard/admin" replace />;
  if (role === "GERENTE" || role === "GERENTE_RRHH")
    return <Navigate to="/dashboard/gerente" replace />;
  if (role === "ASISTENTE" || role === "ASISTENTE_RRHH")
    return <Navigate to="/dashboard/asistente" replace />;
  if (role === "EMPLEADO") return <Navigate to="/dashboard/empleado" replace />;

  
  // 🔚 Fallback (rol no reconocido)
  
  return <Navigate to="/dashboard/empleado" replace />;
}
