// src/services/asistencia.js
import {
  marcarAsistencia,
  listarAsistencias as listar,
  getReporteMensual as repMensual,
  exportarAsistenciaExcel as repExcel,
  exportarAsistenciaPDF as repPDF,
} from "../utils/api";

/**
 * Capa fina por si luego querés transformar datos o cachear.
 */
export const marcar = (tipo) => marcarAsistencia(tipo);
export const listarAsistencias = (params) => listar(params);
export const reporteMensual = (params) => repMensual(params);
export const exportarExcel = (params) => repExcel(params);
export const exportarPDF = (params) => repPDF(params);
