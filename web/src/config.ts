import type { PaddleConfig } from './types';

// Backend API base URL — change this for production
export const API_BASE_URL: string =
  import.meta.env.VITE_API_URL || 'https://intyx-dynamic-widget-production.up.railway.app';

// Paddle (web payments)
const parsePriceIds = (raw: unknown): Record<string, string> => {
  if (!raw) return {};
  try {
    const v = typeof raw === 'string' ? JSON.parse(raw) : raw;
    return v && typeof v === 'object' ? (v as Record<string, string>) : {};
  } catch {
    return {};
  }
};

export const PADDLE_CONFIG: PaddleConfig = {
  env: (import.meta.env.VITE_PADDLE_ENV as string) || 'sandbox',
  publishableToken: (import.meta.env.VITE_PADDLE_PUBLISHABLE_TOKEN as string) || '',
  priceIds: parsePriceIds(import.meta.env.VITE_PADDLE_PRICE_IDS),
};

// Admin dashboard secret — must match INTYX_SERVER_API_KEY on the backend.
export const ADMIN_SECRET: string = (import.meta.env.VITE_ADMIN_SECRET as string) || '';
