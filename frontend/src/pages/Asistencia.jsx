// ============================================================
// 🕒 Control de Asistencia — Sistema de Nómina IS2 (FP-UNA / FAP)
// Integrado con backend Django mediante api.js
// ============================================================

import { useEffect, useState } from "react";
import { listarAsistencias, marcarAsistencia } from "../utils/api";

export default function Asistencia() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);

  // 🔹 Cargar asistencias desde el backend
  async function load() {
    setLoading(true);
    try {
      const data = await listarAsistencias({ page_size: 50 });
      setItems(data.results || data); // Soporte para paginación DRF
    } catch (error) {
      console.error("❌ Error al cargar asistencias:", error);
      alert("Error al obtener la lista de asistencias.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  // 🔹 Marcar entrada o salida
  async function handleMarcar(tipo) {
    try {
      await marcarAsistencia(tipo);
      await load();
      alert(`✅ Asistencia ${tipo} registrada correctamente.`);
    } catch (e) {
      console.error("❌ Error al marcar asistencia:", e);
      alert("Error al marcar asistencia. Revise la consola para más detalles.");
    }
  }

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold text-gray-800">
        Control de Asistencia
      </h1>

      <div className="flex gap-3">
        <button
          onClick={() => handleMarcar("entrada")}
          className="px-4 py-2 rounded-lg border bg-green-600 text-white hover:bg-green-700 transition"
        >
          Marcar Entrada
        </button>

        <button
          onClick={() => handleMarcar("salida")}
          className="px-4 py-2 rounded-lg border bg-blue-600 text-white hover:bg-blue-700 transition"
        >
          Marcar Salida
        </button>
      </div>

      {loading ? (
        <div className="mt-4 text-gray-600">Cargando asistencias…</div>
      ) : (
        <table className="w-full mt-4 text-sm border">
          <thead>
            <tr className="text-left border-b bg-gray-100">
              <th className="py-2 px-2">Empleado</th>
              <th className="px-2">Fecha</th>
              <th className="px-2">Entrada</th>
              <th className="px-2">Salida</th>
              <th className="px-2">Minutos</th>
              <th className="px-2">Estado</th>
              <th className="px-2">Justificación</th>
            </tr>
          </thead>
          <tbody>
            {items.length > 0 ? (
              items.map((r) => (
                <tr key={r.id} className="border-b hover:bg-gray-50">
                  <td className="py-2 px-2">{r.empleado_nombre}</td>
                  <td className="px-2">{r.fecha}</td>
                  <td className="px-2">{r.hora_entrada || "-"}</td>
                  <td className="px-2">{r.hora_salida || "-"}</td>
                  <td className="px-2 text-center">
                    {r.minutos_trabajados ?? "-"}
                  </td>
                  <td className={`px-2 ${colorEstado(r.estado)}`}>
                    {r.estado}
                  </td>
                  <td className="px-2">{r.justificacion || "-"}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="text-center py-4 text-gray-500">
                  No se registran asistencias todavía.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}
    </div>
  );
}

// 🎨 Colores de estado
function colorEstado(est) {
  if (est === "presente") return "text-green-700 font-medium";
  if (est === "tardanza") return "text-yellow-600 font-medium";
  if (est === "ausencia") return "text-red-600 font-medium";
  return "text-gray-600";
}
