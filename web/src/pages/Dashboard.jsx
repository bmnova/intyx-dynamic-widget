import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from '../config';

export default function Dashboard() {
  const apiKey = localStorage.getItem('intyx_api_key') || 'demo';
  const purchasedAt = localStorage.getItem('intyx_purchased_at');
  const [copied, setCopied] = useState(false);
  const [licenseInfo, setLicenseInfo] = useState(null);
  const [validating, setValidating] = useState(!!apiKey);

  useEffect(() => {
    if (!apiKey) return;
    const validate = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/licenses/validate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ api_key: apiKey }),
        });
        if (res.ok) {
          const data = await res.json();
          if (data.valid) {
            setLicenseInfo(data);
            localStorage.setItem('intyx_plan', data.plan);
          }
        }
      } catch (err) {
        console.error('License validation failed:', err);
      } finally {
        setValidating(false);
      }
    };
    validate();
  }, []);

  const plan = licenseInfo?.plan || localStorage.getItem('intyx_plan');

  if (!apiKey) {
    return (
      <main id="main-content" style={{ maxWidth: 600, margin: '0 auto', padding: '80px 24px', textAlign: 'center' }}>
        <div aria-hidden="true" style={{ fontSize: 48, marginBottom: 24 }}>🔒</div>
        <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 12 }}>No plan selected yet</h1>
        <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>
          Choose a plan and get your API key to use the widget system.
        </p>
        <Link to="/pricing" style={styles.btnPrimary}>View Plans →</Link>
      </main>
    );
  }

  const copyKey = () => {
    navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const planLabel = { starter: 'Starter', pro: 'Pro', enterprise: 'Enterprise' }[plan] || plan;

  return (
    <main id="main-content" style={{ maxWidth: 800, margin: '0 auto', padding: '60px 24px' }}>
      <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8 }}>Dashboard</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 40 }}>
        Use your API key in your Flutter project to enable the widget system.
      </p>

      {/* Plan info */}
      <section aria-label="Active plan" style={styles.card}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 4 }}>Active Plan</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{planLabel}</div>
          </div>
          <span style={styles.activeBadge}>Active</span>
        </div>
        {purchasedAt && (
          <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 8 }}>
            Started: {new Date(purchasedAt).toLocaleDateString()}
          </div>
        )}
      </section>

      {/* API Key */}
      <section aria-label="API key" style={{ ...styles.card, marginTop: 16 }}>
        <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 12 }}>API Key</div>
        <div style={styles.keyRow}>
          <code aria-label="Your API key" style={styles.keyCode}>{apiKey}</code>
          <button
            onClick={copyKey}
            aria-label={copied ? 'API key copied to clipboard' : 'Copy API key to clipboard'}
            aria-live="polite"
            style={styles.copyBtn}
          >
            {copied ? '✓ Copied' : 'Copy'}
          </button>
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 12 }}>
          Do not share this key. Each key is tied to a single project.
        </p>
      </section>

      {/* Integration guide */}
      <section aria-labelledby="integration-heading" style={{ ...styles.card, marginTop: 16 }}>
        <h2 id="integration-heading" style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Flutter Integration</h2>

        <div style={styles.step}>
          <span style={styles.stepNum}>1</span>
          <div>
            <div style={styles.stepTitle}>Add to pubspec.yaml</div>
            <pre style={styles.codeBlock}>{`dependencies:
  intyx_dynamic_widget:
    git:
      url: https://github.com/bmnova/intyx-dynamic-widget
      path: flutter_client`}</pre>
          </div>
        </div>

        <div style={styles.step}>
          <span style={styles.stepNum}>2</span>
          <div>
            <div style={styles.stepTitle}>Initialize in your app</div>
            <pre style={styles.codeBlock}>{`import 'package:intyx_dynamic_widget/intyx_dynamic_widget.dart';

void main() {
  IntyxDynamicWidget.init(
    apiKey: '${apiKey}',
  );
  registerDefaultWidgets();
  runApp(MyApp());
}`}</pre>
          </div>
        </div>

        <div style={styles.step}>
          <span style={styles.stepNum}>3</span>
          <div>
            <div style={styles.stepTitle}>Place the widget</div>
            <pre style={styles.codeBlock}>{`DynamicWidgetContainer(
  responseJson: agentResponse,
  colorScheme: Theme.of(context).colorScheme,
  padding: EdgeInsets.all(12),
  onDismiss: (id) => print('dismissed: \$id'),
  onAction: (id, action) => handleAction(action),
)`}</pre>
          </div>
        </div>
      </section>

      {/* Quick actions */}
      <nav aria-label="Quick actions" style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16, marginTop: 16 }}>
        <Link to="/widget-studio" style={{ ...styles.actionCard, textDecoration: 'none', color: 'inherit' }}>
          <div aria-hidden="true" style={{ fontSize: 28, marginBottom: 8 }}>🎨</div>
          <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>Widget Studio</div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            Select widget types, write prompts, preview AI-generated widgets
          </div>
        </Link>
        <Link to="/agent-tasks" style={{ ...styles.actionCard, textDecoration: 'none', color: 'inherit' }}>
          <div aria-hidden="true" style={{ fontSize: 28, marginBottom: 8 }}>🤖</div>
          <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 4 }}>Agent Tasks</div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
            Create reusable AI tasks for automatic widget generation
          </div>
        </Link>
      </nav>

      {/* Quick stats placeholder */}
      <section aria-label="Usage statistics" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginTop: 16 }}>
        <div style={styles.statCard}>
          <div style={styles.statValue}>0</div>
          <div style={styles.statLabel}>Widget Views</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statValue}>0</div>
          <div style={styles.statLabel}>Interactions</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statValue}>0</div>
          <div style={styles.statLabel}>Active Users</div>
        </div>
      </section>

      <div style={{ height: 80 }} />
    </main>
  );
}

