// frontend/src/pages/admin/UsuariosAdmin.jsx

//  UsuariosAdmin — Administración de cuentas de usuario

// Replica la app `auth.User` del Django Admin
// Funcionalidades:
//   • Listado, búsqueda y ordenamiento
//   • Alta, edición y eliminación
//   • Activación / desactivación masiva
//   • Asignación de roles (ADMIN / GERENTE_RRHH / ASISTENTE_RRHH / EMPLEADO)

// Endpoint backend: /api/usuarios/usuarios/


import { useMemo, useState } from "react";
import AdminLayout from "./AdminLayout";
import RequireRole from "./RequireRole";
import AdminFilters from "./AdminFilters";
import AdminActions from "./AdminActions";
import AdminTable from "./AdminTable";
import AdminModal from "./AdminModal";
import AdminPagination from "./AdminPagination";
import useAdminResource from "./useAdminResource";
import useHistorial from "./useHistorial";
import api from "../../utils/api";

export default function UsuariosAdmin() {
  return (
    <RequireRole allow={["ADMIN"]}>
      <UsuariosAdminPage />
    </RequireRole>
  );
}

function UsuariosAdminPage() {
  const resource = useAdminResource({
    basePath: "usuarios/usuarios/",
    defaultOrdering: "username",
  });

  const {
    rows,
    count,
    page,
    setPage,
    pageSize,
    search,
    setSearch,
    ordering,
    setOrdering,
    filters,
    setFilters,
    create,
    update,
    bulkDelete,
    reload,
    loading,
    error,
  } = resource;

  const { openHistorial, Historial } = useHistorial();

  const [open, setOpen] = useState(false);
  const [values, setValues] = useState({});
  const [selected, setSelected] = useState([]);
  const editing = !!values?.id;

  
  //  Columnas visibles en la tabla
  
  const columns = useMemo(
    () => [
      { field: "username", label: "Usuario", sortable: true },
      { field: "email", label: "Correo", sortable: true },
      {
        field: "rol",
        label: "Rol",
        sortable: true,
        render: (v) => v?.toUpperCase(),
      },
      {
        field: "is_active",
        label: "Activo",
        render: (v) => (v ? "" : ""),
      },
      {
        field: "last_login",
        label: "Último acceso",
        sortable: true,
        render: (v) => (v ? new Date(v).toLocaleString("es-PY") : "-"),
      },
      {
        field: "acciones",
        label: "Acciones",
        render: (_, r) => (
          <button
            onClick={() => openHistorial("Usuario", r.id)}
            className="text-xs text-blue-600 hover:underline"
          >
            🕘 Ver historial
          </button>
        ),
      },
    ],
    [openHistorial]
  );

  
  //  Campos del formulario modal
  
  const fields = [
    { name: "username", label: "Usuario" },
    { name: "email", label: "Correo electrónico" },
    {
      name: "rol",
      label: "Rol",
      type: "select",
      options: [
        { value: "ADMIN", label: "Administrador" },
        { value: "GERENTE_RRHH", label: "Gerente RRHH" },
        { value: "ASISTENTE_RRHH", label: "Asistente RRHH" },
        { value: "EMPLEADO", label: "Empleado" },
      ],
    },
    { name: "is_active", label: "Activo (true/false)" },
    { name: "password", label: "Contraseña (solo al crear)", type: "password" },
  ];

  
  // Filtros disponibles
  
  const filterItems = [
    {
      name: "rol",
      label: "Rol",
      type: "select",
      options: [
        { value: "", label: "Todos" },
        { value: "ADMIN", label: "Admin" },
        { value: "GERENTE_RRHH", label: "Gerente RRHH" },
        { value: "ASISTENTE_RRHH", label: "Asistente RRHH" },
        { value: "EMPLEADO", label: "Empleado" },
      ],
    },
  ];

  
  //  Acciones principales
  
  const onNew = () => {
    setValues({ is_active: true });
    setOpen(true);
  };

  const onSave = async () => {
    if (editing) await update(values.id, values);
    else await create(values);
    setOpen(false);
    setValues({});
  };

  const onDelete = async (ids) => {
    await bulkDelete(ids);
    setSelected([]);
  };

  const extraActions = [
    {
      label: "Activar usuarios",
      onClick: async () => {
        await Promise.all(
          selected.map((id) =>
            api.put(`usuarios/usuarios/${id}/`, { is_active: true })
          )
        );
        await reload();
        setSelected([]);
      },
    },
    {
      label: "Desactivar usuarios",
      onClick: async () => {
        await Promise.all(
          selected.map((id) =>
            api.put(`usuarios/usuarios/${id}/`, { is_active: false })
          )
        );
        await reload();
        setSelected([]);
      },
    },
  ];

  
  //  Render principal
  
  return (
    <AdminLayout
      title="Usuarios"
      breadcrumb={[{ label: "Admin" }, { label: "Usuarios" }]}
    >
      <div className="space-y-3">
        <AdminFilters
          items={filterItems}
          values={filters}
          onChange={setFilters}
          search={search}
          setSearch={setSearch}
          onSearch={() => reload()}
        />

        <AdminActions
          selected={selected}
          onNew={onNew}
          onDelete={onDelete}
          extra={extraActions}
        />

        <AdminTable
          columns={columns}
          rows={rows}
          ordering={ordering}
          setOrdering={setOrdering}
          selected={selected}
          setSelected={setSelected}
        />

        <AdminPagination
          page={page}
          setPage={setPage}
          count={count}
          pageSize={pageSize}
        />
      </div>

      <AdminModal
        open={open}
        title={editing ? `Editar usuario #${values.id}` : "Nuevo usuario"}
        fields={fields}
        values={values}
        setValues={setValues}
        onClose={() => setOpen(false)}
        onSave={onSave}
      />

      {loading && <div className="text-sm text-gray-500 mt-2">Cargando…</div>}
      {error && <div className="text-sm text-red-600 mt-2">{error}</div>}

      {/* Historial global */}
      {Historial}
    </AdminLayout>
  );
}
