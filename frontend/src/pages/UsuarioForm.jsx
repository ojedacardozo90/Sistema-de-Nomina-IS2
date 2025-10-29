// ============================================================
// 🧾 UsuarioForm.jsx — Formulario para crear o editar usuario
// Sistema NóminaPro (IS2 - FPUNA)
// ------------------------------------------------------------
// Compatible con backend: /api/usuarios/usuarios/
// Incluye:
//   - Creación y edición de usuario
//   - Roles (ADMIN, GERENTE, ASISTENTE, EMPLEADO)
//   - Activar/desactivar usuario
//   - Validación de contraseña y manejo de errores
// ============================================================

import { useState } from "react";
import api from "../utils/api";

export default function UsuarioForm({ usuario, onClose }) {
  const [form, setForm] = useState(
    usuario || {
      username: "",
      first_name: "",
      last_name: "",
      email: "",
      rol: "EMPLEADO",
      password: "",
      is_active: true,
    }
  );

  const [loading, setLoading] = useState(false);

  // ============================================================
  // 🔹 Manejo de cambios en inputs
  // ============================================================
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm({
      ...form,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  // ============================================================
  // 🧩 Enviar formulario (crear o actualizar)
  // ============================================================
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (usuario) {
        await api.put(`/usuarios/usuarios/${usuario.id}/`, form);
        alert("✅ Usuario actualizado correctamente");
      } else {
        await api.post("/usuarios/usuarios/", form);
        alert("✅ Usuario creado correctamente");
      }
      onClose();
    } catch (err) {
      console.error("Error al guardar usuario:", err);
      if (err.response?.data) {
        alert("❌ Error: " + JSON.stringify(err.response.data));
      } else {
        alert("❌ Error desconocido al guardar el usuario");
      }
    } finally {
      setLoading(false);
    }
  };

  // ============================================================
  // 🎨 Render del formulario
  // ============================================================
  return (
    <div className="bg-gray-50 p-5 rounded border mb-4 shadow-sm">
      <h2 className="text-lg font-semibold mb-3">
        {usuario ? "✏️ Editar Usuario" : "🆕 Nuevo Usuario"}
      </h2>

      <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-3">
        {/* Usuario */}
        <div className="col-span-1">
          <label className="text-sm text-gray-600">Usuario</label>
          <input
            name="username"
            placeholder="Usuario"
            value={form.username}
            onChange={handleChange}
            className="border p-2 rounded w-full"
            required
          />
        </div>

        {/* Email */}
        <div className="col-span-1">
          <label className="text-sm text-gray-600">Correo electrónico</label>
          <input
            name="email"
            type="email"
            placeholder="correo@ejemplo.com"
            value={form.email}
            onChange={handleChange}
            className="border p-2 rounded w-full"
            required
          />
        </div>

        {/* Nombre */}
        <div className="col-span-1">
          <label className="text-sm text-gray-600">Nombre</label>
          <input
            name="first_name"
            placeholder="Nombre"
            value={form.first_name}
            onChange={handleChange}
            className="border p-2 rounded w-full"
          />
        </div>

        {/* Apellido */}
        <div className="col-span-1">
          <label className="text-sm text-gray-600">Apellido</label>
          <input
            name="last_name"
            placeholder="Apellido"
            value={form.last_name}
            onChange={handleChange}
            className="border p-2 rounded w-full"
          />
        </div>

        {/* Rol */}
        <div className="col-span-1">
          <label className="text-sm text-gray-600">Rol del usuario</label>
          <select
            name="rol"
            value={form.rol}
            onChange={handleChange}
            className="border p-2 rounded w-full"
          >
            <option value="ADMIN">Administrador</option>
            <option value="GERENTE">Gerente RRHH</option>
            <option value="ASISTENTE">Asistente RRHH</option>
            <option value="EMPLEADO">Empleado</option>
          </select>
        </div>

        {/* Contraseña */}
        <div className="col-span-1">
          <label className="text-sm text-gray-600">
            {usuario ? "Nueva Contraseña (opcional)" : "Contraseña"}
          </label>
          <input
            name="password"
            type="password"
            placeholder="********"
            value={form.password}
            onChange={handleChange}
            className="border p-2 rounded w-full"
            required={!usuario}
          />
        </div>

        {/* Estado activo */}
        <div className="col-span-2 flex items-center mt-2">
          <input
            type="checkbox"
            name="is_active"
            checked={form.is_active}
            onChange={handleChange}
            className="mr-2"
          />
          <span className="text-sm text-gray-700">Usuario activo</span>
        </div>

        {/* Botones */}
        <div className="col-span-2 flex gap-3 mt-4 justify-end">
          <button
            type="submit"
            disabled={loading}
            className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded disabled:opacity-60"
          >
            {loading ? "Guardando..." : "💾 Guardar"}
          </button>
          <button
            type="button"
            onClick={onClose}
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}
