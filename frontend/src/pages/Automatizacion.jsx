import { useState } from "react";
import api from "../utils/api"; // 👈 corregido
import Layout from "../components/Layout";

// ============================================================
// ⚡ Automatización con Celery
// - Ejecutar tareas programadas manualmente
// - Debug de Celery
// - Generar + Enviar Nóminas
// - Enviar recibo individual por ID
// ============================================================

export default function Automatizacion() {
  const [mensaje, setMensaje] = useState("");
  const [id, setId] = useState("");
  const [log, setLog] = useState([]);

  // 👉 Ejecutar tareas generales
  const ejecutar = async (endpoint) => {
    try {
     const res = await api.post(`/api/nomina_cal/${endpoint}/`);
      setMensaje(res.data.mensaje || "✅ Tarea ejecutada con éxito");
    } catch (err) {
      console.error("❌ Error al ejecutar tarea", err);
      setMensaje("❌ Error al ejecutar tarea");
    }
  };

  // 👉 Enviar un recibo individual por ID
  const enviarUno = async () => {
    try {
       const r = await api.post(`/api/nomina_cal/liquidaciones/${id}/enviar-recibo/`);
      
      setLog((prev) => [...prev, { id, r: r.data }]);
    } catch (err) {
      console.error("❌ Error al enviar recibo", err);
      setLog((prev) => [...prev, { id, r: "❌ Error al enviar recibo" }]);
    }
  };

  return (
    <Layout>
      <div className="p-6 space-y-8">
        <div>
          <h1 className="text-2xl font-bold mb-4">⚡ Automatización de Nóminas</h1>
          <p className="mb-6 text-gray-700">
            Desde aquí puedes lanzar manualmente las tareas automáticas que también
            se pueden programar con <b>Celery Beat</b>.
          </p>

          <div className="space-y-4">
            <button
              onClick={() => ejecutar("tasks/debug")}
              className="w-full bg-gray-700 text-white px-4 py-3 rounded-lg hover:bg-gray-600"
            >
              🐞 Debug Celery
            </button>

            <button
              onClick={() => ejecutar("tasks/generar-nominas")}
              className="w-full bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-500"
            >
              📊 Generar Nóminas Mensuales
            </button>

            <button
              onClick={() => ejecutar("tasks/enviar-recibos")}
              className="w-full bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-500"
            >
              📤 Enviar Recibos por Email
            </button>

            <button
              onClick={() => ejecutar("tasks/generar-y-enviar")}
              className="w-full bg-purple-600 text-white px-4 py-3 rounded-lg hover:bg-purple-500"
            >
              🔄 Generar + Enviar (Automático)
            </button>
          </div>

          {mensaje && (
            <div className="mt-6 p-4 bg-gray-100 text-gray-900 rounded-lg shadow">
              {mensaje}
            </div>
          )}
        </div>

        {/* Bloque para enviar un recibo individual */}
        <div className="p-4 border rounded-lg bg-white shadow space-y-4">
          <h2 className="text-lg font-semibold">📌 Enviar Recibo Individual</h2>
          <div className="flex gap-2">
            <input
              type="number"
              placeholder="ID Liquidación"
              value={id}
              onChange={(e) => setId(e.target.value)}
              className="border p-2 rounded flex-1"
            />
            <button
              onClick={enviarUno}
              className="px-3 py-2 bg-blue-600 text-white rounded"
            >
              Enviar Recibo
            </button>
          </div>
          <pre className="bg-gray-100 p-3 rounded text-xs overflow-x-auto">
            {JSON.stringify(log, null, 2)}
          </pre>
        </div>
      </div>
    </Layout>
  );
}