// src/services/asistencia.js

//  Servicios de Asistencia (Axios + JWT via src/utils/api.js)
// Endpoints esperados (backend Django):
//   GET    /api/asistencia/fichadas/            -> listar
//   POST   /api/asistencia/fichadas/marcar/     -> { tipo: "entrada" | "salida" }
//   GET    /api/asistencia/asistencias/         -> resumen diario/mensual (opcional)


import api from "../utils/api";

export async function listarAsistencias(params = {}) {
  const { data } = await api.get("asistencia/fichadas/", { params });
  return data;
}

export async function marcar(tipo = "entrada") {
  if (!["entrada","salida"].includes(tipo)) {
    throw new Error("Tipo inválido. Use 'entrada' o 'salida'.");
  }
  const { data } = await api.post("asistencia/fichadas/marcar/", { tipo });
  return data;
}
