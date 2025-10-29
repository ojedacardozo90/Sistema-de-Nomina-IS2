// ======================================================
// 🔐 Restablecer Contraseña — /usuarios/password-reset-confirm/
// ======================================================

import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { resetPassword } from "../utils/api";

export default function ResetPassword() {
  const [params] = useSearchParams();
  const [password, setPassword] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [procesando, setProcesando] = useState(false);

  const uid = params.get("uid");
  const token = params.get("token");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password !== confirmar) {
      setMensaje("⚠️ Las contraseñas no coinciden.");
      return;
    }
    setProcesando(true);
    try {
      await resetPassword(uid, token, password);
      setMensaje("✅ Contraseña restablecida correctamente. Ya podés iniciar sesión.");
    } catch (error) {
      console.error(error);
      setMensaje("❌ Error al restablecer la contraseña. Enlace inválido o expirado.");
    } finally {
      setProcesando(false);
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-gray-100">
      <form
        onSubmit={handleSubmit}
        className="bg-white shadow-lg rounded-lg p-8 w-96"
      >
        <h2 className="text-2xl font-bold mb-4 text-center text-gray-700">
          Restablecer Contraseña
        </h2>
        <label className="block text-gray-600 mb-2">Nueva contraseña</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="border border-gray-300 rounded-lg w-full p-2 mb-4"
        />
        <label className="block text-gray-600 mb-2">Confirmar contraseña</label>
        <input
          type="password"
          value={confirmar}
          onChange={(e) => setConfirmar(e.target.value)}
          required
          className="border border-gray-300 rounded-lg w-full p-2 mb-4"
        />
        <button
          type="submit"
          disabled={procesando}
          className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition"
        >
          {procesando ? "Procesando..." : "Cambiar contraseña"}
        </button>
        {mensaje && (
          <p className="mt-4 text-sm text-center text-gray-600">{mensaje}</p>
        )}
      </form>
    </div>
  );
}
