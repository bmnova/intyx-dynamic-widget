// Backend API base URL — change this for production
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

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
