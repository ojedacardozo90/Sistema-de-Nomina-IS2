const UsuariosAdmin = ({ form, setForm, editando, onGuardar, onCancelar }) => {
  return (
    <div className="p-4 border rounded bg-white shadow-sm">
      <h2 className="font-bold text-lg mb-3">
        {editando ? "Editar Usuario" : "Nuevo Usuario"}
      </h2>

      <input
        type="text"
        placeholder="Nombre"
        value={form.username || ""}
        onChange={(e) => setForm({ ...form, username: e.target.value })}
        className="border px-3 py-2 rounded w-full mb-3"
      />

      <input
        type="email"
        placeholder="Email"
        value={form.email || ""}
        onChange={(e) => setForm({ ...form, email: e.target.value })}
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

export default UsuariosAdmin;
