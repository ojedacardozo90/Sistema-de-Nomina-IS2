import { useState } from "react";
import api from "../utils/api";

export default function ReportesPage() {
  const [filtros, setFiltros] = useState({ mes: "", anio: "", empleado_id: "" });
  const [reporte, setReporte] = useState(null);

  const handleChange = (e) =>
    setFiltros({ ...filtros, [e.target.name]: e.target.value });

  const buscar = async () => {
    try {
      const res = await api.get("/nomina/reporte_general/", { params: filtros });
      setReporte(res.data);
    } catch (err) {
      console.error("Error obteniendo reporte:", err);
    }
  };

  const exportarExcel = () => {
    window.open("http://127.0.0.1:8000/api/nomina/exportar_excel/", "_blank");
  };

  const exportarPDF = () => {
    window.open("http://127.0.0.1:8000/api/nomina/exportar_pdf/", "_blank");
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4"> Reportes de Liquidaciones</h1>

      {/* Filtros */}
      <div className="bg-white p-4 rounded shadow space-y-2 mb-4">
        <h2 className="font-semibold mb-2">Filtros</h2>
        <div className="grid grid-cols-3 gap-4">
          <input
            type="number"
            name="mes"
            placeholder="Mes (1-12)"
            value={filtros.mes}
            onChange={handleChange}
            className="p-2 border rounded"
          />
          <input
            type="number"
            name="anio"
            placeholder="Año"
            value={filtros.anio}
            onChange={handleChange}
            className="p-2 border rounded"
          />
          <input
            type="number"
            name="empleado_id"
            placeholder="ID Empleado"
            value={filtros.empleado_id}
            onChange={handleChange}
            className="p-2 border rounded"
          />
        </div>
        <button
          onClick={buscar}
          className="bg-blue-600 text-white px-4 py-2 rounded mt-2"
        >
          Buscar
        </button>
      </div>

      {/* Resultados */}
      {reporte && (
        <div className="bg-white p-4 rounded shadow">
          <h2 className="font-semibold">Resultados</h2>
          <p>
            <strong>Total General:</strong> {reporte.total_general} Gs
          </p>
          <table className="w-full mt-4 border-collapse bg-white shadow">
            <thead>
              <tr className="bg-gray-200">
                <th className="p-2">Empleado</th>
                <th className="p-2">Fecha</th>
                <th className="p-2">Total</th>
              </tr>
            </thead>
            <tbody>
              {reporte.detalle.map((d, i) => (
                <tr key={i} className="border-t">
                  <td className="p-2">{d.empleado}</td>
                  <td className="p-2">{d.mes}/{d.anio}</td>
                  <td className="p-2">{d.total} Gs</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Exportar */}
      <div className="mt-4 space-x-2">
        <button
          onClick={exportarExcel}
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          Exportar Excel
        </button>
        <button
          onClick={exportarPDF}
          className="bg-red-600 text-white px-4 py-2 rounded"
        >
          Exportar PDF
        </button>
      </div>
    </div>
  );
}
