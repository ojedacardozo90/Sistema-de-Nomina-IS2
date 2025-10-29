import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../utils/api";

export default function ConceptoForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [concepto, setConcepto] = useState({
    descripcion: "",
    es_debito: false,
    es_recurrente: true,
    afecta_ips: true,
    para_aguinaldo: true,
  });

  // Cargar datos en modo edición
  useEffect(() => {
    if (id) {
      const fetchConcepto = async () => {
        try {
          setLoading(true);
          const response = await api.get(`/nomina_cal/conceptos/${id}/`);
          setConcepto(response.data);
        } catch (error) {
          console.error("Error cargando concepto:", error);
        } finally {
          setLoading(false);
        }
      };
      fetchConcepto();
    }
  }, [id]);

  // Manejo de formulario
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setConcepto({
      ...concepto,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      if (id) {
        await api.put(`/nomina_cal/conceptos/${id}/`, concepto);
      } else {
        await api.post("/nomina_cal/conceptos/", concepto);
      }
      navigate("/conceptos");
    } catch (error) {
      console.error("Error guardando concepto:", error.response?.data || error);
      alert("Hubo un error guardando el concepto");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <p className="p-4">Cargando...</p>;

  return (
    <div className="p-6 max-w-lg mx-auto bg-white shadow-md rounded-lg">
      <h1 className="text-2xl font-bold mb-6">
        {id ? "Editar Concepto" : "Nuevo Concepto"}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Descripción */}
        <div>
          <label className="block font-medium mb-1">Descripción</label>
          <input
            type="text"
            name="descripcion"
            value={concepto.descripcion}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded-md"
          />
        </div>

        {/* Tipo */}
        <div>
          <label className="block font-medium mb-1">Tipo</label>
          <select
            name="es_debito"
            value={concepto.es_debito ? "true" : "false"}
            onChange={(e) =>
              setConcepto({ ...concepto, es_debito: e.target.value === "true" })
            }
            className="w-full border px-3 py-2 rounded-md"
          >
            <option value="false">Crédito (Ingreso)</option>
            <option value="true">Débito (Descuento)</option>
          </select>
        </div>

        {/* Checkboxes */}
        <div className="space-y-2">
          <label className="flex items-center">
            <input
              type="checkbox"
              name="es_recurrente"
              checked={concepto.es_recurrente}
              onChange={handleChange}
              className="mr-2"
            />
            Es recurrente
          </label>

          <label className="flex items-center">
            <input
              type="checkbox"
              name="afecta_ips"
              checked={concepto.afecta_ips}
              onChange={handleChange}
              className="mr-2"
            />
            Afecta IPS
          </label>

          <label className="flex items-center">
            <input
              type="checkbox"
              name="para_aguinaldo"
              checked={concepto.para_aguinaldo}
              onChange={handleChange}
              className="mr-2"
            />
            Computa para Aguinaldo
          </label>
        </div>

        {/* Botones */}
        <div className="flex justify-between mt-6">
          <button
            type="button"
            onClick={() => navigate("/conceptos")}
            className="bg-gray-400 text-white px-4 py-2 rounded-md hover:bg-gray-500"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={loading}
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
          >
            {loading ? "Guardando..." : "Guardar"}
          </button>
        </div>
      </form>
    </div>
  );
}
