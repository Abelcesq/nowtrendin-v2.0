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
