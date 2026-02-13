import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Landing from './pages/Landing';
import Pricing from './pages/Pricing';
import Dashboard from './pages/Dashboard';
import AgentTasks from './pages/AgentTasks';
import WidgetStudio from './pages/WidgetStudio';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Landing />} />
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
        <Route path="*" element={<NotFound />} />
      </Routes>
    </>
  );
}
