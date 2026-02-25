import { useState } from 'react';
import { Link } from 'react-router-dom';
import WidgetCard from '../components/WidgetCard';

interface DataSource {
  icon: string;
  name: string;
  desc: string;
  badge: string;
  badgeColor: string;
  category: string;
}

const DATA_SOURCES: DataSource[] = [
  { icon: '⛅', name: 'Weather', desc: 'Current conditions, 5-day forecast, coordinates lookup via OpenWeatherMap.', badge: 'API Key', badgeColor: '#f59e0b', category: 'Environment' },
  { icon: '💨', name: 'Air Quality', desc: 'Real-time AQI, PM2.5, PM10, O₃, NO₂ levels from WAQI.', badge: 'Free', badgeColor: '#22c55e', category: 'Environment' },
  { icon: '🌍', name: 'Earthquake', desc: 'Live seismic events worldwide or by area — magnitude, depth, alerts (USGS).', badge: 'Free', badgeColor: '#22c55e', category: 'Safety' },
  { icon: '💱', name: 'Exchange Rates', desc: 'ECB exchange rates for 30+ currencies, live currency conversion.', badge: 'Free', badgeColor: '#22c55e', category: 'Finance' },
  { icon: '🕌', name: 'Prayer Times', desc: 'Fajr → Isha for any city or GPS coords, 12 calculation methods (Aladhan).', badge: 'Free', badgeColor: '#22c55e', category: 'Lifestyle' },
  { icon: '📅', name: 'Holidays', desc: '24+ special days and public holidays with widget suggestions.', badge: 'Built-in', badgeColor: '#6366f1', category: 'Calendar' },
  { icon: '🔥', name: 'Trends', desc: 'Viral topics from Google Trends & Twitter — filtered by category and platform.', badge: 'Optional Key', badgeColor: '#f59e0b', category: 'Social' },
  { icon: '📰', name: 'News', desc: 'Top headlines by country and category via NewsAPI.org.', badge: 'API Key', badgeColor: '#f59e0b', category: 'Content' },
  { icon: '🔮', name: 'Horoscope', desc: 'AI-generated daily horoscope content powered by Gemini.', badge: 'Built-in', badgeColor: '#6366f1', category: 'Lifestyle' },
];

interface WidgetEntry {
  icon: string;
  title: string;
  description: string;
  tag: string;
}

