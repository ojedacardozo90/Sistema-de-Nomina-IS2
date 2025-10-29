export default function NoAutorizado() {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-50">
      <h1 className="text-6xl font-bold text-red-600 mb-4">🚫 Acceso denegado</h1>
      <p className="text-gray-700 text-lg mb-6">
        No tienes permisos para acceder a esta sección del sistema.
      </p>
      <a
        href="/"
        className="bg-emerald-600 text-white px-6 py-3 rounded-lg hover:bg-emerald-700 transition"
      >
        Volver al inicio
      </a>
    </div>
  );
}
