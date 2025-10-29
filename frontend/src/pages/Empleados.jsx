import { useEffect, useState } from "react";
import DashboardLayout from "../layouts/DashboardLayout";
import api, { getEmpleados } from "../utils/api";

export default function Empleados() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let m = true;
    (async () => {
      try {
        const res = await getEmpleados(); // usa tu api.js
        if (m) setRows(res.data || []);
      } catch (e) {
        console.error("Empleados:", e);
      } finally {
        if (m) setLoading(false);
      }
    })();
    return () => { m = false; };
  }, []);

  return (
    <DashboardLayout>
      <h1 className="text-xl font-semibold mb-4">👥 Empleados</h1>
      {loading ? (
        <div className="text-slate-400">Cargando...</div>
      ) : (
        <div className="p-4 bg-[#1E293B] border border-slate-700 rounded-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-[#0f1722]">
                <tr className="text-left">
                  <th className="py-2 px-3">Nombre</th>
                  <th className="px-3">Cédula</th>
                  <th className="px-3">Cargo</th>
                  <th className="px-3">Salario</th>
                  <th className="px-3">Estado</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((e) => (
                  <tr key={e.id} className="border-t border-slate-700">
                    <td className="py-2 px-3">{e.nombre} {e.apellido}</td>
                    <td className="px-3">{e.cedula}</td>
                    <td className="px-3">{e.cargo || "-"}</td>
                    <td className="px-3">{Number(e.salario_base || 0).toLocaleString("es-PY")} Gs</td>
                    <td className="px-3">{e.activo ? "Activo" : "Inactivo"}</td>
                  </tr>
                ))}
                {rows.length === 0 && (
                  <tr><td className="py-2 px-3 text-slate-400" colSpan={5}>Sin empleados</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
