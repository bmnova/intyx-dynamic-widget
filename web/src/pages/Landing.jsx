import { Link } from 'react-router-dom';
import WidgetCard from '../components/WidgetCard';

const WIDGETS = [
  { icon: '🖼️', title: 'Hero Image', description: 'Full-width hero image, overlay title and CTA button', tag: 'UI' },
  { icon: '🏷️', title: 'Promotional', description: 'Campaign/promo card — badge, discount, action', tag: 'Campaign' },
  { icon: '🎠', title: 'Carousel', description: 'Horizontal scrollable multi-content cards', tag: 'UI' },
  { icon: '⏱️', title: 'Countdown Banner', description: 'Campaign banner with countdown timer', tag: 'Campaign' },
  { icon: '☁️', title: 'Contextual', description: 'Contextual info card (weather, horoscope, etc.)', tag: 'AI Driven' },
  { icon: '📢', title: 'Informational', description: 'Info and announcement card with severity support', tag: 'Notice' },
  { icon: '⚡', title: 'Functional', description: 'Action-focused card — buttons and deep link', tag: 'Action' },
  { icon: '🔗', title: 'Clickable Image', description: 'Clickable image, title and redirect link', tag: 'UI' },
  { icon: '📝', title: 'Title + Subtitle', description: 'Card with title, subtitle and image', tag: 'UI' },
  { icon: '🎯', title: 'Icon Text Action', description: 'Icon, title, description and action button', tag: 'Action' },
];

const FEATURES = [
  { icon: '🤖', title: 'AI Agent Decisions', desc: 'The AI agent decides which widget appears where. Automatic selection based on context.' },
  { icon: '🎨', title: 'ColorScheme Match', desc: 'Pass your app\'s ColorScheme as a parameter; widgets adapt automatically.' },
  { icon: '📐', title: 'Responsive Layout', desc: 'Width, height, padding, margin, aspect ratio — all configurable via JSON.' },
  { icon: '🔥', title: 'Firebase + MCP', desc: 'Firestore backend, AI integration via MCP server. Realtime widget management.' },
];

export default function Landing() {
  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px' }}>
      {/* Hero */}
      <section style={styles.hero}>
        <div style={styles.badge}>Flutter Dynamic Widget System</div>
        <h1 style={styles.h1}>
          AI-Driven Widgets,<br />
          <span style={{ color: '#6366f1' }}>In One Line</span>
        </h1>
        <p style={styles.subtitle}>
          Add dynamic, AI-managed widgets to your Flutter app.
          The agent decides which widget to show and with which parameters based on context.
        </p>
        <div style={styles.heroActions}>
          <Link to="/pricing" style={styles.btnPrimary}>
            View Plans →
          </Link>
          <Link to="/dashboard" style={styles.btnSecondary}>
            Dashboard
          </Link>
        </div>

        {/* Code preview */}
        <div style={styles.codeBlock}>
          <div style={styles.codeHeader}>
            <span style={styles.dot('#ef4444')} />
            <span style={styles.dot('#f59e0b')} />
            <span style={styles.dot('#22c55e')} />
            <span style={{ marginLeft: 12, color: '#71717a', fontSize: 12 }}>main.dart</span>
          </div>
          <pre style={styles.code}>{`DynamicWidgetContainer(
  responseJson: agentResponse,
  colorScheme: Theme.of(context).colorScheme,
  padding: EdgeInsets.all(12),
  onAction: (id, action) => handleAction(action),
)`}</pre>
        </div>
      </section>

      {/* Features */}
      <section style={styles.section}>
        <h2 style={styles.h2}>How It Works</h2>
        <div style={styles.featGrid}>
          {FEATURES.map((f) => (
            <div key={f.title} style={styles.featCard}>
              <span style={{ fontSize: 32 }}>{f.icon}</span>
              <h3 style={{ fontSize: 16, fontWeight: 600, marginTop: 12 }}>{f.title}</h3>
              <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 8, lineHeight: 1.5 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Widget catalog */}
      <section style={styles.section}>
        <h2 style={styles.h2}>Widget Catalog</h2>
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginBottom: 40 }}>
          10+ ready-made widget types. The agent picks the right one and fills in the parameters.
        </p>
        <div style={styles.grid}>
          {WIDGETS.map((w) => (
            <WidgetCard key={w.title} {...w} />
          ))}
        </div>
      </section>

      {/* CTA */}
      <section style={{ ...styles.section, textAlign: 'center', paddingBottom: 80 }}>
        <h2 style={styles.h2}>Get Started</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>
          Choose a plan, get your API key, add it to your Flutter project.
        </p>
        <Link to="/pricing" style={styles.btnPrimary}>
          View Plans →
        </Link>
      </section>

      {/* Footer */}
      <footer style={styles.footer}>
        <span style={{ color: '#71717a', fontSize: 13 }}>
          © 2026 Intyx. All rights reserved.
        </span>
      </footer>
    </div>
  );
}

const styles = {
  hero: {
    textAlign: 'center',
    paddingTop: 80,
    paddingBottom: 60,
  },
  badge: {
    display: 'inline-block',
    fontSize: 13,
    fontWeight: 500,
    color: '#6366f1',
    background: 'rgba(99,102,241,0.12)',
    border: '1px solid rgba(99,102,241,0.25)',
    borderRadius: 20,
    padding: '6px 16px',
    marginBottom: 24,
  },
  h1: {
    fontSize: 'clamp(36px, 5vw, 56px)',
    fontWeight: 800,
    lineHeight: 1.15,
    letterSpacing: '-0.02em',
    marginBottom: 20,
  },
  subtitle: {
    fontSize: 18,
    color: 'var(--text-muted)',
    maxWidth: 600,
    margin: '0 auto 36px',
    lineHeight: 1.6,
  },
  heroActions: {
    display: 'flex',
    gap: 16,
    justifyContent: 'center',
    marginBottom: 48,
  },
  btnPrimary: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '12px 28px',
    fontSize: 15,
    fontWeight: 600,
    color: '#fff',
    background: '#6366f1',
    borderRadius: 'var(--radius-sm)',
    border: 'none',
    transition: 'background 0.2s',
  },
  btnSecondary: {
    display: 'inline-flex',
    alignItems: 'center',
    padding: '12px 28px',
    fontSize: 15,
    fontWeight: 600,
    color: 'var(--text)',
    background: 'transparent',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)',
  },
  codeBlock: {
    maxWidth: 520,
    margin: '0 auto',
    background: '#0c0c0e',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    overflow: 'hidden',
    textAlign: 'left',
  },
  codeHeader: {
    display: 'flex',
    alignItems: 'center',
    padding: '12px 16px',
    borderBottom: '1px solid var(--border)',
  },
  dot: (color) => ({
    width: 12,
    height: 12,
    borderRadius: '50%',
    background: color,
    display: 'inline-block',
    marginRight: 8,
  }),
  code: {
    padding: '20px 24px',
    fontSize: 14,
    lineHeight: 1.7,
    color: '#c4b5fd',
    overflow: 'auto',
  },
  section: {
    paddingTop: 60,
    paddingBottom: 40,
  },
  h2: {
    fontSize: 28,
    fontWeight: 700,
    textAlign: 'center',
    marginBottom: 16,
  },
  featGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
    gap: 20,
    marginTop: 32,
  },
  featCard: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: 24,
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))',
    gap: 16,
  },
  footer: {
    borderTop: '1px solid var(--border)',
    padding: '24px 0',
    textAlign: 'center',
  },
};
