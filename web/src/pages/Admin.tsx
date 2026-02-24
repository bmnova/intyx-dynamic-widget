import { useState, useEffect, useCallback } from 'react';
import { API_BASE_URL, ADMIN_SECRET } from '../config';
import type { AdminStats, AdminLicense, Plan } from '../types';

const PLAN_COLORS: Record<Plan, string> = {
  starter: '#a1a1aa',
  pro: '#6366f1',
  enterprise: '#f59e0b',
};

export default function Admin() {
  const [secret, setSecret] = useState(
    ADMIN_SECRET || sessionStorage.getItem('intyx_admin_secret') || ''
  );
  const [authed, setAuthed] = useState(false);
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [licenses, setLicenses] = useState<AdminLicense[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const authHeaders = useCallback(
    () => ({
      'Content-Type': 'application/json',
      Authorization: `Bearer ${secret}`,
    }),
    [secret]
  );

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, licRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/admin/stats`, { headers: authHeaders() }),
        fetch(`${API_BASE_URL}/api/admin/licenses?limit=100`, { headers: authHeaders() }),
      ]);
      if (statsRes.status === 403 || licRes.status === 403) {
        setError('Invalid admin key — check VITE_ADMIN_SECRET / INTYX_SERVER_API_KEY');
        setAuthed(false);
        return;
      }
      if (!statsRes.ok || !licRes.ok) throw new Error('Server error');
      const [statsData, licData] = await Promise.all([
        statsRes.json() as Promise<AdminStats>,
        licRes.json() as Promise<{ licenses: AdminLicense[] }>,
      ]);
      setStats(statsData);
      setLicenses(licData.licenses || []);
      setAuthed(true);
      sessionStorage.setItem('intyx_admin_secret', secret);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [secret, authHeaders]);

  // Auto-fetch if secret pre-filled from env
  useEffect(() => {
    if (secret && !authed) fetchData();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!authed) {
    return (
      <main id="main-content" style={{ maxWidth: 400, margin: '120px auto', padding: '0 24px' }}>
        <h1 style={{ fontSize: 24, fontWeight: 800, marginBottom: 8 }}>Admin</h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: 24, fontSize: 14 }}>
          Enter the server API key to access the admin dashboard.
        </p>
        {error && (
          <div role="alert" style={styles.errorBanner}>{error}</div>
        )}
        <form
          onSubmit={(e) => { e.preventDefault(); fetchData(); }}
          style={{ display: 'flex', flexDirection: 'column', gap: 12 }}
        >
          <label htmlFor="admin-secret" style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            Admin Secret Key
          </label>
          <input
            id="admin-secret"
            type="password"
            value={secret}
            onChange={(e) => setSecret(e.target.value)}
            placeholder="INTYX_SERVER_API_KEY value"
            autoComplete="current-password"
            style={styles.input}
          />
          <button type="submit" disabled={!secret || loading} style={styles.btnPrimary}>
            {loading ? 'Connecting…' : 'Sign in'}
          </button>
        </form>
      </main>
    );
  }

  const planOrder: Plan[] = ['starter', 'pro', 'enterprise'];

  return (
    <main id="main-content" style={{ maxWidth: 1000, margin: '0 auto', padding: '60px 24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32 }}>
        <h1 style={{ fontSize: 28, fontWeight: 800 }}>Admin Dashboard</h1>
        <button
          onClick={() => { setAuthed(false); sessionStorage.removeItem('intyx_admin_secret'); }}
          style={styles.btnGhost}
        >
          Sign out
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <section aria-labelledby="stats-heading" style={{ marginBottom: 32 }}>
          <h2 id="stats-heading" style={styles.sectionHeading}>Overview</h2>
          <div style={styles.statsGrid}>
            <div style={styles.statCard}>
              <div style={styles.statValue}>{stats.total_licenses}</div>
              <div style={styles.statLabel}>Total Licenses</div>
            </div>
            <div style={styles.statCard}>
              <div style={{ ...styles.statValue, color: '#22c55e' }}>{stats.active_licenses}</div>
              <div style={styles.statLabel}>Active</div>
            </div>
            {planOrder.map((plan) => (
              <div key={plan} style={styles.statCard}>
                <div style={{ ...styles.statValue, color: PLAN_COLORS[plan] ?? 'var(--text)' }}>
                  {stats.by_plan?.[plan] ?? 0}
                </div>
                <div style={styles.statLabel}>{plan.charAt(0).toUpperCase() + plan.slice(1)}</div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Licenses table */}
      <section aria-labelledby="licenses-heading">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
          <h2 id="licenses-heading" style={styles.sectionHeading}>Licenses ({licenses.length})</h2>
          <button onClick={fetchData} disabled={loading} style={styles.btnGhost}>
            {loading ? 'Refreshing…' : '↺ Refresh'}
          </button>
        </div>

        {error && <div role="alert" style={styles.errorBanner}>{error}</div>}

        <div style={styles.tableWrap}>
          <table aria-label="License list" style={styles.table}>
            <thead>
              <tr>
                {['API Key', 'Plan', 'Email', 'Status', 'Created'].map((col) => (
                  <th key={col} scope="col" style={styles.th}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {licenses.length === 0 && (
                <tr>
                  <td colSpan={5} style={{ ...styles.td, textAlign: 'center', color: 'var(--text-muted)' }}>
                    No licenses found
                  </td>
                </tr>
              )}
              {licenses.map((lic, i) => (
                <tr key={i} style={{ opacity: lic.active ? 1 : 0.5 }}>
                  <td style={styles.td}>
                    <code style={{ fontSize: 12 }}>{lic.api_key_masked}</code>
                  </td>
                  <td style={styles.td}>
                    <span style={{
                      ...styles.planBadge,
                      color: PLAN_COLORS[lic.plan] ?? 'var(--text-muted)',
                      background: `${PLAN_COLORS[lic.plan] ?? '#aaa'}18`,
                    }}>
                      {lic.plan}
                    </span>
                  </td>
                  <td style={{ ...styles.td, color: 'var(--text-muted)', fontSize: 13 }}>
                    {lic.email || '—'}
                  </td>
                  <td style={styles.td}>
                    <span style={{ color: lic.active ? '#22c55e' : '#ef4444', fontSize: 13, fontWeight: 600 }}>
                      {lic.active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td style={{ ...styles.td, color: 'var(--text-muted)', fontSize: 12 }}>
                    {lic.created_at
                      ? new Date(lic.created_at * 1000).toLocaleDateString()
                      : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div style={{ height: 80 }} />
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  sectionHeading: { fontSize: 18, fontWeight: 700, marginBottom: 16 },
  statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: 12 },
  statCard: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: 20, textAlign: 'center' },
  statValue: { fontSize: 32, fontWeight: 800, marginBottom: 4 },
  statLabel: { fontSize: 13, color: 'var(--text-muted)' },
  tableWrap: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', overflow: 'auto' },
  table: { width: '100%', borderCollapse: 'collapse' },
  th: { padding: '12px 16px', fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textAlign: 'left', borderBottom: '1px solid var(--border)', whiteSpace: 'nowrap' },
  td: { padding: '12px 16px', fontSize: 14, borderBottom: '1px solid var(--border)' },
  planBadge: { fontSize: 11, fontWeight: 700, padding: '3px 10px', borderRadius: 12 },
  input: { width: '100%', padding: '10px 14px', fontSize: 14, background: '#0c0c0e', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text)', outline: 'none', boxSizing: 'border-box' },
  btnPrimary: { padding: '11px 0', fontSize: 14, fontWeight: 600, color: '#fff', background: '#6366f1', border: 'none', borderRadius: 8, cursor: 'pointer' },
  btnGhost: { padding: '8px 16px', fontSize: 13, fontWeight: 500, color: 'var(--text-muted)', background: 'transparent', border: '1px solid var(--border)', borderRadius: 8, cursor: 'pointer' },
  errorBanner: { padding: '10px 16px', marginBottom: 16, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8, color: '#ef4444', fontSize: 14 },
};
