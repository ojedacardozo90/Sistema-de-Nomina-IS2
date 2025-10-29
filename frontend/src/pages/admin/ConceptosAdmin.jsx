const ConceptosAdmin = ({ form, setForm, editando, onGuardar, onCancelar }) => {
  return (
    <div className="p-4 border rounded bg-white shadow-sm">
      <h2 className="font-bold text-lg mb-3">
        {editando ? "Editar Concepto" : "Nuevo Concepto"}
      </h2>

      {/* Campos */}
      <input
        type="text"
        placeholder="Nombre del concepto"
        value={form.nombre || ""}
        onChange={(e) => setForm({ ...form, nombre: e.target.value })}
        className="border px-3 py-2 rounded w-full mb-3"
      />

      <input
        type="number"
        placeholder="Monto"
        value={form.monto || ""}
        onChange={(e) => setForm({ ...form, monto: e.target.value })}
        className="border px-3 py-2 rounded w-full mb-3"
      />

      <button
        onClick={onGuardar}
        className="bg-emerald-600 text-white px-3 py-2 rounded"
      >
        💾 Guardar
      </button>

      {onCancelar && (
        <button
          onClick={onCancelar}
          className="ml-2 bg-gray-400 text-white px-3 py-2 rounded"
        >
          ❌ Cancelar
        </button>
      )}
    </div>
  );
};

export default ConceptosAdmin;
