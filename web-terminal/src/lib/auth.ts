// Terminal auth — talks to the SAME Django JWT backend the mobile app uses,
// so accounts, tiers, and entitlements are centralized across all platforms.
const BACKEND =
  (import.meta as any).env?.VITE_BACKEND_URL ||
  'https://nowtrendin-backend-acb79c396814.herokuapp.com'

export type TierID = 'consumer' | 'business' | 'enterprise'

export interface User {
  id: string; name: string; email: string
  tier: TierID | null
  tokensRemaining: number; gradeTokens: number
}

const ACCESS = 'nt_access', REFRESH = 'nt_refresh'
export const getToken = () => localStorage.getItem(ACCESS)
function setTokens(access?: string, refresh?: string) {
  if (access) localStorage.setItem(ACCESS, access)
  if (refresh) localStorage.setItem(REFRESH, refresh)
}
export function clearTokens() { localStorage.removeItem(ACCESS); localStorage.removeItem(REFRESH) }

async function call(path: string, opts: RequestInit = {}, auth = false): Promise<any> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json', ...(opts.headers as any) }
  if (auth) { const t = getToken(); if (t) headers.Authorization = `Bearer ${t}` }
  const r = await fetch(`${BACKEND}${path}`, { ...opts, headers })
  const body = await r.json().catch(() => ({}))
  if (!r.ok) throw Object.assign(new Error(body.detail || `HTTP ${r.status}`), { status: r.status, data: body })
  return body
}

function normalizeUser(u: any): User {
  return {
    id: String(u.id), name: u.name, email: u.email,
    tier: (u.tier ?? null) as TierID | null,
    tokensRemaining: u.tokensRemaining ?? 0,
    gradeTokens: u.gradeTokens ?? 0,
  }
}

export async function login(email: string, password: string): Promise<User> {
  const d = await call('/api/auth/login/', { method: 'POST', body: JSON.stringify({ email, password }) })
  setTokens(d.access, d.refresh)
  return normalizeUser(d.user)
}

export async function fetchMe(): Promise<User | null> {
  if (!getToken()) return null
  try { const d = await call('/api/auth/me/', {}, true); return normalizeUser(d.user) }
  catch { return null }
}

export async function loginWithGoogle(idToken: string): Promise<User> {
  const d = await call('/api/auth/google/', { method: 'POST', body: JSON.stringify({ id_token: idToken }) })
  setTokens(d.access, d.refresh)
  return normalizeUser(d.user)
}

export function logout() { clearTokens() }

// Account management — SAME Django endpoints the mobile profile screen uses, so
// edits propagate across web, desktop, and mobile.
export async function updateProfile(fields: { name?: string; email?: string }): Promise<User> {
  const d = await call('/api/auth/me/', { method: 'PATCH', body: JSON.stringify(fields) }, true)
  return normalizeUser(d.user ?? d)
}
export async function changePassword(currentPassword: string, newPassword: string) {
  return call('/api/auth/change-password/', {
    method: 'POST',
    body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
  }, true)
}

// Enterprise "Pull Trends" — fresh attention collect, token-metered by the
// backend (1 token). Same endpoint the mobile app uses, so behaviour matches.
export const pullTrends = () =>
  call('/api/pull-trends/', { method: 'POST' }, true) as Promise<any>

// ── Watchlists — backend-synced per-user lists (same API the mobile app uses),
// so the SAME lists appear on web, desktop, and mobile. Items hold key/display/
// kind only; the view looks up live scores by key. ──
export type WatchKind = 'topic' | 'market'
export interface WatchItem { id: number; key: string; display: string; kind: WatchKind; added_at: string }
export interface WatchlistT { id: number; name: string; created_at: string; items: WatchItem[] }

export const listWatchlists = () => call('/api/watchlists/', {}, true) as Promise<WatchlistT[]>
export const createWatchlist = (name: string) =>
  call('/api/watchlists/', { method: 'POST', body: JSON.stringify({ name }) }, true) as Promise<WatchlistT>
export const renameWatchlist = (id: number, name: string) =>
  call(`/api/watchlists/${id}/`, { method: 'PATCH', body: JSON.stringify({ name }) }, true) as Promise<WatchlistT>
export const deleteWatchlist = (id: number) =>
  call(`/api/watchlists/${id}/`, { method: 'DELETE' }, true)
export const addWatchItem = (id: number, item: { key: string; display?: string; kind?: WatchKind }) =>
  call(`/api/watchlists/${id}/items/`, { method: 'POST', body: JSON.stringify(item) }, true) as Promise<WatchItem>
export const removeWatchItem = (id: number, itemId: number) =>
  call(`/api/watchlists/${id}/items/${itemId}/`, { method: 'DELETE' }, true)

// ── Tier-gating — mirrors constants/tiers.ts so entitlements are identical
// across platforms. The engine/backend remain the source of truth; this only
// gates UI affordances. ──
const FEATURES: Record<TierID, Set<string>> = {
  consumer: new Set(['view']),
  business: new Set(['view', 'search']),
  enterprise: new Set(['view', 'search', 'query', 'export', 'api']),
}
export function canAccess(tier: TierID | null, feature: string): boolean {
  return !!tier && FEATURES[tier].has(feature)
}
export const TIER_LABEL: Record<TierID, string> = {
  consumer: 'Consumer', business: 'Business', enterprise: 'Enterprise',
}
