
//  Cálculo individual de nómina — Sistema de Nómina IS2 (FP-UNA / )


import { useState, useEffect } from "react";
import api from "../utils/api";
import Layout from "../components/Layout";

// Formato de guaraníes
const fmtGs = (n) =>
  typeof n === "number" ? n.toLocaleString("es-PY") + " Gs" : n || "-";

export default function CalculoNominaPage() {
  const [empleados, setEmpleados] = useState([]);
  const [empleadoId, setEmpleadoId] = useState("");
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);

  // Cargar lista de empleados
  useEffect(() => {
    api
      .get("empleados/")
      .then((res) => setEmpleados(res.data))
      .catch(() => alert("Error cargando empleados"));
  }, []);

  // Calcular nómina individual
  const calcular = async () => {
    if (!empleadoId) {
      alert("Seleccione un empleado antes de calcular.");
      return;
    }

    setLoading(true);
    try {
      const res = await api.post("nomina/calcular-nomina/", {
        empleado_id: empleadoId,
      });
      setResultado(res.data);
    } catch (err) {
      console.error("Error al calcular la nómina:", err);
      alert("Error al calcular la nómina. Verifique la API.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="p-6 space-y-4">
        <h1 className="text-2xl font-bold mb-4">Cálculo de Nómina</h1>

        {/* Selección de empleado */}
        <div className="flex items-center gap-3">
          <select
            className="p-2 border rounded w-64"
            value={empleadoId}
            onChange={(e) => setEmpleadoId(e.target.value)}
          >
            <option value="">Seleccione empleado</option>
            {empleados.map((e) => (
              <option key={e.id} value={e.id}>
                {e.nombre}
              </option>
            ))}
          </select>

          <button
            onClick={calcular}
            disabled={loading}
            className="bg-[#1ABC9C] text-white px-4 py-2 rounded hover:bg-[#16A085]"
          >
            {loading ? "Calculando..." : "Calcular"}
          </button>
        </div>

        {/* Resultado general */}
        {resultado && (
          <div className="mt-6 bg-white p-4 rounded shadow">
            <h2 className="text-lg font-bold mb-2">Resultado</h2>
            <p>
              <b>Empleado:</b> {resultado.empleado}
            </p>
            <p>
              <b>Total Neto:</b> {fmtGs(resultado.total)}
            </p>
          </div>
        )}

        {/* Desglose detallado */}
        {resultado && (
          <div className="mt-6 bg-white p-4 rounded shadow">
            <h2 className="text-lg font-bold mb-2">
              Desglose de Liquidación
            </h2>
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="text-left text-gray-600 border-b">
                  <th className="py-2">Concepto</th>
                  <th className="py-2">Monto</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Sueldo Base</td>
                  <td>{fmtGs(resultado.base)}</td>
                </tr>
                <tr>
                  <td>Bonificación por hijos</td>
                  <td>{fmtGs(resultado.bonificacion_hijos)}</td>
                </tr>
                <tr>
                  <td>IPS (9%)</td>
                  <td>-{fmtGs(resultado.ips)}</td>
                </tr>

                {Array.isArray(resultado.descuentos) &&
                  resultado.descuentos.map((d) => (
                    <tr key={d.id}>
                      <td>{d.nombre}</td>
                      <td>-{fmtGs(d.monto)}</td>
                    </tr>
                  ))}

                <tr className="border-t font-semibold">
                  <td>Neto a cobrar</td>
                  <td>{fmtGs(resultado.neto)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
