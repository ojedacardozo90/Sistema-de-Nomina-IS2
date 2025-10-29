// src/components/ProtectedRoute.jsx
import React from "react";
import { Navigate, Outlet } from "react-router-dom";
import { getToken } from "../utils/auth";

// 🔹 Este componente envuelve las rutas privadas
const ProtectedRoute = () => {
  const token = getToken();

  // Si NO hay token, redirigimos al login
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // Si hay token, mostramos las rutas hijas
  return <Outlet />;
};

export default ProtectedRoute;
