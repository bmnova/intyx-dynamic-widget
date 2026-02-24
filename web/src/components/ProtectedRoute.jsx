import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const apiKey = localStorage.getItem('intyx_api_key');

  // Allow access without API key in Vite dev mode OR when Paddle is not configured
  // (no payment integration = demo / self-hosted setup)
  const devMode = import.meta.env.DEV;
  const paddleConfigured = !!import.meta.env.VITE_PADDLE_PUBLISHABLE_TOKEN;

  if (!apiKey && !devMode && paddleConfigured) {
    return <Navigate to="/pricing" replace />;
  }

  return children;
}
