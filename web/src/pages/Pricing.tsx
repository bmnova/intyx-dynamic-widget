import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL, PADDLE_CONFIG } from '../config';
import Toast from '../components/Toast';
import * as paddle from '../lib/paddle';
import type { Plan } from '../types';

interface PricingPlan {
  id: Plan | 'enterprise';
  name: string;
  price: number;
  period: string;
  description: string;
  features: string[];
  cta: string;
  popular: boolean;
}

const PLANS: PricingPlan[] = [
  {
    id: 'starter',
    name: 'Starter',
    price: 0,
    period: 'free',
    description: 'Ideal to try it out',
    features: [
      '3 widget types',
      '1,000 MAU',
      'Community support',
      'Basic analytics',
    ],
    cta: 'Start Free',
    popular: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 49,
    period: '/mo',
    description: 'For growing apps',
    features: [
      '10 widget types (all)',
      '50,000 MAU',
      'AI agent suggestions',
      'ColorScheme integration',
      'Trigger system',
      'Priority support',
    ],
    cta: 'Choose Pro',
    popular: true,
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 199,
    period: '/mo',
    description: 'For scale',
    features: [
      'Unlimited widgets',
      'Unlimited MAU',
      'Custom widget types',
      'Custom AI model fine-tune',
      'SLA guarantee',
      'Dedicated support',
      'On-premise option',
    ],
    cta: 'Contact Us',
    popular: false,
  },
];

interface ToastState {
  type: 'error' | 'success' | 'info';
  message: string;
}

const hasPaddle =
  PADDLE_CONFIG.publishableToken && Object.keys(PADDLE_CONFIG.priceIds).length > 0;

export default function Pricing() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState<string | null>(null);
  const [toast, setToast] = useState<ToastState | null>(null);
  const [paddleReady, setPaddleReady] = useState(false);

  useEffect(() => {
    if (!hasPaddle) return;
    paddle.setPaddleConfig(PADDLE_CONFIG);
    paddle
      .loadPaddleScript()
      .then(() => paddle.initPaddle())
      .then(() => setPaddleReady(true))
      .catch(console.warn);
  }, []);

  const createLicenseAndRedirect = async (planId: string, email = '') => {
    const res = await fetch(`${API_BASE_URL}/api/licenses`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plan: planId, email: email || undefined }),
    });
    if (!res.ok) {
      const err: { error?: string } = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Could not create license');
    }
    const data: { api_key: string } = await res.json();
    localStorage.setItem('intyx_api_key', data.api_key);
    localStorage.setItem('intyx_plan', planId);
    localStorage.setItem('intyx_purchased_at', new Date().toISOString());
    navigate('/dashboard');
  };

  const handlePurchase = async (planId: string) => {
    setLoading(planId);

    try {
      if (planId === 'starter') {
        await createLicenseAndRedirect(planId);
        return;
      }

      if (hasPaddle && paddleReady) {
        const result = await paddle.openCheckout({
          planKey: planId,
          customData: { plan: planId },
        });

        if (result.status === 'completed') {
          const data = result.data as { customer?: { email?: string }; customer_email?: string } | undefined;
          const email = data?.customer?.email || data?.customer_email || '';
          await createLicenseAndRedirect(planId, email);
        } else {
          setToast({ type: 'info', message: 'Checkout was closed. You can try again when ready.' });
        }
        return;
      }

      await createLicenseAndRedirect(planId);
    } catch (err) {
      console.error('Purchase failed:', err);
      setToast({ type: 'error', message: (err as Error).message || 'Something went wrong. Please try again.' });
    } finally {
      setLoading(null);
    }
  };

  return (
    <main id="main-content" style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px' }}>
      <section aria-labelledby="pricing-heading" style={styles.hero}>
        <h1 id="pricing-heading" style={styles.h1}>Simple Pricing</h1>
        <p style={styles.subtitle}>
          Choose a plan based on your project size. Upgrade or cancel anytime.
        </p>
      </section>

      <section aria-label="Pricing plans">
        <div style={styles.grid}>
          {PLANS.map((plan) => (
            <article
              key={plan.id}
              aria-label={`${plan.name} plan`}
              style={{
                ...styles.card,
                ...(plan.popular ? styles.cardPopular : {}),
              }}
            >
              {plan.popular && <div aria-label="Most popular plan" style={styles.popularBadge}>Popular</div>}
              <h2 style={styles.planName}>{plan.name}</h2>
              <p style={styles.planDesc}>{plan.description}</p>
              <div style={styles.priceRow}>
                <span style={styles.price}>
                  {plan.price === 0 ? 'Free' : `$${plan.price}`}
                </span>
                {plan.price > 0 && (
                  <span style={styles.period}>{plan.period}</span>
                )}
              </div>
              <button
                aria-label={`${plan.cta} — ${plan.name} plan`}
                aria-busy={loading === plan.id}
                style={{
                  ...styles.btn,
                  ...(plan.popular ? styles.btnPopular : styles.btnDefault),
                  opacity: loading === plan.id ? 0.7 : 1,
                }}
                onClick={() => handlePurchase(plan.id)}
                disabled={loading !== null}
              >
                {loading === plan.id ? 'Processing...' : plan.cta}
              </button>
              <ul aria-label={`${plan.name} features`} style={styles.features}>
                {plan.features.map((f) => (
                  <li key={f} style={styles.feature}>
                    <span aria-hidden="true" style={styles.check}>✓</span> {f}
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>

      <div style={styles.notice}>
        <span aria-hidden="true" style={{ fontSize: 18 }}>💳</span>
        <p style={{ color: 'var(--text-muted)', fontSize: 14 }}>
          {hasPaddle
            ? <><strong style={{ color: 'var(--text)' }}>Paddle</strong> ile güvenli ödeme.</>
            : <>Ödemeler <strong style={{ color: 'var(--text)' }}>Paddle</strong> üzerinden. <code>VITE_PADDLE_PUBLISHABLE_TOKEN</code> ve <code>VITE_PADDLE_PRICE_IDS</code> ayarlayın.</>}
        </p>
      </div>

      <div style={{ height: 80 }} />

      {toast && (
        <Toast
          type={toast.type}
          message={toast.message}
          onClose={() => setToast(null)}
        />
      )}
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
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
