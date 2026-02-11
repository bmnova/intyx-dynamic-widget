import { Link } from 'react-router-dom';
import WidgetCard from '../components/WidgetCard';

const WIDGETS = [
  { icon: '🖼️', title: 'Hero Image', description: 'Tam genislikte hero resim, overlay baslik ve CTA butonu', tag: 'UI' },
  { icon: '🏷️', title: 'Promotional', description: 'Kampanya/promosyon karti - rozet, indirim, aksiyon', tag: 'Kampanya' },
  { icon: '🎠', title: 'Carousel', description: 'Yatay kaydirmali coklu icerik karti', tag: 'UI' },
  { icon: '⏱️', title: 'Countdown Banner', description: 'Geri sayim zamanlayici ile kampanya banner\'i', tag: 'Kampanya' },
  { icon: '☁️', title: 'Contextual', description: 'Hava durumu, burc gibi baglamsal bilgi karti', tag: 'AI Driven' },
  { icon: '📢', title: 'Informational', description: 'Bilgilendirme ve duyuru karti - severity destegi', tag: 'Bildirim' },
  { icon: '⚡', title: 'Functional', description: 'Aksiyon odakli kart - buton(lar) ve deep link', tag: 'Aksiyon' },
  { icon: '🔗', title: 'Clickable Image', description: 'Tiklanabilir resim, baslik ve yonlendirme linki', tag: 'UI' },
  { icon: '📝', title: 'Title + Subtitle', description: 'Baslik, alt baslik ve resim iceren kart', tag: 'UI' },
  { icon: '🎯', title: 'Icon Text Action', description: 'Ikon, baslik, aciklama ve aksiyon butonu', tag: 'Aksiyon' },
];

const FEATURES = [
  { icon: '🤖', title: 'AI Agent Kararlari', desc: 'Hangi widget\'in nerede gorunecegine AI agent karar verir. Context\'e gore otomatik secim.' },
  { icon: '🎨', title: 'ColorScheme Uyumu', desc: 'Host uygulamanin ColorScheme\'ini parametre olarak ver, widget\'lar otomatik uyumlansin.' },
  { icon: '📐', title: 'Responsive Layout', desc: 'Width, height, padding, margin, aspect ratio — her sey JSON\'dan konfigurasyon.' },
  { icon: '🔥', title: 'Firebase + MCP', desc: 'Firestore backend, MCP server ile AI entegrasyonu. Realtime widget yonetimi.' },
];

export default function Landing() {
  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px' }}>
      {/* Hero */}
      <section style={styles.hero}>
        <div style={styles.badge}>Flutter Dynamic Widget System</div>
        <h1 style={styles.h1}>
          AI-Driven Widget'lar,<br />
          <span style={{ color: '#6366f1' }}>Tek Satirda</span>
        </h1>
        <p style={styles.subtitle}>
          Flutter uygulamana dinamik, AI tarafindan yonetilen widget'lar ekle.
          Agent context'e bakarak hangi widget'i, hangi parametrelerle gosterecegine kendisi karar versin.
        </p>
        <div style={styles.heroActions}>
          <Link to="/pricing" style={styles.btnPrimary}>
            Paketleri Incele →
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
        <h2 style={styles.h2}>Nasil Calisiyor?</h2>
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
        <h2 style={styles.h2}>Widget Katalogu</h2>
        <p style={{ color: 'var(--text-muted)', textAlign: 'center', marginBottom: 40 }}>
          10 hazir widget tipi. Agent bunlardan uygun olani secer, parametreleri doldurur.
        </p>
        <div style={styles.grid}>
          {WIDGETS.map((w) => (
            <WidgetCard key={w.title} {...w} />
          ))}
        </div>
      </section>

      {/* CTA */}
      <section style={{ ...styles.section, textAlign: 'center', paddingBottom: 80 }}>
        <h2 style={styles.h2}>Hemen Basla</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: 32 }}>
          Paket sec, API key'ini al, Flutter projenize ekle.
        </p>
        <Link to="/pricing" style={styles.btnPrimary}>
          Paketleri Gor →
        </Link>
      </section>

      {/* Footer */}
      <footer style={styles.footer}>
        <span style={{ color: '#71717a', fontSize: 13 }}>
          © 2026 Intyx. Tum haklari saklidir.
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
