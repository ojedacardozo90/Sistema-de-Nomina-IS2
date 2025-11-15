
//  Dashboard Asistente RRHH — NóminaPro (Sprint 6–7)

// Backend actual devuelve:
//  • total_nominas, monto_total, promedio_nomina
//  • ultimas_nominas: [{id, empleado__nombre, mes, anio, neto_cobrar}, ...]
// Endpoint: GET /nomina_cal/dashboard/asistente/

import HeaderDashboard from "../components/HeaderDashboard";

import { useEffect, useState } from "react";
import api from "../utils/api";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function DashboardAsistente() {
  const [ultimas, setUltimas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [resumen, setResumen] = useState({
    totalNominas: 0,
    montoTotal: 0,
    promedio: 0,
  });
  const [error, setError] = useState(null);

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await api.get("/nomina_cal/dashboard/asistente/");

        // Campos según tu views_dashboard.py
        const totalNominas = Number(res.data.total_nominas || 0);
        const montoTotal = Number(res.data.monto_total || 0);
        const promedio = Number(res.data.promedio_nomina || 0);

        const fila = (res.data.ultimas_nominas || []).map((n) => ({
          id: n.id,
          empleado: n.empleado__nombre,
          periodo: `${n.mes}/${n.anio}`,
          total: Number(n.neto_cobrar || 0),
        }));

        setResumen({ totalNominas, montoTotal, promedio });
        setUltimas(fila);
      } catch (e) {
        console.error("Error cargando asistente:", e);
        setError("No se pudieron cargar los datos del asistente.");
      } finally {
        setLoading(false);
      }
    };
    run();
  }, []);

  if (loading)
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="flex flex-col items-center gap-2">
          <div className="w-12 h-12 border-4 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600 font-medium">
            Cargando dashboard asistente...
          </p>
        </div>
      </div>
    );
  if (error)
    return (
      <div className="text-center text-red-600 mt-10 font-semibold">
        {error}
      </div>
    );

  
  //  Render con encabezado principal
  
  return (
    <div className="p-6">
      <HeaderDashboard titulo="Dashboard Asistente RRHH" />

      {/* Contenido principal del dashboard */}
      <section className="mt-4 space-y-6">
        {/* KPIs principales */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <KpiCard
            titulo="Total de Nóminas"
            valor={resumen.totalNominas.toLocaleString("es-PY")}
          />
          <KpiCard
            titulo="Monto Total"
            valor={`${resumen.montoTotal.toLocaleString("es-PY")} Gs`}
          />
          <KpiCard
            titulo="Promedio por Nómina"
            valor={`${resumen.promedio.toLocaleString("es-PY")} Gs`}
          />
        </div>

        {/* Tabla últimas nóminas */}
        <div className="bg-white shadow p-4 rounded">
          <h2 className="font-semibold mb-2">Últimas Nóminas</h2>
          {ultimas.length === 0 ? (
            <p className="text-gray-500">Aún no hay nóminas registradas.</p>
          ) : (
            <table className="w-full text-sm border mt-2">
              <thead className="bg-gray-50">
                <tr>
                  <th className="p-2 text-left">Empleado</th>
                  <th className="p-2 text-left">Periodo</th>
                  <th className="p-2 text-right">Total (Gs)</th>
                  <th className="p-2 text-center">Acción</th>
                </tr>
              </thead>
              <tbody>
                {ultimas.map((n) => (
                  <tr key={n.id} className="border-b hover:bg-gray-50">
                    <td className="p-2">{n.empleado}</td>
                    <td className="p-2">{n.periodo}</td>
                    <td className="p-2 text-right">
                      {n.total.toLocaleString("es-PY")}
                    </td>
                    <td className="p-2 text-center">
                      <button
                        onClick={() => window.open(`/recibos/${n.id}`, "_blank")}
                        className="px-2 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition"
                      >
                        Ver Recibo
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Gráfico de barras */}
        <div className="bg-white shadow p-4 rounded h-80">
          <h2 className="font-semibold mb-2">Gráfico de Últimas Nóminas</h2>
          {ultimas.length === 0 ? (
            <p className="text-gray-500 text-center mt-10">
              Sin datos para mostrar.
            </p>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ultimas}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="empleado" />
                <YAxis />
                <Tooltip
                  formatter={(v) => Number(v).toLocaleString("es-PY")}
                />
                <Bar dataKey="total" fill="#E67E22" name="Total (Gs)" />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </section>
    </div>
  );
}

function KpiCard({ titulo, valor }) {
  return (
    <div className="bg-white shadow p-4 rounded text-center">
      <h2 className="text-gray-500 text-sm">{titulo}</h2>
      <p className="text-2xl font-bold">{valor}</p>
    </div>
  );
}
