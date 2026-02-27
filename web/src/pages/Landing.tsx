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
  { icon: '☁️', title: 'Contextual', description: 'Contextual info card (weather, horoscope, etc.)', tag: 'Context' },
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
  { icon: '📐', title: 'Predefined Templates', desc: 'Every widget is a typed template — hero, promo, countdown, poll, progress. No arbitrary layouts generated at runtime.' },
  { icon: '📡', title: 'Live Signal Inputs', desc: 'User data, external APIs, seasonal events, and developer-defined parameters feed into the decision layer.' },
  { icon: '🔀', title: 'Decision Layer', desc: 'Evaluates incoming signals against your template catalog and selects the right widget with the right parameters.' },
  { icon: '🎨', title: 'Theme-Aware Rendering', desc: "Pass your app's ColorScheme; widgets adapt automatically. No extra styling needed." },
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
    preview: { type: 'banner', emoji: '👋', text: "Welcome! Here's what's new in this version." },
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
    preview: { type: 'poll', question: 'Which feature should we build next?', options: ['Dark mode', 'Offline support', 'Widgets'] },
  },
];

interface UserContext {
  key: string;
  label: string;
  desc: string;
  suggestedWidget: string;
  reason: string;
}

const USER_CONTEXTS: UserContext[] = [
  {
    key: 'new_user',
    label: 'New User',
    desc: 'First session, no history',
    suggestedWidget: 'banner',
    reason: 'Onboarding banner — introduce the key feature on first open.',
  },
  {
    key: 'active_user',
    label: 'Active User',
    desc: '30+ sessions, 60% weekly goal',
    suggestedWidget: 'progress',
    reason: 'Progress card — keep engaged users motivated with goal tracking.',
  },
  {
    key: 'promo_target',
    label: 'Promo Target',
    desc: 'In summer campaign segment',
    suggestedWidget: 'promotional',
    reason: 'Promotional card — show campaign offer to eligible segment only.',
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
  const [activeContext, setActiveContext] = useState('new_user');

  const currentContext = USER_CONTEXTS.find((c) => c.key === activeContext)!;

  function selectContext(ctx: UserContext) {
    setActiveContext(ctx.key);
    setActiveDemo(ctx.suggestedWidget);
  }

  return (
    <main id="main-content" style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px' }}>

      {/* Hero */}
      <section aria-labelledby="hero-heading" style={styles.hero}>
        <div aria-hidden="true" style={styles.badge}>Experimental · Flutter Dynamic Widget System</div>
        <h1 id="hero-heading" style={styles.h1}>
          Update your app's content in real time —<br />
          <span style={{ color: '#6366f1' }}>without shipping a new build</span>
        </h1>
        <p style={styles.subtitle}>
          Predefined widget templates, dynamically populated via live signals.
          Drop one component into your Flutter app; the decision layer picks the right content for each user.
        </p>

        <div style={styles.heroActions}>
          <Link to="/developers" style={styles.btnPrimary}>
            I'm a developer →
          </Link>
          <Link to="/product" style={styles.btnSecondary}>
            I'm in product / growth
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
  responseJson: widgetResponse,
  colorScheme: Theme.of(context).colorScheme,
  padding: EdgeInsets.all(12),
  onAction: (id, action) => handleAction(action),
)`}</pre>
        </figure>
      </section>

      {/* How it works */}
      <section aria-labelledby="features-heading" style={styles.section}>
        <h2 id="features-heading" style={styles.h2}>How It Works</h2>
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginBottom: 40 }}>
          Three layers. One component call.
        </p>
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

      {/* What this IS */}
      <section aria-labelledby="usecases-heading" style={styles.section}>
        <h2 id="usecases-heading" style={styles.h2}>Where this makes sense</h2>
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginBottom: 40 }}>
          Good fit for slot-based surfaces where content changes per user or campaign.
        </p>
        <div style={styles.twoColGrid}>
          {[
            { icon: '🚀', title: 'Onboarding variants', desc: 'Show different welcome messages or feature highlights based on how the user signed up.' },
            { icon: '📣', title: 'Campaign banners', desc: 'Push seasonal or event-based banners live — no release needed.' },
            { icon: '🧪', title: 'Paywall experiments', desc: 'Test different upsell messages and CTAs across user segments.' },
            { icon: '📊', title: 'Dashboard cards', desc: 'Surface contextual tips, alerts, or stats based on what the user has (or hasn\'t) done.' },
          ].map((item) => (
            <div key={item.title} style={styles.usecaseCard}>
              <span aria-hidden="true" style={{ fontSize: 28, display: 'block', marginBottom: 10 }}>{item.icon}</span>
              <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 6 }}>{item.title}</h3>
              <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6, margin: 0 }}>{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* What this is NOT */}
      <section aria-labelledby="notusecase-heading" style={styles.section}>
        <h2 id="notusecase-heading" style={styles.h2}>What this is NOT</h2>
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginBottom: 40 }}>
          Knowing the limits helps you decide if it's the right tool.
        </p>
        <div style={styles.notGrid}>
          {[
            { title: 'Not replacing your widget tree', desc: 'It fills a specific slot in your existing layout. Your navigation, screens, and core UI are unchanged.' },
            { title: 'Not generating arbitrary layouts', desc: 'Only predefined templates are used. The decision layer picks which one — it doesn\'t invent new UI.' },
            { title: 'Not bypassing app store policies', desc: 'Widget content and parameters change dynamically; the structural code ships with your app as normal.' },
            { title: 'Not a real-time database replacement', desc: 'It\'s not Firebase Remote Config or a feature flag system. It handles widget selection and content, not raw config values.' },
          ].map((item) => (
            <div key={item.title} style={styles.notCard}>
              <span style={{ fontSize: 18, color: '#ef4444', fontWeight: 700, marginRight: 8 }}>✕</span>
              <div>
                <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 4 }}>{item.title}</div>
                <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6 }}>{item.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Where this does NOT make sense */}
      <section aria-labelledby="badfit-heading" style={{ ...styles.section, paddingTop: 20 }}>
        <h2 id="badfit-heading" style={{ ...styles.h2, fontSize: 22 }}>Where this does NOT make sense</h2>
        <div style={{ maxWidth: 640, margin: '24px auto 0', display: 'flex', flexDirection: 'column', gap: 10 }}>
          {[
            'Complex forms or multi-step flows that require custom state',
            'Screens where every pixel is brand-controlled and pixel-perfect',
            'Features that require native capabilities or platform APIs',
            'Cases where widget logic is simple enough to hardcode without pain',
          ].map((item) => (
            <div key={item} style={{ display: 'flex', alignItems: 'flex-start', gap: 10, fontSize: 14, color: 'var(--text-muted)', lineHeight: 1.6 }}>
              <span style={{ color: '#71717a', marginTop: 2, flexShrink: 0 }}>—</span>
              <span>{item}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Interactive demo */}
      <section aria-labelledby="demo-heading" style={styles.section}>
        <h2 id="demo-heading" style={styles.h2}>See the Decision Layer in Action</h2>

        {/* How this works explanation */}
        <div style={styles.demoExplainer}>
          <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 8 }}>How this works</div>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.7, margin: 0 }}>
            Your app sends a signal bundle to the backend (user segment, session count, active campaigns, etc.).
            The decision layer evaluates those signals against your widget catalog and returns the right template
            with the right parameters — already filled in. Your Flutter component renders it without any conditional logic on your side.
          </p>
        </div>

        {/* Context switcher */}
        <div style={{ marginBottom: 28 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 12, textAlign: 'center' }}>
            Simulate a different user context:
          </div>
          <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
            {USER_CONTEXTS.map((ctx) => (
              <button
                key={ctx.key}
                onClick={() => selectContext(ctx)}
                style={{
                  padding: '8px 18px',
                  borderRadius: 20,
                  border: '1px solid',
                  borderColor: activeContext === ctx.key ? '#6366f1' : 'var(--border)',
                  background: activeContext === ctx.key ? 'rgba(99,102,241,0.12)' : 'transparent',
                  color: activeContext === ctx.key ? '#818cf8' : 'var(--text-muted)',
                  fontSize: 13,
                  fontWeight: 600,
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                }}
              >
                {ctx.label}
                <span style={{ fontSize: 11, fontWeight: 400, display: 'block', color: activeContext === ctx.key ? '#a5b4fc' : '#52525b' }}>
                  {ctx.desc}
                </span>
              </button>
            ))}
          </div>
          {/* Context reason */}
          <div style={{ textAlign: 'center', marginTop: 14, fontSize: 13, color: '#818cf8', fontStyle: 'italic' }}>
            Decision layer selects: <strong style={{ color: '#a5b4fc' }}>{currentContext.reason}</strong>
          </div>
        </div>

        {/* Widget tabs + preview */}
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
                  borderColor: activeDemo === w.key ? 'var(--primary)' : (currentContext.suggestedWidget === w.key ? 'rgba(99,102,241,0.35)' : 'transparent'),
                  color: activeDemo === w.key ? '#818cf8' : 'var(--text-muted)',
                  position: 'relative',
                }}
              >
                <span aria-hidden="true" style={{ fontSize: 18 }}>{w.icon}</span>
                <span style={{ fontSize: 13, fontWeight: 600 }}>{w.label}</span>
                {currentContext.suggestedWidget === w.key && activeDemo !== w.key && (
                  <span style={{ position: 'absolute', top: 6, right: 6, width: 6, height: 6, borderRadius: '50%', background: '#6366f1' }} />
                )}
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
              Parameters are filled by the decision layer — no hardcoded content in your app
            </p>
          </div>
        </div>

        {/* Why this matters */}
        <div style={styles.demoWhyMatters}>
          <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 6 }}>Why this matters</div>
          <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.7, margin: 0 }}>
            Without a system like this, showing different content per user segment means adding conditional logic
            throughout your widget tree, hardcoding strings, or waiting for a release cycle to update a banner.
            With one component and a signal bundle, the right content shows up for the right user — and you can
            change it without touching the app.
          </p>
        </div>
      </section>

      {/* Data Sources */}
      <section aria-labelledby="datasources-heading" style={styles.section}>
        <h2 id="datasources-heading" style={styles.h2}>Live Signal Sources</h2>
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginBottom: 8 }}>
          The decision layer pulls from real-time data sources to make widget selection contextually relevant.
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
        <h2 id="catalog-heading" style={styles.h2}>Widget Template Catalog</h2>
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginBottom: 40 }}>
          10+ ready-made templates. The decision layer picks the right one and fills in the parameters.
        </p>
        <div style={styles.grid}>
          {WIDGETS.map((w) => (
            <WidgetCard key={w.title} {...w} />
          ))}
        </div>
      </section>

      {/* CTA */}
      <section aria-labelledby="cta-heading" style={{ ...styles.section, textAlign: 'center', paddingBottom: 80 }}>
        <h2 id="cta-heading" style={styles.h2}>Ready to try it?</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>
          Start with the developer docs or explore the dashboard.
        </p>
        <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/developers" style={styles.btnPrimary}>
            Developer docs →
          </Link>
          <Link to="/pricing" style={styles.btnSecondary}>
            View Plans
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer role="contentinfo" style={styles.footer}>
        <span style={{ color: '#71717a', fontSize: 13 }}>
          © 2026 Intyx. All rights reserved. · Experimental project — see{' '}
          <Link to="/developers" style={{ color: '#6366f1' }}>disclaimer</Link>
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
  h1: { fontSize: 'clamp(32px, 4.5vw, 52px)' as unknown as number, fontWeight: 800, lineHeight: 1.2, letterSpacing: '-0.02em', marginBottom: 20 },
  subtitle: { fontSize: 18, color: 'var(--text-muted)', maxWidth: 620, margin: '0 auto 36px', lineHeight: 1.6 },
  heroActions: { display: 'flex', gap: 16, justifyContent: 'center', marginBottom: 48, flexWrap: 'wrap' },
  btnPrimary: { display: 'inline-flex', alignItems: 'center', padding: '12px 28px', fontSize: 15, fontWeight: 600, color: '#fff', background: '#6366f1', borderRadius: 'var(--radius-sm)', border: 'none', transition: 'background 0.2s', textDecoration: 'none' },
  btnSecondary: { display: 'inline-flex', alignItems: 'center', padding: '12px 28px', fontSize: 15, fontWeight: 600, color: 'var(--text)', background: 'transparent', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', textDecoration: 'none' },
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
  twoColGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 },
  usecaseCard: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: 24 },
  notGrid: { display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 720, margin: '0 auto' },
  notCard: { display: 'flex', alignItems: 'flex-start', gap: 12, background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '16px 20px' },
  demoExplainer: { background: 'rgba(99,102,241,0.06)', border: '1px solid rgba(99,102,241,0.2)', borderRadius: 'var(--radius)', padding: '16px 20px', maxWidth: 680, margin: '0 auto 32px' },
  demoWhyMatters: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '16px 20px', maxWidth: 680, margin: '24px auto 0' },
};
