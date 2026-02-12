import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const apiKey = localStorage.getItem('intyx_api_key');

  if (!apiKey) {
    return <Navigate to="/pricing" replace />;
  }

  return children;
}
