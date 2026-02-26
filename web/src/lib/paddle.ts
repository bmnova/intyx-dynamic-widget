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
let checkoutReject: ((err: Error) => void) | null = null;
let paddleInitialized = false;

function storeEventResult(eventData: PaddleEvent): void {
  // Log all events for debugging
  console.info('[Paddle] event:', eventData.name, eventData.data);

  if (eventData.name === 'checkout.completed') {
    isCompletedOrClosed = true;
    lastCheckoutStatus = 'completed';
    lastCheckoutEventData = eventData.data ?? null;
    if (checkoutResolve) {
      checkoutResolve({ status: 'completed', data: lastCheckoutEventData });
      checkoutResolve = null;
      checkoutReject = null;
    }
  } else if (eventData.name === 'checkout.closed') {
    isCompletedOrClosed = true;
    lastCheckoutStatus = 'closed';
    lastCheckoutEventData = eventData.data ?? null;
    if (checkoutResolve) {
      checkoutResolve({ status: 'closed', data: lastCheckoutEventData });
      checkoutResolve = null;
      checkoutReject = null;
    }
  } else if (eventData.name === 'checkout.error') {
    console.error('[Paddle] checkout.error event:', eventData.data);
    if (checkoutReject) {
      const errMsg =
        (eventData.data as { message?: string })?.message ||
        'Paddle checkout error';
      checkoutReject(new Error(`Paddle: ${errMsg}`));
      checkoutResolve = null;
      checkoutReject = null;
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

  const existing = document.getElementById('paddle-cdn-script') as HTMLScriptElement | null;
  if (existing) {
    // Script tag exists (e.g. from index.html) but may still be loading — wait for it
    return new Promise((resolve, reject) => {
      if (window.Paddle) { resolve(); return; }
      existing.addEventListener('load', () => resolve(), { once: true });
      existing.addEventListener('error', () => reject(new Error('Paddle CDN script failed to load')), { once: true });
    });
  }

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
  // Paddle.Initialize() can only be called once per page — guard against double calls
  if (paddleInitialized) return;

  const cfg = getPaddleConfig();
  if (!cfg || !cfg.publishableToken) {
    console.warn('[Paddle] init: config not available');
    return;
  }
  if (!window.Paddle) {
    await loadPaddleScript();
  }
  // Re-check after await in case another call already initialized
  if (paddleInitialized) return;
  paddleInitialized = true;

  const env = (cfg.env || 'sandbox').toLowerCase();
  // Environment.set() is only for sandbox — omit for production per Paddle docs
  if (env !== 'production') {
    window.Paddle!.Environment.set(env);
  }
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
  if (!cfg?.priceIds) throw new Error('Paddle price IDs are missing from config');
  const priceId =
    cfg.priceIds[planKey] || cfg.priceIds.monthly || Object.values(cfg.priceIds)[0];
  if (!priceId) {
    throw new Error(`No Paddle price ID found for plan: ${planKey}`);
  }
  const items = [{ priceId, quantity: 1 }];
  const customer = email ? { email } : undefined;

  if (!window.Paddle) await initPaddle();

  console.info('[Paddle] Opening checkout — env:', cfg.env, 'priceId:', priceId);

  return new Promise((resolve, reject) => {
    checkoutResolve = resolve;
    checkoutReject = reject;
    try {
      window.Paddle!.Checkout.open({
        items,
        ...(customer && { customer }),
        customData: { ...customData },
      });
    } catch (err) {
      console.error('[Paddle] Checkout.open threw:', err);
      checkoutResolve = null;
      checkoutReject = null;
      reject(err instanceof Error ? err : new Error(String(err)));
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
