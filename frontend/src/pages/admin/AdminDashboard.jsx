// src/pages/admin/AdminDashboard.jsx
import { useEffect, useState } from "react";
import api from "../../utils/api";
import Layout from "../../components/Layout";
import { TrendingUp, Users, FileText, Clock } from "lucide-react";

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    cargarDatos();
  }, []);

  const cargarDatos = async () => {
    try {
      // KPIs globales — usa tus endpoints ya disponibles
      const [kpiNomina, empleados, conceptos, auditoria] = await Promise.all([
        api.get("/nomina_cal/analytics/kpis/"),
        api.get("/empleados/"),
        api.get("/nomina_cal/conceptos/"),
        api.get("/auditoria/logs/?limit=5"),
      ]);

      setStats({
        total_general: kpiNomina.data.kpis?.total_general || 0,
        promedio_neto: kpiNomina.data.kpis?.promedio_neto || 0,
        total_empleados: empleados.data.count || empleados.data.length || 0,
        total_conceptos: conceptos.data.count || conceptos.data.length || 0,
      });

      setLogs(auditoria.data.results || auditoria.data || []);
    } catch (err) {
      console.error("Error al cargar dashboard:", err);
    }
  };

  if (!stats) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-screen text-gray-500">
          <div className="animate-pulse text-lg font-semibold">
            Cargando panel administrativo...
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="p-6 space-y-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">
           Panel de Control — Administración
        </h1>

        {/* === TARJETAS KPI === */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard
            icon={<FileText className="text-blue-600" size={24} />}
            titulo="Total Nómina"
            valor={`${stats.total_general.toLocaleString("es-PY")} Gs`}
          />
          <KpiCard
            icon={<TrendingUp className="text-green-600" size={24} />}
            titulo="Promedio Neto"
            valor={`${stats.promedio_neto.toLocaleString("es-PY")} Gs`}
          />
          <KpiCard
            icon={<Users className="text-purple-600" size={24} />}
            titulo="Empleados Activos"
            valor={stats.total_empleados}
          />
          <KpiCard
            icon={<Clock className="text-orange-600" size={24} />}
            titulo="Conceptos Registrados"
            valor={stats.total_conceptos}
          />
        </div>

        {/* === GRÁFICO === */}
        <div className="bg-white shadow rounded-lg p-5">
          <h2 className="text-lg font-semibold mb-3 text-gray-700">
            Evolución Mensual de la Nómina
          </h2>
          <iframe
            src="http://127.0.0.1:8000/api/nomina_cal/analytics/chart/"
            className="w-full h-80 rounded border"
            title="Gráfico Nómina"
          ></iframe>
          <p className="text-xs text-gray-500 mt-2">
            (Este iframe puede reemplazarse por Recharts o Chart.js si preferís integrarlo directo)
          </p>
        </div>

        {/* === LOGS RECIENTES === */}
        <div className="bg-white shadow rounded-lg p-5">
          <h2 className="text-lg font-semibold mb-3 text-gray-700">
            🕓 Actividad Reciente (Auditoría)
          </h2>
          <table className="min-w-full border text-sm">
            <thead className="bg-gray-100 text-gray-700">
              <tr>
                <th className="border px-2 py-1 text-left">Usuario</th>
                <th className="border px-2 py-1 text-left">Acción</th>
                <th className="border px-2 py-1 text-left">Modelo</th>
                <th className="border px-2 py-1 text-left">Fecha</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((l) => (
                <tr key={l.id} className="hover:bg-gray-50">
                  <td className="border px-2 py-1">{l.usuario_nombre || "-"}</td>
                  <td className="border px-2 py-1">{l.accion}</td>
                  <td className="border px-2 py-1">{l.modelo}</td>
                  <td className="border px-2 py-1">{l.fecha}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </Layout>
  );
}


// # Componente KPI reutilizable

function KpiCard({ titulo, valor, icon }) {
  return (
    <div className="bg-white shadow p-4 rounded flex items-center justify-between">
      <div>
        <h3 className="text-gray-500 text-sm">{titulo}</h3>
        <p className="text-xl font-bold text-gray-800">{valor}</p>
      </div>
      <div className="bg-gray-100 p-2 rounded-full">{icon}</div>
    </div>
  );
}
