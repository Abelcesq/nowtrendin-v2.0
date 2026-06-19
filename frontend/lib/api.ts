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
  put: (path: string, body?: object) =>
    request(path, { method: 'PUT', body: JSON.stringify(body ?? {}) }),
  patch: (path: string, body?: object) =>
    request(path, { method: 'PATCH', body: JSON.stringify(body ?? {}) }),
  delete: (path: string) => request(path, { method: 'DELETE' }),
};

// Customizable dashboard + Favorites — same /api/dashboard/ the web terminal uses,
// so layout + favorites are identical across web, desktop, and mobile.
export interface Favorite { id: string; label: string; section: 'trends' | 'market' | 'history' | 'watchlist'; filter?: string; kind?: 'topic' | 'market'; color?: string }
export const dashboardApi = {
  get: () => api.get('/api/dashboard/') as Promise<{ tiles: any[]; favorites: Favorite[] }>,
  saveFavorites: (favorites: Favorite[]) => api.put('/api/dashboard/', { favorites }) as Promise<{ favorites: Favorite[] }>,
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
  // The signed-in user's grade history (12 months, no token charge). ?q= search.
  gradeHistory: (q?: string) => api.get(`/api/grade/history/${q ? `?q=${encodeURIComponent(q)}` : ''}`),
  // All topics graded by any member (deduped). No token charge. ?q= search.
  gradedAll: (q?: string) => api.get(`/api/grade/all/${q ? `?q=${encodeURIComponent(q)}` : ''}`),
};

export const alertsApi = {
  list: () => api.get('/api/alerts/'),
  create: (data: object) => api.post('/api/alerts/', data),
  update: (id: number, data: object) => api.patch(`/api/alerts/${id}/`, data),
  remove: (id: number) => api.delete(`/api/alerts/${id}/`),
};

// Backend-synced watchlists — the SAME /api/watchlists/ the web/desktop terminal
// uses, so a member's lists are identical across every platform. Items store
// key/display/kind only; the live Detection/Confidence is looked up client-side.
export const watchlistApi = {
  list: () => api.get('/api/watchlists/'),
  create: (name: string) => api.post('/api/watchlists/', { name }),
  rename: (id: number, name: string) => api.patch(`/api/watchlists/${id}/`, { name }),
  update: (id: number, fields: { notify_email?: boolean; notify_sms?: boolean; notify_threshold?: number }) =>
    api.patch(`/api/watchlists/${id}/`, fields),
  remove: (id: number) => api.delete(`/api/watchlists/${id}/`),
  addItem: (id: number, item: { key: string; display?: string; kind?: 'topic' | 'market' }) =>
    api.post(`/api/watchlists/${id}/items/`, item),
  removeItem: (id: number, itemId: number) => api.delete(`/api/watchlists/${id}/items/${itemId}/`),
};

export const signalsApi = {
  list: (params?: Record<string, string>) => {
    const q = params ? `?${new URLSearchParams(params).toString()}` : '';
    return api.get(`/api/signals/${q}`);
  },
  detail: (id: string) => api.get(`/api/signals/${id}/`),
};
