// src/pages/admin/AdminHeader.jsx

//  Encabezado del Panel Administrativo
// Combina búsqueda, actualización y encabezado fijo


export default function AdminHeader({ title, onRefresh, onSearch, search }) {
  return (
    <header className="flex justify-between items-center bg-white border-b p-4 shadow-sm sticky top-0 z-10">
      {/* 🔠 Título */}
      <h1 className="text-xl font-bold text-gray-700">{title}</h1>

      {/* Búsqueda + Actualizar */}
      <div className="flex gap-2">
        <input
          type="text"
          placeholder="Buscar..."
          value={search}
          onChange={(e) => onSearch(e.target.value)}
          className="border rounded px-2 py-1 text-sm"
        />
        <button
          onClick={onRefresh}
          className="bg-blue-600 text-white px-4 py-1 rounded hover:bg-blue-700"
          title="Actualizar"  // ⬅️ añadido del segundo fragmento
        >
          
        </button>
      </div>
    </header>
  );
}
