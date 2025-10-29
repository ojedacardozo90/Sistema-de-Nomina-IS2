// ============================================================
// 🌐 API central — Sistema de Nómina IS2 (FP-UNA / FAP)
// Archivo completo, estable y coherente.
// ============================================================

// ============================================================
// 🌐 API central — Sistema de Nómina IS2
// ============================================================

import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api",
});

// ============================================================
// 🔒 Interceptor para JWT
// ============================================================
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn("⚠️ Token expirado o sin autorización");
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);



// ============================================================
// 🧩 AUTENTICACIÓN
// ============================================================

// Login — devuelve tokens + user (tu endpoint actual)
export const login = (data) => api.post("usuarios/login/", data);

// Logout local (opcionalmente podés pegarle a un endpoint si usás blacklist)
export const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  localStorage.removeItem("refresh");
  window.location.href = "/login";
};

// Perfil (coherente con views_auth.user_profile -> sugerido "profile/")
export const obtenerPerfil = () => api.get("usuarios/profile/");

// Compatibilidad si en algún lugar quedó "me/"
export const obtenerPerfilAlt = () => api.get("usuarios/me/");

// Recuperación de contraseña
export const forgotPassword = (data) =>
  api.post("usuarios/forgot-password/", data);

// Reset con uid/token (la forma correcta del backend)
export const resetPasswordWithToken = (uid, token, payload) =>
  api.post(`usuarios/reset-password/${uid}/${token}/`, payload);

// Compatibilidad: si tenías un POST simple sin uid/token
export const resetPassword = (data) =>
  api.post("usuarios/reset-password/", data);

// ============================================================
// 👥 EMPLEADOS (CRUD)
// ============================================================
export const listarEmpleados = (params = {}) => api.get("empleados/", { params });
export const crearEmpleado = (data) => api.post("empleados/", data);
export const actualizarEmpleado = (id, data) => api.put(`empleados/${id}/`, data);
export const eliminarEmpleado = (id) => api.delete(`empleados/${id}/`);
export const obtenerEmpleado = (id) => api.get(`empleados/${id}/`);

// ============================================================
// 💡 CONCEPTOS (CRUD)
// ============================================================
export const listarConceptos = () => api.get("nomina_cal/conceptos/");
export const crearConcepto = (data) => api.post("nomina_cal/conceptos/", data);
export const actualizarConcepto = (id, data) =>
  api.put(`nomina_cal/conceptos/${id}/`, data);
export const eliminarConcepto = (id) =>
  api.delete(`nomina_cal/conceptos/${id}/`);

// ============================================================
// 💵 LIQUIDACIONES (CRUD + acciones)
// ============================================================
export const listarLiquidaciones = (params = {}) =>
  api.get("nomina_cal/liquidaciones/", { params });

export const obtenerLiquidacion = (id) =>
  api.get(`nomina_cal/liquidaciones/${id}/`);

export const crearLiquidacion = (data) =>
  api.post("nomina_cal/liquidaciones/", data);

export const actualizarLiquidacion = (id, data) =>
  api.put(`nomina_cal/liquidaciones/${id}/`, data);

export const eliminarLiquidacion = (id) =>
  api.delete(`nomina_cal/liquidaciones/${id}/`);

// Acciones: calcular / cerrar / enviar-recibo
export const calcularLiquidacion = (id) =>
  api.post(`nomina_cal/liquidaciones/${id}/calcular/`);

export const cerrarLiquidacion = (id) =>
  api.post(`nomina_cal/liquidaciones/${id}/cerrar/`);

export const enviarRecibo = (id) =>
  api.post(`nomina_cal/liquidaciones/${id}/enviar-recibo/`);

// ============================================================
// 🧾 REPORTES / EXPORTACIONES (Nómina)
// ============================================================

// JSON resumido (alias en tus urls.py)
export const reporteGeneral = (params = {}) =>
  api.get("nomina_cal/reporte-general/", { params });

// Excel / PDF — usamos las rutas “reportes/*” que existen seguro
export const exportarExcelNomina = async () => {
  const res = await api.get("nomina_cal/reportes/excel/", { responseType: "blob" });
  return res.data;
};

