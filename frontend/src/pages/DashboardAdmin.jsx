// ============================================================
// 📊 Dashboard Administrador (Sprint 6–7 Final Integrado)
// ------------------------------------------------------------
// Panel global con:
//   • KPIs generales
//   • Filtro por mes
//   • Exportaciones PDF / Excel
//   • Gráfico de barras y gráfico circular
// ------------------------------------------------------------
// Endpoints Django:
//   • GET /api/nomina_cal/reporte-general/?mes=AAAA-MM
//   • GET /api/nomina_cal/exportar-pdf/
//   • GET /api/nomina_cal/exportar-excel/
// ============================================================
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
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import Layout from "../components/Layout";

export default function DashboardAdmin() {
  // ==============================
  // 🔹 Estados principales
  // ==============================
  const [data, setData] = useState(null);
  const [detalle, setDetalle] = useState([]);
  const [mes, setMes] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // ============================================================
  // 🎯 Obtener datos del backend (reporte general)
  // ============================================================
  const fetchData = async (filtroMes = "") => {
    setLoading(true);
    setError(null);
    try {
      const endpoint = filtroMes
        ? `/nomina_cal/reporte-general/?mes=${filtroMes}`
        : "/nomina_cal/reporte-general/";

      const res = await api.get(endpoint);
      setData({
        total_general: res.data.total_general || 0,
        total_empleados: res.data.detalle?.length || 0,
      });
      setDetalle(res.data.detalle || []);
    } catch (err) {
      console.error("❌ Error cargando dashboard admin:", err);
      setError("No se pudieron cargar los datos del reporte general.");
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // 🔄 Cargar datos iniciales
  // ============================================================
  useEffect(() => {
    fetchData();
  }, []);

  // ============================================================
  // 📤 Exportar archivos PDF / Excel
  // ============================================================
  const exportarArchivo = async (tipo) => {
    try {
      const endpoint =
        tipo === "pdf"
          ? "/nomina_cal/exportar-pdf/"
          : "/nomina_cal/exportar-excel/";

      const res = await api.get(endpoint, { responseType: "blob" });
      const url = URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement("a");
      a.href = url;
      a.download =
        tipo === "pdf" ? "reporte_nomina.pdf" : "reporte_nomina.xlsx";
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error(`❌ Error exportando ${tipo}:`, err);
    }
  };

  // ============================================================
  // ⏳ Indicadores de carga / error
  // ============================================================
  if (loading)
    return (
      <Layout>
        <div className="flex justify-center items-center h-screen">
          <div className="flex flex-col items-center gap-2">
            <div className="w-12 h-12 border-4 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-gray-600 font-medium">
              Cargando datos del Dashboard Administrador...
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

  // ============================================================
  // 🎨 Render principal del Dashboard
  // ============================================================
  const COLORS = ["#1ABC9C", "#3498DB", "#9B59B6", "#E67E22", "#E74C3C"];

  return (
    <Layout>
      <div className="p-6">
        <HeaderDashboard titulo="Dashboard Administrativo" />

        {/* Contenido principal del dashboard */}
        <section className="mt-4 space-y-6">
          {/* =====================================================
               📅 Filtros temporales y exportación
             ===================================================== */}
          <div className="flex flex-col sm:flex-row justify-between items-center bg-white shadow p-4 rounded gap-3">
            <div className="flex gap-2 items-center">
              <label className="text-sm text-gray-600">Mes:</label>
              <input
                type="month"
                value={mes}
                onChange={(e) => {
                  setMes(e.target.value);
                  fetchData(e.target.value);
                }}
                className="border p-1 rounded"
              />
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => exportarArchivo("pdf")}
                className="px-3 py-1 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Exportar PDF
              </button>
              <button
                onClick={() => exportarArchivo("excel")}
                className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Exportar Excel
              </button>
            </div>
          </div>

          {/* =====================================================
               🔹 KPIs principales
             ===================================================== */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <KpiCard
              titulo="Total Empleados"
              valor={data.total_empleados?.toLocaleString("es-PY")}
            />
            <KpiCard
              titulo="Total General de Nómina"
              valor={`${data.total_general?.toLocaleString("es-PY")} Gs`}
            />
            <KpiCard titulo="Reportes Exportables" valor="Excel / PDF" />
          </div>

          {/* =====================================================
               📊 Gráfico de barras (Totales por empleado)
             ===================================================== */}
          <div className="bg-white shadow p-4 rounded h-80">
            <h2 className="font-semibold mb-2">Totales por Empleado</h2>
            <p className="text-gray-500 text-sm mb-2">
              Totales por empleado según el período filtrado
            </p>

            {detalle.length === 0 ? (
              <p className="text-gray-500 text-center mt-10">
                No hay datos para mostrar en este período.
              </p>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={detalle}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="empleado" />
                  <YAxis />
                  <Tooltip formatter={(v) => v.toLocaleString("es-PY")} />
                  <Legend />
                  <Bar dataKey="total" fill="#3498DB" name="Monto Total" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* =====================================================
               🥧 Gráfico circular (Distribución de Liquidaciones)
             ===================================================== */}
          <div className="bg-white shadow p-4 rounded h-80">
            <h2 className="font-semibold mb-2">
              Distribución de Liquidaciones
            </h2>
            <p className="text-gray-500 text-sm mb-2">
              Representa el porcentaje de monto total por empleado.
            </p>

            {detalle.length === 0 ? (
              <p className="text-gray-500 text-center mt-10">
                Sin datos para mostrar.
              </p>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={detalle}
                    dataKey="total"
                    nameKey="empleado"
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    label
                  >
                    {detalle.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip formatter={(v) => v.toLocaleString("es-PY")} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </section>
      </div>
    </Layout>
  );
}

// ============================================================
// 🔸 Componente reutilizable para KPIs
// ============================================================
function KpiCard({ titulo, valor }) {
  return (
    <div className="bg-white shadow p-4 rounded text-center">
      <h2 className="text-gray-500 text-sm">{titulo}</h2>
      <p className="text-2xl font-bold">{valor}</p>
    </div>
  );
}
