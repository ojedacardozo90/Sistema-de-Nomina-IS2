const LiquidacionesAdmin = ({ form, setForm, editando, onGuardar, onCancelar }) => {
  return (
    <div className="p-4 border rounded bg-white shadow-sm">
      <h2 className="font-bold text-lg mb-3">
        {editando ? "Editar Liquidación" : "Nueva Liquidación"}
      </h2>

      <input
        type="text"
        placeholder="Periodo"
        value={form.periodo || ""}
        onChange={(e) => setForm({ ...form, periodo: e.target.value })}
        className="border px-3 py-2 rounded w-full mb-3"
      />

      <input
        type="number"
        placeholder="Monto total"
        value={form.total || ""}
        onChange={(e) => setForm({ ...form, total: e.target.value })}
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

export default LiquidacionesAdmin;
