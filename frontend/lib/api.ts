// Real API client for Now TrendIn 2.0 (Django on Heroku).
// Phase 1 uses mock auth (see lib/auth.ts) — these endpoints are wired in a later phase.
import * as SecureStore from './storage';

export const BASE_URL =
  process.env.EXPO_PUBLIC_API_URL ||
  'https://nowtrendin-backend-acb79c396814.herokuapp.com';

async function request(path: string, options: RequestInit = {}) {
  const token = await SecureStore.getItemAsync('access_token');
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw { status: res.status, data: body };
  }
  return res.json();
}

export const api = {
  get: (path: string) => request(path, { method: 'GET' }),
  post: (path: string, body?: object) =>
    request(path, { method: 'POST', body: JSON.stringify(body ?? {}) }),
  patch: (path: string, body?: object) =>
    request(path, { method: 'PATCH', body: JSON.stringify(body ?? {}) }),
  delete: (path: string) => request(path, { method: 'DELETE' }),
};

export const queryApi = {
  // Enterprise direct topic query (token-metered) → { found, result, tokensRemaining, detail }
  run: (topic: string) => api.post('/api/query/', { topic }),
  // Enterprise "Pull Trends" — fresh attention/diffusion collect (Apify Google Trends, X,
  // GitHub, HN, blogs, news APIs) → { status, message, tokensRemaining }. Token-metered.
  pullTrends: () => api.post('/api/pull-trends/', {}),
  // Enterprise "Pull Market" — fresh risk/financial collect (FINRA, OFR, WhaleWisdom 13F,
  // Finnhub, Alpha Vantage, Yahoo Finance, creator + broadcast YouTube). Token-metered.
  pullMarket: () => api.post('/api/pull-market/', {}),
  // Enterprise AI Grade — web research + proposed score (token-metered)
  grade: (topic: string) => api.post('/api/grade/', { topic }),
};

export const alertsApi = {
  list: () => api.get('/api/alerts/'),
  create: (data: object) => api.post('/api/alerts/', data),
  update: (id: number, data: object) => api.patch(`/api/alerts/${id}/`, data),
  remove: (id: number) => api.delete(`/api/alerts/${id}/`),
};

export const signalsApi = {
  list: (params?: Record<string, string>) => {
    const q = params ? `?${new URLSearchParams(params).toString()}` : '';
    return api.get(`/api/signals/${q}`);
  },
  detail: (id: string) => api.get(`/api/signals/${id}/`),
};
