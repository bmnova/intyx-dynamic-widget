// Backend API base URL — change this for production
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://intyx-dynamic-widget-production.up.railway.app';

// Paddle (web payments)
const parsePriceIds = (raw) => {
  if (!raw) return {};
  try {
    const v = typeof raw === 'string' ? JSON.parse(raw) : raw;
    return v && typeof v === 'object' ? v : {};
  } catch {
    return {};
  }
};

export const PADDLE_CONFIG = {
  env: import.meta.env.VITE_PADDLE_ENV || 'sandbox',
  publishableToken: import.meta.env.VITE_PADDLE_PUBLISHABLE_TOKEN || '',
  priceIds: parsePriceIds(import.meta.env.VITE_PADDLE_PRICE_IDS),
};

// Admin dashboard secret — must match INTYX_SERVER_API_KEY on the backend.
// Leave empty to disable the /admin page.
export const ADMIN_SECRET = import.meta.env.VITE_ADMIN_SECRET || '';
