import { Link } from 'react-router-dom';

export default function Developers() {
  return (
    <main id="main-content" style={{ maxWidth: 900, margin: '0 auto', padding: '0 24px 80px' }}>

      {/* Header */}
      <section style={{ paddingTop: 64, paddingBottom: 40, textAlign: 'center' }}>
        <div style={styles.badge}>Developer Docs</div>
        <h1 style={styles.h1}>How Intyx Dynamic Widget works</h1>
        <p style={styles.subtitle}>
          A signal-driven content selection system for Flutter.
          Predefined templates + live context signals = the right widget for the right user.
        </p>
        <p style={{ marginTop: 16 }}>
          <a
            href="https://github.com/bmnova/intyx-dynamic-widget"
            target="_blank"
            rel="noopener noreferrer"
            style={styles.btnSecondary}
          >
            GitHub →
          </a>
        </p>
      </section>

      {/* Disclaimer */}
      <div style={styles.disclaimer}>
        <strong>Experimental project.</strong> This is an early-stage open-source system under active development.
        APIs and widget schemas may change between versions. Not recommended for production apps without thorough testing.
        Contributions and feedback welcome.
      </div>

      {/* Architecture: 3-step flow */}
      <section aria-labelledby="arch-heading" style={styles.section}>
        <h2 id="arch-heading" style={styles.h2}>Architecture: 3-Step Flow</h2>

        <div style={styles.stepsGrid}>
          <div style={styles.stepCard}>
            <div style={styles.stepNum}>1</div>
            <h3 style={styles.stepTitle}>Predefined Templates</h3>
            <p style={styles.stepDesc}>
              Your widget catalog lives in the backend. Each entry is a typed template —
              hero image, countdown banner, promotional card, progress tracker, poll, etc.
              Templates define which parameters they accept (title, image, action, etc.)
              and which signals they respond to.
            </p>
            <pre style={styles.codeSnippet}>{`// Widget catalog entry (JSON)
{
  "type": "promotional",
  "accepts": ["title", "badge", "description", "cta"],
  "triggers": ["campaign_active", "user_segment"]
}`}</pre>
          </div>

          <div style={styles.stepCard}>
            <div style={styles.stepNum}>2</div>
            <h3 style={styles.stepTitle}>Live Signal Inputs</h3>
            <p style={styles.stepDesc}>
              Your app sends a signal bundle with each widget request. Signals can include
              user data (session count, segment, subscription), external data (weather, news, trends),
              seasonal events, and developer-defined parameters.
            </p>
            <pre style={styles.codeSnippet}>{`// Signal bundle from your app
{
  "user_segment": "premium",
  "session_count": 42,
  "location": "Istanbul",
  "custom_params": {
    "last_purchase_days_ago": 7
  }
}`}</pre>
          </div>

          <div style={styles.stepCard}>
            <div style={styles.stepNum}>3</div>
            <h3 style={styles.stepTitle}>Decision Layer Selects Content</h3>
            <p style={styles.stepDesc}>
              The backend evaluates incoming signals against your widget catalog.
              It selects the highest-priority matching template, fills in the parameters,
              and returns a populated widget response. Your Flutter component renders it.
            </p>
            <pre style={styles.codeSnippet}>{`// Response to your Flutter app
{
  "widget_type": "promotional",
  "params": {
    "title": "Summer sale — 50% off",
    "badge": "MEMBERS ONLY",
    "cta": { "label": "Shop now", "url": "..." }
  }
}`}</pre>
          </div>
        </div>

        {/* Simple diagram */}
        <div style={styles.diagram}>
          <div style={styles.diagramBox}>Flutter App<br /><span style={styles.diagramSub}>signal bundle</span></div>
          <div style={styles.diagramArrow}>→</div>
          <div style={styles.diagramBox}>Decision Layer<br /><span style={styles.diagramSub}>evaluates signals</span></div>
          <div style={styles.diagramArrow}>→</div>
          <div style={styles.diagramBox}>Template Catalog<br /><span style={styles.diagramSub}>selects + fills</span></div>
          <div style={styles.diagramArrow}>→</div>
          <div style={{ ...styles.diagramBox, borderColor: '#6366f1', color: '#818cf8' }}>
            Widget Response<br /><span style={{ ...styles.diagramSub, color: '#a5b4fc' }}>rendered in app</span>
          </div>
        </div>
      </section>

      {/* Flutter integration */}
      <section aria-labelledby="flutter-heading" style={styles.section}>
        <h2 id="flutter-heading" style={styles.h2}>Flutter Integration</h2>

        <h3 style={styles.h3}>1. Add the package</h3>
        <pre style={styles.codeBlock}>{`# pubspec.yaml
dependencies:
  intyx_dynamic_widget:
    path: ../flutter_client   # local
    # or from pub.dev once published`}</pre>

        <h3 style={styles.h3}>2. Initialise the SDK</h3>
        <pre style={styles.codeBlock}>{`import 'package:intyx_dynamic_widget/intyx_dynamic_widget.dart';

void main() {
  registerDefaultWidgets();   // registers all built-in templates
  runApp(MyApp());
}`}</pre>

        <h3 style={styles.h3}>3. Drop the component into your layout</h3>
        <pre style={styles.codeBlock}>{`// In any screen or widget tree
DynamicWidgetContainer(
  responseJson: widgetResponse,          // JSON from your API call
  colorScheme: Theme.of(context).colorScheme,
  padding: EdgeInsets.all(12),
  onAction: (widgetId, action) {
    // handle deep links, dismiss, custom actions
    handleAction(action);
  },
)`}</pre>

        <h3 style={styles.h3}>4. Fetch a widget for a user</h3>
        <pre style={styles.codeBlock}>{`final response = await http.post(
  Uri.parse('https://your-api/api/widgets/evaluate'),
  headers: {'Authorization': 'Bearer \$licenseKey'},
  body: jsonEncode({
    'user_id': userId,
    'session_count': sessionCount,
    'user_segment': 'premium',
    'custom_params': {'feature_used': 'checkout'},
  }),
);

final widgetResponse = jsonDecode(response.body);
// Pass widgetResponse to DynamicWidgetContainer`}</pre>
      </section>

      {/* Behaviour details */}
      <section aria-labelledby="behaviour-heading" style={styles.section}>
        <h2 id="behaviour-heading" style={styles.h2}>Behaviour Details</h2>

        <div style={styles.behaviourGrid}>
          <div style={styles.behaviourCard}>
            <h3 style={styles.behaviourTitle}>Fallback behaviour</h3>
            <p style={styles.behaviourDesc}>
              If the decision layer finds no matching widget for the current signals, it returns a{' '}
              <code style={styles.inlineCode}>null</code> response.{' '}
              <code style={styles.inlineCode}>DynamicWidgetContainer</code> renders nothing in that case —
              your layout remains intact. You can also pass a custom fallback widget via the{' '}
              <code style={styles.inlineCode}>fallback</code> parameter.
            </p>
          </div>

          <div style={styles.behaviourCard}>
            <h3 style={styles.behaviourTitle}>Determinism</h3>
            <p style={styles.behaviourDesc}>
              Widget selection is deterministic given the same signal bundle. The decision layer applies
              priority rules and condition matching — not probabilistic sampling.
              The same user with the same signals sees the same widget every time.
            </p>
          </div>

          <div style={styles.behaviourCard}>
            <h3 style={styles.behaviourTitle}>Guardrails</h3>
            <p style={styles.behaviourDesc}>
              Only predefined template types can be rendered. The backend cannot inject arbitrary
              Flutter widget code. Parameter values are typed and validated server-side before
              being returned to the client.
            </p>
          </div>

          <div style={styles.behaviourCard}>
            <h3 style={styles.behaviourTitle}>Logging & debugging</h3>
            <p style={styles.behaviourDesc}>
              Each evaluate call logs the incoming signals, matched template, and applied parameters
              to Firestore. You can inspect widget impressions, dismiss events, and action clicks
              from the Dashboard. Pass <code style={styles.inlineCode}>INTYX_DEV_MODE=true</code>{' '}
              in your backend to bypass license checks during development.
            </p>
          </div>
        </div>
      </section>

      {/* Links */}
      <section aria-labelledby="links-heading" style={{ ...styles.section, textAlign: 'center' }}>
        <h2 id="links-heading" style={styles.h2}>Links</h2>
        <div style={{ display: 'flex', gap: 16, justifyContent: 'center', flexWrap: 'wrap', marginTop: 24 }}>
          <a
            href="https://github.com/bmnova/intyx-dynamic-widget"
            target="_blank"
            rel="noopener noreferrer"
            style={styles.btnPrimary}
          >
            GitHub repository →
          </a>
          <Link to="/pricing" style={styles.btnSecondary}>
            View Plans
          </Link>
          <Link to="/product" style={styles.btnSecondary}>
            Product overview
          </Link>
        </div>
      </section>

    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  badge: { display: 'inline-block', fontSize: 13, fontWeight: 500, color: '#6366f1', background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.25)', borderRadius: 20, padding: '6px 16px', marginBottom: 20 },
  h1: { fontSize: 'clamp(28px, 4vw, 44px)' as unknown as number, fontWeight: 800, lineHeight: 1.2, letterSpacing: '-0.02em', marginBottom: 16, marginTop: 12 },
  subtitle: { fontSize: 17, color: 'var(--text-muted)', maxWidth: 600, margin: '0 auto', lineHeight: 1.6 },
  disclaimer: { background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.25)', borderRadius: 8, padding: '14px 18px', fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 16 },
  section: { paddingTop: 56, paddingBottom: 16 },
  h2: { fontSize: 24, fontWeight: 700, marginBottom: 24 },
  h3: { fontSize: 16, fontWeight: 600, marginTop: 28, marginBottom: 10, color: 'var(--text)' },
  stepsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16, marginBottom: 32 },
  stepCard: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '20px 20px 16px' },
  stepNum: { width: 32, height: 32, borderRadius: '50%', background: 'rgba(99,102,241,0.15)', color: '#818cf8', fontWeight: 800, fontSize: 16, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 12 },
  stepTitle: { fontSize: 15, fontWeight: 700, marginBottom: 8 },
  stepDesc: { fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 12 },
  codeSnippet: { background: '#0c0c0e', border: '1px solid var(--border)', borderRadius: 6, padding: '12px 14px', fontSize: 12, color: '#c4b5fd', overflow: 'auto', lineHeight: 1.6 },
  codeBlock: { background: '#0c0c0e', border: '1px solid var(--border)', borderRadius: 8, padding: '18px 20px', fontSize: 13, color: '#c4b5fd', overflow: 'auto', lineHeight: 1.7, marginBottom: 8 },
  diagram: { display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, flexWrap: 'wrap', padding: '24px 0', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)' },
  diagramBox: { border: '1px solid var(--border)', borderRadius: 8, padding: '10px 16px', fontSize: 13, fontWeight: 600, textAlign: 'center', lineHeight: 1.4 },
  diagramSub: { fontSize: 11, fontWeight: 400, color: 'var(--text-muted)' },
  diagramArrow: { fontSize: 18, color: 'var(--text-muted)' },
  behaviourGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 },
  behaviourCard: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '18px 20px' },
  behaviourTitle: { fontSize: 14, fontWeight: 700, marginBottom: 8 },
  behaviourDesc: { fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6, margin: 0 },
  inlineCode: { background: 'rgba(99,102,241,0.12)', color: '#a5b4fc', padding: '1px 5px', borderRadius: 4, fontSize: 12, fontFamily: 'monospace' },
  btnPrimary: { display: 'inline-flex', alignItems: 'center', padding: '11px 26px', fontSize: 14, fontWeight: 600, color: '#fff', background: '#6366f1', borderRadius: 'var(--radius-sm)', border: 'none', textDecoration: 'none', transition: 'background 0.2s' },
  btnSecondary: { display: 'inline-flex', alignItems: 'center', padding: '11px 26px', fontSize: 14, fontWeight: 600, color: 'var(--text)', background: 'transparent', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', textDecoration: 'none' },
};
