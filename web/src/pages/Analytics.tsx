import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';

interface WidgetStat {
  name: string;
  type: string;
  total: number;
  actions: Record<string, number>;
}

interface AnalyticsData {
  widget_count: number;
  totals: Record<string, number>;
  by_widget: Record<string, WidgetStat>;
}

const ACTION_COLORS: Record<string, string> = {
  impression: '#6366f1',
  tap: '#22c55e',
  dismiss: '#ef4444',
  expand: '#f59e0b',
  link_click: '#06b6d4',
  other: '#71717a',
};

const ACTION_LABELS: Record<string, string> = {
  impression: 'Impression',
  tap: 'Tap',
  dismiss: 'Dismiss',
  expand: 'Expand',
  link_click: 'Link Click',
  other: 'Other',
};

export default function Analytics() {
  const apiKey = localStorage.getItem('intyx_api_key') || 'demo';
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/analytics/widgets`, {
          headers: { Authorization: `Bearer ${apiKey}` },
        });
        if (!res.ok) {
          const err: { error?: string } = await res.json().catch(() => ({}));
          throw new Error(err.error || `Request failed (${res.status})`);
        }
        const json: AnalyticsData = await res.json();
        setData(json);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, [apiKey]);

  if (loading) {
    return (
      <main id="main-content" style={styles.main}>
        <h1 style={styles.h1}>Analytics</h1>
        <div style={{ textAlign: 'center', padding: 60, color: 'var(--text-muted)' }}>Loading...</div>
      </main>
    );
  }

  if (error) {
    return (
      <main id="main-content" style={styles.main}>
        <h1 style={styles.h1}>Analytics</h1>
        <div role="alert" style={styles.errorBanner}>{error}</div>
      </main>
    );
  }

  const totals = data?.totals ?? {};
  const byWidget = data?.by_widget ?? {};
  const sortedWidgets = Object.entries(byWidget).sort(([, a], [, b]) => b.total - a.total);
  const topActions = ['impression', 'tap', 'dismiss', 'expand', 'link_click'].filter(
    (a) => (totals[a] ?? 0) > 0 || a === 'impression' || a === 'tap' || a === 'dismiss'
  );

  return (
    <main id="main-content" style={styles.main}>
      <h1 style={styles.h1}>Analytics</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 40 }}>
        Widget interaction data for your project.
      </p>

      {/* Summary cards */}
      <section aria-label="Summary statistics" style={styles.summaryGrid}>
        <div style={styles.statCard}>
          <div style={styles.statValue}>{data?.widget_count ?? 0}</div>
          <div style={styles.statLabel}>Total Widgets</div>
        </div>
        <div style={styles.statCard}>
          <div style={{ ...styles.statValue, color: '#6366f1' }}>{totals.impression ?? 0}</div>
          <div style={styles.statLabel}>Impressions</div>
        </div>
        <div style={styles.statCard}>
          <div style={{ ...styles.statValue, color: '#22c55e' }}>{totals.tap ?? 0}</div>
          <div style={styles.statLabel}>Taps</div>
        </div>
        <div style={styles.statCard}>
          <div style={{ ...styles.statValue, color: '#ef4444' }}>{totals.dismiss ?? 0}</div>
          <div style={styles.statLabel}>Dismisses</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statValue}>{totals.total ?? 0}</div>
          <div style={styles.statLabel}>Total Events</div>
        </div>
        <div style={styles.statCard}>
          <div style={{ ...styles.statValue, color: '#f59e0b' }}>
            {totals.impression
              ? `${Math.round(((totals.tap ?? 0) / totals.impression) * 100)}%`
              : '—'}
          </div>
          <div style={styles.statLabel}>CTR (Tap/Impression)</div>
        </div>
      </section>

      {/* Per-widget breakdown */}
      <section aria-labelledby="widget-breakdown-heading" style={{ marginTop: 40 }}>
        <h2 id="widget-breakdown-heading" style={styles.h2}>
          Widget Breakdown
          <span style={{ fontSize: 14, fontWeight: 400, color: 'var(--text-muted)', marginLeft: 8 }}>
            — sorted by total events
          </span>
        </h2>

        {sortedWidgets.length === 0 ? (
          <div style={{ ...styles.card, textAlign: 'center', padding: 48, color: 'var(--text-muted)' }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>📊</div>
            No interaction data yet. Widget events will appear here once users interact with your widgets.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {sortedWidgets.map(([widgetId, stat]) => {
              const maxCount = Math.max(...Object.values(stat.actions), 1);
              return (
                <div key={widgetId} style={styles.card}>
                  <div style={styles.widgetCardHeader}>
                    <div>
                      <div style={{ fontSize: 15, fontWeight: 600 }}>{stat.name}</div>
                      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                        <code style={{ fontSize: 11 }}>{widgetId}</code>
                        {' · '}
                        <span style={styles.typeBadge}>{stat.type}</span>
                      </div>
                    </div>
                    <div style={styles.totalBadge}>{stat.total} events</div>
                  </div>

                  {/* Action bars */}
                  {topActions.map((action) => {
                    const count = stat.actions[action] ?? 0;
                    const pct = Math.round((count / maxCount) * 100);
                    return (
                      <div key={action} style={styles.barRow}>
                        <div style={styles.barLabel}>
                          <span style={{ color: ACTION_COLORS[action] ?? '#aaa', marginRight: 6, fontSize: 13 }}>●</span>
                          {ACTION_LABELS[action] ?? action}
                        </div>
                        <div style={styles.barTrack}>
                          <div
                            style={{
                              ...styles.barFill,
                              width: `${pct}%`,
                              background: ACTION_COLORS[action] ?? '#6366f1',
                            }}
                          />
                        </div>
                        <div style={styles.barCount}>{count}</div>
                      </div>
                    );
                  })}
                </div>
              );
            })}
          </div>
        )}
      </section>

      <div style={{ height: 80 }} />
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  main: { maxWidth: 900, margin: '0 auto', padding: '60px 24px' },
  h1: { fontSize: 28, fontWeight: 800, marginBottom: 8 },
  h2: { fontSize: 20, fontWeight: 700, marginBottom: 20 },
  summaryGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
    gap: 12,
  },
  statCard: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: 20,
    textAlign: 'center',
  },
  statValue: { fontSize: 28, fontWeight: 800, marginBottom: 4 },
  statLabel: { fontSize: 13, color: 'var(--text-muted)' },
  card: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: 20,
  },
  widgetCardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  typeBadge: {
    fontSize: 11,
    fontWeight: 500,
    color: 'var(--primary)',
    background: 'var(--primary-muted)',
    padding: '2px 8px',
    borderRadius: 12,
  },
  totalBadge: {
    fontSize: 13,
    fontWeight: 700,
    color: 'var(--text-muted)',
    background: 'rgba(99,102,241,0.08)',
    padding: '4px 12px',
    borderRadius: 20,
    whiteSpace: 'nowrap',
  },
  barRow: {
    display: 'grid',
    gridTemplateColumns: '120px 1fr 48px',
    alignItems: 'center',
    gap: 12,
    marginBottom: 8,
  },
  barLabel: {
    fontSize: 13,
    color: 'var(--text-muted)',
    display: 'flex',
    alignItems: 'center',
  },
  barTrack: {
    height: 8,
    borderRadius: 4,
    background: 'rgba(255,255,255,0.06)',
    overflow: 'hidden',
  },
  barFill: {
    height: '100%',
    borderRadius: 4,
    transition: 'width 0.4s ease',
    minWidth: 2,
  },
  barCount: {
    fontSize: 13,
    fontWeight: 600,
    color: 'var(--text)',
    textAlign: 'right',
  },
  errorBanner: {
    padding: '12px 16px',
    background: 'rgba(239,68,68,0.1)',
    border: '1px solid rgba(239,68,68,0.3)',
    borderRadius: 8,
    color: '#ef4444',
    fontSize: 14,
  },
};
