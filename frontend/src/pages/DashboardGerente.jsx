// ============================================================
// 📈 Dashboard Gerente RRHH (Sprint 6–7) — NóminaPro
// ------------------------------------------------------------
// Muestra:
//  • Total empleados, total liquidaciones, promedio de nómina
//  • Evolución últimos meses (línea)
//  • KPIs complementarios desde /analytics/kpis/
// Endpoints:
//  • GET /nomina_cal/dashboard/gerente/
//  • GET /nomina_cal/analytics/kpis/
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
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function DashboardGerente() {
  const [data, setData] = useState([]);
  const [info, setInfo] = useState(null);
  const [kpis, setKpis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [resDashboard, resKpis] = await Promise.all([
        api.get("/nomina_cal/dashboard/gerente/"),
        api.get("/nomina_cal/analytics/kpis/"),
      ]);

      const evolucion = resDashboard.data.evolucion || [];
      const formatted = evolucion.map((item) => ({
        mes: `${item.mes}/${item.anio}`,
        total: Number(item.total_mes || 0),
      }));

      setInfo(resDashboard.data);
      setData(formatted);
      setKpis(resKpis.data);
    } catch (err) {
      console.error("Error dashboard gerente:", err);
      setError("No se pudieron cargar los datos del dashboard.");
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
          <div className="w-12 h-12 border-4 border-emerald-400 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-600 font-medium">
            Cargando datos del Dashboard Gerente...
          </p>
        </div>
      </div>
    );
  }

  if (error)
    return (
      <div className="text-center text-red-600 mt-10 font-semibold">
        {error}
      </div>
    );
  if (!info)
    return (
      <div className="text-center text-gray-600 mt-10">
        No se pudieron obtener datos.
      </div>
    );

  // ✅ Estructura con HeaderDashboard y sección principal
  return (
    <div className="p-6">
      {/* Encabezado superior */}
      <HeaderDashboard titulo="Dashboard Administrativo" />

      {/* Contenido principal */}
      <section className="mt-4 space-y-6">
        {/* KPIs principales */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <KpiCard
            titulo="Total Empleados"
            valor={Number(info.total_empleados || 0).toLocaleString("es-PY")}
          />
          <KpiCard
            titulo="Total Liquidaciones"
            valor={Number(info.total_liquidaciones || 0).toLocaleString("es-PY")}
          />
          <KpiCard
            titulo="Promedio de Nómina"
            valor={`${Number(info.promedio_nomina || 0).toLocaleString("es-PY")} Gs`}
          />
        </div>

        {/* KPIs complementarios */}
        {kpis && (
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            <KpiCard
              titulo="Costo Total Mes"
              valor={`${Number(kpis.total_nomina_mes || 0).toLocaleString("es-PY")} Gs`}
            />
            <KpiCard
              titulo="Total Descuentos"
              valor={`${Number(kpis.total_descuentos_mes || 0).toLocaleString("es-PY")} Gs`}
            />
            <KpiCard
              titulo="Total IPS"
              valor={`${Number(kpis.total_ips_mes || 0).toLocaleString("es-PY")} Gs`}
            />
            <KpiCard titulo="Mes Analizado" valor={`${kpis.mes}/${kpis.anio}`} />
          </div>
        )}

        {/* Gráfico de evolución mensual */}
        <div className="bg-white shadow p-4 rounded h-80">
          <h2 className="font-semibold mb-2">
            Evolución de Nóminas (últimos meses)
          </h2>
          {data.length === 0 ? (
            <p className="text-gray-500 text-center mt-10">
              No hay datos para mostrar.
            </p>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="mes" />
                <YAxis />
                <Tooltip formatter={(v) => Number(v).toLocaleString("es-PY")} />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="total"
                  stroke="#1ABC9C"
                  strokeWidth={2}
                  dot={{ r: 4, fill: "#1ABC9C" }}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Tabla comparativa */}
        <div className="bg-white p-4 rounded shadow">
          <h2 className="font-semibold mb-2">Comparativo Mensual</h2>
          <table className="w-full text-sm border border-gray-200">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="p-2 text-left">Mes</th>
                <th className="p-2 text-right">Total (Gs)</th>
              </tr>
            </thead>
            <tbody>
              {data.length > 0 ? (
                data.map((row, i) => (
                  <tr key={i} className="border-b hover:bg-gray-50">
                    <td className="p-2">{row.mes}</td>
                    <td className="p-2 text-right">
                      {Number(row.total).toLocaleString("es-PY")}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan="2"
                    className="p-2 text-center text-gray-500"
                  >
                    No hay datos disponibles.
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
      <p className="text-2xl font-bold">{valor}</p>
    </div>
  );
}
