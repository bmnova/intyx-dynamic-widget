import { useState } from 'react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const apiKey = localStorage.getItem('intyx_api_key');
  const plan = localStorage.getItem('intyx_plan');
  const purchasedAt = localStorage.getItem('intyx_purchased_at');
  const [copied, setCopied] = useState(false);

  if (!apiKey) {
    return (
      <div style={{ maxWidth: 600, margin: '0 auto', padding: '80px 24px', textAlign: 'center' }}>
        <div style={{ fontSize: 48, marginBottom: 24 }}>🔒</div>
        <h2 style={{ fontSize: 24, fontWeight: 700, marginBottom: 12 }}>Henuz paket almadiniz</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>
          Widget sistemini kullanmak icin bir paket secin ve API key'inizi alin.
        </p>
        <Link to="/pricing" style={styles.btnPrimary}>Paketleri Incele →</Link>
      </div>
    );
  }

  const copyKey = () => {
    navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const planLabel = { starter: 'Starter', pro: 'Pro', enterprise: 'Enterprise' }[plan] || plan;

  return (
    <div style={{ maxWidth: 800, margin: '0 auto', padding: '60px 24px' }}>
      <h1 style={{ fontSize: 28, fontWeight: 800, marginBottom: 8 }}>Dashboard</h1>
      <p style={{ color: 'var(--text-muted)', marginBottom: 40 }}>
        API key'inizi Flutter projenizde kullanarak widget sistemini aktif edin.
      </p>

      {/* Plan info */}
      <div style={styles.card}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 4 }}>Aktif Paket</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{planLabel}</div>
          </div>
          <span style={styles.activeBadge}>Aktif</span>
        </div>
        {purchasedAt && (
          <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 8 }}>
            Baslangic: {new Date(purchasedAt).toLocaleDateString('tr-TR')}
          </div>
        )}
      </div>

      {/* API Key */}
      <div style={{ ...styles.card, marginTop: 16 }}>
        <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 12 }}>API Key</div>
        <div style={styles.keyRow}>
          <code style={styles.keyCode}>{apiKey}</code>
          <button onClick={copyKey} style={styles.copyBtn}>
            {copied ? '✓ Kopyalandi' : 'Kopyala'}
          </button>
        </div>
        <p style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 12 }}>
          Bu key'i kimseyle paylasmayın. Her key tek bir projeye aittir.
        </p>
      </div>

      {/* Integration guide */}
      <div style={{ ...styles.card, marginTop: 16 }}>
        <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Flutter Entegrasyonu</h3>

        <div style={styles.step}>
          <span style={styles.stepNum}>1</span>
          <div>
            <div style={styles.stepTitle}>pubspec.yaml'a ekle</div>
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
            <div style={styles.stepTitle}>Uygulamanda initialize et</div>
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
            <div style={styles.stepTitle}>Widget'i yerlestir</div>
            <pre style={styles.codeBlock}>{`DynamicWidgetContainer(
  responseJson: agentResponse,
  colorScheme: Theme.of(context).colorScheme,
  padding: EdgeInsets.all(12),
  onDismiss: (id) => print('dismissed: \$id'),
  onAction: (id, action) => handleAction(action),
)`}</pre>
          </div>
        </div>
      </div>

      {/* Quick stats placeholder */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginTop: 16 }}>
        <div style={styles.statCard}>
          <div style={styles.statValue}>0</div>
          <div style={styles.statLabel}>Widget Gosterim</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statValue}>0</div>
          <div style={styles.statLabel}>Etkilesim</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statValue}>0</div>
          <div style={styles.statLabel}>Aktif Kullanici</div>
        </div>
      </div>

      <div style={{ height: 80 }} />
    </div>
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
