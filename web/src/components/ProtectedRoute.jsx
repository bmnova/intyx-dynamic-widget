import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const apiKey = localStorage.getItem('intyx_api_key');

  // Auth gate is opt-in: only enforce when VITE_REQUIRE_AUTH=true is explicitly set.
  // This lets demo / self-hosted deployments work without a Paddle integration.
  const requireAuth = import.meta.env.VITE_REQUIRE_AUTH === 'true';

  if (requireAuth && !apiKey) {
    return <Navigate to="/pricing" replace />;
  }

  return children;
}
