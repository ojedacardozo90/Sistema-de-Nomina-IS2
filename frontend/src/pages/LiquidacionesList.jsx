// ============================================================
// 📄 Listado de Liquidaciones — Sistema de Nómina IS2
// Con botón para enviar recibo por correo (SendGrid)
// ============================================================

import { useEffect, useState } from "react";
import { listarLiquidaciones, enviarRecibo } from "../utils/api";

// ============================================================
// 📦 COMPONENTE PRINCIPAL
// ============================================================
export default function LiquidacionesList() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sendingId, setSendingId] = useState(null);

  // ===============================
  // 🔹 Cargar liquidaciones al montar
  // ===============================
  useEffect(() => {
    listarLiquidaciones()
      .then((res) => {
        setItems(res.data || []);
      })
      .catch((err) => {
        console.error("Error al cargar:", err);
        alert("❌ Error al cargar las liquidaciones");
      })
      .finally(() => setLoading(false));
  }, []);

  // ===============================
  // 📩 Enviar recibo individual
  // ===============================
  const handleEnviar = async (id) => {
    if (!window.confirm("¿Deseas enviar el recibo por correo?")) return;
    setSendingId(id);
    try {
      const data = await enviarRecibo(id);
      alert(data.mensaje || "✅ Recibo enviado correctamente.");
      // ✅ Actualizar estado visual
      setItems((prev) =>
        prev.map((l) =>
          l.id === id ? { ...l, enviado_email: true } : l
        )
      );
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error || "❌ Error al enviar el recibo.");
    } finally {
      setSendingId(null);
    }
  };

  // ===============================
  // 🧾 Renderizado
  // ===============================
  if (loading)
    return (
      <div className="p-6 text-center text-gray-600">
        Cargando liquidaciones...
      </div>
    );

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Listado de Liquidaciones</h1>

      <table className="w-full text-sm border rounded-lg overflow-hidden shadow">
        <thead className="bg-blue-600 text-white">
          <tr>
            <th className="py-2 px-3 text-left">ID</th>
            <th className="py-2 px-3 text-left">Empleado</th>
            <th className="py-2 px-3 text-left">Periodo</th>
            <th className="py-2 px-3 text-left">Neto a Cobrar</th>
            <th className="py-2 px-3 text-center">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {items.length === 0 && (
            <tr>
              <td colSpan="5" className="text-center py-4 text-gray-500">
                No hay liquidaciones registradas.
              </td>
            </tr>
          )}

          {items.map((liq) => (
            <tr
              key={liq.id}
              className="border-t hover:bg-gray-50 transition-all"
            >
              <td className="py-2 px-3">{liq.id}</td>
              <td className="py-2 px-3">{liq.empleado_nombre}</td>
              <td className="py-2 px-3">{liq.periodo}</td>
              <td className="py-2 px-3">{liq.salario_neto} Gs</td>
              <td className="py-2 px-3 text-center">
                {liq.enviado_email ? (
                  <span className="text-green-600 font-medium">📨 Enviado</span>
                ) : (
                  <button
                    onClick={() => handleEnviar(liq.id)}
                    disabled={sendingId === liq.id}
                    className={`${
                      sendingId === liq.id
                        ? "bg-gray-400 cursor-not-allowed"
                        : "bg-blue-600 hover:bg-blue-700"
                    } text-white px-3 py-1 rounded transition-all`}
                  >
                    {sendingId === liq.id ? "Enviando..." : "Enviar Recibo"}
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
