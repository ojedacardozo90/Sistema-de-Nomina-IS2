// frontend/src/pages/admin/ConceptosAdmin.jsx
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

export default function ConceptosAdmin() {
  return (
    <RequireRole allow={["ADMIN", "GERENTE_RRHH"]}>
      <ConceptosAdminPage />
    </RequireRole>
  );
}

function ConceptosAdminPage() {
  const resource = useAdminResource({
    basePath: "nomina_cal/conceptos/",
    defaultOrdering: "descripcion",
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
    loading,
    error,
  } = resource;

  const { openHistorial, Historial } = useHistorial();

  const [open, setOpen] = useState(false);
  const [values, setValues] = useState({});
  const [selected, setSelected] = useState([]);
  const editing = !!values?.id;

  const columns = useMemo(
    () => [
      { field: "descripcion", label: "Descripción", sortable: true },
      {
        field: "es_debito",
        label: "Tipo",
        sortable: true,
        render: (v) => (v ? "Descuento" : "Ingreso"),
      },
      {
        field: "es_recurrente",
        label: "Recurrente",
        sortable: true,
        render: (v) => (v ? "Sí" : "No"),
      },
      {
        field: "afecta_ips",
        label: "Afecta IPS",
        sortable: true,
        render: (v) => (v ? "Sí" : "No"),
      },
      {
        field: "para_aguinaldo",
        label: "Para Aguinaldo",
        sortable: true,
        render: (v) => (v ? "Sí" : "No"),
      },
      {
        field: "acciones",
        label: "Acciones",
        render: (_, r) => (
          <button
            onClick={() => openHistorial("Concepto", r.id)}
            className="text-xs text-blue-600 hover:underline"
          >
            🕘 Ver historial
          </button>
        ),
      },
    ],
    [openHistorial]
  );

  const fields = [
    { name: "descripcion", label: "Descripción", full: true },
    { name: "es_debito", label: "¿Es débito? (true/false)" },
    { name: "es_recurrente", label: "Recurrente (true/false)" },
    { name: "afecta_ips", label: "Afecta IPS (true/false)" },
    { name: "para_aguinaldo", label: "Para aguinaldo (true/false)" },
  ];

  const onNew = () => {
    setValues({ es_debito: false, es_recurrente: true });
    setOpen(true);
  };

  const onSave = async () => {
    if (editing) await update(values.id, values);
    else await create(values);
    setOpen(false);
    setValues({});
  };

  return (
    <AdminLayout
      title="Conceptos"
      breadcrumb={[{ label: "Admin", to: "/admin/conceptos" }, { label: "Conceptos" }]}
    >
      <div className="space-y-3">
        <AdminFilters
          items={[]}
          values={filters}
          onChange={setFilters}
          search={search}
          setSearch={setSearch}
          onSearch={() => resource.reload()}
        />

        <AdminActions selected={selected} onNew={onNew} onDelete={bulkDelete} />

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
        title={editing ? `Editar concepto #${values.id}` : "Nuevo concepto"}
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
