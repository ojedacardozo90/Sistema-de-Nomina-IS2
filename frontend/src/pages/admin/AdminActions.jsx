// src/pages/admin/AdminActions.jsx
export default function AdminActions({ model, selected, onAction, onExport }) {
  const hasSelection = selected.length > 0;

  const run = (action) => {
    if (!hasSelection) return alert("No hay registros seleccionados.");
    onAction(action);
  };

  const BUTTONS = {
    "empleados": [
      { label: "Activar", action: "activar" },
      { label: "Desactivar", action: "desactivar" },
      { label: "Exportar Excel", action: "exportar" },
    ],
    "nomina_cal/liquidaciones": [
      { label: "Cerrar", action: "cerrar" },
      { label: "Recalcular", action: "recalcular" },
      { label: "Enviar Recibos", action: "enviar" },
    ],
    "nomina_cal/conceptos": [
      { label: "Habilitar", action: "habilitar" },
      { label: "Deshabilitar", action: "deshabilitar" },
    ],
    "usuarios/usuarios": [
      { label: "Activar", action: "activar" },
      { label: "Desactivar", action: "desactivar" },
    ],
  };

  const actions = BUTTONS[model] || [];

  return (
    <div className="flex gap-2 px-4 py-2 border-b bg-white">
      {actions.map((btn) => (
        <button
          key={btn.action}
          onClick={() => run(btn.action)}
          className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700"
        >
          {btn.label}
        </button>
      ))}
      <button
        onClick={onExport}
        className="bg-gray-600 text-white px-3 py-1 rounded hover:bg-gray-700"
      >
        📊 Exportar
      </button>
    </div>
  );
}



// frontend/src/pages/admin/AdminActions.jsx
export default function AdminActions({ selected=[], onNew, onDelete, extra=[] }) {
  return (
    <div className="bg-white border rounded p-3 flex items-center gap-2">
      <button className="bg-green-600 text-white px-3 py-2 rounded" onClick={onNew}>➕ Nuevo</button>
      <button
        className="px-3 py-2 rounded border disabled:opacity-50"
        disabled={selected.length===0}
        onClick={()=>onDelete(selected)}
      >
        🗑️ Eliminar ({selected.length})
      </button>
      {extra.map((btn, i)=>(
        <button key={i} className="px-3 py-2 rounded border" onClick={btn.onClick}>{btn.label}</button>
      ))}
      <div className="ml-auto text-sm text-gray-500">Seleccionados: {selected.length}</div>
    </div>
  );
}
