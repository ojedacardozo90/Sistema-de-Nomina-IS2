import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../utils/api";

export default function LiquidacionForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [empleados, setEmpleados] = useState([]);
  const [formData, setFormData] = useState({
    empleado: "",
    mes: "",
    anio: new Date().getFullYear(),
    sueldo_base: "",
  });
  const [loading, setLoading] = useState(true);
  const [detalles, setDetalles] = useState([]);

  // ====
  // Cargar empleados + liquidación existente
  // ====
  useEffect(() => {
    const fetchData = async () => {
      try {
        const resEmpleados = await api.get("/empleados/");
        setEmpleados(resEmpleados.data);

        if (id) {
          const res = await api.get(`/nomina/liquidaciones/${id}/`);
          setFormData({
            empleado: res.data.empleado,
            mes: res.data.mes,
            anio: res.data.anio,
            sueldo_base: res.data.sueldo_base,
          });
          setDetalles(res.data.detalles);
        }
      } catch (error) {
        console.error("Error al cargar datos:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) return <p>Cargando formulario...</p>;

  // ====
  // Manejo de cambios
  // ====
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  // ====
  // Guardar liquidación
  // ====
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (id) {
        await api.put(`/nomina/liquidaciones/${id}/`, formData);
        alert("Liquidación actualizada");
      } else {
        await api.post("/nomina/liquidaciones/", formData);
        alert("Liquidación creada");
      }
      navigate("/liquidaciones");
    } catch (error) {
      console.error("Error al guardar:", error);
      alert("No se pudo guardar la liquidación");
    }
  };

  // ====
  // Calcular liquidación (backend)
  // ====
  const calcular = async () => {
    try {
      if (!id) {
        alert("Primero debes guardar la liquidación.");
        return;
      }
      const res = await api.post(`/nomina/liquidaciones/${id}/calcular/`);
      setDetalles(res.data.detalles);
      alert("Liquidación calculada con éxito");
    } catch (error) {
      console.error("Error al calcular liquidación:", error);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">
        {id ? "Editar Liquidación" : "Nueva Liquidación"}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block font-medium">Empleado</label>
          <select
            name="empleado"
            value={formData.empleado}
            onChange={handleChange}
            className="border rounded px-3 py-2 w-full"
            required
          >
            <option value="">Seleccione un empleado</option>
            {empleados.map((emp) => (
              <option key={emp.id} value={emp.id}>
                {emp.nombre} {emp.apellido} ({emp.cedula})
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block font-medium">Mes</label>
            <input
              type="number"
              name="mes"
              value={formData.mes}
              onChange={handleChange}
              min="1"
              max="12"
              className="border rounded px-3 py-2 w-full"
              required
            />
          </div>
          <div>
            <label className="block font-medium">Año</label>
            <input
              type="number"
              name="anio"
              value={formData.anio}
              onChange={handleChange}
              className="border rounded px-3 py-2 w-full"
              required
            />
          </div>
        </div>

        <div>
          <label className="block font-medium">Sueldo Base</label>
          <input
            type="number"
            step="0.01"
            name="sueldo_base"
            value={formData.sueldo_base}
            onChange={handleChange}
            className="border rounded px-3 py-2 w-full"
            required
          />
        </div>

        <div className="flex space-x-4">
          <button
            type="submit"
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
          >
            {id ? "Actualizar" : "Crear"}
          </button>

          {id && (
            <button
              type="button"
              onClick={calcular}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              Calcular Liquidación
            </button>
          )}
        </div>
      </form>

      {detalles.length > 0 && (
        <div className="mt-6">
          <h2 className="text-xl font-semibold mb-2">Detalles Calculados</h2>
          <table className="w-full border-collapse border text-sm">
            <thead className="bg-gray-200">
              <tr>
                <th className="border px-3 py-2">Concepto</th>
                <th className="border px-3 py-2">Monto</th>
              </tr>
            </thead>
            <tbody>
              {detalles.map((d) => (
                <tr key={d.id}>
                  <td className="border px-3 py-2">{d.concepto_descripcion}</td>
                  <td className="border px-3 py-2">{d.monto}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
