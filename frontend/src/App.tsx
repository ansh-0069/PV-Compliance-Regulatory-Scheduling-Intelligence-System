/**
 * Root application component.
 *
 * Defines all page routes and wraps them in the AppShell layout.
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import AppShell from './components/layout/AppShell';
import DashboardPage from './pages/DashboardPage';
import SubmissionsPage from './pages/SubmissionsPage';
import QCPage from './pages/QCPage';
import CAPAPage from './pages/CAPAPage';
import AuditPage from './pages/AuditPage';
import CopilotPage from './pages/CopilotPage';
import LoginPage from './pages/LoginPage';

function App() {
  const isAuthenticated = !!localStorage.getItem('access_token');

  if (!isAuthenticated) {
    return (
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/submissions" element={<SubmissionsPage />} />
        <Route path="/qc" element={<QCPage />} />
        <Route path="/capas" element={<CAPAPage />} />
        <Route path="/audit" element={<AuditPage />} />
        <Route path="/copilot" element={<CopilotPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppShell>
  );
}

export default App;
