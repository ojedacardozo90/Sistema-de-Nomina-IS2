// src/pages/admin/AdminSidebar.jsx

// Barra lateral del Panel Administrativo
// Combina funcionalidad de navegación + estilo moderno


const ITEMS = [
  { key: "empleados", label: "Empleados", endpoint: "empleados" },
  { key: "nomina_cal/liquidaciones", label: "Liquidaciones", endpoint: "nomina_cal/liquidaciones" },
  { key: "nomina_cal/conceptos", label: "Conceptos", endpoint: "nomina_cal/conceptos" },
  { key: "asistencia/asistencias", label: "Asistencias", endpoint: "asistencia/asistencias" },
  { key: "usuarios/usuarios", label: "Usuarios", endpoint: "usuarios/usuarios" },
  { key: "auditoria/logs", label: "Auditoría", endpoint: "auditoria/logs" }, // ⬅️ Añadido del primer fragmento
];

export default function AdminSidebar({ current, onChange }) {
  return (
    <aside className="w-64 bg-gray-900 text-white h-screen sticky top-0 flex flex-col">
      {/* 🔧 Encabezado */}
      <div className="p-4 font-bold text-lg border-b border-gray-700">
         Panel Administrativo
      </div>

      {/*  Menú de navegación */}
      <nav className="flex-1 overflow-y-auto space-y-1 px-2 py-2">
        {ITEMS.map((it) => (
          <button
            key={it.key}
            onClick={() => onChange(it.endpoint)}
            className={`w-full text-left px-3 py-2 rounded transition-colors hover:bg-gray-800 ${
              current === it.endpoint ? "bg-gray-800" : ""
            }`}
          >
            {it.label}
          </button>
        ))}
      </nav>
    </aside>
  );
}
