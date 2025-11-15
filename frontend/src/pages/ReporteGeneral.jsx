import { useEffect, useState } from "react";
import api from "../utils/api"; 
import Layout from "../components/Layout";


// 📑 Nóminas (Sprint 3 - IS2 Nómina)


export default function Nominas() {
  const [nominas, setNominas] = useState([]);
  const [mensaje, setMensaje] = useState("");

  useEffect(() => {
    cargarNominas();
  }, []);

  const cargarNominas = async () => {
    try {
      const res = await api.get("nomina/"); //  corregido
      setNominas(res.data);
    } catch (err) {
      console.error(" Error al cargar nóminas", err);
    }
  };

  const calcularTodas = async () => {
    if (!window.confirm("¿Seguro que deseas recalcular todas las nóminas?")) return;
    try {
      await api.post("nomina/calcular_todas/"); //  corregido
      setMensaje(" Todas las nóminas recalculadas");
      cargarNominas();
    } catch (err) {
      console.error(" Error al calcular todas", err);
      setMensaje(" Error al calcular todas las nóminas");
    }
  };

  const descargarExcel = () => {
    window.open("http://127.0.0.1:8000/api/reporte/excel/", "_blank");
  };

  const descargarPDF = () => {
    window.open("http://127.0.0.1:8000/api/reporte/pdf/", "_blank");
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

        <table className="min-w-full border rounded shadow">
          <thead className="bg-gray-200">
            <tr>
              <th className="px-4 py-2 border">Empleado</th>
              <th className="px-4 py-2 border">Fecha</th>
              <th className="px-4 py-2 border">Total Neto</th>
              <th className="px-4 py-2 border">Detalle</th>
            </tr>
          </thead>
          <tbody>
            {nominas.map((n) => (
              <tr key={n.id} className="hover:bg-gray-100">
                <td className="border px-4 py-2">{n.empleado}</td>
                <td className="border px-4 py-2">{n.fecha}</td>
                <td className="border px-4 py-2 font-semibold text-green-700">{n.total} Gs</td>
                <td className="border px-4 py-2">
                  <details>
                    <summary className="cursor-pointer text-blue-600">Ver Detalle</summary>
                    <ul className="ml-4 list-disc">
                      {n.detalles?.map((d, idx) => (
                        <li key={idx}>
                          {d.concepto} : {d.monto} Gs
                        </li>
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
