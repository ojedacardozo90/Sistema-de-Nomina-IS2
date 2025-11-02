import { useState } from "react";
import api from "../../utils/api";

// 🔍 Detectar tipo de input según el nombre o valor del campo
function guessType(key, value) {
  if (key.toLowerCase().includes("fecha")) return "date";
  if (key.startsWith("is_") || typeof value === "boolean") return "checkbox";
  if (key.includes("activo")) return "checkbox";
  if (key === "rol") return "select";
  return "text";
}

export default function AdminModal({ model, data, onClose, onSaved }) {
  const [form, setForm] = useState(data);
  const isNew = !data.id;

  // 🧠 Manejador de cambios
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  };

  // 💾 Guardar registro (POST o PUT)
  const handleSave = async () => {
    try {
      if (isNew) await api.post(`/${model}/`, form);
      else await api.put(`/${model}/${form.id}/`, form);
      onSaved();
      onClose();
    } catch (err) {
      console.error(err);
      alert("Error al guardar el registro.");
    }
  };

  // 🧩 Render dinámico del campo según tipo
  const renderInput = (key, value) => {
    const type = guessType(key, value);

    if (key === "rol") {
      return (
        <select
          name={key}
          value={form[key] || ""}
          onChange={handleChange}
          className="border rounded w-full p-2 text-sm"
        >
          <option value="">Seleccionar rol</option>
          <option value="admin">Admin</option>
          <option value="gerente_rrhh">Gerente RRHH</option>
          <option value="asistente_rrhh">Asistente RRHH</option>
          <option value="empleado">Empleado</option>
        </select>
      );
    }

    if (type === "checkbox") {
      return (
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            name={key}
            checked={form[key] || false}
            onChange={handleChange}
            className="h-4 w-4"
          />
          <span className="text-sm text-gray-700">Activo</span>
        </div>
      );
    }

    return (
      <input
        type={type}
        name={key}
        value={form[key] ?? ""}
        onChange={handleChange}
        className="border rounded w-full p-2 text-sm"
      />
    );
  };

  // 🎨 Render principal del modal
  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white p-6 rounded-lg shadow-lg w-full max-w-xl">
        <h2 className="text-lg font-bold mb-4">
          {isNew ? "Nuevo Registro" : "Editar Registro"}
        </h2>

        <div className="grid grid-cols-2 gap-3">
          {Object.keys(form)
            .filter(
              (key) =>
                !["id", "created_at", "updated_at", "password", "last_login"].includes(
                  key
                )
            )
            .map((key) => (
              <div key={key}>
                <label className="block text-sm text-gray-600 mb-1">
                  {key.toUpperCase()}
                </label>
                {renderInput(key, form[key])}
              </div>
            ))}
        </div>

        <div className="flex justify-end gap-2 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 hover:bg-gray-400 rounded"
          >
            Cancelar
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Guardar
          </button>
        </div>
      </div>
    </div>
  );
}


// frontend/src/pages/admin/AdminModal.jsx
export default function AdminModal({ open, title, fields=[], values={}, setValues, onClose, onSave }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white w-[720px] max-w-[95vw] rounded shadow-lg">
        <header className="px-4 py-3 border-b flex justify-between items-center">
          <h3 className="font-semibold">{title}</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">✕</button>
        </header>
        <div className="p-4 grid grid-cols-2 gap-3">
          {fields.map(f=>(
            <div key={f.name} className={f.full? "col-span-2": ""}>
              <label className="text-xs text-gray-500">{f.label}</label>
              {f.type === "select" ? (
                <select
                  className="border rounded p-2 w-full"
                  value={values[f.name] ?? ""}
                  onChange={(e)=>setValues(v=>({ ...v, [f.name]: e.target.value }))}>
                  <option value="">Seleccione…</option>
                  {f.options?.map(o=><option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
              ) : (
                <input
                  type={f.type || "text"}
                  className="border rounded p-2 w-full"
                  value={values[f.name] ?? ""}
                  onChange={(e)=>setValues(v=>({ ...v, [f.name]: e.target.value }))}
                />
              )}
              {f.help && <div className="text-[11px] text-gray-400 mt-0.5">{f.help}</div>}
            </div>
          ))}
        </div>
        <footer className="px-4 py-3 border-t flex gap-2 justify-end">
          <button className="px-3 py-2 rounded border" onClick={onClose}>Cancelar</button>
          <button className="px-3 py-2 rounded bg-blue-600 text-white" onClick={onSave}>Guardar</button>
        </footer>
      </div>
    </div>
  );
}
