import { useEffect, useState } from "react";
import api from "../utils/api";
import Layout from "../components/Layout";

export default function Nominas() {
  const [nominas, setNominas] = useState([]);
  const [mensaje, setMensaje] = useState("");

  useEffect(() => {
    cargarNominas();
  }, []);

  const cargarNominas = async () => {
    try {
      const res = await api.get("nomina_cal/liquidaciones/");
      setNominas(res.data);
    } catch (err) {
      console.error(" Error al cargar nóminas", err);
    }
  };

  const calcularTodas = async () => {
    if (!window.confirm("¿Seguro que deseas recalcular todas las nóminas?")) return;
    try {
      await api.post("nomina_cal/liquidaciones/calcular_todas/");
      setMensaje(" Todas las nóminas recalculadas correctamente");
      cargarNominas();
    } catch (err) {
      console.error(" Error al calcular todas", err);
      setMensaje(" Error al calcular las nóminas");
    }
  };

  const descargarExcel = () => {
    window.open("http://127.0.0.1:8000/api/nomina_cal/reportes/excel/", "_blank");
  };

  const descargarPDF = () => {
    window.open("http://127.0.0.1:8000/api/nomina_cal/reportes/pdf/", "_blank");
  };

  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">📑 Gestión de Nóminas</h1>

        <div className="flex gap-4 mb-6">
          <button onClick={calcularTodas} className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-500">
             Calcular Todas
          </button>
          <button onClick={descargarExcel} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-500">
             Exportar Excel
          </button>
          <button onClick={descargarPDF} className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-500">
             Exportar PDF
          </button>
        </div>

        {mensaje && <div className="mb-4 p-3 bg-gray-200 rounded">{mensaje}</div>}

        <table className="min-w-full border rounded shadow text-sm">
          <thead className="bg-gray-200">
            <tr>
              <th className="px-4 py-2 border">Empleado</th>
              <th className="px-4 py-2 border">Mes/Año</th>
              <th className="px-4 py-2 border">Neto Cobrar</th>
              <th className="px-4 py-2 border">Detalle</th>
            </tr>
          </thead>
          <tbody>
            {nominas.map((n) => (
              <tr key={n.id} className="hover:bg-gray-50">
                <td className="border px-4 py-2">{n.empleado_nombre}</td>
                <td className="border px-4 py-2">{n.mes}/{n.anio}</td>
                <td className="border px-4 py-2 font-semibold text-green-700">
                  {parseFloat(n.neto_cobrar || 0).toLocaleString("es-PY")} Gs
                </td>
                <td className="border px-4 py-2">
                  <details>
                    <summary className="cursor-pointer text-blue-600">Ver Detalle</summary>
                    <ul className="ml-4 list-disc">
                      {n.detalles?.map((d, idx) => (
                        <li key={idx}>{d.concepto} : {parseFloat(d.monto).toLocaleString("es-PY")} Gs</li>
                      ))}
                    </ul>
                  </details>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}
