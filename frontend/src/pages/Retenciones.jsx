import { useEffect, useState } from "react";
import api from "../utils/api"; // 👈 corregido
import Layout from "../components/Layout";
// ============================================================
// 💰 Retenciones y Anticipos (Sprint 2 - IS2 Nómina)
// - Listar retenciones activas por empleado
// - Crear nuevas retenciones
// - Marcar retenciones como inactivas (soft delete)
// ============================================================

export default function Retenciones() {
  const [retenciones, setRetenciones] = useState([]);
  const [form, setForm] = useState({
    empleado: "",
    descripcion: "",
    monto: "",
    vigente: true,
  });
  const [empleados, setEmpleados] = useState([]);
  const [mensaje, setMensaje] = useState("");

  // 🔹 Cargar datos iniciales
  useEffect(() => {
    cargarRetenciones();
    cargarEmpleados();
  }, []);

  const cargarRetenciones = async () => {
    try {
      const res = await api.get("retenciones/"); // 👈 quitado /api/
      setRetenciones(res.data);
    } catch (err) {
      console.error("❌ Error al cargar retenciones", err);
    }
  };

  const cargarEmpleados = async () => {
    try {
      const res = await api.get("empleados/"); // 👈 quitado /api/
      setEmpleados(res.data);
    } catch (err) {
      console.error("❌ Error al cargar empleados", err);
    }
  };

  // 🔹 Guardar retención
  const guardarRetencion = async (e) => {
    e.preventDefault();
    try {
      await api.post("retenciones/", form); // 👈 quitado /api/
      setMensaje("✅ Retención registrada correctamente");
      setForm({ empleado: "", descripcion: "", monto: "", vigente: true });
      cargarRetenciones();
    } catch (err) {
      console.error("❌ Error al guardar retención", err);
      setMensaje("❌ Error al guardar retención");
    }
  };

  // 🔹 Desactivar retención (soft delete)
  const desactivarRetencion = async (id) => {
    if (!window.confirm("¿Seguro que deseas desactivar esta retención?")) return;
    try {
      await api.patch(`retenciones/${id}/`, { vigente: false }); // 👈 quitado /api/
      setMensaje("⚠️ Retención desactivada");
      cargarRetenciones();
    } catch (err) {
      console.error("❌ Error al desactivar retención", err);
      setMensaje("❌ Error al desactivar retención");
    }
  };

  return (
    <Layout>
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">💰 Gestión de Retenciones</h1>

        {/* Formulario */}
        <form
          onSubmit={guardarRetencion}
          className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-gray-100 p-4 rounded-lg shadow mb-6"
        >
          <select
            className="p-2 border rounded"
            value={form.empleado}
            onChange={(e) => setForm({ ...form, empleado: e.target.value })}
            required
          >
            <option value="">Seleccionar Empleado</option>
            {empleados.map((emp) => (
              <option key={emp.id} value={emp.id}>
                {emp.nombre} {emp.apellido}
              </option>
            ))}
          </select>
          <input
            type="text"
            placeholder="Descripción (ej: Préstamo, Anticipo, Embargo)"
            className="p-2 border rounded"
            value={form.descripcion}
            onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
            required
          />
          <input
            type="number"
            placeholder="Monto"
            className="p-2 border rounded"
            value={form.monto}
            onChange={(e) => setForm({ ...form, monto: e.target.value })}
            required
          />
          <button
            type="submit"
            className="col-span-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-500"
          >
            ➕ Registrar Retención
          </button>
        </form>

        {/* Mensajes */}
        {mensaje && (
          <div className="mb-4 p-3 bg-gray-200 text-gray-800 rounded">
            {mensaje}
          </div>
        )}

        {/* Tabla */}
        <table className="min-w-full border rounded-lg shadow">
          <thead className="bg-gray-200">
            <tr>
              <th className="px-4 py-2 border">Empleado</th>
              <th className="px-4 py-2 border">Descripción</th>
              <th className="px-4 py-2 border">Monto</th>
              <th className="px-4 py-2 border">Estado</th>
              <th className="px-4 py-2 border">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {retenciones.map((r) => (
              <tr key={r.id} className="hover:bg-gray-100">
                <td className="border px-4 py-2">
                  {r.empleado_nombre || r.empleado}
                </td>
                <td className="border px-4 py-2">{r.descripcion}</td>
                <td className="border px-4 py-2 text-red-700 font-semibold">
                  -{r.monto} Gs
                </td>
                <td className="border px-4 py-2">
                  {r.vigente ? "✅ Activa" : "❌ Inactiva"}
                </td>
                <td className="border px-4 py-2">
                  {r.vigente && (
                    <button
                      onClick={() => desactivarRetencion(r.id)}
                      className="bg-yellow-500 text-white px-2 py-1 rounded hover:bg-yellow-400"
                    >
                      ⚠️ Desactivar
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Layout>
  );
}
