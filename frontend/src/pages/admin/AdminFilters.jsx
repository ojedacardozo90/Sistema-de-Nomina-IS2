// src/pages/admin/AdminFilters.jsx
import { useEffect, useState } from "react";

const FILTERS_BY_MODEL = {
  "empleados": [
    { name: "activo", label: "Activo", type: "select", options: [
      { value: "", label: "Todos" }, { value: "true", label: "Sí" }, { value: "false", label: "No" },
    ]},
    { name: "area", label: "Área", type: "text" },
    { name: "cargo", label: "Cargo", type: "text" },
  ],
  "nomina_cal/liquidaciones": [
    { name: "anio", label: "Año", type: "number" },
    { name: "mes", label: "Mes", type: "number" },
    { name: "empleado__cedula", label: "Cédula", type: "text" },
  ],
  "nomina_cal/conceptos": [
    { name: "es_debito", label: "Tipo", type: "select", options: [
      { value: "", label: "Todos" }, { value: "true", label: "Débito" }, { value: "false", label: "Crédito" },
    ]},
    { name: "afecta_ips", label: "Afecta IPS", type: "select", options: [
      { value: "", label: "Todos" }, { value: "true", label: "Sí" }, { value: "false", label: "No" },
    ]},
  ],
  "asistencia/asistencias": [
    { name: "tipo", label: "Tipo", type: "select", options: [
      { value: "", label: "Todos" }, { value: "ENTRADA", label: "Entrada" }, { value: "SALIDA", label: "Salida" },
    ]},
    { name: "fecha", label: "Fecha", type: "date" },
  ],
  "usuarios/usuarios": [
    { name: "rol", label: "Rol", type: "select", options: [
      { value: "", label: "Todos" },
      { value: "admin", label: "Admin" },
      { value: "gerente_rrhh", label: "Gerente RRHH" },
      { value: "asistente_rrhh", label: "Asistente RRHH" },
      { value: "empleado", label: "Empleado" },
    ]},
    { name: "is_active", label: "Activo", type: "select", options: [
      { value: "", label: "Todos" }, { value: "true", label: "Sí" }, { value: "false", label: "No" },
    ]},
  ],
};

export default function AdminFilters({ model, values, onChange, onClear }) {
  const [fields, setFields] = useState([]);

  useEffect(() => {
    setFields(FILTERS_BY_MODEL[model] || []);
  }, [model]);

  return (
    <div className="bg-white border-b p-3 flex flex-wrap gap-3 items-end">
      {fields.map((f) => (
        <div key={f.name} className="flex flex-col">
          <label className="text-xs text-gray-500">{f.label}</label>
          {f.type === "select" ? (
            <select
              value={values[f.name] ?? ""}
              onChange={(e) => onChange({ ...values, [f.name]: e.target.value })}
              className="border rounded px-2 py-1 text-sm"
            >
              {f.options.map((op) => (
                <option key={op.value} value={op.value}>{op.label}</option>
              ))}
            </select>
          ) : (
            <input
              type={f.type}
              value={values[f.name] ?? ""}
              onChange={(e) => onChange({ ...values, [f.name]: e.target.value })}
              className="border rounded px-2 py-1 text-sm"
            />
          )}
        </div>
      ))}
      <button
        onClick={() => onClear()}
        className="ml-auto bg-gray-200 hover:bg-gray-300 px-3 py-1 rounded text-sm"
      >
        Limpiar
      </button>
    </div>
  );
}


// frontend/src/pages/admin/AdminFilters.jsx
export default function AdminFilters({ items=[], values={}, onChange, onSearch, search, setSearch }) {
  return (
    <div className="bg-white border rounded p-3 flex flex-wrap gap-2 items-end">
      <div>
        <label className="text-xs text-gray-500">Buscar</label>
        <input
          value={search} onChange={e=>setSearch(e.target.value)}
          onKeyDown={e=>e.key==="Enter"&&onSearch?.()}
          placeholder="nombre, cédula…"
          className="border rounded p-1 w-64 block"
        />
      </div>
      {items.map((f)=>(
        <div key={f.name}>
          <label className="text-xs text-gray-500">{f.label}</label>
          {f.type==="select" ? (
            <select
              className="border rounded p-1 min-w-[160px] block"
              value={values[f.name] ?? ""}
              onChange={e=>onChange({ ...values, [f.name]: e.target.value })}>
              <option value="">Todos</option>
              {f.options.map(o=><option key={o.value} value={o.value}>{o.label}</option>)}
            </select>
          ) : (
            <input
              type={f.type||"text"}
              className="border rounded p-1 min-w-[160px] block"
              value={values[f.name] ?? ""}
              onChange={e=>onChange({ ...values, [f.name]: e.target.value })}
            />
          )}
        </div>
      ))}
      <button className="ml-auto bg-blue-600 text-white px-3 py-2 rounded" onClick={onSearch}>
        Aplicar
      </button>
    </div>
  );
}
