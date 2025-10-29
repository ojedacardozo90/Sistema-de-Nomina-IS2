import { useState } from "react";
import Layout from "../components/Layout";
import { importarEmpleados, importarLiquidaciones } from "../utils/api";

export default function ImportarDatos() {
  const [fileEmp, setFileEmp] = useState(null);
  const [fileLiq, setFileLiq] = useState(null);
  const [out, setOut] = useState(null);
  const [loading, setLoading] = useState(false);

  const subir = async (tipo) => {
    setLoading(true); setOut(null);
    try {
      const res = tipo === "emp"
        ? await importarEmpleados(fileEmp)
        : await importarLiquidaciones(fileLiq);
      setOut(res.data);
    } catch (e) {
      console.error(e);
      setOut({ error: e.response?.data?.error || "Error al importar" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="p-6 space-y-6">
        <h1 className="text-2xl font-bold">⬆️ Importar datos (CSV/Excel)</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white rounded shadow p-4 space-y-3">
            <h2 className="font-semibold">Empleados</h2>
            <p className="text-sm text-gray-500">Columnas: nombre, apellido, cedula, email, telefono, salario_base, activo</p>
            <input type="file" accept=".csv,.xlsx,.xls" onChange={e=>setFileEmp(e.target.files?.[0] || null)} />
            <button disabled={!fileEmp||loading} onClick={()=>subir("emp")}
              className="bg-indigo-600 text-white px-3 py-2 rounded hover:bg-indigo-700 disabled:opacity-50">
              {loading ? "Subiendo…" : "Importar Empleados"}
            </button>
          </div>

          <div className="bg-white rounded shadow p-4 space-y-3">
            <h2 className="font-semibold">Liquidaciones</h2>
            <p className="text-sm text-gray-500">Columnas: cedula, mes, anio, neto_cobrar, total_ingresos, total_descuentos, cerrada</p>
            <input type="file" accept=".csv,.xlsx,.xls" onChange={e=>setFileLiq(e.target.files?.[0] || null)} />
            <button disabled={!fileLiq||loading} onClick={()=>subir("liq")}
              className="bg-emerald-600 text-white px-3 py-2 rounded hover:bg-emerald-700 disabled:opacity-50">
              {loading ? "Subiendo…" : "Importar Liquidaciones"}
            </button>
          </div>
        </div>

        {out && (
          <pre className="bg-gray-900 text-green-300 p-4 rounded overflow-auto text-xs">
{JSON.stringify(out, null, 2)}
          </pre>
        )}
      </div>
    </Layout>
  );
}
