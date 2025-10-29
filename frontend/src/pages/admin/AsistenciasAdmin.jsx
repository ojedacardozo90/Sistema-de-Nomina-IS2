// ============================================================
// 👥 UsuariosAdmin.jsx — Formulario de Usuarios
// Sistema de Nómina IS2 (FP-UNA / FAP)
// ------------------------------------------------------------
// - Crea y edita usuarios desde el panel React.
// - Oculta el campo contraseña al editar.
// ============================================================

import { useState, useEffect } from "react";

export default function UsuariosAdmin({ form, setForm, editando, onGuardar, onCancelar }) {
  const [roles] = useState([
    { value: "admin", label: "Administrador" },
    { value: "gerente_rrhh", label: "Gerente RRHH" },
    { value: "asistente_rrhh", label: "Asistente RRHH" },
    { value: "empleado", label: "Empleado" },
  ]);

  return (
    <div className="mt-6 p-4 border rounded bg-gray-50">
      <h2 className="font-semibold mb-3">
        {editando ? "✏️ Editar Usuario" : "🆕 Crear Usuario"}
      </h2>

      <div className="grid grid-cols-3 gap-3">
        <div>
          <label>Nombre</label>
          <input
            type="text"
            name="first_name"
            value={form.first_name || ""}
            onChange={(e) => setForm({ ...form, first_name: e.target.value })}
            className="border p-2 rounded w-full"
          />
        </div>
        <div>
          <label>Apellido</label>
          <input
            type="text"
            name="last_name"
            value={form.last_name || ""}
            onChange={(e) => setForm({ ...form, last_name: e.target.value })}
            className="border p-2 rounded w-full"
          />
        </div>
        <div>
          <label>Email</label>
          <input
            type="email"
            name="email"
            value={form.email || ""}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            className="border p-2 rounded w-full"
          />
        </div>
        <div>
          <label>Nombre de usuario</label>
          <input
            type="text"
            name="username"
            value={form.username || ""}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            className="border p-2 rounded w-full"
          />
        </div>

        {!editando && (
          <div>
            <label>Contraseña</label>
            <input
              type="password"
              name="password"
              value={form.password || ""}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="border p-2 rounded w-full"
            />
          </div>
        )}

        <div>
          <label>Rol</label>
          <select
            name="rol"
            value={form.rol || ""}
            onChange={(e) => setForm({ ...form, rol: e.target.value })}
            className="border p-2 rounded w-full"
          >
            <option value="">Seleccionar...</option>
            {roles.map((r) => (
              <option key={r.value} value={r.value}>
                {r.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="mt-4 flex gap-3">
        <button
          onClick={onGuardar}
          className="bg-emerald-600 text-white px-4 py-2 rounded"
        >
          💾 Guardar
        </button>
        <button
          onClick={onCancelar}
          className="bg-gray-500 text-white px-4 py-2 rounded"
        >
          Cancelar
        </button>
      </div>
    </div>
  );
}
