// src/pages/admin/AdminPanel.jsx
import { useEffect, useMemo, useState } from "react";
import Layout from "../../components/Layout";
import api from "../../utils/api";
import { getUser, fetchProfile, clearSession } from "../../utils/auth";
import { canUseAdmin } from "../../utils/acl";
import { buildQuery } from "../../utils/query";

import AdminSidebar from "./AdminSidebar";
import AdminHeader from "./AdminHeader";
import AdminFilters from "./AdminFilters";
import AdminTable from "./AdminTable";
import AdminModal from "./AdminModal";
import AdminPagination from "./AdminPagination";
import AdminActions from "./AdminActions"; //  agregado

export default function AdminPanel() {
  const [endpoint, setEndpoint] = useState("empleados");
  const [data, setData] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);
  const [search, setSearch] = useState("");
  const [filters, setFilters] = useState({});
  const [selected, setSelected] = useState([]);
  const [modalData, setModalData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);
  const [user, setUser] = useState(null);

  // ====
  //  Validar permisos
  // ====
  useEffect(() => {
    const boot = async () => {
      try {
        let u = getUser();
        if (!u) u = await fetchProfile();
        setUser(u);
        if (!canUseAdmin(u)) {
          alert("No tenés permisos para acceder al panel administrativo.");
          clearSession();
          window.location.href = "/login";
        }
      } catch (e) {
        console.error(e);
        clearSession();
        window.location.href = "/login";
      }
    };
    boot();
  }, []);

  // ====
  //  Fetch listado
  // ====
  const query = useMemo(() => {
    const params = { page, page_size: pageSize, search, ...filters };
    return buildQuery(params);
  }, [page, pageSize, search, filters]);

  const loadData = async () => {
    setLoading(true);
    setErr(null);
    try {
      const res = await api.get(`/${endpoint}/${query}`);
      if (Array.isArray(res.data)) {
        setData(res.data);
        setCount(res.data.length);
      } else {
        setData(res.data.results || []);
        setCount(res.data.count ?? (res.data.results || []).length);
      }
    } catch (e) {
      console.error(e);
      setErr("No se pudo cargar la lista.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    setSelected([]);
  }, [endpoint, query]);

  const reload = () => loadData();

  // ====
  //  Acciones masivas básicas
  // ====
  const eliminarSeleccionados = async () => {
    if (!selected.length) return alert("No hay elementos seleccionados.");
    if (!window.confirm("¿Eliminar registros seleccionados?")) return;
    try {
      await Promise.all(selected.map((id) => api.delete(`/${endpoint}/${id}/`)));
      await loadData();
      setSelected([]);
    } catch (e) {
      console.error(e);
      alert("Error al eliminar.");
    }
  };

  const exportarExcel = () => {
    window.open(`http://127.0.0.1:8000/api/${endpoint}/${buildQuery(filters)}`, "_blank");
  };

  const nuevoRegistro = () => {
    const plant = data[0] ? Object.keys(data[0]) : ["nombre"];
    const obj = Object.fromEntries(plant.map((k) => [k, ""]));
    delete obj.id;
    setModalData(obj);
  };

  // ====
  //  Acciones masivas personalizadas (AdminActions)
  // ====
  const handleBulkAction = async (action) => {
    if (!selected.length) return alert("Seleccioná al menos un registro.");
    try {
      let endpointUrl = null;

      switch (endpoint) {
        case "nomina_cal/liquidaciones":
          if (action === "cerrar") endpointUrl = "cerrar";
          if (action === "enviar") endpointUrl = "enviar-recibo";
          if (action === "recalcular") endpointUrl = "calcular";
          break;
        case "empleados":
        case "usuarios/usuarios":
          if (action === "activar") endpointUrl = "activar";
          if (action === "desactivar") endpointUrl = "desactivar";
          break;
        default:
          alert("Acción no soportada para este módulo.");
          return;
      }

      if (!endpointUrl) return;

      await Promise.all(
        selected.map((id) => api.post(`/${endpoint}/${id}/${endpointUrl}/`))
      );

      alert("Acción ejecutada correctamente.");
      loadData();
      setSelected([]);
    } catch (err) {
      console.error(err);
      alert("Error al ejecutar acción masiva.");
    }
  };

  // ====
  //  UI
  // ====
  return (
    <Layout>
      <div className="flex h-screen bg-gray-50">
        <AdminSidebar current={endpoint} onChange={(e) => { setEndpoint(e); setPage(1); }} />

        <div className="flex-1 flex flex-col">
          <AdminHeader
            title={endpoint.toUpperCase()}
            onRefresh={reload}
            onSearch={setSearch}
            search={search}
          />

          <AdminFilters
            model={endpoint}
            values={filters}
            onChange={(vals) => { setFilters(vals); setPage(1); }}
            onClear={() => { setFilters({}); setPage(1); }}
          />

          {/* 🔧 Acciones disponibles */}
          <div className="flex flex-wrap gap-2 px-4 py-2 border-b bg-white items-center">
            <button
              onClick={nuevoRegistro}
              className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
            >
              ➕ Nuevo
            </button>
            <button
              onClick={eliminarSeleccionados}
              className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700"
            >
              🗑️ Eliminar
            </button>
            <button
              onClick={exportarExcel}
              className="bg-gray-600 text-white px-3 py-1 rounded hover:bg-gray-700"
            >
               Exportar
            </button>

            {/*  Nuevo bloque: acciones específicas según módulo */}
            <AdminActions
           model={endpoint}
           selected={selected}
      S     onAction={handleBulkAction}
           onExport={exportarExcel}
            />
          </div>

          <div className="flex-1 overflow-auto p-4">
            {loading ? (
              <p className="text-gray-500 text-center mt-10">Cargando…</p>
            ) : err ? (
              <p className="text-center text-red-600">{err}</p>
            ) : (
              <>
                <AdminTable
                  data={data}
                  model={endpoint}
                  selected={selected}
                  setSelected={setSelected}
                  onEdit={(row) => setModalData(row)}
                />
                <AdminPagination
                  page={page}
                  pageSize={pageSize}
                  count={count}
                  onPage={setPage}
                />
              </>
            )}
          </div>
        </div>
      </div>

      {modalData && (
        <AdminModal
          model={endpoint}
          data={modalData}
          onClose={() => setModalData(null)}
          onSaved={reload}
        />
      )}
    </Layout>
  );
}
