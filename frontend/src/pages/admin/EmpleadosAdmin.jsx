// frontend/src/pages/admin/EmpleadosAdmin.jsx
export default function EmpleadosAdmin({ form, setForm, onGuardar, onCancelar, editando }) {
  return (
    <div className="mt-6 p-4 border rounded bg-gray-50">
      <h2 className="font-semibold mb-3">
        {editando ? "✏️ Editar Empleado" : "🆕 Crear Empleado"}
      </h2>
      {/* Campos ejemplo */}
      <div className="grid grid-cols-3 gap-3">
        <div>
          <label>Nombre</label>
          <input
            type="text"
            value={form.nombre || ""}
            onChange={(e) => setForm({ ...form, nombre: e.target.value })}
            className="border p-2 rounded w-full"
          />
        </div>
        <div>
          <label>Cédula</label>
          <input
            type="text"
            value={form.cedula || ""}
            onChange={(e) => setForm({ ...form, cedula: e.target.value })}
            className="border p-2 rounded w-full"
          />
        </div>
      </div>
      <div className="mt-4 flex gap-3">
        <button onClick={onGuardar} className="bg-emerald-600 text-white px-4 py-2 rounded">
          💾 Guardar
        </button>
        <button onClick={onCancelar} className="bg-gray-500 text-white px-4 py-2 rounded">
          Cancelar
        </button>
      </div>
    </div>
  );
}