export const exportarPDFNomina = async () => {
  const res = await api.get("nomina_cal/reportes/pdf/", { responseType: "blob" });
  return res.data;
};

// Compatibilidad (si en alguna parte tenías “export/*”):
export const exportarExcelNominaAlt = async () => {
  const res = await api.get("nomina_cal/export/excel/", { responseType: "blob" });
  return res.data;
};
export const exportarPDFNominaAlt = async () => {
  const res = await api.get("nomina_cal/export/pdf/", { responseType: "blob" });
  return res.data;
};

// ============================================================
// 🔄 Procesos masivos / período
// ============================================================
export const calcularTodas = () => api.post("nomina_cal/calcular-todas/");
export const recalcularPeriodo = (data) =>
  api.post("nomina_cal/liquidaciones/calcular-periodo/", data);
// Compatibilidad con nombre viejo:
export const recalcularPeriodoAlt = (data) =>
  api.post("nomina_cal/recalcular-periodo/", data);

// ============================================================
// 📊 DASHBOARDS POR ROL
// ============================================================
export const dashboardAdmin = () => api.get("nomina_cal/dashboard/admin/");
export const dashboardGerente = () => api.get("nomina_cal/dashboard/gerente/");
export const dashboardAsistente = () => api.get("nomina_cal/dashboard/asistente/");
export const dashboardEmpleado = () => api.get("nomina_cal/dashboard/empleado/");

// ============================================================
// 🕒 ASISTENCIAS
// ============================================================
export const listarAsistencias = (params = {}) =>
  api.get("asistencia/asistencias/", { params });

export const marcarAsistencia = (tipo) =>
  api.post("asistencia/fichadas/marcar/", { tipo });

export const exportarAsistenciasExcel = async (mes, anio) => {
  const res = await api.get("asistencia/exportar-excel/", {
    params: { mes, anio },
    responseType: "blob",
  });
  return res.data;
};

export const exportarAsistenciasPDF = async (mes, anio) => {
  const res = await api.get("asistencia/exportar-pdf/", {
    params: { mes, anio },
    responseType: "blob",
  });
  return res.data;
};

// ============================================================
// 🧰 UTILIDADES
// ============================================================
export const descargarArchivo = (blob, nombreArchivo) => {
  const url = window.URL.createObjectURL(new Blob([blob]));
  const link = document.createElement("a");
  link.href = url;
  link.download = nombreArchivo;
  document.body.appendChild(link);
  link.click();
  link.remove();
};

export async function getProfile(token) {
  try {
    const response = await api.get("usuarios/profile/", {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  } catch (error) {
    console.error("Error al obtener el perfil:", error);
    throw error;
  }
}


// --- Reportes Avanzados ---
export const reportesAvanzados = (params={}) =>
  api.get("nomina_cal/reportes/avanzados/", { params });

export const exportarAvanzadoExcel = (params={}) =>
  api.get("nomina_cal/reportes/avanzados/excel/", { params, responseType: "blob" });

export const exportarAvanzadoPDF = (params={}) =>
  api.get("nomina_cal/reportes/avanzados/pdf/", { params, responseType: "blob" });

// --- Auditoría ---
export const listarAuditoria = (params={}) =>
  api.get("auditoria/logs/", { params });


// ==== Usuarios ====
export const listarUsuarios = () => api.get("/usuarios/usuarios/");
export const crearUsuario  = (data) => api.post("/usuarios/usuarios/", data);
export const actualizarUsuario = (id, data) => api.put(`/usuarios/usuarios/${id}/`, data);
export const eliminarUsuario   = (id) => api.delete(`/usuarios/usuarios/${id}/`);

// ==== Importación ====
export const importarEmpleados = (archivo) => {
  const form = new FormData();
  form.append("archivo", archivo);
  return api.post("/nomina_cal/importar/empleados/", form, { headers: { "Content-Type": "multipart/form-data" }});
};

export const importarLiquidaciones = (archivo) => {
  const form = new FormData();
  form.append("archivo", archivo);
  return api.post("/nomina_cal/importar/liquidaciones/", form, { headers: { "Content-Type": "multipart/form-data" }});
};


// ============================================================
// ✅ Export default
// ============================================================
export default api;
