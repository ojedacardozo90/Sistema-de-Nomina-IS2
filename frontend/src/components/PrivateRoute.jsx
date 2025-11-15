import { Navigate } from "react-router-dom";
import { getUser } from "../services/auth";

/**

 *  PrivateRoute
 * - Verifica si hay usuario logueado
 * - Opcionalmente filtra por roles permitidos

 */
export default function PrivateRoute({ children, allowedRoles }) {
  const user = getUser();

  if (!user) {
    // No autenticado
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.rol)) {
    // Rol no autorizado
    return <Navigate to="/no-autorizado" replace />;
  }

  return children;
}
