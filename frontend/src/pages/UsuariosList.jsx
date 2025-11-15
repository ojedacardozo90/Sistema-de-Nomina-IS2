
//  UsuariosList.jsx — Gestión completa de usuarios
// Sistema de NóminaPro (IS2 - )

// • Lista, crea, edita y elimina usuarios
// • Con roles, estado, búsqueda y control de acceso


import { useEffect, useState } from "react";
import api from "../utils/api";
import { Pencil, Trash2, PlusCircle } from "lucide-react";
import Layout from "../components/Layout";
import { Link } from "react-router-dom";
import UsuarioForm from "./UsuarioForm";


//  Componente principal

export default function UsuariosList() {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState("");
  const [editing, setEditing] = useState(null);
  const [showForm, setShowForm] = useState(false);

  
  // # Cargar usuarios desde backend
  
  const fetchUsuarios = async () => {
    setLoading(true);
    try {
      const res = await api.get("/usuarios/usuarios/");
      setUsuarios(res.data);
      setError(null);
    } catch (err) {
      console.error("Error cargando usuarios:", err);
      setError("No se pudieron cargar los usuarios.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsuarios();
  }, []);

  
  // # Filtrar usuarios (búsqueda)
  
  const filtered = usuarios.filter(
    (u) =>
      (u.email || "").toLowerCase().includes(query.toLowerCase()) ||
      (u.username || "").toLowerCase().includes(query.toLowerCase()) ||
      (u.first_name || "").toLowerCase().includes(query.toLowerCase()) ||
      (u.last_name || "").toLowerCase().includes(query.toLowerCase())
  );

  
  //  Eliminar usuario
  
  const handleDelete = async (id) => {
    if (!window.confirm("¿Seguro que deseas eliminar este usuario?")) return;
    try {
      await api.delete(`/usuarios/usuarios/${id}/`);
      await fetchUsuarios();
      alert("Usuario eliminado correctamente ");
    } catch (err) {
      console.error("Error al eliminar usuario:", err);
      alert("No se pudo eliminar el usuario ");
    }
  };

  
  // Render principal
  
  return (
    <Layout>
      <div className="p-6 space-y-6">
        {/* Encabezado */}
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold"> Gestión de Usuarios</h1>
          <button
            onClick={() => {
              setEditing(null);
              setShowForm(true);
            }}
            className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-3 py-2 rounded-lg"
          >
            <PlusCircle size={18} /> Nuevo Usuario
          </button>
        </div>

        {/* Buscador */}
        <div className="flex justify-between items-center gap-4">
          <input
            type="text"
            placeholder="Buscar por nombre, usuario o email..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="border px-3 py-2 rounded w-full"
          />
        </div>

        {/* Formulario (Crear/Editar) */}
        {showForm && (
          <UsuarioForm
            usuario={editing}
            onClose={() => {
              setShowForm(false);
              fetchUsuarios();
            }}
          />
        )}

        {/* Tabla principal */}
        {loading ? (
          <p className="text-center text-gray-600 mt-10">Cargando usuarios...</p>
        ) : error ? (
          <p className="text-center text-red-600 mt-10">{error}</p>
        ) : (
          <div className="overflow-x-auto bg-white rounded shadow">
            <table className="w-full border text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="p-2 border text-left">ID</th>
                  <th className="p-2 border text-left">Usuario</th>
                  <th className="p-2 border text-left">Nombre</th>
                  <th className="p-2 border text-left">Email</th>
                  <th className="p-2 border text-left">Rol</th>
                  <th className="p-2 border text-left">Activo</th>
                  <th className="p-2 border text-center">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length > 0 ? (
                  filtered.map((u) => (
                    <tr key={u.id} className="border-t hover:bg-gray-50">
                      <td className="p-2">{u.id}</td>
                      <td className="p-2">{u.username}</td>
                      <td className="p-2">
                        {u.first_name} {u.last_name}
                      </td>
                      <td className="p-2">{u.email}</td>
                      <td className="p-2">{u.rol}</td>
                      <td className="p-2">
                        {u.is_active ? (
                          <span className="text-emerald-600 font-semibold">Sí</span>
                        ) : (
                          <span className="text-red-600 font-semibold">No</span>
                        )}
                      </td>
                      <td className="p-2 flex gap-2 justify-center">
                        <button
                          onClick={() => {
                            setEditing(u);
                            setShowForm(true);
                          }}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          <Pencil size={18} />
                        </button>
                        <button
                          onClick={() => handleDelete(u.id)}
                          className="text-red-600 hover:text-red-800"
                        >
                          <Trash2 size={18} />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="p-3 text-center" colSpan="7">
                      Sin resultados.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
