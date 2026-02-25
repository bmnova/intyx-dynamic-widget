import { Navigate } from 'react-router-dom';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const apiKey = localStorage.getItem('intyx_api_key');

  // Auth gate is opt-in: only enforce when VITE_REQUIRE_AUTH=true is explicitly set.
  const requireAuth = import.meta.env.VITE_REQUIRE_AUTH === 'true';

  if (requireAuth && !apiKey) {
    return <Navigate to="/pricing" replace />;
  }

  return <>{children}</>;
}
