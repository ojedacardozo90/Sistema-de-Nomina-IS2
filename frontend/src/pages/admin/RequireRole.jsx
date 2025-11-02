// frontend/src/pages/admin/RequireRole.jsx
import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { obtenerPerfil } from "../../utils/api";

export default function RequireRole({ allow = [], children }) {
  const [state, setState] = useState({ loading: true, ok: false });

  useEffect(() => {
    (async () => {
      try {
        const r = await obtenerPerfil();
        const rol = (r.data?.rol || r.rol || "").toUpperCase();
        const map = {
          ADMIN: "ADMIN",
          GERENTE_RRHH: "GERENTE_RRHH",
          ASISTENTE_RRHH: "ASISTENTE_RRHH",
          EMPLEADO: "EMPLEADO",
          GERENTE: "GERENTE_RRHH",
          ASISTENTE: "ASISTENTE_RRHH",
        };
        const norm = map[rol] || rol;
        setState({ loading: false, ok: allow.includes(norm) });
      } catch {
        setState({ loading: false, ok: false });
      }
    })();
  }, [allow]);

  if (state.loading) return <div className="p-8 text-gray-500">Verificando permisos…</div>;
  if (!state.ok) return <Navigate to="/dashboard/empleado" replace />;
  return children;
}
