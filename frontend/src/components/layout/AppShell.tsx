/**
 * AppShell — main layout with sidebar navigation and header.
 *
 * All authenticated pages render inside this shell.
 */

import { ReactNode } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  CalendarClock,
  CheckCircle2,
  AlertTriangle,
  Shield,
  Bot,
  LogOut,
} from 'lucide-react';

const navItems = [
  { path: '/',             icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/submissions',  icon: CalendarClock,   label: 'Submissions' },
  { path: '/qc',           icon: CheckCircle2,    label: 'QC Checks' },
  { path: '/capas',        icon: AlertTriangle,   label: 'CAPAs' },
  { path: '/audit',        icon: Shield,          label: 'Audit' },
  { path: '/copilot',      icon: Bot,             label: 'Copilot' },
];

interface AppShellProps {
  children: ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    navigate('/login');
    window.location.reload();
  };

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* Sidebar */}
      <aside
        style={{
          width: 240,
          backgroundColor: 'hsl(222 47% 8%)',
          borderRight: '1px solid hsl(217 33% 17%)',
          display: 'flex',
          flexDirection: 'column',
          padding: '1rem 0',
        }}
      >
        {/* Logo */}
        <div style={{ padding: '0 1.25rem 1.5rem', borderBottom: '1px solid hsl(217 33% 17%)' }}>
          <h1 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'hsl(217 91% 60%)' }}>
            PV Compliance
          </h1>
          <p style={{ fontSize: '0.7rem', color: 'hsl(215 20% 65%)', marginTop: 2 }}>
            Regulatory Intelligence
          </p>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: '0.75rem 0.5rem' }}>
          {navItems.map(({ path, icon: Icon, label }) => {
            const active = location.pathname === path;
            return (
              <Link
                key={path}
                to={path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '0.6rem 0.75rem',
                  borderRadius: 6,
                  marginBottom: 2,
                  fontSize: '0.85rem',
                  fontWeight: active ? 600 : 400,
                  color: active ? 'hsl(210 40% 98%)' : 'hsl(215 20% 65%)',
                  backgroundColor: active ? 'hsl(217 33% 17%)' : 'transparent',
                  textDecoration: 'none',
                  transition: 'all 0.15s',
                }}
              >
                <Icon size={18} />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* Logout */}
        <div style={{ padding: '0 0.5rem' }}>
          <button
            onClick={handleLogout}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 10,
              padding: '0.6rem 0.75rem',
              borderRadius: 6,
              fontSize: '0.85rem',
              color: 'hsl(215 20% 65%)',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              width: '100%',
            }}
          >
            <LogOut size={18} />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main style={{ flex: 1, overflow: 'auto', padding: '2rem' }}>
        {children}
      </main>
    </div>
  );
}
