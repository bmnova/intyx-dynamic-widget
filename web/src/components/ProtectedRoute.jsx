import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const apiKey = localStorage.getItem('intyx_api_key');

  // In Vite dev mode allow access without API key so pages can be tested
  const devMode = import.meta.env.DEV;

  if (!apiKey && !devMode) {
    return <Navigate to="/pricing" replace />;
  }

  return children;
}
