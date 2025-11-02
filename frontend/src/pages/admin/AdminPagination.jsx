// src/pages/admin/AdminPagination.jsx
export default function AdminPagination({ page, pageSize, count, onPage }) {
  const totalPages = Math.max(1, Math.ceil(count / pageSize));
  const prev = () => onPage(Math.max(1, page - 1));
  const next = () => onPage(Math.min(totalPages, page + 1));

  return (
    <div className="flex items-center justify-end gap-2 mt-3">
      <span className="text-sm text-gray-600">
        Página {page} de {totalPages} — {count} registros
      </span>
      <button onClick={prev} className="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300">⟨</button>
      <button onClick={next} className="px-2 py-1 bg-gray-200 rounded hover:bg-gray-300">⟩</button>
    </div>
  );
}


// frontend/src/pages/admin/AdminPagination.jsx
export default function AdminPagination({ page, setPage, count, pageSize }) {
  const totalPages = Math.max(1, Math.ceil((count || 0) / pageSize));
  return (
    <div className="flex items-center justify-between text-sm mt-3">
      <div>Mostrando página {page} de {totalPages} — {count} registros</div>
      <div className="flex gap-1">
        <button className="border rounded px-2 py-1" onClick={()=>setPage(1)} disabled={page===1}>«</button>
        <button className="border rounded px-2 py-1" onClick={()=>setPage(p=>Math.max(1,p-1))} disabled={page===1}>‹</button>
        <button className="border rounded px-2 py-1" onClick={()=>setPage(p=>Math.min(totalPages,p+1))} disabled={page===totalPages}>›</button>
        <button className="border rounded px-2 py-1" onClick={()=>setPage(totalPages)} disabled={page===totalPages}>»</button>
      </div>
    </div>
  );
}
