import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';

const PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    price: 0,
    period: 'ucretsiz',
    description: 'Denemek icin ideal',
    features: [
      '3 widget tipi',
      '1.000 MAU',
      'Topluluk destegi',
      'Temel analitik',
    ],
    cta: 'Ucretsiz Basla',
    popular: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 49,
    period: '/ay',
    description: 'Buyuyen uygulamalar icin',
    features: [
      '10 widget tipi (tumu)',
      '50.000 MAU',
      'AI agent oneriler',
      'ColorScheme entegrasyonu',
      'Trigger sistemi',
      'Oncelikli destek',
    ],
    cta: 'Pro Paketi Sec',
    popular: true,
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 199,
    period: '/ay',
    description: 'Olceklenen urunler icin',
    features: [
      'Sinirsiz widget',
      'Sinirsiz MAU',
      'Ozel widget tipleri',
      'Ozel AI model fine-tune',
      'SLA garantisi',
      'Dedicated destek',
      'On-premise secenegi',
    ],
    cta: 'Iletisime Gec',
    popular: false,
  },
];

export default function Pricing() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(null);

  const handlePurchase = async (planId) => {
    setLoading(planId);

    // TODO: Paddle entegrasyonu buraya gelecek
    // Paddle.Checkout.open({
    //   product: PADDLE_PRODUCT_IDS[planId],
    //   successCallback: (data) => { ... },
    // });

    try {
      const res = await fetch(`${API_BASE_URL}/api/licenses`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan: planId }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || 'Lisans olusturulamadi');
      }

      const data = await res.json();
      localStorage.setItem('intyx_api_key', data.api_key);
      localStorage.setItem('intyx_plan', planId);
      localStorage.setItem('intyx_purchased_at', new Date().toISOString());
      navigate('/dashboard');
    } catch (err) {
      console.error('License creation failed:', err);
      alert(err.message || 'Bir hata olustu, tekrar deneyin.');
    } finally {
      setLoading(null);
    }
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px' }}>
      <section style={styles.hero}>
        <h1 style={styles.h1}>Basit Fiyatlandirma</h1>
        <p style={styles.subtitle}>
          Projenin buyuklugune gore paket sec. Istedigin zaman yukselt veya iptal et.
        </p>
      </section>

      <div style={styles.grid}>
        {PLANS.map((plan) => (
          <div
            key={plan.id}
            style={{
              ...styles.card,
              ...(plan.popular ? styles.cardPopular : {}),
            }}
          >
            {plan.popular && <div style={styles.popularBadge}>Populer</div>}
            <h3 style={styles.planName}>{plan.name}</h3>
            <p style={styles.planDesc}>{plan.description}</p>
            <div style={styles.priceRow}>
              <span style={styles.price}>
                {plan.price === 0 ? 'Ucretsiz' : `$${plan.price}`}
              </span>
              {plan.price > 0 && (
                <span style={styles.period}>{plan.period}</span>
              )}
            </div>
            <button
              style={{
                ...styles.btn,
                ...(plan.popular ? styles.btnPopular : styles.btnDefault),
                opacity: loading === plan.id ? 0.7 : 1,
              }}
              onClick={() => handlePurchase(plan.id)}
              disabled={loading !== null}
            >
              {loading === plan.id ? 'Isleniyor...' : plan.cta}
            </button>
            <ul style={styles.features}>
              {plan.features.map((f) => (
                <li key={f} style={styles.feature}>
                  <span style={styles.check}>✓</span> {f}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Paddle placeholder notice */}
      <div style={styles.notice}>
        <span style={{ fontSize: 18 }}>💳</span>
        <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
          Odeme altyapisi olarak <strong style={{ color: 'var(--text)' }}>Paddle</strong> kullanilacaktir.
          Suanda demo modunda — satin alma islemleri simule edilir.
        </p>
      </div>

      <div style={{ height: 80 }} />
    </div>
  );
}

const styles = {
  hero: {
    textAlign: 'center',
    paddingTop: 60,
    paddingBottom: 40,
  },
  h1: {
    fontSize: 36,
    fontWeight: 800,
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 16,
    color: 'var(--text-muted)',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: 20,
    alignItems: 'start',
  },
  card: {
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: 32,
    position: 'relative',
  },
  cardPopular: {
    border: '2px solid #6366f1',
    background: 'linear-gradient(180deg, rgba(99,102,241,0.06) 0%, var(--bg-card) 40%)',
  },
  popularBadge: {
    position: 'absolute',
    top: -12,
    left: '50%',
    transform: 'translateX(-50%)',
    background: '#6366f1',
    color: '#fff',
    fontSize: 12,
    fontWeight: 600,
    padding: '4px 16px',
    borderRadius: 20,
  },
  planName: {
    fontSize: 20,
    fontWeight: 700,
    marginBottom: 4,
  },
  planDesc: {
    fontSize: 14,
    color: 'var(--text-muted)',
    marginBottom: 20,
  },
  priceRow: {
    display: 'flex',
    alignItems: 'baseline',
    gap: 4,
    marginBottom: 24,
  },
  price: {
    fontSize: 40,
    fontWeight: 800,
    letterSpacing: '-0.02em',
  },
  period: {
    fontSize: 16,
    color: 'var(--text-muted)',
  },
  btn: {
    width: '100%',
    padding: '12px 0',
    fontSize: 15,
    fontWeight: 600,
    borderRadius: 'var(--radius-sm)',
    border: 'none',
    marginBottom: 24,
    transition: 'opacity 0.2s',
  },
  btnPopular: {
    background: '#6366f1',
    color: '#fff',
  },
  btnDefault: {
    background: 'transparent',
    color: 'var(--text)',
    border: '1px solid var(--border)',
  },
  features: {
    listStyle: 'none',
    display: 'flex',
    flexDirection: 'column',
    gap: 12,
  },
  feature: {
    fontSize: 14,
    color: 'var(--text-muted)',
    display: 'flex',
    alignItems: 'center',
    gap: 10,
  },
  check: {
    color: '#22c55e',
    fontWeight: 700,
  },
  notice: {
    display: 'flex',
    alignItems: 'center',
    gap: 12,
    background: 'var(--bg-card)',
    border: '1px solid var(--border)',
    borderRadius: 'var(--radius)',
    padding: '16px 24px',
    marginTop: 40,
    maxWidth: 600,
    margin: '40px auto 0',
  },
};
