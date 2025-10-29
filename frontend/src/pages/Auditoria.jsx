// ============================================================
// 🔎 Auditoría del Sistema — NóminaPro
// GET /auditoria/logs/?modelo=&accion=&usuario=&desde=&hasta=&q=
// ============================================================
import { useEffect, useState } from "react";
import { listarAuditoria } from "../utils/api";

export default function Auditoria() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [f, setF] = useState({ modelo:"", accion:"", usuario:"", desde:"", hasta:"", q:"" });

  const load = async () => {
    setLoading(true);
    try {
      const { data } = await listarAuditoria(f);
      setLogs(data.results || data); // por si luego paginás
    } catch (e) {
      console.error("Error auditoría:", e);
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const onChange = (e) => setF({ ...f, [e.target.name]: e.target.value });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">🔎 Auditoría del Sistema</h1>

      <div className="bg-white p-4 rounded shadow grid grid-cols-2 md:grid-cols-6 gap-3">
        <input name="modelo" placeholder="Modelo (Empleado…)" value={f.modelo} onChange={onChange} className="border p-2 rounded" />
        <select name="accion" value={f.accion} onChange={onChange} className="border p-2 rounded">
          <option value="">Acción</option>
          <option value="create">CREATE</option>
          <option value="update">UPDATE</option>
          <option value="delete">DELETE</option>
        </select>
        <input name="usuario" placeholder="Usuario ID" value={f.usuario} onChange={onChange} className="border p-2 rounded" />
        <input name="desde" placeholder="Desde (YYYY-MM-DD)" value={f.desde} onChange={onChange} className="border p-2 rounded" />
        <input name="hasta" placeholder="Hasta (YYYY-MM-DD)" value={f.hasta} onChange={onChange} className="border p-2 rounded" />
        <input name="q" placeholder="Buscar en cambios/UA" value={f.q} onChange={onChange} className="border p-2 rounded" />
        <div className="col-span-2 md:col-span-6">
          <button onClick={load} className="bg-indigo-600 text-white px-3 py-2 rounded hover:bg-indigo-700">Aplicar filtros</button>
        </div>
      </div>

      <div className="bg-white p-4 rounded shadow">
        {loading ? (
          <div className="py-10 text-center text-gray-500">Cargando…</div>
        ) : logs.length === 0 ? (
          <div className="py-10 text-center text-gray-500">Sin registros.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border">
              <thead className="bg-gray-50">
                <tr>
                  <th className="p-2 text-left">Fecha</th>
                  <th className="p-2 text-left">Modelo</th>
                  <th className="p-2 text-left">Objeto</th>
                  <th className="p-2 text-left">Acción</th>
                  <th className="p-2 text-left">Usuario</th>
                  <th className="p-2 text-left">IP</th>
                  <th className="p-2 text-left">Cambios</th>
                </tr>
              </thead>
              <tbody>
                {logs.map(l => (
                  <tr key={l.id} className="border-b hover:bg-gray-50">
                    <td className="p-2">{new Date(l.fecha).toLocaleString()}</td>
                    <td className="p-2">{l.modelo}</td>
                    <td className="p-2">{l.objeto_id}</td>
                    <td className="p-2 uppercase">{l.accion}</td>
                    <td className="p-2">{l.usuario_username || l.usuario || "-"}</td>
                    <td className="p-2">{l.ip || "-"}</td>
                    <td className="p-2">
                      <pre className="text-[11px] whitespace-pre-wrap break-words">
                        {JSON.stringify(l.cambios, null, 2)}
                      </pre>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
