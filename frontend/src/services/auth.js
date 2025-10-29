// src/services/auth.js
import { login as loginRequest, getProfile } from "../utils/api";

/**
 * ============================================================
 * 🔑 Auth Service (JWT)
 * - login(): guarda tokens + user en localStorage
 * - logout(): limpia sesión
 * - getUser(): devuelve usuario logueado (o null)
 * ============================================================
 */
export async function login(username, password) {
  // Usamos el alias 'loginRequest' para evitar colisión
  const { data } = await loginRequest({ username, password });

  // SimpleJWT: devuelve { access, refresh, user: { id, username, email, rol } }
  localStorage.setItem("access_token", data.access);
  localStorage.setItem("refresh_token", data.refresh);
  localStorage.setItem("user", JSON.stringify(data.user));

  return data.user; // útil para redireccionar por rol
}

export function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  localStorage.removeItem("user");
}

export function getUser() {
  const raw = localStorage.getItem("user");
  return raw ? JSON.parse(raw) : null;
}

// (Opcional) Validar sesión golpeando backend
export async function fetchProfile() {
  const { data } = await getProfile();
  return data;
}
