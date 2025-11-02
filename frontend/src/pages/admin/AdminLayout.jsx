// frontend/src/pages/admin/AdminLayout.jsx
import { Link, NavLink } from "react-router-dom";
import { useEffect, useState } from "react";
import { obtenerPerfil } from "../../utils/api";

export default function AdminLayout({ title, breadcrumb = [], children }) {
  const [me, setMe] = useState(null);

  useEffect(() => {
    obtenerPerfil().then(r => setMe(r.data ?? r)).catch(()=>{});
  }, []);

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-md">
        <div className="px-4 py-4 border-b">
          <h1 className="text-lg font-bold">Nómina — Admin</h1>
          <p className="text-xs text-gray-500">Replica Django Admin</p>
        </div>
        <nav className="p-2 space-y-1">
          <Section label="Aplicaciones">
            <Item to="/admin/empleados">Empleados</Item>
            <Item to="/admin/conceptos">Conceptos</Item>
            <Item to="/admin/liquidaciones">Liquidaciones</Item>
            <Item to="/admin/asistencias">Asistencias</Item>
            <Item to="/admin/usuarios">Usuarios</Item>
          </Section>
          <Section label="Reportes">
            <Item to="/reportes">KPIs / Gráficos</Item>
          </Section>
        </nav>
      </aside>

      {/* Main */}
      <main className="flex-1">
        <header className="bg-white border-b px-6 py-3 flex items-center justify-between">
          <div>
            <div className="text-sm text-gray-500">
              {breadcrumb.map((b,i)=>(
                <span key={i}>
                  {i>0 && " / "}
                  {b.to ? <Link className="hover:underline" to={b.to}>{b.label}</Link> : b.label}
                </span>
              ))}
            </div>
            <h2 className="text-xl font-semibold">{title}</h2>
          </div>
          <div className="text-sm text-gray-600">
            {me ? (
              <span>👤 {me?.username || me?.email} — <strong>{(me.rol||"").toUpperCase()}</strong></span>
            ) : "Cargando…"}
          </div>
        </header>
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}

function Section({label, children}) {
  return (
    <div>
      <div className="px-2 text-[11px] uppercase text-gray-400 font-semibold">{label}</div>
      <div className="mt-1 space-y-1">{children}</div>
    </div>
  );
}
function Item({to, children}) {
  return (
    <NavLink
      to={to}
      className={({isActive}) =>
        `block px-3 py-2 rounded text-sm ${isActive ? "bg-blue-50 text-blue-700 font-medium" : "hover:bg-gray-50"}`
      }
    >
      {children}
    </NavLink>
  );
}
