import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../utils/api";
import { saveSession } from "../utils/auth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const response = await api.post("usuarios/login/", {
        email,
        password,
      });

      const { access, refresh, usuario } = response.data;

      if (!usuario) throw new Error("Respuesta inválida del servidor");

      // Guardar sesión coherente
      saveSession(access, refresh, usuario);

      // Redirigir según rol
      const rol = usuario.rol?.toLowerCase();
      if (rol.includes("admin")) navigate("/dashboard/admin");
      else if (rol.includes("gerente")) navigate("/dashboard/gerente");
      else if (rol.includes("asistente")) navigate("/dashboard/asistente");
      else navigate("/dashboard/empleado");
    } catch (err) {
      console.error("Error en inicio de sesión:", err);
      setError("Credenciales incorrectas o error del servidor.");
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-gray-100">
      <div className="bg-white p-8 rounded-2xl shadow-md w-96">
        <h2 className="text-2xl font-bold text-center mb-6">Iniciar Sesión</h2>

        {error && (
          <div className="bg-red-100 text-red-600 p-2 rounded mb-4 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <label className="block mb-2 text-sm font-medium">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 mb-4 border rounded-lg focus:ring focus:ring-blue-300"
            placeholder="ejemplo@correo.com"
            required
          />

          <label className="block mb-2 text-sm font-medium">Contraseña</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 mb-4 border rounded-lg focus:ring focus:ring-blue-300"
            placeholder="********"
            required
          />

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Ingresar
          </button>
        </form>
      </div>
    </div>
  );
}