const styles = {
  btnPrimary: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '12px 28px',
    fontSize: 15,
    fontWeight: 600,
    color: '#fff',
    background: '#6366f1',
    borderRadius: 8,
    border: 'none',
  },
  card: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: 24,
  },
  activeBadge: {
    fontSize: 13,
    fontWeight: 600,
    color: '#22c55e',
    background: 'rgba(34,197,94,0.12)',
    padding: '4px 14px',
    borderRadius: 20,
  },
  keyRow: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
  },
  keyCode: {
    flex: 1,
    background: '#0c0c0e',
    border: '1px solid var(--border)',
    borderRadius: 8,
    padding: '10px 16px',
    fontSize: 14,
    color: '#c4b5fd',
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
    userSelect: 'all',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  copyBtn: {
    padding: '10px 20px',
    fontSize: 13,
    fontWeight: 600,
    background: 'var(--bg-card-hover)',
    color: 'var(--text)',
    border: '1px solid var(--border)',
    borderRadius: 8,
    whiteSpace: 'nowrap',
  },
  step: {
    display: 'flex',
    gap: 16,
    marginBottom: 24,
  },
  stepNum: {
    width: 28,
    height: 28,
    minWidth: 28,
    borderRadius: '50%',
    background: 'var(--primary-muted)',
    color: '#6366f1',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 13,
    fontWeight: 700,
    marginTop: 2,
  },
  stepTitle: {
    fontSize: 14,
    fontWeight: 600,
    marginBottom: 8,
  },
  codeBlock: {
    background: '#0c0c0e',
    border: '1px solid var(--border)',
    borderRadius: 8,
    padding: '14px 18px',
    fontSize: 13,
    lineHeight: 1.6,
    color: '#c4b5fd',
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
    overflow: 'auto',
    whiteSpace: 'pre',
    margin: 0,
  },
  actionCard: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: 24,
    transition: 'border-color 0.2s',
    cursor: 'pointer',
  },
  statCard: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: 20,
    textAlign: 'center',
  },
  statValue: {
    fontSize: 28,
    fontWeight: 800,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 13,
    color: 'var(--text-muted)',
  },
};
