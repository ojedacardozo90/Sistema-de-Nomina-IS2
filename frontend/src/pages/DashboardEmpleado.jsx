// ============================================================
// 👤 Dashboard Empleado — NóminaPro (Sprint 6–7)
// ------------------------------------------------------------
// Backend: GET /nomina_cal/dashboard/empleado/
// Respuesta esperada: { empleado, ultimas_liquidaciones: [{mes, anio, neto_cobrar}] }
// ============================================================
import HeaderDashboard from "../components/HeaderDashboard";
import { useEffect, useState } from "react";
import api from "../utils/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function DashboardEmpleado() {
  const [data, setData] = useState([]);
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get("/nomina_cal/dashboard/empleado/");
      const liqs = res.data.ultimas_liquidaciones || [];

      const chartData = liqs
        .map((x) => ({
          periodo: `${x.mes}/${x.anio}`,
          neto: Number(x.neto_cobrar || 0),
        }))
        .reverse();

      const total = chartData.reduce((acc, cur) => acc + (cur.neto || 0), 0);
      const promedio = chartData.length > 0 ? total / chartData.length : 0;

      setData(chartData);
      setInfo({ empleado: res.data.empleado, total, promedio });
    } catch (e) {
      console.error("Error dashboard empleado:", e);
      setError("No se pudieron cargar los datos personales.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="flex flex-col items-center gap-2">
          <div className="w-12 h-12 border-4 border-indigo-400 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600 font-medium">Cargando tus datos de nómina...</p>
        </div>
      </div>
    );
  }
  if (error) return <div className="text-center text-red-600 mt-10 font-semibold">{error}</div>;
  if (!info) return <div className="text-center text-gray-600 mt-10">No se encontró información del empleado.</div>;

  // ✅ Estructura con encabezado (HeaderDashboard)
  return (
    <div className="p-6">
      <HeaderDashboard titulo="Panel Personal del Empleado" />

      {/* Contenido principal */}
      <section className="mt-4 space-y-6">
        <h1 className="text-2xl font-bold">👤 {info.empleado}</h1>

        {/* KPIs */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <KpiCard titulo="Total Acumulado" valor={`${info.total.toLocaleString("es-PY")} Gs`} />
          <KpiCard titulo="Promedio Mensual" valor={`${info.promedio.toLocaleString("es-PY")} Gs`} />
          <KpiCard titulo="Liquidaciones" valor={data.length} />
        </div>

        {/* Gráfico */}
        <div className="bg-white shadow p-4 rounded h-80">
          <h2 className="font-semibold mb-2">Evolución de tus últimos cobros</h2>
          {data.length === 0 ? (
            <p className="text-gray-500 text-center mt-10">No hay datos suficientes para mostrar.</p>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="periodo" />
                <YAxis />
                <Tooltip formatter={(v) => Number(v).toLocaleString("es-PY")} />
                <Line
                  type="monotone"
                  dataKey="neto"
                  stroke="#4F46E5"
                  strokeWidth={2}
                  dot={{ r: 4, fill: "#4F46E5" }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Tabla */}
        <div className="bg-white p-4 rounded shadow">
          <h2 className="font-semibold mb-2">Últimas Liquidaciones</h2>
          <table className="w-full text-sm border border-gray-200">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="p-2 text-left">Periodo</th>
                <th className="p-2 text-right">Neto a Cobrar (Gs)</th>
              </tr>
            </thead>
            <tbody>
              {data.length > 0 ? (
                data.map((row, i) => (
                  <tr key={i} className="border-b hover:bg-gray-50">
                    <td className="p-2">{row.periodo}</td>
                    <td className="p-2 text-right">{row.neto.toLocaleString("es-PY")}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="2" className="text-center text-gray-500 p-3">
                    No hay liquidaciones registradas.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

function KpiCard({ titulo, valor }) {
  return (
    <div className="bg-white shadow p-4 rounded text-center">
      <h2 className="text-gray-500 text-sm">{titulo}</h2>
      <p className="text-2xl font-bold text-gray-800">{valor}</p>
    </div>
  );
}