const WIDGETS: WidgetEntry[] = [
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

interface Feature {
  icon: string;
  title: string;
  desc: string;
}

const FEATURES: Feature[] = [
  { icon: '🤖', title: 'AI Agent Decisions', desc: "The AI agent decides which widget appears where. Automatic selection based on context." },
  { icon: '🎨', title: 'ColorScheme Match', desc: "Pass your app's ColorScheme as a parameter; widgets adapt automatically." },
  { icon: '📐', title: 'Responsive Layout', desc: 'Width, height, padding, margin, aspect ratio — all configurable via JSON.' },
  { icon: '🔥', title: 'Firebase + MCP', desc: 'Firestore backend, AI integration via MCP server. Realtime widget management.' },
];

interface DemoWidget {
  key: string;
  label: string;
  icon: string;
  preview: DemoPreviewData;
}

interface DemoPreviewData {
  type: string;
  emoji?: string;
  text?: string;
  badge?: string;
  title?: string;
  description?: string;
  subtitle?: string;
  stars?: number;
  pct?: number;
  label?: string;
  question?: string;
  options?: string[];
}

const DEMO_WIDGETS: DemoWidget[] = [
  {
    key: 'banner',
    label: 'Banner',
    icon: '📢',
    preview: { type: 'banner', emoji: '☀️', text: 'Good morning! Today is a great day to ship something.' },
  },
  {
    key: 'promotional',
    label: 'Promotional',
    icon: '🏷️',
    preview: { type: 'promotional', badge: 'SUMMER SALE', title: '50% off all styles', description: 'Limited time offer — ends Sunday midnight.' },
  },
  {
    key: 'countdown',
    label: 'Countdown',
    icon: '⏱️',
    preview: { type: 'countdown', title: 'Flash Sale ends in' },
  },
  {
    key: 'rating',
    label: 'Rating',
    icon: '⭐',
    preview: { type: 'rating', title: 'Enjoying the app?', subtitle: 'Tap to rate your experience', stars: 5 },
  },
  {
    key: 'progress',
    label: 'Progress',
    icon: '📈',
    preview: { type: 'progress', title: 'Your fitness goal this week', pct: 72, label: '72% — 3 more workouts to go!' },
  },
  {
    key: 'poll',
    label: 'Poll',
    icon: '📊',
    preview: { type: 'poll', question: 'Which feature should we build next?', options: ['Dark mode', 'Offline support', 'AI suggestions'] },
  },
];

function DemoPreview({ widget }: { widget: DemoPreviewData }) {
  const box: React.CSSProperties = {
    background: '#0c0c0e',
    border: '1px solid var(--border)',
    borderRadius: 12,
    padding: 20,
    color: 'var(--text)',
    minHeight: 120,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
  };

  if (widget.type === 'banner') {
    return (
      <div style={{ ...box, textAlign: 'center', fontSize: 15 }}>
        <span aria-hidden="true" style={{ fontSize: 24, display: 'block', marginBottom: 8 }}>{widget.emoji}</span>
        {widget.text}
      </div>
    );
  }
  if (widget.type === 'promotional') {
    return (
      <div style={box}>
        <span style={{ fontSize: 11, fontWeight: 700, color: '#f59e0b', background: 'rgba(245,158,11,0.15)', padding: '3px 10px', borderRadius: 12, display: 'inline-block', marginBottom: 8 }}>
          {widget.badge}
        </span>
        <div style={{ fontSize: 18, fontWeight: 700 }}>{widget.title}</div>
        <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 6 }}>{widget.description}</div>
      </div>
    );
  }
  if (widget.type === 'countdown') {
    return (
      <div style={{ ...box, textAlign: 'center' }}>
        <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 8 }}>{widget.title}</div>
        <div style={{ fontSize: 32, fontWeight: 800, color: '#6366f1', letterSpacing: 2 }}>02:47:13</div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>hours · minutes · seconds</div>
      </div>
    );
  }
  if (widget.type === 'rating') {
    return (
      <div style={{ ...box, textAlign: 'center' }}>
        <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>{widget.title}</div>
        <div style={{ fontSize: 30, letterSpacing: 4, color: '#f59e0b' }}>{'★'.repeat(widget.stars ?? 5)}</div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>{widget.subtitle}</div>
      </div>
    );
  }
  if (widget.type === 'progress') {
    return (
      <div style={box}>
        <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>{widget.title}</div>
        <div style={{ height: 10, borderRadius: 5, background: '#27272a', overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${widget.pct ?? 0}%`, background: 'linear-gradient(90deg,#6366f1,#818cf8)', borderRadius: 5 }} />
        </div>
        <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 8 }}>{widget.label}</div>
      </div>
    );
  }
  if (widget.type === 'poll') {
    return (
      <div style={box}>
        <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 10 }}>{widget.question}</div>
        {(widget.options ?? []).map((o) => (
          <div key={o} style={{ padding: '8px 12px', marginBottom: 6, border: '1px solid var(--border)', borderRadius: 6, fontSize: 13 }}>{o}</div>
        ))}
      </div>
    );
  }
  return null;
}

export default function Landing() {
  const [activeDemo, setActiveDemo] = useState('banner');
  return (
    <main id="main-content" style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px' }}>
      {/* Hero */}
      <section aria-labelledby="hero-heading" style={styles.hero}>
        <div aria-hidden="true" style={styles.badge}>Flutter Dynamic Widget System</div>
        <h1 id="hero-heading" style={styles.h1}>
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
        <figure aria-label="Code example: DynamicWidgetContainer usage in Flutter" style={styles.codeBlock}>
          <div aria-hidden="true" style={styles.codeHeader}>
            <span style={dot('#ef4444')} />
            <span style={dot('#f59e0b')} />
            <span style={dot('#22c55e')} />
            <span style={{ marginLeft: 12, color: '#71717a', fontSize: 12 }}>main.dart</span>
          </div>
          <pre style={styles.code}>{`DynamicWidgetContainer(
  responseJson: agentResponse,
  colorScheme: Theme.of(context).colorScheme,
  padding: EdgeInsets.all(12),
  onAction: (id, action) => handleAction(action),
)`}</pre>
        </figure>
      </section>

      {/* Features */}
      <section aria-labelledby="features-heading" style={styles.section}>
        <h2 id="features-heading" style={styles.h2}>How It Works</h2>
        <div style={styles.featGrid}>
          {FEATURES.map((f) => (
            <div key={f.title} style={styles.featCard}>
              <span aria-hidden="true" style={{ fontSize: 32 }}>{f.icon}</span>
              <h3 style={{ fontSize: 16, fontWeight: 600, marginTop: 12 }}>{f.title}</h3>
              <p style={{ fontSize: 14, color: 'var(--text-muted)', marginTop: 8, lineHeight: 1.5 }}>{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Data Sources */}
      <section aria-labelledby="datasources-heading" style={styles.section}>
        <h2 id="datasources-heading" style={styles.h2}>Live Data Sources</h2>
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginBottom: 8 }}>
          The AI agent pulls from real-time data sources to make every widget contextually relevant.
        </p>
        <p style={{ textAlign: 'center', marginBottom: 36 }}>
          <Link to="/integrations" style={{ color: '#6366f1', fontSize: 13, fontWeight: 600 }}>
            View all integrations →
          </Link>
        </p>
        <div style={styles.dsGrid}>
          {DATA_SOURCES.map((ds) => (
            <div key={ds.name} style={styles.dsCard}>
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
                <span aria-hidden="true" style={{ fontSize: 28, lineHeight: 1 }}>{ds.icon}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap', marginBottom: 4 }}>
                    <span style={{ fontWeight: 700, fontSize: 15 }}>{ds.name}</span>
                    <span style={{
                      fontSize: 10,
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: 20,
                      background: `${ds.badgeColor}22`,
                      color: ds.badgeColor,
                      border: `1px solid ${ds.badgeColor}44`,
                      letterSpacing: '0.03em',
                    }}>{ds.badge}</span>
                  </div>
                  <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: 0, lineHeight: 1.5 }}>{ds.desc}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Widget catalog */}
      <section aria-labelledby="catalog-heading" style={styles.section}>
        <h2 id="catalog-heading" style={styles.h2}>Widget Catalog</h2>
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginBottom: 40 }}>
          10+ ready-made widget types. The agent picks the right one and fills in the parameters.
        </p>
        <div style={styles.grid}>
          {WIDGETS.map((w) => (
            <WidgetCard key={w.title} {...w} />
          ))}
        </div>
      </section>

      {/* Interactive demo */}
      <section aria-labelledby="demo-heading" style={styles.section}>
        <h2 id="demo-heading" style={styles.h2}>Live Widget Preview</h2>
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginBottom: 32 }}>
          Click a widget type to see how it looks inside your Flutter app.
        </p>
        <div style={styles.demoWrap}>
          <div role="tablist" aria-label="Widget type selector" style={styles.demoSelector}>
            {DEMO_WIDGETS.map((w) => (
              <button
                key={w.key}
                role="tab"
                aria-selected={activeDemo === w.key}
                aria-controls="demo-preview-panel"
                id={`demo-tab-${w.key}`}
                onClick={() => setActiveDemo(w.key)}
                style={{
                  ...styles.demoTab,
                  background: activeDemo === w.key ? 'var(--primary-muted)' : 'transparent',
                  borderColor: activeDemo === w.key ? 'var(--primary)' : 'transparent',
                  color: activeDemo === w.key ? '#818cf8' : 'var(--text-muted)',
                }}
              >
                <span aria-hidden="true" style={{ fontSize: 18 }}>{w.icon}</span>
                <span style={{ fontSize: 13, fontWeight: 600 }}>{w.label}</span>
              </button>
            ))}
          </div>

          <div
            id="demo-preview-panel"
            role="tabpanel"
            aria-labelledby={`demo-tab-${activeDemo}`}
            style={styles.demoPreview}
          >
            <div style={{ fontSize: 11, color: '#52525b', marginBottom: 12, fontFamily: 'monospace' }}>
              widget_type: &quot;{DEMO_WIDGETS.find((w) => w.key === activeDemo)?.key}&quot;
            </div>
            <DemoPreview widget={DEMO_WIDGETS.find((w) => w.key === activeDemo)!.preview} />
            <p style={{ fontSize: 12, color: '#52525b', marginTop: 16, textAlign: 'center' }}>
              AI fills these parameters automatically based on user context
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section aria-labelledby="cta-heading" style={{ ...styles.section, textAlign: 'center', paddingBottom: 80 }}>
        <h2 id="cta-heading" style={styles.h2}>Get Started</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>
          Choose a plan, get your API key, add it to your Flutter project.
        </p>
        <Link to="/pricing" style={styles.btnPrimary}>
          View Plans →
        </Link>
      </section>

      {/* Footer */}
      <footer role="contentinfo" style={styles.footer}>
        <span style={{ color: '#71717a', fontSize: 13 }}>
          © 2026 Intyx. All rights reserved.
        </span>
      </footer>
    </main>
  );
}

const dot = (color: string): React.CSSProperties => ({
  width: 12,
  height: 12,
  borderRadius: '50%',
  background: color,
  display: 'inline-block',
  marginRight: 8,
});

const styles: Record<string, React.CSSProperties> = {
  hero: { textAlign: 'center', paddingTop: 80, paddingBottom: 60 },
  badge: { display: 'inline-block', fontSize: 13, fontWeight: 500, color: '#6366f1', background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.25)', borderRadius: 20, padding: '6px 16px', marginBottom: 24 },
  h1: { fontSize: 'clamp(36px, 5vw, 56px)' as unknown as number, fontWeight: 800, lineHeight: 1.15, letterSpacing: '-0.02em', marginBottom: 20 },
  subtitle: { fontSize: 18, color: 'var(--text-muted)', maxWidth: 600, margin: '0 auto 36px', lineHeight: 1.6 },
  heroActions: { display: 'flex', gap: 16, justifyContent: 'center', marginBottom: 48 },
  btnPrimary: { display: 'inline-flex', alignItems: 'center', padding: '12px 28px', fontSize: 15, fontWeight: 600, color: '#fff', background: '#6366f1', borderRadius: 'var(--radius-sm)', border: 'none', transition: 'background 0.2s' },
  btnSecondary: { display: 'inline-flex', alignItems: 'center', padding: '12px 28px', fontSize: 15, fontWeight: 600, color: 'var(--text)', background: 'transparent', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)' },
  codeBlock: { maxWidth: 520, margin: '0 auto', background: '#0c0c0e', border: '1px solid var(--border)', borderRadius: 'var(--radius)', overflow: 'hidden', textAlign: 'left' },
  codeHeader: { display: 'flex', alignItems: 'center', padding: '12px 16px', borderBottom: '1px solid var(--border)' },
  code: { padding: '20px 24px', fontSize: 14, lineHeight: 1.7, color: '#c4b5fd', overflow: 'auto' },
  section: { paddingTop: 60, paddingBottom: 40 },
  h2: { fontSize: 28, fontWeight: 700, textAlign: 'center', marginBottom: 16 },
  featGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 20, marginTop: 32 },
  featCard: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: 24 },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 16 },
  footer: { borderTop: '1px solid var(--border)', padding: '24px 0', textAlign: 'center' },
  demoWrap: { display: 'grid', gridTemplateColumns: '200px 1fr', gap: 24, alignItems: 'start' },
  demoSelector: { display: 'flex', flexDirection: 'column', gap: 4 },
  demoTab: { display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px', borderRadius: 8, border: '1px solid transparent', cursor: 'pointer', textAlign: 'left', transition: 'background 0.15s, border-color 0.15s', background: 'transparent' },
  demoPreview: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: 24 },
  dsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 16 },
  dsCard: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '18px 20px', transition: 'border-color 0.2s' },
};
