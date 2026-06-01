// Real API client for Now TrendIn 2.0 (Django on Heroku).
// Phase 1 uses mock auth (see lib/auth.ts) — these endpoints are wired in a later phase.
import * as SecureStore from 'expo-secure-store';

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

export const signalsApi = {
  list: (params?: Record<string, string>) => {
    const q = params ? `?${new URLSearchParams(params).toString()}` : '';
    return api.get(`/api/signals/${q}`);
  },
  detail: (id: string) => api.get(`/api/signals/${id}/`),
};
