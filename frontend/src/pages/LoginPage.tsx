/**
 * Login Page — JWT authentication form.
 */

import { useState } from 'react';
import axios from 'axios';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const API_BASE = import.meta.env.VITE_API_URL || '';
      const { data } = await axios.post(`${API_BASE}/api/v1/auth/login`, new URLSearchParams({
        username: email,
        password,
      }));
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      window.location.href = '/';
    } catch {
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: 'hsl(222 47% 6%)',
    }}>
      <div style={{
        width: 380,
        padding: '2.5rem',
        backgroundColor: 'hsl(222 47% 8%)',
        borderRadius: 12,
        border: '1px solid hsl(217 33% 17%)',
      }}>
        <h1 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'hsl(217 91% 60%)', marginBottom: 4 }}>
          PV Compliance
        </h1>
        <p style={{ color: 'hsl(215 20% 65%)', fontSize: '0.8rem', marginBottom: '1.5rem' }}>
          Regulatory Scheduling Intelligence System
        </p>

        <form onSubmit={handleLogin}>
          <label style={{ fontSize: '0.8rem', color: 'hsl(215 20% 65%)' }}>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '0.6rem',
              borderRadius: 6,
              border: '1px solid hsl(217 33% 17%)',
              backgroundColor: 'hsl(222 47% 6%)',
              color: 'white',
              fontSize: '0.85rem',
              marginTop: 4,
              marginBottom: '0.75rem',
              outline: 'none',
              boxSizing: 'border-box',
            }}
          />

          <label style={{ fontSize: '0.8rem', color: 'hsl(215 20% 65%)' }}>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{
              width: '100%',
              padding: '0.6rem',
              borderRadius: 6,
              border: '1px solid hsl(217 33% 17%)',
              backgroundColor: 'hsl(222 47% 6%)',
              color: 'white',
              fontSize: '0.85rem',
              marginTop: 4,
              marginBottom: '1rem',
              outline: 'none',
              boxSizing: 'border-box',
            }}
          />

          {error && <p style={{ color: 'hsl(0 62% 50%)', fontSize: '0.8rem', marginBottom: '0.75rem' }}>{error}</p>}

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '0.65rem',
              borderRadius: 6,
              border: 'none',
              backgroundColor: 'hsl(217 91% 60%)',
              color: 'white',
              fontSize: '0.85rem',
              fontWeight: 600,
              cursor: loading ? 'wait' : 'pointer',
              opacity: loading ? 0.7 : 1,
            }}
          >
            {loading ? 'Signing in…' : 'Sign In'}
          </button>
        </form>

        <p style={{ marginTop: '1rem', fontSize: '0.7rem', color: 'hsl(215 20% 55%)', textAlign: 'center' }}>
          Demo: admin@pvcompli.com / admin123
        </p>
      </div>
    </div>
  );
}
