// frontend/src/pages/admin/EmpleadosAdmin.jsx
import { useMemo, useState } from "react";
import AdminLayout from "./AdminLayout";
import RequireRole from "./RequireRole";
import AdminFilters from "./AdminFilters";
import AdminActions from "./AdminActions";
import AdminTable from "./AdminTable";
import AdminModal from "./AdminModal";
import AdminPagination from "./AdminPagination";
import useAdminResource from "./useAdminResource";
// 🕘 Importar el hook de historial
import useHistorial from "./useHistorial";

export default function EmpleadosAdmin() {
  return (
    <RequireRole allow={["ADMIN", "GERENTE_RRHH", "ASISTENTE_RRHH"]}>
      <EmpleadosAdminPage />
    </RequireRole>
  );
}

function EmpleadosAdminPage() {
  const resource = useAdminResource({ basePath: "empleados/", defaultOrdering: "apellido" });
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
    remove,
    bulkDelete,
    reload,
    loading,
    error,
  } = resource;

  const [open, setOpen] = useState(false);
  const [values, setValues] = useState({});
  const [selected, setSelected] = useState([]);
  const editing = !!values?.id;

  // 🕘 Hook para historial
  const { openHistorial, Historial } = useHistorial();

  const columns = useMemo(
    () => [
      { field: "cedula", label: "Cédula", sortable: true },
      { field: "apellido", label: "Apellido", sortable: true },
      { field: "nombre", label: "Nombre", sortable: true },
      { field: "cargo", label: "Cargo", sortable: true },
      { field: "area", label: "Área", sortable: true },
      {
        field: "salario_base",
        label: "Salario",
        sortable: true,
        render: (v) => Number(v || 0).toLocaleString("es-PY"),
      },
      { field: "activo", label: "Activo", render: (v) => (v ? "Sí" : "No") },
      {
        field: "acciones",
        label: "Acciones",
        render: (_, r) => (
          <button
            onClick={() => openHistorial("Empleado", r.id)}
            className="text-xs text-blue-600 hover:underline"
          >
            🕘 Ver historial
          </button>
        ),
      },
    ],
    [openHistorial]
  );

  return (
    <AdminLayout
      title="Empleados"
      breadcrumb={[{ label: "Admin", to: "/admin/empleados" }, { label: "Empleados" }]}
    >
      <div className="space-y-3">
        <AdminFilters
          items={[
            { name: "area", label: "Área", type: "text" },
            { name: "tipo_contrato", label: "Contrato", type: "text" },
            {
              name: "activo",
              label: "Activo",
              type: "select",
              options: [
                { value: "true", label: "Sí" },
                { value: "false", label: "No" },
              ],
            },
          ]}
          values={filters}
          onChange={setFilters}
          search={search}
          setSearch={setSearch}
          onSearch={() => reload()}
        />

        <AdminActions selected={selected} onNew={() => setOpen(true)} onDelete={bulkDelete} />

        <AdminTable
          columns={columns}
          rows={rows}
          ordering={ordering}
          setOrdering={setOrdering}
          selected={selected}
          setSelected={setSelected}
        />

        <AdminPagination page={page} setPage={setPage} count={count} pageSize={pageSize} />
      </div>

      {/* Modal de creación/edición */}
      <AdminModal
        open={open}
        title={editing ? `Editar empleado #${values.id}` : "Nuevo empleado"}
        fields={[
          { name: "cedula", label: "Cédula" },
          { name: "nombre", label: "Nombre" },
          { name: "apellido", label: "Apellido" },
          { name: "cargo", label: "Cargo" },
          { name: "area", label: "Área" },
          { name: "salario_base", label: "Salario base" },
          { name: "email", label: "Correo electrónico", full: true },
        ]}
        values={values}
        setValues={setValues}
        onClose={() => setOpen(false)}
        onSave={async () => {
          if (editing) await update(values.id, values);
          else await create(values);
          setOpen(false);
        }}
      />

      {/* Historial global */}
      {Historial}
    </AdminLayout>
  );
}
