import { useState } from 'react';
import Toast from '../components/Toast';
import { API_BASE_URL } from '../config';

export default function LiveEventSignup() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [toast, setToast] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = email.trim().toLowerCase();
    if (!trimmed) return;

    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/email-signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: trimmed, source: 'live_event' }),
      });
      const data = await res.json();

      if (!res.ok) {
        setToast({ type: 'error', message: data.error || 'Something went wrong.' });
        return;
      }

      setSubmitted(true);
      if (data.already_registered) {
        setToast({ type: 'info', message: 'This email is already registered.' });
      } else {
        setToast({ type: 'success', message: 'Successfully subscribed! We\'ll notify you when we go live.' });
      }
    } catch {
      setToast({ type: 'error', message: 'Connection error. Please try again.' });
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ maxWidth: 640, margin: '0 auto', padding: '0 24px' }}>
      {toast && <Toast type={toast.type} message={toast.message} onClose={() => setToast(null)} />}

      <section style={styles.hero}>
        <div style={styles.badge}>Live Event</div>
        <h1 style={styles.h1}>
          Don't want to<br />
          <span style={{ color: '#6366f1' }}>miss the live event?</span>
        </h1>
        <p style={styles.subtitle}>
          Drop your email and we'll let you know when we go live.
          Never miss a thing!
        </p>
      </section>

      {!submitted ? (
        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.inputWrap}>
            <input
              type="email"
              required
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              aria-label="Your email address"
              style={styles.input}
            />
            <button
              type="submit"
              disabled={loading}
              style={{
                ...styles.btn,
                opacity: loading ? 0.6 : 1,
                cursor: loading ? 'not-allowed' : 'pointer',
              }}
            >
              {loading ? 'Subscribing...' : 'Notify Me'}
            </button>
          </div>
          <p style={styles.privacy}>
            Only used for live notifications. We never send spam.
          </p>
        </form>
      ) : (
        <div style={styles.successCard}>
          <div style={{ fontSize: 48, marginBottom: 16 }}>&#10003;</div>
          <h2 style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>You're in!</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: 15, lineHeight: 1.6 }}>
            We'll send a notification to <strong style={{ color: 'var(--text)' }}>{email.trim().toLowerCase()}</strong> when
            we go live.
          </p>
          <button
            onClick={() => { setSubmitted(false); setEmail(''); }}
            style={styles.btnSecondary}
          >
            Add another email
          </button>
        </div>
      )}

      {/* Info cards */}
      <section style={styles.infoSection}>
        <div style={styles.infoGrid}>
          {[
            { icon: '\u{1F514}', title: 'Instant Alert', desc: 'Get notified the moment we go live — straight to your inbox.' },
            { icon: '\u{1F512}', title: 'Privacy First', desc: 'Your email is only used for live notifications and is never shared with third parties.' },
            { icon: '\u{26A1}', title: 'Never Miss Out', desc: 'Be the first to know about announcements, live events, and exclusive content.' },
          ].map((item) => (
            <div key={item.title} style={styles.infoCard}>
              <span style={{ fontSize: 28, display: 'block', marginBottom: 12 }}>{item.icon}</span>
              <h3 style={{ fontSize: 15, fontWeight: 700, marginBottom: 6 }}>{item.title}</h3>
              <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6, margin: 0 }}>{item.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  hero: {
    textAlign: 'center',
    paddingTop: 80,
    paddingBottom: 32,
  },
  badge: {
    display: 'inline-block',
    fontSize: 13,
    fontWeight: 600,
    color: '#ef4444',
    background: 'rgba(239,68,68,0.12)',
    border: '1px solid rgba(239,68,68,0.25)',
    borderRadius: 20,
    padding: '6px 16px',
    marginBottom: 24,
    letterSpacing: '0.03em',
  },
  h1: {
    fontSize: 'clamp(28px, 4vw, 42px)' as unknown as number,
    fontWeight: 800,
    lineHeight: 1.2,
    letterSpacing: '-0.02em',
    marginBottom: 16,
  },
  subtitle: {
    fontSize: 16,
    color: 'var(--text-muted)',
    lineHeight: 1.7,
    maxWidth: 480,
    margin: '0 auto',
  },
  form: {
    marginTop: 8,
  },
  inputWrap: {
    display: 'flex',
    gap: 12,
    maxWidth: 480,
    margin: '0 auto',
  },
  input: {
    flex: 1,
    padding: '14px 18px',
    fontSize: 15,
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)',
    color: 'var(--text)',
    outline: 'none',
    transition: 'border-color 0.2s',
  },
  btn: {
    padding: '14px 28px',
    fontSize: 15,
    fontWeight: 600,
    color: '#fff',
    background: '#6366f1',
    border: 'none',
    borderRadius: 'var(--radius-sm)',
    transition: 'background 0.2s, opacity 0.2s',
    whiteSpace: 'nowrap',
  },
  btnSecondary: {
    marginTop: 20,
    padding: '10px 24px',
    fontSize: 14,
    fontWeight: 600,
    color: 'var(--text)',
    background: 'transparent',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius-sm)',
    cursor: 'pointer',
  },
  privacy: {
    textAlign: 'center',
    fontSize: 12,
    color: '#71717a',
    marginTop: 12,
  },
  successCard: {
    textAlign: 'center',
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: '40px 32px',
    marginTop: 8,
  },
  infoSection: {
    paddingTop: 48,
    paddingBottom: 60,
  },
  infoGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: 16,
  },
  infoCard: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: 20,
  },
};
