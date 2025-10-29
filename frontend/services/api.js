// src/utils/api.js
import axios from "axios";

/**
 * ======================================================
 * 🌐 Cliente Axios
 * - Base URL: backend Django (con barra final)
 * - Interceptor: adjunta JWT 'access' en Authorization
 * ======================================================
 */
const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api/", // 👈 importante: barra final
  headers: { "Content-Type": "application/json" },
});

// ======================================================
// 🔑 INTERCEPTOR PARA JWT
//   - Usamos la clave 'access' (coherente con SimpleJWT)
// ======================================================
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ======================================================
// 👤 AUTENTICACIÓN (Usuarios)
//  - Login: /api/usuarios/login/  (CustomTokenObtainPairView)
//  - Perfil: /api/usuarios/me/    (o /perfil/)
// ======================================================
export const loginApi = (data) => api.post("usuarios/login/", data);
export const getProfile = () => api.get("usuarios/me/");

// ======================================================
// 🧑‍💼 EMPLEADOS
// ======================================================
export const getEmpleados = () => api.get("empleados/");
export const getEmpleado = (id) => api.get(`empleados/${id}/`);
export const createEmpleado = (data) => api.post("empleados/", data);
export const updateEmpleado = (id, data) => api.put(`empleados/${id}/`, data);
export const deleteEmpleado = (id) => api.delete(`empleados/${id}/`);

// ======================================================
// 📊 CONCEPTOS (nómina)
// ======================================================
export const getConceptos = () => api.get("nomina_cal/conceptos/");
export const getConcepto = (id) => api.get(`nomina_cal/conceptos/${id}/`);
export const createConcepto = (data) => api.post("nomina_cal/conceptos/", data);
export const updateConcepto = (id, data) => api.put(`nomina_cal/conceptos/${id}/`, data);
export const deleteConcepto = (id) => api.delete(`nomina_cal/conceptos/${id}/`);

// ======================================================
// 💵 LIQUIDACIONES
// ======================================================
export const getLiquidaciones = () => api.get("nomina_cal/liquidaciones/");
export const getLiquidacion = (id) => api.get(`nomina_cal/liquidaciones/${id}/`);
export const createLiquidacion = (data) => api.post("nomina_cal/liquidaciones/", data);
export const updateLiquidacion = (id, data) => api.put(`nomina_cal/liquidaciones/${id}/`, data);
export const deleteLiquidacion = (id) => api.delete(`nomina_cal/liquidaciones/${id}/`);

export const calcularLiquidacion = (id) => api.post(`nomina_cal/liquidaciones/${id}/calcular/`);
export const cerrarLiquidacion   = (id) => api.post(`nomina_cal/liquidaciones/${id}/cerrar/`);

// ======================================================
// 📈 REPORTES NÓMINA
// ======================================================
export const getReporteGeneral = (params) => api.get("nomina_cal/reportes/general/", { params });
export const exportarExcelNomina = () => api.get("nomina_cal/reportes/excel/", { responseType: "blob" });
export const exportarPDFNomina   = () => api.get("nomina_cal/reportes/pdf/",   { responseType: "blob" });

// ======================================================
// 📊 ANALYTICS / KPI (nómina)
// ======================================================
export const getKpisResumen   = (params = {}) => api.get("nomina_cal/analytics/kpis/", { params });
export const getSerie6        = () => api.get("nomina_cal/analytics/serie6/");
export const getTopDescuentos = (params = {}) => api.get("nomina_cal/analytics/top-descuentos/", { params });

// ======================================================
// 🕒 ASISTENCIA (nuevo servicio API)
// ======================================================
export const marcarAsistencia = (tipo) => api.post("asistencia/fichadas/marcar/", { tipo });
export const listarAsistencias = (params = {}) => api.get("asistencia/asistencias/", { params });

export const reporteMensualAsistencia = (params = {}) =>
  api.get("asistencia/asistencias/reporte-mensual/", { params });

export const exportarExcelAsistencia = (params = {}) =>
  api.get("asistencia/asistencias/reporte-excel/", { params, responseType: "blob" });

export const exportarPDFAsistencia = (params = {}) =>
  api.get("asistencia/asistencias/reporte-pdf/", { params, responseType: "blob" });

export default api;
