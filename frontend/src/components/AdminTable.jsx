
// Componente genérico AdminTable

// Replica las funciones principales del Django Admin
// para cualquier modelo del backend.


import { useEffect, useState } from "react";
import api from "../utils/api";

export default function AdminTable({ model, title }) {
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);

  // Cargar registros del modelo
  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await api.get(`${model}/?search=${search}`);
      const results = res.data.results || res.data;
      setData(results);
      if (results.length > 0) {
        setColumns(Object.keys(results[0]));
      }
    } catch (e) {
      console.error("Error al cargar datos:", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [search]);

  // Eliminar registro
  const eliminar = async (id) => {
    if (!window.confirm("¿Está seguro de eliminar este registro?")) return;
    await api.delete(`${model}/${id}/`);
    fetchData();
  };

  // Crear o actualizar registro
  const guardar = async (e) => {
    e.preventDefault();
    const method = editing ? api.put : api.post;
    const url = editing ? `${model}/${selected.id}/` : `${model}/`;
    await method(url, selected);
    setEditing(false);
    fetchData();
  };

  if (loading) return <p>Cargando {title}...</p>;

  return (
    <div className="bg-white p-4 shadow rounded-lg">
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-xl font-bold">{title}</h2>
        <button
          onClick={() => {
            setSelected({});
            setEditing(true);
          }}
          className="bg-blue-600 text-white px-3 py-1 rounded"
        >
          ➕ Agregar
        </button>
      </div>

      <input
        type="text"
        placeholder="Buscar..."
        className="border p-1 w-full mb-3"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <table className="w-full border text-sm">
        <thead>
          <tr className="bg-gray-100">
            {columns.map((c) => (
              <th key={c} className="border px-2 py-1 text-left capitalize">
                {c.replaceAll("_", " ")}
              </th>
            ))}
            <th className="border px-2 py-1">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.id} className="hover:bg-gray-50">
              {columns.map((c) => (
                <td key={c} className="border px-2 py-1">
                  {String(row[c])}
                </td>
              ))}
              <td className="border px-2 py-1 space-x-2">
                <button
                  onClick={() => {
                    setSelected(row);
                    setEditing(true);
                  }}
                  className="text-blue-600"
                >
                  ✏️
                </button>
                <button
                  onClick={() => eliminar(row.id)}
                  className="text-red-600"
                >
                  🗑️
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {editing && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center">
          <form
            onSubmit={guardar}
            className="bg-white p-6 rounded shadow w-[500px]"
          >
            <h3 className="text-lg font-semibold mb-3">
              {selected?.id ? "Editar registro" : "Nuevo registro"}
            </h3>
            {columns.map((c) =>
              c === "id" ? null : (
                <div key={c} className="mb-2">
                  <label className="text-sm capitalize">{c}</label>
                  <input
                    type="text"
                    className="border p-1 w-full"
                    value={selected[c] || ""}
                    onChange={(e) =>
                      setSelected({ ...selected, [c]: e.target.value })
                    }
                  />
                </div>
              )
            )}
            <div className="flex justify-end gap-2 mt-3">
              <button
                type="button"
                onClick={() => setEditing(false)}
                className="bg-gray-300 px-3 py-1 rounded"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="bg-green-600 text-white px-3 py-1 rounded"
              >
                Guardar
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
