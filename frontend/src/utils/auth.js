// ============================================================
// 🔐 Auth Utils — Unificación de almacenamiento local
// ============================================================
import api from "./api";

const TOKEN_KEY = "access_token";
const REFRESH_KEY = "refresh_token";
const USER_KEY = "usuario"; // coincide con la respuesta del backend
const ROLE_KEY = "rol";

// ========================
// 📌 TOKEN
// ========================
export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const saveToken = (access, refresh) => {
  localStorage.setItem(TOKEN_KEY, access);
  localStorage.setItem(REFRESH_KEY, refresh);
};
export const clearToken = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_KEY);
};

// ========================
// 📌 USER
// ========================
export const getUser = () => {
  const user = localStorage.getItem(USER_KEY);
  return user ? JSON.parse(user) : null;
};
export const setUser = (user) =>
  localStorage.setItem(USER_KEY, JSON.stringify(user));

// ========================
// 📌 ROLE
// ========================
export const getRole = () => localStorage.getItem(ROLE_KEY);
export const setRole = (role) => localStorage.setItem(ROLE_KEY, role);

// ========================
// 🧩 SESIÓN
// ========================
export const saveSession = (access, refresh, user) => {
  saveToken(access, refresh);
  setUser(user);
  setRole(user.rol);
};

export const clearSession = () => {
  clearToken();
  localStorage.removeItem(USER_KEY);
  localStorage.removeItem(ROLE_KEY);
  window.location.href = "/login";
};

// ============================================================
// 🔄 Perfil (compatibilidad con RoleRouter y Login)
// ============================================================



export async function fetchProfile() {
  try {
    const token = getToken();
    if (!token) return null;

    const res = await api.get("/usuarios/me/");
    return res.data;
  } catch (error) {
    console.error("Error al obtener perfil:", error);
    return null;
  }
}
