/**
 * Paddle payment integration for web (adapted from Everpixel paddle_wrapper.js).
 * Requires Paddle CDN script to be loaded (e.g. in index.html or via loadPaddleScript).
 */

const PADDLE_CDN = 'https://cdn.paddle.com/paddle/v2/paddle.js';

let isCompletedOrClosed = false;
let lastCheckoutStatus = null;
let lastCheckoutEventData = null;
let checkoutResolve = null;

function storeEventResult(eventData) {
  if (eventData.name === 'checkout.completed' || eventData.name === 'checkout.closed') {
    isCompletedOrClosed = true;
    lastCheckoutStatus = eventData.name === 'checkout.completed' ? 'completed' : 'closed';
    lastCheckoutEventData = eventData.data || null;
    if (checkoutResolve) {
      checkoutResolve({ status: lastCheckoutStatus, data: lastCheckoutEventData });
      checkoutResolve = null;
    }
  }
}

let __paddleConfig = null;

/**
 * Set Paddle config (env, publishableToken, priceIds).
 * @param {{ env?: string, publishableToken: string, priceIds: Record<string, string> }} config
 */
export function setPaddleConfig(config) {
  if (!config || typeof config !== 'object') return;
  const priceIds = config.priceIds && typeof config.priceIds === 'object' ? { ...config.priceIds } : {};
  __paddleConfig = Object.freeze({
    env: (config.env || 'sandbox').toLowerCase(),
    publishableToken: String(config.publishableToken || ''),
    priceIds,
  });
}

function getPaddleConfig() {
  return __paddleConfig;
}

/**
 * Load Paddle CDN script dynamically. Call once before init.
 * @returns {Promise<void>}
 */
export function loadPaddleScript() {
  if (typeof window === 'undefined') return Promise.resolve();
  if (window.Paddle) return Promise.resolve();
  const existing = document.getElementById('paddle-cdn-script');
  if (existing) return Promise.resolve();

  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.id = 'paddle-cdn-script';
    script.src = PADDLE_CDN;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Paddle CDN script failed to load'));
    document.head.appendChild(script);
  });
}

/**
 * Initialize Paddle SDK. Call after loadPaddleScript and setPaddleConfig.
 * @returns {Promise<void>}
 */
export async function initPaddle() {
  const cfg = getPaddleConfig();
  if (!cfg || !cfg.publishableToken) {
    console.warn('[Paddle] init: config not available');
    return;
  }
  if (!window.Paddle) {
    await loadPaddleScript();
  }
  const env = (cfg.env || 'sandbox').toLowerCase();
  window.Paddle.Environment.set(env);
  window.Paddle.Initialize({
    token: cfg.publishableToken,
    eventCallback: storeEventResult,
  });
  console.info('[Paddle] Initialized, env:', env);
}

/**
 * Open Paddle checkout for a plan.
 * @param {{ email?: string, planKey: string, customData?: Record<string, string> }} options
 * @returns {Promise<{ status: 'completed' | 'closed', data?: unknown }>}
 */
export async function openCheckout({ email, planKey, customData = {} }) {
  isCompletedOrClosed = false;
  lastCheckoutStatus = null;
  lastCheckoutEventData = null;

  const cfg = getPaddleConfig();
  if (!cfg?.priceIds) throw new Error('Missing Paddle price IDs in config');
  const priceId = cfg.priceIds[planKey] || cfg.priceIds.monthly || Object.values(cfg.priceIds)[0];
  const items = [{ priceId, quantity: 1 }];
  const customer = email ? { email } : undefined;

  if (!window.Paddle) await initPaddle();

  return new Promise((resolve) => {
    checkoutResolve = resolve;
    try {
      window.Paddle.Checkout.open({
        items,
        ...(customer && { customer }),
        customData: { ...customData },
      });
    } catch (err) {
      console.error('[Paddle] Checkout failed:', err);
      checkoutResolve = null;
      resolve({ status: 'closed' });
    }
  });
}

/**
 * Fetch product/price preview from Paddle for configured priceIds.
 * @returns {Promise<Array<{ key: string, priceId: string, price: number, currency: string, priceString?: string, billing_interval: string }>>}
 */
export async function fetchProducts() {
  if (!window.Paddle) await initPaddle();
  const cfg = getPaddleConfig();
  if (!cfg?.priceIds) {
    console.error('[Paddle] Missing priceIds in config');
    return [];
  }

  const products = [];
  for (const [key, priceId] of Object.entries(cfg.priceIds)) {
    try {
      const preview = await window.Paddle.PricePreview({ items: [{ priceId, quantity: 1 }] });
      const details = preview?.data?.details;
      const li = Array.isArray(details?.lineItems) && details.lineItems.length > 0 ? details.lineItems[0] : null;
      const totals = li?.totals || details?.totals || {};
      const formattedTotals = li?.formattedTotals || details?.formattedTotals || {};
      const priceNode = li?.price || {};
      const billingCycle = priceNode?.billingCycle || {};
      const totalCents = Number(totals.total ?? 0);
      const amount = isNaN(totalCents) ? 0 : totalCents / 100;
      const currencyCode = priceNode?.unitPrice?.currencyCode || details?.currencyCode || 'USD';
      const formatted = typeof formattedTotals.total === 'string' ? formattedTotals.total : undefined;
      let billingInterval = (billingCycle.interval || '').toString().toLowerCase();
      if (!billingInterval) {
        const kLower = String(key).toLowerCase();
        if (kLower.includes('month')) billingInterval = 'month';
        else if (kLower.includes('year')) billingInterval = 'year';
        else billingInterval = 'one_time';
      }
      products.push({
        key,
        priceId,
        price: amount,
        currency: currencyCode,
        priceString: formatted,
        billing_interval: billingInterval,
      });
    } catch (e) {
      console.warn('PricePreview failed for', priceId, e);
    }
  }
  return products;
}
