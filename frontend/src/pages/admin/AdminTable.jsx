// src/pages/admin/AdminTable.jsx
export default function AdminTable({ data, model, selected, setSelected, onEdit }) {
  const keys = Object.keys(data[0]);

  const toggleSelect = (id) => {
    if (selected.includes(id)) setSelected(selected.filter((x) => x !== id));
    else setSelected([...selected, id]);
  };

  return (
    <table className="min-w-full bg-white border border-gray-200 shadow-sm rounded text-sm">
      <thead className="bg-gray-100 text-gray-700">
        <tr>
          <th className="p-2 border-b">
            <input
              type="checkbox"
              onChange={(e) =>
                setSelected(e.target.checked ? data.map((r) => r.id) : [])
              }
              checked={selected.length === data.length}
            />
          </th>
          {keys.slice(0, 6).map((key) => (
            <th key={key} className="p-2 border-b text-left font-semibold">
              {key.toUpperCase()}
            </th>
          ))}
          <th className="p-2 border-b text-center">Acciones</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row) => (
          <tr key={row.id} className="hover:bg-gray-50">
            <td className="p-2 border-b text-center">
              <input
                type="checkbox"
                checked={selected.includes(row.id)}
                onChange={() => toggleSelect(row.id)}
              />
            </td>
            {keys.slice(0, 6).map((key) => (
              <td key={key} className="p-2 border-b">
                {String(row[key] ?? "-")}
              </td>
            ))}
            <td className="p-2 border-b text-center">
              <button
                onClick={() => onEdit(row)}
                className="text-blue-600 hover:underline"
              >
                Editar
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
// frontend/src/pages/admin/AdminTable.jsx
export default function AdminTable({ columns, rows, ordering, setOrdering, selected, setSelected }) {
  const toggle = (id) => {
    setSelected((prev) => prev.includes(id) ? prev.filter(x=>x!==id) : [...prev, id]);
  };

  const toggleAll = () => {
    if (selected.length === rows.length) setSelected([]);
    else setSelected(rows.map(r => r.id));
  };

  const handleSort = (col) => {
    if (!col.sortable) return;
    const field = col.orderField || col.field;
    const isCurrent = ordering.replace("-", "") === field;
    const next = isCurrent && !ordering.startsWith("-") ? `-${field}` : field;
    setOrdering(next);
  };

  return (
    <div className="border rounded overflow-x-auto">
      <table className="min-w-full bg-white">
        <thead className="bg-gray-50 text-xs uppercase">
          <tr>
            <th className="px-3 py-2 w-10">
              <input type="checkbox" onChange={toggleAll}
                checked={rows.length>0 && selected.length === rows.length}/>
            </th>
            {columns.map(col => (
              <th key={col.field} onClick={()=>handleSort(col)}
                  className={`px-3 py-2 text-left ${col.sortable?"cursor-pointer select-none":""}`}>
                {col.label}
                {col.sortable && (
                  <span className="ml-1 text-gray-400">
                    {ordering.replace("-", "") === (col.orderField || col.field)
                      ? (ordering.startsWith("-") ? "↓" : "↑")
                      : "↕"}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="text-sm">
          {rows.map((r)=>(
            <tr key={r.id} className="border-t hover:bg-gray-50">
              <td className="px-3 py-2">
                <input type="checkbox" checked={selected.includes(r.id)} onChange={()=>toggle(r.id)} />
              </td>
              {columns.map(col => (
                <td key={col.field} className="px-3 py-2">
                  {col.render ? col.render(r[col.field], r) : String(r[col.field] ?? "")}
                </td>
              ))}
            </tr>
          ))}
          {rows.length===0 && (
            <tr><td colSpan={columns.length+1} className="px-3 py-8 text-center text-gray-500">
              Sin resultados
            </td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
