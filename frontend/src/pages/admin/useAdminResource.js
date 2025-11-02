// frontend/src/pages/admin/useAdminResource.js
import { useCallback, useEffect, useMemo, useState } from "react";
import api from "../../utils/api";

/**
 * Hook genérico que replica la mecánica del Django Admin:
 *  - lista con search, ordering y paginación server-side
 *  - create/update/delete
 *  - bulk delete
 */
export default function useAdminResource({ basePath, defaultOrdering = "-id" }) {
  const [rows, setRows] = useState([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50); // igual al DRF
  const [search, setSearch] = useState("");
  const [ordering, setOrdering] = useState(defaultOrdering);
  const [filters, setFilters] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const params = useMemo(() => {
    const p = { page, search, ordering };
    Object.entries(filters).forEach(([k, v]) => { if (v !== "" && v != null) p[k] = v; });
    return p;
  }, [page, search, ordering, filters]);

  const list = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const r = await api.get(basePath, { params });
      // DRF PageNumberPagination: results + count
      const data = r.data?.results ? r.data : { results: r.data, count: r.data?.length ?? 0 };
      setRows(data.results || []);
      setCount(data.count || 0);
    } catch (e) {
      setError("No se pudo cargar la lista");
    } finally {
      setLoading(false);
    }
  }, [basePath, params]);

  useEffect(() => { list(); }, [list]);

  const create = async (payload) => {
    const r = await api.post(basePath, payload);
    await list(); 
    return r.data;
  };
  const update = async (id, payload) => {
    const r = await api.put(`${basePath}${id}/`, payload);
    await list();
    return r.data;
  };
  const remove = async (id) => {
    await api.delete(`${basePath}${id}/`);
    await list();
  };
  const bulkDelete = async (ids=[]) => {
    // opción simple: varias llamadas DELETE (como actions del admin)
    await Promise.all(ids.map(id => api.delete(`${basePath}${id}/`).catch(()=>{})));
    await list();
  };

  return {
    rows, count, page, setPage, pageSize,
    search, setSearch, ordering, setOrdering,
    filters, setFilters, loading, error,
    create, update, remove, bulkDelete, reload: list
  };
}
