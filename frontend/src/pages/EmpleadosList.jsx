
//  EmpleadosList — Gestión completa de empleados

// Incluye:
//   • Listado con filtros dinámicos
//   • Búsqueda en tiempo real
//   • Eliminación con confirmación
//   • Navegación a edición y creación
//   • Integración total con el backend Django

// Endpoint base: /api/empleados/


import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../utils/api";
import Layout from "../components/Layout";

export default function EmpleadosList() {
  // ===
  // # Estados principales
  // ===
  const [empleados, setEmpleados] = useState([]); // siempre array
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");

  
  //  Cargar empleados desde el backend
  
  const fetchEmpleados = async () => {
    setLoading(true);
    try {
      const res = await api.get("/empleados/");
      const data = Array.isArray(res.data) ? res.data : [];
      setEmpleados(data);
    } catch (error) {
      console.error(" Error al cargar empleados:", error);
      setEmpleados([]); // evitar crash
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEmpleados();
  }, []);

  
  // 🗑️ Eliminar empleado
  
  const handleDelete = async (id) => {
    if (!window.confirm("¿Seguro que deseas eliminar este empleado?")) return;
    try {
      await api.delete(`/empleados/${id}/`);
      alert(" Empleado eliminado correctamente.");
      fetchEmpleados();
    } catch (error) {
      console.error(" Error eliminando empleado:", error);
      alert("Hubo un error al eliminar el empleado.");
    }
  };

  
  // Filtrado local por nombre, apellido o cédula
  
  const empleadosFiltrados = Array.isArray(empleados)
    ? empleados.filter(
        (e) =>
          (e.nombre || "").toLowerCase().includes(search.toLowerCase()) ||
          (e.apellido || "").toLowerCase().includes(search.toLowerCase()) ||
          (e.cedula || "").toLowerCase().includes(search.toLowerCase())
      )
    : [];

  
  //  Render principal
  
  return (
    <Layout>
      <div className="p-6">
        {/* Título y botón superior */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold"> Empleados</h1>
          <Link
            to="/empleados/nuevo"
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition"
          >
            + Nuevo Empleado
          </Link>
        </div>

        {/* Buscador */}
        <div className="mb-4">
          <input
            type="text"
            placeholder="Buscar por nombre, apellido o cédula..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="border w-full px-3 py-2 rounded-md shadow-sm focus:ring focus:ring-blue-200 outline-none"
          />
        </div>

        {/* Tabla de empleados */}
        {loading ? (
          <div className="text-center text-gray-500">Cargando empleados...</div>
        ) : empleadosFiltrados.length === 0 ? (
          <div className="text-center text-gray-500 mt-4">
            No se encontraron empleados.
          </div>
        ) : (
          <div className="overflow-x-auto bg-white shadow-md rounded-lg border border-gray-200">
            <table className="w-full text-sm text-left border-collapse">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-4 py-2 border">Nombre</th>
                  <th className="px-4 py-2 border">Apellido</th>
                  <th className="px-4 py-2 border">Cédula</th>
                  <th className="px-4 py-2 border">Email</th>
                  <th className="px-4 py-2 border">Teléfono</th>
                  <th className="px-4 py-2 border">Cargo</th>
                  <th className="px-4 py-2 border">Salario Base</th>
                  <th className="px-4 py-2 border text-center">Activo</th>
                  <th className="px-4 py-2 border text-center">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {empleadosFiltrados.map((e) => (
                  <tr
                    key={e.id}
                    className="hover:bg-gray-50 transition-colors duration-200"
                  >
                    <td className="px-4 py-2 border">{e.nombre}</td>
                    <td className="px-4 py-2 border">{e.apellido}</td>
                    <td className="px-4 py-2 border">{e.cedula}</td>
                    <td className="px-4 py-2 border">{e.email}</td>
                    <td className="px-4 py-2 border">{e.telefono}</td>
                    <td className="px-4 py-2 border">{e.cargo || "—"}</td>
                    <td className="px-4 py-2 border">
                      {parseFloat(e.salario_base || 0).toLocaleString("es-PY")} Gs
                    </td>
                    <td className="px-4 py-2 border text-center">
                      {e.activo ? (
                        <span className="text-green-600 font-semibold">Sí</span>
                      ) : (
                        <span className="text-red-600 font-semibold">No</span>
                      )}
                    </td>
                    <td className="px-4 py-2 border text-center space-x-2">
                      <Link
                        to={`/empleados/${e.id}/editar`}
                        className="bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700 transition"
                      >
                        Editar
                      </Link>
                      <button
                        onClick={() => handleDelete(e.id)}
                        className="bg-red-600 text-white px-3 py-1 rounded-md hover:bg-red-700 transition"
                      >
                        Eliminar
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
