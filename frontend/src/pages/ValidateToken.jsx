import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import api from "../utils/api";
import Layout from "../components/Layout";
export default function ValidateToken() {
  const { uidb64, token } = useParams();
  const [estado, setEstado] = useState("Cargando...");
  const navigate = useNavigate();

  useEffect(() => {
    const validar = async () => {
      try {
        await axios.get(`http://localhost:8000/api/password_reset/validate/${uidb64}/${token}/`);
        setEstado("Token válido. Redirigiendo...");
        setTimeout(() => navigate(`/reset-password/${uidb64}/${token}`), 2000);
      } catch {
        setEstado(" Token inválido o expirado.");
      }
    };
    validar();
  }, [uidb64, token, navigate]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 px-4">
      <div className="bg-white shadow-lg rounded-2xl p-8 w-full max-w-md text-center">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Validación de Token</h2>
        <p>{estado}</p>
      </div>
    </div>
  );
}
