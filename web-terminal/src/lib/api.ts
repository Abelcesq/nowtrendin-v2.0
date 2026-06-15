// Engine client for the institutional terminal. Reads the public engine
// endpoints directly (scores/topics/categories/ledger). Auth-gated and
// write endpoints come later via the backend.
const ENGINE =
  (import.meta as any).env?.VITE_ENGINE_URL ||
  'https://nowtrendin-e62dcb9ecb69.herokuapp.com'

async function get<T>(path: string): Promise<T> {
  const r = await fetch(`${ENGINE}${path}`, { headers: { Accept: 'application/json' } })
  if (!r.ok) throw new Error(`${path} → HTTP ${r.status}`)
  return r.json() as Promise<T>
}

export interface LedgerSummary {
  status: string
  hitRate?: number; naiveHitRate?: number
  avgLead?: number; medianLead?: number; maxLead?: number
  total?: number; led?: number; sameDay?: number; lagged?: number
  falsePositives?: number; pending?: number; smallSample?: boolean
  best?: { topic: string; leadDays: number }[]
}

export interface LedgerRow {
  topic_key: string; topic_display: string
  detection_date?: string; detection_score?: number
  breakout_date?: string; breakout_multiple?: number
  lead_time_days?: number | null; verdict?: string
  validated_at?: string; provider?: string
}

export interface TopicRow {
  topic_key: string; topic_display: string; category?: string
  current_stage?: string; overall_score?: number
  detection_score?: number; confidence_score?: number
  total_mentions?: number; last_seen_at?: string; is_anomaly?: number
}

export const api = {
  ledger: () => get<LedgerSummary>('/accuracy/ledger'),
  ledgerDetail: (verdict = '') =>
    get<{ status: string; count: number; rows: LedgerRow[] }>(
      `/accuracy/ledger/detail?limit=500${verdict ? `&verdict=${verdict}` : ''}`),
  topics: (limit = 200, category = '') =>
    get<{ count: number; topics: TopicRow[] }>(
      `/topics?limit=${limit}${category ? `&category=${encodeURIComponent(category)}` : ''}`),
  categories: () =>
    get<{ categories: { key: string; label: string; count: number }[] }>('/categories'),
  score: (key: string) => get<any>(`/scores/${encodeURIComponent(key)}`),
}
