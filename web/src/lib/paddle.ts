/**
 * Paddle payment integration for web.
 * Requires Paddle CDN script to be loaded (e.g. in index.html or via loadPaddleScript).
 */

import type { PaddleConfig, CheckoutResult } from '../types';

declare global {
  interface Window {
    Paddle?: {
      Environment: { set(env: string): void };
      Initialize(opts: { token: string; eventCallback: (e: PaddleEvent) => void }): void;
      Checkout: { open(opts: Record<string, unknown>): void };
      PricePreview(opts: Record<string, unknown>): Promise<PaddlePreviewResponse>;
    };
  }
}

interface PaddleEvent {
  name: string;
  data?: unknown;
}

interface PaddlePreviewResponse {
  data?: {
    details?: {
      lineItems?: PaddleLineItem[];
      totals?: Record<string, string>;
      formattedTotals?: Record<string, string>;
      currencyCode?: string;
    };
  };
}

interface PaddleLineItem {
  price?: {
    unitPrice?: { currencyCode?: string };
    billingCycle?: { interval?: string };
  };
  totals?: Record<string, string>;
  formattedTotals?: Record<string, string>;
}

export interface PaddleProduct {
  key: string;
  priceId: string;
  price: number;
  currency: string;
  priceString?: string;
  billing_interval: string;
}

const PADDLE_CDN = 'https://cdn.paddle.com/paddle/v2/paddle.js';

let isCompletedOrClosed = false;
let lastCheckoutStatus: 'completed' | 'closed' | null = null;
let lastCheckoutEventData: unknown = null;
let checkoutResolve: ((value: CheckoutResult) => void) | null = null;

function storeEventResult(eventData: PaddleEvent): void {
  if (eventData.name === 'checkout.completed' || eventData.name === 'checkout.closed') {
    isCompletedOrClosed = true;
    lastCheckoutStatus = eventData.name === 'checkout.completed' ? 'completed' : 'closed';
    lastCheckoutEventData = eventData.data ?? null;
    if (checkoutResolve) {
      checkoutResolve({ status: lastCheckoutStatus, data: lastCheckoutEventData });
      checkoutResolve = null;
    }
  }
}

let __paddleConfig: PaddleConfig | null = null;

export function setPaddleConfig(config: PaddleConfig): void {
  if (!config || typeof config !== 'object') return;
  const priceIds =
    config.priceIds && typeof config.priceIds === 'object' ? { ...config.priceIds } : {};
  __paddleConfig = Object.freeze({
    env: (config.env || 'sandbox').toLowerCase(),
    publishableToken: String(config.publishableToken || ''),
    priceIds,
  });
}

function getPaddleConfig(): PaddleConfig | null {
  return __paddleConfig;
}

export function loadPaddleScript(): Promise<void> {
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

export async function initPaddle(): Promise<void> {
  const cfg = getPaddleConfig();
  if (!cfg || !cfg.publishableToken) {
    console.warn('[Paddle] init: config not available');
    return;
  }
  if (!window.Paddle) {
    await loadPaddleScript();
  }
  const env = (cfg.env || 'sandbox').toLowerCase();
  window.Paddle!.Environment.set(env);
  window.Paddle!.Initialize({
    token: cfg.publishableToken,
    eventCallback: storeEventResult,
  });
  console.info('[Paddle] Initialized, env:', env);
}

export async function openCheckout({
  email,
  planKey,
  customData = {},
}: {
  email?: string;
  planKey: string;
  customData?: Record<string, string>;
}): Promise<CheckoutResult> {
  isCompletedOrClosed = false;
  lastCheckoutStatus = null;
  lastCheckoutEventData = null;

  const cfg = getPaddleConfig();
  if (!cfg?.priceIds) throw new Error('Missing Paddle price IDs in config');
  const priceId =
    cfg.priceIds[planKey] || cfg.priceIds.monthly || Object.values(cfg.priceIds)[0];
  const items = [{ priceId, quantity: 1 }];
  const customer = email ? { email } : undefined;

  if (!window.Paddle) await initPaddle();

  return new Promise((resolve) => {
    checkoutResolve = resolve;
    try {
      window.Paddle!.Checkout.open({
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

export async function fetchProducts(): Promise<PaddleProduct[]> {
  if (!window.Paddle) await initPaddle();
  const cfg = getPaddleConfig();
  if (!cfg?.priceIds) {
    console.error('[Paddle] Missing priceIds in config');
    return [];
  }

  const products: PaddleProduct[] = [];
  for (const [key, priceId] of Object.entries(cfg.priceIds)) {
    try {
      const preview = await window.Paddle!.PricePreview({ items: [{ priceId, quantity: 1 }] });
      const details = preview?.data?.details;
      const li =
        Array.isArray(details?.lineItems) && details.lineItems.length > 0
          ? details.lineItems[0]
          : null;
      const totals = li?.totals || details?.totals || {};
      const formattedTotals = li?.formattedTotals || details?.formattedTotals || {};
      const priceNode = li?.price || {};
      const billingCycle = priceNode?.billingCycle || {};
      const totalCents = Number(totals.total ?? 0);
      const amount = isNaN(totalCents) ? 0 : totalCents / 100;
      const currencyCode =
        priceNode?.unitPrice?.currencyCode || details?.currencyCode || 'USD';
      const formatted =
        typeof formattedTotals.total === 'string' ? formattedTotals.total : undefined;
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
