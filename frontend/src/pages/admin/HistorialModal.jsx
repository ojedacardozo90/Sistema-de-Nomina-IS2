// ============================================================
// 🕘 HistorialModal — Registro de auditoría por objeto
// ------------------------------------------------------------
// Replica el "Historial de cambios" del Django Admin
// Utiliza tu app auditoria para mostrar los logs de cambios
// Endpoint: /api/auditoria/logs/?obj=model&id=pk
// ============================================================

import { useEffect, useState } from "react";
import api from "../../utils/api";

export default function HistorialModal({ open, model, id, onClose }) {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    if (open && model && id) {
      api.get(`auditoria/logs/`, { params: { obj: model, id } })
        .then(r => setLogs(r.data || []))
        .catch(() => setLogs([]));
    }
  }, [open, model, id]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white w-[640px] max-w-[95vw] rounded shadow-lg">
        <header className="px-4 py-3 border-b flex justify-between items-center">
          <h3 className="font-semibold">Historial de cambios</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
        </header>
        <div className="p-4 max-h-[70vh] overflow-auto">
          {logs.length === 0 ? (
            <p className="text-gray-500 text-sm text-center">Sin registros de auditoría.</p>
          ) : (
            <table className="min-w-full text-sm">
              <thead>
                <tr className="text-left border-b">
                  <th className="py-1 px-2">Fecha</th>
                  <th className="py-1 px-2">Usuario</th>
                  <th className="py-1 px-2">Acción</th>
                  <th className="py-1 px-2">Detalle</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, i) => (
                  <tr key={i} className="border-b hover:bg-gray-50">
                    <td className="py-1 px-2">{new Date(log.fecha).toLocaleString("es-PY")}</td>
                    <td className="py-1 px-2">{log.usuario}</td>
                    <td className="py-1 px-2">{log.accion}</td>
                    <td className="py-1 px-2">{log.detalle}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        <footer className="px-4 py-2 border-t text-right">
          <button className="px-3 py-2 rounded border" onClick={onClose}>Cerrar</button>
        </footer>
      </div>
    </div>
  );
}
