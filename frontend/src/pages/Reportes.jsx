
//  Reportes — Gráficos analíticos de nómina (versión extendida)

// Muestra:
//   • Gráfico de evolución mensual de totales
//   • Filtros por mes y año
//   • Exportaciones PDF / Excel
//   • Totales de nómina en cabecera

// Endpoints utilizados:
//   • GET /api/nomina_cal/analytics/kpis/?mes=AAAA-MM
//   • GET /api/nomina_cal/reportes/pdf/?mes=&anio=
//   • GET /api/nomina_cal/reportes/excel/?mes=&anio=


import { useEffect, useState } from "react";
import api from "../utils/api";
import Layout from "../components/Layout";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function Reportes() {
  // 
  // # Estados principales
  // 
  const [data, setData] = useState([]);
  const [kpis, setKpis] = useState(null);
  const [anio, setAnio] = useState(new Date().getFullYear());
  const [mes, setMes] = useState(new Date().getMonth() + 1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  
  //  Cargar datos del backend
  
  const cargarKpis = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get(
        `/nomina_cal/analytics/kpis/?mes=${anio}-${String(mes).padStart(2, "0")}`
      );
      setData(res.data.evolucion || []);
      setKpis(res.data.kpis || null);
    } catch (err) {
      console.error(" Error al cargar KPIs:", err);
      setError("No se pudieron cargar los datos de los reportes.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarKpis();
  }, [anio, mes]);

  
  //  Exportar reportes (PDF / Excel)
  
  const exportarPDF = () =>
    window.open(
      `${import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api"}/nomina_cal/reportes/pdf/?mes=${mes}&anio=${anio}`,
      "_blank"
    );

  const exportarExcel = () =>
    window.open(
      `${import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api"}/nomina_cal/reportes/excel/?mes=${mes}&anio=${anio}`,
      "_blank"
    );

  
  //  Indicadores de carga / error
  
  if (loading)
    return (
      <Layout>
        <div className="flex justify-center items-center h-screen">
          <div className="flex flex-col items-center gap-2">
            <div className="w-12 h-12 border-4 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-gray-600 font-medium">
              Cargando reportes de nómina...
            </p>
          </div>
        </div>
      </Layout>
    );

  if (error)
    return (
      <Layout>
        <div className="text-center text-red-600 mt-10">
          <p className="font-semibold">{error}</p>
        </div>
      </Layout>
    );

  
  //  Render principal
  
  return (
    <Layout>
      <div className="p-6 space-y-6">
        <h1 className="text-2xl font-bold"> Reportes de Nómina</h1>

        {/* =====
              Filtros y exportaciones
           ===== */}
        <div className="flex flex-col sm:flex-row justify-between items-center bg-white p-4 shadow rounded gap-3">
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Año:</label>
            <input
              type="number"
              min="2020"
              max={new Date().getFullYear()}
              value={anio}
              onChange={(e) => setAnio(e.target.value)}
              className="border rounded p-1 w-24"
            />
            <label className="text-sm text-gray-600 ml-2">Mes:</label>
            <select
              value={mes}
              onChange={(e) => setMes(Number(e.target.value))}
              className="border rounded p-1"
            >
              {Array.from({ length: 12 }, (_, i) => (
                <option key={i + 1} value={i + 1}>
                  {new Date(0, i).toLocaleString("es", { month: "long" })}
                </option>
              ))}
            </select>
          </div>

          <div className="flex gap-2">
            <button
              onClick={exportarPDF}
              className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            >
               Exportar PDF
            </button>
            <button
              onClick={exportarExcel}
              className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
            >
               Exportar Excel
            </button>
          </div>
        </div>

        {/* =====
             # KPIs (totales y promedios)
           ===== */}
        {kpis && (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <KpiCard
              titulo="Total General"
              valor={`${kpis.total_general?.toLocaleString("es-PY")} Gs`}
            />
            <KpiCard
              titulo="Promedio Neto"
              valor={`${kpis.promedio_neto?.toLocaleString("es-PY")} Gs`}
            />
            <KpiCard
              titulo="Total Empleados"
              valor={kpis.total_empleados?.toLocaleString("es-PY")}
            />
          </div>
        )}

        {/* =====
              Gráfico de evolución mensual
           ===== */}
        <div className="bg-white shadow rounded p-4">
          <h2 className="text-lg font-semibold mb-2">
            Evolución de la Nómina ({anio})
          </h2>
          <p className="text-sm text-gray-500 mb-3">
            Visualiza el total mensual de la nómina en el período seleccionado.
          </p>
          {data.length === 0 ? (
            <p className="text-gray-500 text-center mt-10">
              No hay datos disponibles.
            </p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="mes" />
                <YAxis />
                <Tooltip
                  formatter={(v) =>
                    `${parseFloat(v).toLocaleString("es-PY")} Gs`
                  }
                />
                <Line
                  type="monotone"
                  dataKey="total"
                  stroke="#2563eb"
                  name="Total mensual"
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </Layout>
  );
}


// 🔸 Componente reutilizable para KPIs

function KpiCard({ titulo, valor }) {
  return (
    <div className="bg-white shadow p-4 rounded text-center">
      <h3 className="text-gray-500 text-sm">{titulo}</h3>
      <p className="text-2xl font-bold">{valor}</p>
    </div>
  );
}
