// frontend/src/pages/admin/LiquidacionesAdmin.jsx
import { useMemo, useState } from "react";
import AdminLayout from "./AdminLayout";
import RequireRole from "./RequireRole";
import AdminFilters from "./AdminFilters";
import AdminActions from "./AdminActions";
import AdminTable from "./AdminTable";
import AdminModal from "./AdminModal";
import AdminPagination from "./AdminPagination";
import useAdminResource from "./useAdminResource";
import api, { enviarRecibo, calcularLiquidacion, cerrarLiquidacion } from "../../utils/api";
import useHistorial from "./useHistorial";

export default function LiquidacionesAdmin() {
  return (
    <RequireRole allow={["ADMIN", "GERENTE_RRHH", "ASISTENTE_RRHH"]}>
      <LiquidacionesAdminPage />
    </RequireRole>
  );
}

function LiquidacionesAdminPage() {
  const resource = useAdminResource({
    basePath: "nomina_cal/liquidaciones/",
    defaultOrdering: "-anio,-mes",
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
  } = resource;

  const [open, setOpen] = useState(false);
  const [values, setValues] = useState({});
  const [selected, setSelected] = useState([]);
  const editing = !!values?.id;

  // 🕘 Hook de historial
  const { openHistorial, Historial } = useHistorial();

  const columns = useMemo(
    () => [
      {
        field: "empleado",
        label: "Empleado",
        render: (v, r) => r.empleado?.nombre || r.empleado_nombre || v,
      },
      { field: "mes", label: "Mes", sortable: true },
      { field: "anio", label: "Año", sortable: true },
      {
        field: "total_ingresos",
        label: "Ingresos",
        sortable: true,
        render: (v) => Number(v || 0).toLocaleString("es-PY"),
      },
      {
        field: "total_descuentos",
        label: "Descuentos",
        sortable: true,
        render: (v) => Number(v || 0).toLocaleString("es-PY"),
      },
      {
        field: "neto_cobrar",
        label: "Neto",
        sortable: true,
        render: (v) => Number(v || 0).toLocaleString("es-PY"),
      },
      {
        field: "cerrada",
        label: "Estado",
        render: (v) => (v ? "CERRADA" : "ABIERTA"),
      },
      {
        field: "acciones",
        label: "Acciones",
        render: (_, r) => (
          <button
            onClick={() => openHistorial("Liquidacion", r.id)}
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
    {
      name: "empleado",
      label: "Empleado (id)",
      help: "ID del empleado (o usar formulario dedicado)",
    },
    { name: "mes", label: "Mes", type: "number" },
    { name: "anio", label: "Año", type: "number" },
  ];

  const filterItems = [
    { name: "mes", label: "Mes", type: "number" },
    { name: "anio", label: "Año", type: "number" },
    {
      name: "cerrada",
      label: "Estado",
      type: "select",
      options: [
        { value: "false", label: "Abiertas" },
        { value: "true", label: "Cerradas" },
      ],
    },
  ];

  const onNew = () => {
    setValues({});
    setOpen(true);
  };

  const onSave = async () => {
    if (editing) await update(values.id, values);
    else await create(values);
    setOpen(false);
    setValues({});
  };

  const extraActions = [
    {
      label: "Calcular seleccionadas",
      onClick: async () => {
        await Promise.all(selected.map((id) => calcularLiquidacion(id).catch(() => {})));
        await resource.reload();
        setSelected([]);
      },
    },
    {
      label: "Cerrar seleccionadas",
      onClick: async () => {
        await Promise.all(selected.map((id) => cerrarLiquidacion(id).catch(() => {})));
        await resource.reload();
        setSelected([]);
      },
    },
    {
      label: "Enviar recibos",
      onClick: async () => {
        await Promise.all(selected.map((id) => enviarRecibo(id).catch(() => {})));
        await resource.reload();
        setSelected([]);
      },
    },
    {
      label: "Exportar PDF (todas)",
      onClick: async () => {
        window.open("http://127.0.0.1:8000/api/nomina_cal/reportes/pdf/", "_blank");
      },
    },
  ];

  return (
    <AdminLayout
      title="Liquidaciones"
      breadcrumb={[
        { label: "Admin", to: "/admin/liquidaciones" },
        { label: "Liquidaciones" },
      ]}
    >
      <div className="space-y-3">
        <AdminFilters
          items={filterItems}
          values={filters}
          onChange={setFilters}
          search={search}
          setSearch={setSearch}
          onSearch={() => resource.reload()}
        />

        <AdminActions
          selected={selected}
          onNew={onNew}
          onDelete={bulkDelete}
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
        title={editing ? `Editar liquidación #${values.id}` : "Nueva liquidación"}
        fields={fields}
        values={values}
        setValues={setValues}
        onClose={() => setOpen(false)}
        onSave={onSave}
      />

      {loading && <div className="text-sm text-gray-500 mt-2">Cargando…</div>}

      {/* Historial global */}
      {Historial}
    </AdminLayout>
  );
}
