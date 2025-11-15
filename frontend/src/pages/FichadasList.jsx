
//  FichadasList — Gestión idéntica al admin (listar/filtrar/eliminar/marcar)
// Endpoints esperados:
//   • GET    /asistencia/fichadas/
//   • POST   /asistencia/fichadas/marcar/  (body: { tipo: "entrada"|"salida" })
//   • DELETE /asistencia/fichadas/:id/


import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../utils/api";
import Layout from "../components/Layout";

// Helpers seguros para normalizar valores sin romperse
const s = (v) => (v ?? "").toString().toLowerCase();

const textoEmpleado = (f) => {
  const e = f?.empleado;
  if (!e) return "";
  if (typeof e === "string") return e;                 // "Juan Pérez"
  if (typeof e === "number") return String(e);         // 123
  // Objeto: { nombre, apellido, cedula, email, ... }
  const partes = [e.nombre, e.apellido, e.cedula, e.email]
    .filter(Boolean)
    .join(" ");
  return partes || (e.username ?? "");
};

export default function FichadasList() {
  const [rows, setRows] = useState([]);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(true);

  // =
  // Cargar fichadas
  // =
  const load = async () => {
    setLoading(true);
    try {
      const res = await api.get("/asistencia/fichadas/");
      const data = Array.isArray(res.data) ? res.data : [];
      setRows(data);
    } catch (err) {
      console.error(" Error cargando fichadas:", err);
      setRows([]); // evitar crash
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  // =
  // Marcar entrada / salida
  // =
  const marcar = async (tipo) => {
    try {
      await api.post("/asistencia/fichadas/marcar/", { tipo });
      await load();
    } catch (err) {
      console.error(" Error marcando fichada:", err);
      alert("No se pudo marcar la fichada.");
    }
  };

  // =
  // Eliminar fichada
  // =
  const onDelete = async (id) => {
    if (!window.confirm("¿Eliminar esta fichada?")) return;
    try {
      await api.delete(`/asistencia/fichadas/${id}/`);
      await load();
    } catch (err) {
      console.error(" Error eliminando fichada:", err);
      alert("No se pudo eliminar la fichada.");
    }
  };

  // =
  // Filtro local (como admin)
  // =
  const filtered = rows.filter((f) => {
    const empleadoTxt = textoEmpleado(f);
    return (
      s(empleadoTxt).includes(s(q)) ||
      s(f.tipo).includes(s(q)) ||
      s(f.fecha).includes(s(q)) ||
      s(f.hora).includes(s(q)) ||
      s(f.timestamp).includes(s(q)) ||
      s(f.observacion || f.nota || f.detalle).includes(s(q))
    );
  });

  // =
  // Render
  // =
  return (
    <Layout>
      <div className="p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <h1 className="text-2xl font-bold"> Fichadas</h1>

          <div className="flex gap-2">
            <button
              onClick={() => marcar("entrada")}
              className="bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-2 rounded"
            >
              + Marcar Entrada
            </button>
            <button
              onClick={() => marcar("salida")}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-3 py-2 rounded"
            >
              ⇄ Marcar Salida
            </button>
          </div>
        </div>

        <input
          className="border px-3 py-2 rounded w-full"
          placeholder="Buscar por empleado, tipo, fecha, hora…"
          value={q}
          onChange={(e) => setQ(e.target.value)}
        />

        {loading ? (
          <p className="text-gray-600">Cargando fichadas…</p>
        ) : (
          <div className="overflow-x-auto bg-white rounded shadow">
            <table className="w-full text-sm border">
              <thead className="bg-gray-50">
                <tr>
                  <th className="p-2 border">Empleado</th>
                  <th className="p-2 border">Tipo</th>
                  <th className="p-2 border">Fecha</th>
                  <th className="p-2 border">Hora</th>
                  <th className="p-2 border">Observación</th>
                  <th className="p-2 border text-center">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((f) => {
                  const empTxt = textoEmpleado(f);
                  // Compatibilidad de campos de tiempo:
                  const fecha = f.fecha || (f.timestamp ? String(f.timestamp).slice(0, 10) : "");
                  const hora =
                    f.hora ||
                    (f.timestamp ? new Date(f.timestamp).toTimeString().slice(0, 8) : "");

                  return (
                    <tr key={f.id} className="border-t hover:bg-gray-50">
                      <td className="p-2 border">{empTxt}</td>
                      <td className="p-2 border capitalize">{f.tipo}</td>
                      <td className="p-2 border">{fecha}</td>
                      <td className="p-2 border">{hora}</td>
                      <td className="p-2 border">
                        {f.observacion || f.nota || f.detalle || "—"}
                      </td>
                      <td className="p-2 border text-center">
                        <button
                          onClick={() => onDelete(f.id)}
                          className="bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded"
                        >
                          Eliminar
                        </button>
                      </td>
                    </tr>
                  );
                })}
                {filtered.length === 0 && (
                  <tr>
                    <td className="p-3 text-center text-gray-500" colSpan={6}>
                      Sin resultados.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
