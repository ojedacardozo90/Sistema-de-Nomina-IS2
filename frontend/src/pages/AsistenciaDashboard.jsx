
//  Dashboard de Asistencia Mensual — Sistema de Nómina IS2
// FP-UNA / Fuerza Aérea Paraguaya


import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import {
  listarAsistencias,
  exportarAsistenciasExcel,
  exportarAsistenciasPDF,
} from "../utils/api";

export default function AsistenciaDashboard() {
  const [data, setData] = useState([]);
  const [mes, setMes] = useState(new Date().getMonth() + 1);
  const [anio, setAnio] = useState(new Date().getFullYear());
  const [totales, setTotales] = useState({});
  const [loading, setLoading] = useState(false);

  
  // # Obtener datos del backend
  
  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await listarAsistencias({ mes, anio });
      const resumen = res?.data?.resumen || res?.results || res || [];

      const dataset = resumen.map((r) => ({
        empleado: r.empleado__nombre || r.empleado_nombre || "Empleado",
        cedula: r.empleado__cedula || r.cedula || "",
        presentes: r.presentes || 0,
        tardanzas: r.tardanzas || 0,
        ausencias: r.ausencias || 0,
        incompletos: r.incompletos || 0,
        minutos_trabajados: r.minutos_trabajados || 0,
      }));
      setData(dataset);

      const sum = (key) => dataset.reduce((acc, r) => acc + (r[key] || 0), 0);
      setTotales({
        presentes: sum("presentes"),
        tardanzas: sum("tardanzas"),
        ausencias: sum("ausencias"),
        incompletos: sum("incompletos"),
        minutos: sum("minutos_trabajados"),
      });
    } catch (err) {
      console.error(" Error al obtener el reporte de asistencia:", err);
      alert("No se pudo obtener el reporte de asistencia mensual.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [mes, anio]);

  
  // 💾 Descarga de reportes (Excel / PDF)
  
  const handleExport = async (formato) => {
    try {
      if (formato === "excel") {
        const blob = await exportarAsistenciasExcel(mes, anio);
        descargar(blob, `reporte_asistencia_${mes}_${anio}.xlsx`);
      } else {
        const blob = await exportarAsistenciasPDF(mes, anio);
        descargar(blob, `reporte_asistencia_${mes}_${anio}.pdf`);
      }
    } catch (err) {
      console.error(` Error al exportar ${formato}:`, err);
      alert("No se pudo descargar el reporte. Verifica el backend.");
    }
  };

  
  //  Utilidad de descarga
  
  function descargar(blob, nombreArchivo) {
    const url = window.URL.createObjectURL(new Blob([blob]));
    const link = document.createElement("a");
    link.href = url;
    link.download = nombreArchivo;
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  }

  
  // 🔸 Render principal
  
  return (
    <Layout>
      <div className="p-6 space-y-6">
        <h1 className="text-3xl font-bold text-emerald-700">
          Dashboard de Asistencia — {mes}/{anio}
        </h1>

        {/*  Filtros + Exportación */}
        <div className="flex flex-wrap gap-4 items-end justify-between">
          <div className="flex gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-600">
                Mes
              </label>
              <input
                type="number"
                min="1"
                max="12"
                value={mes}
                onChange={(e) => setMes(Number(e.target.value))}
                className="border rounded-lg px-3 py-1 w-24"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-600">
                Año
              </label>
              <input
                type="number"
                min="2020"
                value={anio}
                onChange={(e) => setAnio(Number(e.target.value))}
                className="border rounded-lg px-3 py-1 w-28"
              />
            </div>

            <button
              onClick={fetchData}
              className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700"
            >
               Actualizar
            </button>
          </div>

          {/* 💾 Botones de exportación */}
          <div className="flex gap-2">
            <button
              onClick={() => handleExport("excel")}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
               Exportar Excel
            </button>
            <button
              onClick={() => handleExport("pdf")}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
            >
               Exportar PDF
            </button>
          </div>
        </div>

        {/*  Gráfico */}
        {loading ? (
          <p className="text-gray-500">Cargando datos...</p>
        ) : data.length > 0 ? (
          <>
            <div className="bg-white shadow-lg rounded-xl p-4 h-[450px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={data}
                  margin={{ top: 20, right: 20, left: 0, bottom: 50 }}
                >
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="empleado"
                    angle={-30}
                    textAnchor="end"
                    interval={0}
                    height={70}
                  />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="presentes" fill="#10B981" name="Presentes" />
                  <Bar dataKey="tardanzas" fill="#F59E0B" name="Tardanzas" />
                  <Bar dataKey="ausencias" fill="#EF4444" name="Ausencias" />
                  <Bar
                    dataKey="incompletos"
                    fill="#6366F1"
                    name="Incompletos"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/*  Totales globales */}
            <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 mt-6 shadow-sm">
              <h2 className="text-xl font-semibold text-emerald-700 mb-2">
                Totales Generales
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3 text-gray-800">
                <div>
                   <strong>Presentes:</strong> {totales.presentes}
                </div>
                <div>
                  ⏰ <strong>Tardanzas:</strong> {totales.tardanzas}
                </div>
                <div>
                  🚫 <strong>Ausencias:</strong> {totales.ausencias}
                </div>
                <div>
                   <strong>Incompletos:</strong> {totales.incompletos}
                </div>
                <div>
                   <strong>Minutos:</strong> {totales.minutos}
                </div>
              </div>
            </div>
          </>
        ) : (
          <p className="text-gray-600">
            No hay datos disponibles para este mes.
          </p>
        )}
      </div>
    </Layout>
  );
}
