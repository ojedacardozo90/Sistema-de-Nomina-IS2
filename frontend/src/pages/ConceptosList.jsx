// ============================================================
// 💼 ConceptosList — Gestión de Conceptos (IS2 Nómina)
// ------------------------------------------------------------
// Muestra los conceptos de liquidación, con tabla y CRUD básico
// • Corrige error de .map no es función
// • Soporta respuesta con paginación ({ results: [...] })
// ============================================================

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../utils/api";

export default function ConceptosList() {
  const [conceptos, setConceptos] = useState([]); // array garantizado
  const [loading, setLoading] = useState(true);

  // ============================================================
  // 🔄 Cargar conceptos desde API
  // ============================================================
  useEffect(() => {
    const fetchConceptos = async () => {
      try {
        const response = await api.get("/nomina_cal/conceptos/");
        // Si la API devuelve { results: [...] }, usamos eso
        const data = Array.isArray(response.data)
          ? response.data
          : response.data.results || [];
        setConceptos(data);
      } catch (error) {
        console.error("❌ Error cargando conceptos:", error);
        setConceptos([]); // seguridad extra
      } finally {
        setLoading(false);
      }
    };
    fetchConceptos();
  }, []);

  // ============================================================
  // ⏳ Estado de carga
  // ============================================================
  if (loading) return <p className="p-4">Cargando conceptos...</p>;

  // ============================================================
  // 🎨 Render principal
  // ============================================================
  return (
    <div className="p-6">
      {/* 🔹 Título y botón superior */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-emerald-700">
          Gestión de Conceptos
        </h1>
        <Link
          to="/conceptos/nuevo"
          className="bg-emerald-600 text-white px-4 py-2 rounded-lg hover:bg-emerald-700"
        >
          + Nuevo Concepto
        </Link>
      </div>

      {/* 🔹 Tabla */}
      <table className="w-full border-collapse border shadow-sm rounded">
        <thead>
          <tr className="bg-gray-100 text-gray-700">
            <th className="border px-4 py-2">ID</th>
            <th className="border px-4 py-2">Descripción</th>
            <th className="border px-4 py-2">Tipo</th>
            <th className="border px-4 py-2">Afecta IPS</th>
            <th className="border px-4 py-2">Aguinaldo</th>
            <th className="border px-4 py-2">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {Array.isArray(conceptos) && conceptos.length > 0 ? (
            conceptos.map((c) => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="border px-4 py-2">{c.id}</td>
                <td className="border px-4 py-2">{c.descripcion}</td>
                <td className="border px-4 py-2">
                  {c.es_debito ? "Débito" : "Crédito"}
                </td>
                <td className="border px-4 py-2">
                  {c.afecta_ips ? "Sí" : "No"}
                </td>
                <td className="border px-4 py-2">
                  {c.para_aguinaldo ? "Sí" : "No"}
                </td>
                <td className="border px-4 py-2 text-center">
                  <Link
                    to={`/conceptos/${c.id}/editar`}
                    className="text-blue-600 hover:underline"
                  >
                    Editar
                  </Link>
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td
                colSpan="6"
                className="text-center p-4 text-gray-500 italic"
              >
                No hay conceptos registrados.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
