// ============================================================
// 🧭 DashboardGestion.jsx — Panel administrativo tipo Django
// ------------------------------------------------------------
// Permite gestionar todos los modelos vía API REST interna.
// Soporta:
//   • Listado dinámico de modelos
//   • CRUD completo (crear, editar, eliminar)
//   • Búsqueda y refresco
//   • Interfaz similar al admin Django
// ============================================================

import { useEffect, useState } from "react";
import api from "../utils/api";
import { Database, PlusCircle, Trash2, RefreshCcw } from "lucide-react";
import UsuariosAdmin from "./admin/UsuariosAdmin";
import EmpleadosAdmin from "./admin/EmpleadosAdmin";
import ConceptosAdmin from "./admin/ConceptosAdmin";
import LiquidacionesAdmin from "./admin/LiquidacionesAdmin";
import AsistenciasAdmin from "./admin/AsistenciasAdmin";
import toast from "react-hot-toast";
import HeaderDashboard from "../components/HeaderDashboard";

export default function DashboardGestion() {
  // -------------------------------
  // 🔹 Estado principal
  // -------------------------------
  toast.success("Registro creado correctamente");
  toast.error("Error al eliminar");

  const [modelos, setModelos] = useState([]);
  const [selected, setSelected] = useState(null);
  const [data, setData] = useState([]);
  const [columns, setColumns] = useState([]);
  const [form, setForm] = useState({});
  const [editando, setEditando] = useState(false);
  const [busqueda, setBusqueda] = useState("");
  const [loading, setLoading] = useState(false);
  const [pagina, setPagina] = useState(1);

  // -------------------------------
  // 📦 Modelos administrables
  // -------------------------------
  useEffect(() => {
    setModelos([
      { name: "Usuarios", endpoint: "usuarios" },
      { name: "Empleados", endpoint: "empleados" },
      { name: "Conceptos", endpoint: "conceptos" },
      { name: "Liquidaciones", endpoint: "liquidaciones" },
      { name: "Asistencias", endpoint: "asistencias" },
    ]);
  }, []);

  // -------------------------------
  // 🔄 Cargar datos del modelo seleccionado
  // -------------------------------
  const cargarDatos = async (endpoint) => {
    try {
      setLoading(true);
      const res = await api.get(`/admin-panel/${endpoint}/`);
      setData(res.data);
      if (res.data.length > 0) {
        setColumns(Object.keys(res.data[0]));
      } else {
        setColumns([]);
      }
    } catch (error) {
      console.error("Error al cargar datos:", error);
      setData([]);
      setColumns([]);
    } finally {
      setLoading(false);
    }
  };

  // -------------------------------
  // 🧩 Crear / Editar registro
  // -------------------------------
  const guardar = async () => {
    try {
      if (editando) {
        await api.put(`/admin-panel/${selected.endpoint}/${form.id}/`, form);
        alert("✅ Registro actualizado correctamente");
      } else {
        await api.post(`/admin-panel/${selected.endpoint}/`, form);
        alert("✅ Registro creado correctamente");
      }
      setForm({});
      setEditando(false);
      await cargarDatos(selected.endpoint);
    } catch (error) {
      console.error("Error guardando registro:", error);
      alert("❌ Error al guardar: " + JSON.stringify(error.response?.data || {}));
    }
  };

  // -------------------------------
  // ❌ Eliminar registro
  // -------------------------------
  const eliminar = async (id) => {
    if (!window.confirm("¿Seguro que deseas eliminar este registro?")) return;
    try {
      await api.delete(`/admin-panel/${selected.endpoint}/${id}/`);
      await cargarDatos(selected.endpoint);
      alert("🗑️ Registro eliminado correctamente");
    } catch (error) {
      alert("❌ Error al eliminar");
    }
  };

  // -------------------------------
  // 🔍 Filtrar por texto y paginación
  // -------------------------------
  const porPagina = 25;
  const arrayData = Array.isArray(data) ? data : [];

  const resultados = arrayData.filter((item) =>
    Object.values(item).some((val) =>
      String(val).toLowerCase().includes(busqueda.toLowerCase())
    )
  );

  const paginados = resultados.slice(
    (pagina - 1) * porPagina,
    pagina * porPagina
  );

  // -------------------------------
  // 🎨 Render
  // -------------------------------
  return (
    <div className="p-6">
      <HeaderDashboard titulo="Panel de Gestión Administrativa" />

      {/* Contenido principal */}
      <section className="mt-4">
        <h1 className="text-2xl font-bold flex items-center gap-2 mb-4">
          <Database className="text-emerald-600" /> Panel Administrativo (Replica Django)
        </h1>

        {/* Selector de modelos */}
        <div className="flex gap-3 mb-5">
          {modelos.map((m) => (
            <button
              key={m.endpoint}
              onClick={() => {
                setSelected(m);
                cargarDatos(m.endpoint);
              }}
              className={`px-3 py-2 rounded text-sm font-semibold border ${
                selected?.endpoint === m.endpoint
                  ? "bg-emerald-600 text-white"
                  : "bg-gray-100 hover:bg-gray-200"
              }`}
            >
              {m.name}
            </button>
          ))}
        </div>

        {/* Buscador y acciones */}
        {selected && (
          <div className="flex justify-between items-center mb-3">
            <input
              type="text"
              placeholder="Buscar..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="border px-3 py-2 rounded w-1/3"
            />
            <div className="flex gap-2">
              <button
                onClick={() => {
                  setForm({});
                  setEditando(false);
                }}
                className="flex items-center gap-2 bg-emerald-600 text-white px-3 py-2 rounded"
              >
                <PlusCircle size={16} /> Nuevo
              </button>
              <button
                onClick={() => selected && cargarDatos(selected.endpoint)}
                className="flex items-center gap-2 bg-gray-500 text-white px-3 py-2 rounded"
              >
                <RefreshCcw size={16} /> Refrescar
              </button>
            </div>
          </div>
        )}

        {/* Paginación */}
        <div className="flex justify-center items-center gap-3 mt-4">
          <button onClick={() => setPagina((p) => Math.max(p - 1, 1))} className="px-3 py-1 border rounded">
            ⬅️
          </button>
          <span>Página {pagina}</span>
          <button onClick={() => setPagina((p) => p + 1)} className="px-3 py-1 border rounded">
            ➡️
          </button>
        </div>

        {/* Tabla */}
        {loading ? (
          <p className="text-gray-600">Cargando datos...</p>
        ) : selected ? (
          <>
            <table className="w-full border text-sm bg-white rounded shadow">
              <thead className="bg-gray-100">
                <tr>
                  {columns.map((c) => (
                    <th key={c} className="border p-2 text-left">
                      {c}
                    </th>
                  ))}
                  <th className="border p-2 text-center">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {resultados.length > 0 ? (
                  resultados.map((item) => (
                    <tr key={item.id} className="hover:bg-gray-50">
                      {columns.map((c) => (
                        <td key={c} className="border p-2">
                          {String(item[c])}
                        </td>
                      ))}
                      <td className="border p-2 text-center">
                        <button
                          onClick={() => {
                            setForm(item);
                            setEditando(true);
                          }}
                          className="text-blue-600 hover:text-blue-800 mx-1"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => eliminar(item.id)}
                          className="text-red-600 hover:text-red-800 mx-1"
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={columns.length + 1} className="text-center p-4">
                      Sin resultados.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>

            {/* ============================ */}
            {/* 🔹 FORMULARIO DINÁMICO NUEVO */}
            {/* ============================ */}
            <div className="mt-6">
              {selected?.endpoint === "usuarios" && (
                <UsuariosAdmin
                  form={form}
                  setForm={setForm}
                  editando={editando}
                  onGuardar={guardar}
                  onCancelar={() => {
                    setForm({});
                    setEditando(false);
                  }}
                />
              )}

              {selected?.endpoint === "empleados" && (
                <EmpleadosAdmin
                  form={form}
                  setForm={setForm}
                  editando={editando}
                  onGuardar={guardar}
                  onCancelar={() => {
                    setForm({});
                    setEditando(false);
                  }}
                />
              )}

              {selected?.endpoint === "conceptos" && (
                <ConceptosAdmin
                  form={form}
                  setForm={setForm}
                  editando={editando}
                  onGuardar={guardar}
                />
              )}

              {selected?.endpoint === "liquidaciones" && (
                <LiquidacionesAdmin
                  form={form}
                  setForm={setForm}
                  editando={editando}
                  onGuardar={guardar}
                />
              )}

              {selected?.endpoint === "asistencias" && (
                <AsistenciasAdmin
                  form={form}
                  setForm={setForm}
                  editando={editando}
                  onGuardar={guardar}
                />
              )}
            </div>
          </>
        ) : (
          <p>Seleccioná un modelo para administrar.</p>
        )}
      </section>
    </div>
  );
}
