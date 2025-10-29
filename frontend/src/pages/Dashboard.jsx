// src/pages/Dashboard.jsx
import { useEffect, useState } from "react";
import api from "../utils/api";
import Layout from "../components/Layout";

// ============================================================
// 📊 DASHBOARD GENERAL (Sprint 4 - Informes Estratégicos)
// - Admin → ver totales de empleados, nóminas y general
// - Gerente RRHH → ver cantidad de empleados y promedio de nómina
// - Asistente RRHH → ver últimas nóminas cargadas
// - Empleado → ver sus propias nóminas con detalle
// ============================================================

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  // ✅ Rol se guarda en localStorage en el login
  const rol = localStorage.getItem("rol") || "empleado";

  useEffect(() => {
    const fetchData = async () => {
      try {
        // 🔹 Definir endpoint según rol
        let endpoint = "";
        if (rol === "admin") endpoint = "/dashboard/admin/";
        else if (rol === "gerente_rrhh") endpoint = "/dashboard/gerente/";
        else if (rol === "asistente_rrhh") endpoint = "/dashboard/asistente/";
        else endpoint = "/dashboard/empleado/";

        // 🔹 Llamada a la API
        const res = await api.get(endpoint);
        setData(res.data);
      } catch (err) {
        console.error("❌ Error cargando dashboard", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [rol]);

  // 🔹 Mensajes de carga
  if (loading) return <p className="p-6">Cargando dashboard...</p>;
  if (!data) return <p className="p-6">No hay datos disponibles.</p>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-blue-900 mb-6">Dashboard</h1>

      {/* =========================================================
          🟢 ADMINISTRADOR
      ========================================================= */}
      {rol === "admin" && (
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-white shadow rounded p-4">
            <h2 className="font-semibold">Total Empleados</h2>
            <p className="text-2xl">{data.total_empleados}</p>
          </div>
          <div className="bg-white shadow rounded p-4">
            <h2 className="font-semibold">Total Nóminas</h2>
            <p className="text-2xl">{data.total_liquidaciones}</p>
          </div>
          <div className="bg-white shadow rounded p-4">
            <h2 className="font-semibold">Total General</h2>
            <p className="text-2xl text-green-700 font-bold">
              {parseFloat(data.total_general).toLocaleString()} Gs
            </p>
          </div>
        </div>
      )}

      {/* =========================================================
          🟡 GERENTE RRHH
      ========================================================= */}
      {rol === "gerente_rrhh" && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white shadow rounded p-4">
            <h2 className="font-semibold">Total Empleados</h2>
            <p className="text-2xl">{data.total_empleados}</p>
          </div>
          <div className="bg-white shadow rounded p-4">
            <h2 className="font-semibold">Promedio Nómina</h2>
            <p className="text-2xl text-blue-700 font-bold">
              {parseFloat(data.promedio_nomina).toLocaleString()} Gs
            </p>
          </div>
        </div>
      )}

      {/* =========================================================
          🔵 ASISTENTE RRHH
      ========================================================= */}
      {rol === "asistente_rrhh" && (
        <div className="bg-white shadow rounded p-4">
          <h2 className="font-semibold mb-4">Últimas Nóminas</h2>
          <ul>
            {data.ultimas_liquidaciones.map((n, i) => (
              <li key={i} className="border-b py-2">
                {n.empleado} - {n.mes}/{n.anio} -{" "}
                <span className="font-bold">{n.total} Gs</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* =========================================================
          🔴 EMPLEADO
      ========================================================= */}
      {rol === "empleado" && (
        <div className="bg-white shadow rounded p-4">
          <h2 className="font-semibold mb-4">Mis Nóminas</h2>
          <ul>
            {data.mis_liquidaciones.map((n, i) => (
              <li key={i} className="border-b py-2">
                {n.mes}/{n.anio} -{" "}
                <span className="font-bold">{n.neto} Gs</span>
                <ul className="ml-4 text-sm text-gray-600">
                  {n.detalle.map((d, j) => (
                    <li key={j}>
                      {d.concepto}: {d.monto} Gs
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
