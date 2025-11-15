// src/components/LogoutButton.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import { clearToken } from "../utils/auth";

const LogoutButton = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    clearToken(); // # eliminamos access + refresh
    navigate("/login"); // # volvemos al login
  };

  return (
    <button
      onClick={handleLogout}
      className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition"
    >
      Cerrar Sesión
    </button>
  );
};

export default LogoutButton;
