import { Link } from 'react-router-dom';

export default function Product() {
  return (
    <main id="main-content" style={{ maxWidth: 900, margin: '0 auto', padding: '0 24px 80px' }}>

      {/* Header */}
      <section style={{ paddingTop: 64, paddingBottom: 40, textAlign: 'center' }}>
        <div style={styles.badge}>For Product &amp; Growth Teams</div>
        <h1 style={styles.h1}>
          Run experiments and update content —<br />
          <span style={{ color: '#6366f1' }}>without waiting for a release</span>
        </h1>
        <p style={styles.subtitle}>
          Intyx lets your team change what shows up inside the app for different users —
          without a developer writing new code or submitting a new build to the app store.
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap', marginTop: 28 }}>
          <Link to="/pricing" style={styles.btnPrimary}>Get started →</Link>
          <Link to="/developers" style={styles.btnSecondary}>Technical details</Link>
        </div>
      </section>

      {/* Plain-language explanation */}
      <section aria-labelledby="explain-heading" style={styles.section}>
        <h2 id="explain-heading" style={styles.h2}>What does it actually do?</h2>
        <div style={styles.explainCard}>
          <p style={styles.explainText}>
            Your app has slots — places where a card, banner, or callout can appear.
            Usually those slots show a hardcoded message or nothing at all.
          </p>
          <p style={styles.explainText}>
            With Intyx, those slots can show <strong>different content for different users</strong>,
            based on things like who they are, what they've done in the app, what campaigns are running,
            or even what the weather is like outside.
          </p>
          <p style={{ ...styles.explainText, marginBottom: 0 }}>
            You control what shows up, when it shows up, and to whom — directly from the dashboard.
            No app update required.
          </p>
        </div>
      </section>

      {/* Use case blocks */}
      <section aria-labelledby="usecases-heading" style={styles.section}>
        <h2 id="usecases-heading" style={styles.h2}>What your team can do with it</h2>
        <div style={styles.usecaseGrid}>

          <div style={styles.usecaseCard}>
            <div style={styles.usecaseIcon}>⚡</div>
            <h3 style={styles.usecaseTitle}>Faster experiments</h3>
            <p style={styles.usecaseDesc}>
              Test a different headline, offer, or call-to-action for a segment of users.
              No code change. No release cycle. See results in hours, not weeks.
            </p>
          </div>

          <div style={styles.usecaseCard}>
            <div style={styles.usecaseIcon}>📣</div>
            <h3 style={styles.usecaseTitle}>Live campaign updates</h3>
            <p style={styles.usecaseDesc}>
              Push a Black Friday banner, a holiday message, or a flash sale card directly to users
              right now — even if the app was submitted to the store two months ago.
            </p>
          </div>

          <div style={styles.usecaseCard}>
            <div style={styles.usecaseIcon}>🎯</div>
            <h3 style={styles.usecaseTitle}>Show the right thing to the right user</h3>
            <p style={styles.usecaseDesc}>
              New users see an onboarding tip. Power users see a loyalty reward. Lapsed users
              see a win-back offer. Each person gets what makes sense for them — automatically.
            </p>
          </div>

          <div style={styles.usecaseCard}>
            <div style={styles.usecaseIcon}>🔄</div>
            <h3 style={styles.usecaseTitle}>No app release required</h3>
            <p style={styles.usecaseDesc}>
              Content changes happen server-side. Your development team ships the app once with
              the widget slot in place — after that, your team controls what appears in it.
            </p>
          </div>

        </div>
      </section>

      {/* Benefits */}
      <section aria-labelledby="benefits-heading" style={styles.section}>
        <h2 id="benefits-heading" style={styles.h2}>Why teams use it</h2>
        <div style={styles.benefitList}>
          {[
            {
              icon: '🚀',
              title: 'Faster iteration',
              desc: 'Cut the feedback loop from weeks (write → review → release → wait for adoption) down to hours. Update messaging on the fly based on what you learn.',
            },
            {
              icon: '🧩',
              title: 'Adaptive content',
              desc: 'Content that adapts to the user\'s context feels more relevant — not generic. Users who see content relevant to them are more likely to engage.',
            },
            {
              icon: '✂️',
              title: 'Segmentation without messy rules',
              desc: 'Instead of maintaining a tangle of if/else conditions in your codebase, define segments once in the dashboard. The system handles routing.',
            },
          ].map((b) => (
            <div key={b.title} style={styles.benefitCard}>
              <span style={{ fontSize: 28, marginRight: 16, flexShrink: 0 }}>{b.icon}</span>
              <div>
                <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 6 }}>{b.title}</div>
                <div style={{ fontSize: 14, color: 'var(--text-muted)', lineHeight: 1.6 }}>{b.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Common questions */}
      <section aria-labelledby="faq-heading" style={styles.section}>
        <h2 id="faq-heading" style={styles.h2}>Common questions</h2>
        <div style={styles.faqList}>
          {[
            {
              q: 'Why not just use Firebase Remote Config?',
              a: 'Remote Config gives you raw key/value pairs. You still have to write all the UI logic yourself and manage which values go to which users. Intyx handles the full widget — selection, content, layout type, and rendering — in one call.',
            },
            {
              q: 'What happens if it fails?',
              a: 'If the widget request fails or returns nothing, the slot stays empty. No crash, no error screen. Your app works exactly as before — just without the dynamic content in that slot.',
            },
            {
              q: 'Does my dev team need to maintain this?',
              a: 'Once the widget slot is placed in the app, your product team can manage content from the dashboard without developer involvement. New widget templates do require a developer to add them.',
            },
            {
              q: 'Who is this for?',
              a: 'Small-to-medium mobile teams building Flutter apps who want faster content iteration and basic segmentation without building a custom content management layer from scratch.',
            },
          ].map((item) => (
            <div key={item.q} style={styles.faqCard}>
              <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 8 }}>{item.q}</div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.7 }}>{item.a}</div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section style={{ textAlign: 'center', paddingTop: 48 }}>
        <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 12 }}>Ready to try it?</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 28, fontSize: 15 }}>
          Talk to your dev team about adding the widget slot, then take it from there.
        </p>
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link to="/pricing" style={styles.btnPrimary}>View Plans →</Link>
          <Link to="/developers" style={styles.btnSecondary}>Developer docs</Link>
        </div>
      </section>

    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  badge: { display: 'inline-block', fontSize: 13, fontWeight: 500, color: '#6366f1', background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.25)', borderRadius: 20, padding: '6px 16px', marginBottom: 20 },
  h1: { fontSize: 'clamp(28px, 4vw, 44px)' as unknown as number, fontWeight: 800, lineHeight: 1.2, letterSpacing: '-0.02em', marginBottom: 16, marginTop: 12 },
  subtitle: { fontSize: 17, color: 'var(--text-muted)', maxWidth: 600, margin: '0 auto', lineHeight: 1.6 },
  section: { paddingTop: 56, paddingBottom: 8 },
  h2: { fontSize: 24, fontWeight: 700, marginBottom: 24 },
  explainCard: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '24px 28px', maxWidth: 700, margin: '0 auto' },
  explainText: { fontSize: 15, color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: 16 },
  usecaseGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 16 },
  usecaseCard: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '22px 22px 18px' },
  usecaseIcon: { fontSize: 28, marginBottom: 12 },
  usecaseTitle: { fontSize: 15, fontWeight: 700, marginBottom: 8 },
  usecaseDesc: { fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6, margin: 0 },
  benefitList: { display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 700, margin: '0 auto' },
  benefitCard: { display: 'flex', alignItems: 'flex-start', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '18px 20px' },
  faqList: { display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 700, margin: '0 auto' },
  faqCard: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '18px 20px' },
  btnPrimary: { display: 'inline-flex', alignItems: 'center', padding: '11px 26px', fontSize: 14, fontWeight: 600, color: '#fff', background: '#6366f1', borderRadius: 'var(--radius-sm)', border: 'none', textDecoration: 'none', transition: 'background 0.2s' },
  btnSecondary: { display: 'inline-flex', alignItems: 'center', padding: '11px 26px', fontSize: 14, fontWeight: 600, color: 'var(--text)', background: 'transparent', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', textDecoration: 'none' },
};
