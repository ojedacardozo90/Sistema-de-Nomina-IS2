// ============================================================
// 🧠 useHistorial — Hook para gestionar el HistorialModal
// ------------------------------------------------------------
// Proporciona un estado reutilizable para abrir/cerrar el
// historial desde cualquier tabla del Admin Panel.
// ============================================================

import { useState } from "react";
import HistorialModal from "./HistorialModal";

export default function useHistorial() {
  const [historial, setHistorial] = useState({ open: false, model: "", id: null });

  const openHistorial = (model, id) => setHistorial({ open: true, model, id });
  const closeHistorial = () => setHistorial({ open: false, model: "", id: null });

  const Historial = (
    <HistorialModal
      open={historial.open}
      model={historial.model}
      id={historial.id}
      onClose={closeHistorial}
    />
  );

  return { openHistorial, closeHistorial, Historial };
}
