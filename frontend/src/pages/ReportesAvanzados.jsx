// ============================================================
// 📈 Reportes Avanzados — filtros + export (NóminaPro)
// ============================================================
import { useEffect, useState } from "react";
import { reportesAvanzados, exportarAvanzadoExcel, exportarAvanzadoPDF } from "../utils/api";

export default function ReportesAvanzados() {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const [filtros, setFiltros] = useState({
    mes: "", anio: "", empleado_id: "", area: "", contrato: "",
    min_total: "", max_total: "", q: ""
  });

  const load = async () => {
    setLoading(true);
    try {
      const { data } = await reportesAvanzados(filtros);
      setItems(data.items || []);
      setTotal(data.total || 0);
    } catch (e) {
      console.error("Error Reportes Avanzados:", e);
      setItems([]); setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const onChange = (e) => setFiltros({ ...filtros, [e.target.name]: e.target.value });
  const buscar = () => load();

  const exportar = async (tipo) => {
    try {
      const call = tipo === "excel" ? exportarAvanzadoExcel : exportarAvanzadoPDF;
      const res = await call(filtros);
      const blob = new Blob([res.data], { type: tipo === "excel"
        ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        : "application/pdf" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = tipo === "excel" ? "reporte_avanzado.xlsx" : "reporte_avanzado.pdf";
      a.click(); URL.revokeObjectURL(url);
    } catch (e) {
      alert("No se pudo exportar.");
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">📈 Reportes Avanzados</h1>

      {/* Filtros */}
      <div className="bg-white p-4 rounded shadow grid grid-cols-2 md:grid-cols-4 gap-3">
        <input name="anio" placeholder="Año (YYYY)" value={filtros.anio} onChange={onChange} className="border p-2 rounded" />
        <input name="mes" placeholder="Mes (1-12)" value={filtros.mes} onChange={onChange} className="border p-2 rounded" />
        <input name="empleado_id" placeholder="Empleado ID" value={filtros.empleado_id} onChange={onChange} className="border p-2 rounded" />
        <input name="area" placeholder="Área" value={filtros.area} onChange={onChange} className="border p-2 rounded" />
        <input name="contrato" placeholder="Tipo contrato" value={filtros.contrato} onChange={onChange} className="border p-2 rounded" />
        <input name="min_total" placeholder="Min Neto" value={filtros.min_total} onChange={onChange} className="border p-2 rounded" />
        <input name="max_total" placeholder="Max Neto" value={filtros.max_total} onChange={onChange} className="border p-2 rounded" />
        <input name="q" placeholder="Buscar (nombre/cedula)" value={filtros.q} onChange={onChange} className="border p-2 rounded" />
        <div className="col-span-2 md:col-span-4 flex gap-2">
          <button onClick={buscar} className="bg-indigo-600 text-white px-3 py-2 rounded hover:bg-indigo-700">Aplicar filtros</button>
          <button onClick={() => exportar("pdf")} className="bg-red-600 text-white px-3 py-2 rounded hover:bg-red-700">Exportar PDF</button>
          <button onClick={() => exportar("excel")} className="bg-green-600 text-white px-3 py-2 rounded hover:bg-green-700">Exportar Excel</button>
        </div>
      </div>

      {/* Tabla */}
      <div className="bg-white p-4 rounded shadow">
        <div className="flex justify-between mb-2">
          <h2 className="font-semibold">Resultados</h2>
          <div className="text-sm text-gray-600">Total: {total.toLocaleString("es-PY")} Gs</div>
        </div>

        {loading ? (
          <div className="py-10 text-center text-gray-500">Cargando…</div>
        ) : items.length === 0 ? (
          <div className="py-10 text-center text-gray-500">Sin resultados.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm border">
              <thead className="bg-gray-50">
                <tr>
                  <th className="p-2 text-left">Empleado</th>
                  <th className="p-2 text-left">Cédula</th>
                  <th className="p-2 text-left">Área</th>
                  <th className="p-2 text-left">Contrato</th>
                  <th className="p-2 text-center">Periodo</th>
                  <th className="p-2 text-right">Neto (Gs)</th>
                </tr>
              </thead>
              <tbody>
                {items.map((r) => (
                  <tr key={r.id} className="border-b hover:bg-gray-50">
                    <td className="p-2">{r.empleado}</td>
                    <td className="p-2">{r.cedula}</td>
                    <td className="p-2">{r.area}</td>
                    <td className="p-2">{r.contrato}</td>
                    <td className="p-2 text-center">{r.mes}/{r.anio}</td>
                    <td className="p-2 text-right">{Number(r.neto).toLocaleString("es-PY")}</td>
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
