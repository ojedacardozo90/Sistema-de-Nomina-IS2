import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../utils/api";

export default function EmpleadoForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  // ====
  // Estado principal
  // ====
  const [empleado, setEmpleado] = useState({
    nombre: "",
    apellido: "",
    cedula: "",
    direccion: "",
    telefono: "",
    email: "",
    salario_base: 0,
    activo: true,
    usuario: null,
    hijos: [],
  });

  const [usuarios, setUsuarios] = useState([]);

  // ====
  // Cargar datos iniciales
  // ====
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Obtener usuarios disponibles
        const usuariosRes = await api.get("/usuarios/");
        setUsuarios(usuariosRes.data);

        // Si estamos en edición
        if (id) {
          const res = await api.get(`/empleados/${id}/`);
          setEmpleado(res.data);
        }
      } catch (error) {
        console.error("Error cargando datos:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  // ====
  // Manejo de cambios
  // ====
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setEmpleado({
      ...empleado,
      [name]: type === "checkbox" ? checked : value,
    });
  };

  // ====
  // Hijos: agregar/eliminar
  // ====
  const handleAddHijo = () => {
    setEmpleado({
      ...empleado,
      hijos: [...empleado.hijos, { nombre: "", fecha_nacimiento: "", reside_py: true }],
    });
  };

  const handleRemoveHijo = (index) => {
    const nuevos = [...empleado.hijos];
    nuevos.splice(index, 1);
    setEmpleado({ ...empleado, hijos: nuevos });
  };

  const handleChangeHijo = (index, e) => {
    const { name, value, type, checked } = e.target;
    const nuevos = [...empleado.hijos];
    nuevos[index][name] = type === "checkbox" ? checked : value;
    setEmpleado({ ...empleado, hijos: nuevos });
  };

  // ====
  // Guardar
  // ====
  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      let response;
      if (id) {
        response = await api.put(`/empleados/${id}/`, empleado);
      } else {
        response = await api.post("/empleados/", empleado);
      }
      alert("Empleado guardado correctamente");
      navigate("/empleados");
    } catch (error) {
      console.error("Error guardando empleado:", error.response?.data || error);
      alert("Hubo un error guardando el empleado");
    } finally {
      setLoading(false);
    }
  };

  // ====
  // Render
  // ====
  if (loading) return <p className="p-4">Cargando...</p>;

  return (
    <div className="p-6 max-w-3xl mx-auto bg-white shadow-md rounded-lg">
      <h1 className="text-2xl font-bold mb-6">
        {id ? "Editar Empleado" : "Nuevo Empleado"}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Datos básicos */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block font-medium mb-1">Nombre</label>
            <input
              type="text"
              name="nombre"
              value={empleado.nombre}
              onChange={handleChange}
              required
              className="w-full border px-3 py-2 rounded-md"
            />
          </div>
          <div>
            <label className="block font-medium mb-1">Apellido</label>
            <input
              type="text"
              name="apellido"
              value={empleado.apellido}
              onChange={handleChange}
              required
              className="w-full border px-3 py-2 rounded-md"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block font-medium mb-1">Cédula</label>
            <input
              type="text"
              name="cedula"
              value={empleado.cedula}
              onChange={handleChange}
              required
              className="w-full border px-3 py-2 rounded-md"
            />
          </div>
          <div>
            <label className="block font-medium mb-1">Teléfono</label>
            <input
              type="text"
              name="telefono"
              value={empleado.telefono}
              onChange={handleChange}
              className="w-full border px-3 py-2 rounded-md"
            />
          </div>
        </div>

        <div>
          <label className="block font-medium mb-1">Dirección</label>
          <input
            type="text"
            name="direccion"
            value={empleado.direccion}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded-md"
          />
        </div>

        <div>
          <label className="block font-medium mb-1">Email</label>
          <input
            type="email"
            name="email"
            value={empleado.email}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded-md"
          />
        </div>

        {/* Usuario asignado */}
        <div>
          <label className="block font-medium mb-1">Usuario del Sistema</label>
          <select
            name="usuario"
            value={empleado.usuario || ""}
            onChange={handleChange}
            className="w-full border px-3 py-2 rounded-md"
          >
            <option value="">Ninguno</option>
            {usuarios.map((u) => (
              <option key={u.id} value={u.id}>
                {u.username} ({u.email})
              </option>
            ))}
          </select>
        </div>

        {/* Salario base */}
        <div>
          <label className="block font-medium mb-1">Salario Base</label>
          <input
            type="number"
            name="salario_base"
            value={empleado.salario_base}
            onChange={handleChange}
            required
            className="w-full border px-3 py-2 rounded-md"
          />
        </div>

        {/* Activo */}
        <div className="flex items-center">
          <input
            type="checkbox"
            name="activo"
            checked={empleado.activo}
            onChange={handleChange}
            className="mr-2"
          />
          <label>Empleado Activo</label>
        </div>

        {/* Hijos */}
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-2">Hijos</h2>
          {empleado.hijos.map((h, index) => (
            <div key={index} className="grid grid-cols-3 gap-2 mb-2 items-center">
              <input
                type="text"
                name="nombre"
                value={h.nombre}
                onChange={(e) => handleChangeHijo(index, e)}
                placeholder="Nombre hijo"
                className="border px-2 py-1 rounded-md"
              />
              <input
                type="date"
                name="fecha_nacimiento"
                value={h.fecha_nacimiento}
                onChange={(e) => handleChangeHijo(index, e)}
                className="border px-2 py-1 rounded-md"
              />
              <div className="flex items-center">
                <input
                  type="checkbox"
                  name="reside_py"
                  checked={h.reside_py}
                  onChange={(e) => handleChangeHijo(index, e)}
                  className="mr-2"
                />
                <label>Reside en PY</label>
              </div>
              <button
                type="button"
                onClick={() => handleRemoveHijo(index)}
                className="bg-red-500 text-white px-2 py-1 rounded-md hover:bg-red-600"
              >
                Eliminar
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={handleAddHijo}
            className="bg-blue-600 text-white px-3 py-1 rounded-md hover:bg-blue-700"
          >
            Agregar Hijo
          </button>
        </div>

        {/* Botones */}
        <div className="flex justify-between mt-6">
          <button
            type="button"
            onClick={() => navigate("/empleados")}
            className="bg-gray-400 text-white px-4 py-2 rounded-md hover:bg-gray-500"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={loading}
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
          >
            Guardar
          </button>
        </div>
      </form>
    </div>
  );
}
