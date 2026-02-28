import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Landing from './pages/Landing';
import Pricing from './pages/Pricing';
import Dashboard from './pages/Dashboard';
import AgentTasks from './pages/AgentTasks';
import WidgetStudio from './pages/WidgetStudio';
import Admin from './pages/Admin';
import Analytics from './pages/Analytics';
import Integrations from './pages/Integrations';
import Developers from './pages/Developers';
import Product from './pages/Product';
import LiveEventSignup from './pages/LiveEventSignup';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/live" element={<LiveEventSignup />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/widget-studio"
          element={
            <ProtectedRoute>
              <WidgetStudio />
            </ProtectedRoute>
          }
        />
        <Route
          path="/agent-tasks"
          element={
            <ProtectedRoute>
              <AgentTasks />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics"
          element={
            <ProtectedRoute>
              <Analytics />
            </ProtectedRoute>
          }
        />
        <Route path="/integrations" element={<Integrations />} />
        <Route path="/developers" element={<Developers />} />
        <Route path="/product" element={<Product />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </>
  );
}
