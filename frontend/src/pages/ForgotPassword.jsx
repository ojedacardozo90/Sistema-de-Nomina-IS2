
//  Recuperar contraseña - Enlace a /usuarios/password-reset/


import { useState } from "react";
import { forgotPassword } from "../utils/api";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [enviando, setEnviando] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setEnviando(true);
    setMensaje("");
    try {
      await forgotPassword(email);
      setMensaje(
        "Si tu correo está registrado, recibirás un enlace para restablecer tu contraseña."
      );
    } catch (error) {
      console.error(error);
      setMensaje(" No se pudo enviar el correo. Intenta de nuevo más tarde.");
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-gray-100">
      <form
        onSubmit={handleSubmit}
        className="bg-white shadow-lg rounded-lg p-8 w-96"
      >
        <h2 className="text-2xl font-bold mb-4 text-center text-gray-700">
          Recuperar Contraseña
        </h2>
        <label className="block text-gray-600 mb-2">Correo electrónico</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="border border-gray-300 rounded-lg w-full p-2 mb-4"
          placeholder="tu@correo.com"
        />
        <button
          type="submit"
          disabled={enviando}
          className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
        >
          {enviando ? "Enviando..." : "Enviar enlace"}
        </button>
        {mensaje && (
          <p className="mt-4 text-sm text-center text-gray-600">{mensaje}</p>
        )}
      </form>
    </div>
  );
}
