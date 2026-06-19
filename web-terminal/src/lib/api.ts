// Engine client for the institutional terminal. Reads the public engine
// endpoints directly (scores/topics/categories/ledger). Auth-gated and
// write endpoints come later via the backend.
// The dedicated v2.0 engine (separate from v1.0's). One database feeds all
// v2.0 surfaces (website, desktop, mobile) — this is that single source.
const ENGINE =
  (import.meta as any).env?.VITE_ENGINE_URL ||
  'https://nowtrendin-v2-engine-edcb10d44f91.herokuapp.com'

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
  nowtrendin_score?: number   // N — internal "Now Trending" demand metric
  total_mentions?: number; last_seen_at?: string; is_anomaly?: number
}

// ── Market Signal (the finance-native dual score — same data the mobile Market
// tab renders, via /risk/scores). The Market Gradient is distinct from attention:
// detection = analyst sentiment + smart-money positioning; tier vocab is
// ELEVATED / ACTIVE / BUILDING / ROUTINE / DORMANT (NOT BREAKOUT/STRONG). ──
export interface MarketComponent { score: number; feeds?: string; z?: number }
export interface MarketGradient {
  detection?: number; confidence?: number; gap?: number
  tier?: string; gap_state?: string; interpretation?: string
  leverage_health?: number | null; calibrating?: boolean
  components?: Record<string, MarketComponent>
}
export interface RiskRow {
  risk_topic: string; risk_display: string
  detection_score?: number; confidence_score?: number
  classification?: string; risk_stage?: string
  total_signals?: number; scored_at?: string
  percent_delta?: number | null; abnormality?: number | null
  baseline_cycles?: number; baseline_signals?: number; sufficient_baseline?: boolean
  baseline_status?: string; baseline_note?: string
  interpretation?: string; market_gradient?: MarketGradient
  positioning_score?: number; maturity?: string; maturity_note?: string
  source_provenance?: string
  components?: Record<string, number>
  diffusion?: Record<string, { count?: number; z?: number | null }>
  sustainability?: any; short_interest?: any; institutional_holdings?: any
  creator_coverage?: any; broadcast_coverage?: any; alpha_vantage?: any
  macro_leverage?: any
}

export interface HistoryPoint { t: string; overall: number; det: number; conf: number }
export interface HistoryRow {
  topic_key: string; topic_display: string; category?: string
  overall: number; det: number; conf: number; n: number
  stage?: string; is_anomaly?: boolean; scored_at?: string
  series: HistoryPoint[]; trend: 'up' | 'down' | 'flat'; slope: number
}

export const api = {
  ledger: () => get<LedgerSummary>('/accuracy/ledger'),
  historyRecent: (window = '7d', limit = 80) =>
    get<{ window: string; count: number; results: HistoryRow[] }>(
      `/history/recent?window=${window}&limit=${limit}`),
  historyAnalysis: (key: string, topic = '') =>
    get<{ available: boolean; direction?: string; short?: string; full?: string; citations?: string[]; reason?: string }>(
      `/history/${encodeURIComponent(key)}/analysis${topic ? `?topic=${encodeURIComponent(topic)}` : ''}`),
  risk: (limit = 200) => get<{ count: number; results: RiskRow[] }>(`/risk/scores?limit=${limit}`),
  ledgerDetail: (verdict = '') =>
    get<{ status: string; count: number; rows: LedgerRow[] }>(
      `/accuracy/ledger/detail?limit=500${verdict ? `&verdict=${verdict}` : ''}`),
  topics: (limit = 200, category = '') =>
    get<{ count: number; topics: TopicRow[] }>(
      `/topics?limit=${limit}${category ? `&category=${encodeURIComponent(category)}` : ''}`),
  categories: () =>
    get<{ categories: { key: string; label: string; count: number }[] }>('/categories'),
  score: (key: string) => get<any>(`/scores/${encodeURIComponent(key)}`),
  // Source-aware AI definition (short + full) — same /explainer the mobile app uses.
  explainer: (key: string) => get<{ available: boolean; short?: string; full?: string }>(
    `/explainer/${encodeURIComponent(key)}`),
  // Lazy trend-detail panels — same endpoints the mobile signal page uses.
  convergence: (key: string) => get<any>(`/convergence/${encodeURIComponent(key)}`),
  xsignal: (topic: string) => get<any>(`/signal-x/${encodeURIComponent(topic)}`),
  scoreHistory: (key: string) => get<any>(`/scores/${encodeURIComponent(key)}/score-history`),
  researchHistory: (key: string) => get<any>(`/scores/${encodeURIComponent(key)}/history`),
}
