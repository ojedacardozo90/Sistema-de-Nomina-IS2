// ============================================================
// 💵 Cálculo Masivo de Nóminas — Sistema de Nómina IS2 (FP-UNA / FAP)
// ============================================================

import { useState } from "react";
import { calcularTodas } from "../utils/api";
import Layout from "../components/Layout";

export default function CalcularTodasNominas() {
  const [resultado, setResultado] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCalcularTodas = async () => {
    setLoading(true);
    setResultado(null);

    try {
      const res = await calcularTodas();
      setResultado(res.data || { mensaje: "Cálculo masivo completado" });
    } catch (error) {
      console.error("Error al calcular todas las nóminas:", error);
      alert("Error al calcular todas las nóminas. Verifique el backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="p-6 space-y-4">
        <h1 className="text-2xl font-bold">Cálculo Masivo de Nóminas</h1>

        <button
          onClick={handleCalcularTodas}
          disabled={loading}
          className="bg-[#1ABC9C] text-white px-4 py-2 rounded hover:bg-[#16A085]"
        >
          {loading ? "Calculando todas..." : "Calcular Todas"}
        </button>

        {resultado && (
          <div className="mt-6 bg-white p-4 rounded shadow">
            <h2 className="text-lg font-bold mb-2">Resultado</h2>
            <p>{resultado.mensaje || "Cálculo realizado correctamente."}</p>
            {resultado.total && <p><b>Total registros:</b> {resultado.total}</p>}
          </div>
        )}
      </div>
    </Layout>
  );
}
