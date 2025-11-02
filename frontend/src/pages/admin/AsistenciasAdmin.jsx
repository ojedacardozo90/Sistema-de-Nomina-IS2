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

// ============================================================
// 🕒 AsistenciasAdmin — Control de asistencia del personal
// ------------------------------------------------------------
// Replica el módulo de "Fichadas" y "Asistencia" del Django Admin
// Funcionalidades:
//   • Listado de asistencias
//   • Filtros por fecha, empleado y tipo (Entrada / Salida)
//   • Exportaciones PDF / Excel
// ------------------------------------------------------------
// Endpoints:
//   • GET /api/asistencia/asistencias/
//   • GET /api/asistencia/exportar-excel/
//   • GET /api/asistencia/exportar-pdf/
// ============================================================

import { useMemo, useState } from "react";
import AdminLayout from "./AdminLayout";
import RequireRole from "./RequireRole";
import AdminFilters from "./AdminFilters";
import AdminActions from "./AdminActions";
import AdminTable from "./AdminTable";
import AdminPagination from "./AdminPagination";
import useAdminResource from "./useAdminResource";
import useHistorial from "./useHistorial";
import { exportarAsistenciasExcel, exportarAsistenciasPDF, descargarArchivo } from "../../utils/api";

export default function AsistenciasAdmin() {
  return (
    <RequireRole allow={["ADMIN","GERENTE_RRHH","ASISTENTE_RRHH"]}>
      <AsistenciasAdminPage />
    </RequireRole>
  );
}

function AsistenciasAdminPage() {
  const resource = useAdminResource({ basePath: "asistencia/asistencias/", defaultOrdering: "-fecha" });
  const { rows, count, page, setPage, pageSize, search, setSearch,
          ordering, setOrdering, filters, setFilters,
          loading, reload } = resource;

  const [selected, setSelected] = useState([]);
  const { openHistorial, Historial } = useHistorial();

  const columns = useMemo(() => [
    { field: "empleado_nombre", label: "Empleado" },
    { field: "fecha", label: "Fecha", sortable: true },
    { field: "hora", label: "Hora", sortable: true },
    { field: "tipo", label: "Tipo", render: v => v === "E" ? "Entrada" : "Salida" },
    {
      field: "acciones",
      label: "Acciones",
      render: (_, r) => (
        <button
          onClick={() => openHistorial("Asistencia", r.id)}
          className="text-xs text-blue-600 hover:underline"
        >
          🕘 Ver historial
        </button>
      ),
    },
  ], [openHistorial]);

  const filterItems = [
    { name: "fecha", label: "Fecha", type: "date" },
    { name: "tipo", label: "Tipo", type: "select", options: [
      { value: "", label: "Todos" },
      { value: "E", label: "Entradas" },
      { value: "S", label: "Salidas" },
    ]},
  ];

  const extraActions = [
    {
      label: "Exportar Excel",
      onClick: async () => {
        const blob = await exportarAsistenciasExcel(filters.mes, filters.anio);
        descargarArchivo(blob, "asistencias.xlsx");
      },
    },
    {
      label: "Exportar PDF",
      onClick: async () => {
        const blob = await exportarAsistenciasPDF(filters.mes, filters.anio);
        descargarArchivo(blob, "asistencias.pdf");
      },
    },
  ];

  return (
    <AdminLayout title="Asistencias" breadcrumb={[{ label: "Admin" }, { label: "Asistencias" }]}>
      <div className="space-y-3">
        <AdminFilters
          items={filterItems}
          values={filters}
          onChange={setFilters}
          search={search}
          setSearch={setSearch}
          onSearch={() => reload()}
        />
        <AdminActions selected={selected} onNew={() => {}} onDelete={() => {}} extra={extraActions} />
        <AdminTable
          columns={columns}
          rows={rows}
          ordering={ordering}
          setOrdering={setOrdering}
          selected={selected}
          setSelected={setSelected}
        />
        <AdminPagination page={page} setPage={setPage} count={count} pageSize={pageSize} />
        {loading && <div className="text-sm text-gray-500">Cargando…</div>}
        {/* 🕘 Modal del historial */}
        {Historial}
      </div>
    </AdminLayout>
  );
}
