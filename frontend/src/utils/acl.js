// src/utils/acl.js
export function canUseAdmin(user) {
  if (!user) return false;
  const rol = String(user.rol || "").toUpperCase();
  return ["ADMIN", "GERENTE", "GERENTE_RRHH"].includes(rol);
}
