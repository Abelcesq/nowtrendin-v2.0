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

async function post<T>(path: string, body: any): Promise<T> {
  const r = await fetch(`${ENGINE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(body),
  })
  if (!r.ok) throw new Error(`${path} → HTTP ${r.status}`)
  return r.json() as Promise<T>
}

// Per-item Signal Analysis (held-out, reproducible narrative; formula-confidential, measurement-only).
export interface SignalAnalysis {
  title?: string; kind?: string; item?: string; headline?: string
  facts?: { label: string; value: string }[]
  sections?: { heading: string; body: string }[]
  disclaimer?: string; generated?: string; available?: boolean
}

export interface LedgerSummary {
  status: string
  hitRate?: number; naiveHitRate?: number
  avgLead?: number; medianLead?: number; maxLead?: number
  total?: number; led?: number; sameDay?: number; lagged?: number
  falsePositives?: number; pending?: number; smallSample?: boolean
  // Pre-broken split of LAGGED: near = races run and lost; preBroken = Google broke
  // out >grace before our first sighting (never a race). Blended hitRate counts BOTH.
  laggedNear?: number | null; preBroken?: number | null
  trackedRaceHitRate?: number | null; trackedRaceSample?: number | null
  // Match validity of the LED wins (independent Wikipedia referee).
  ledCorroborated?: number | null; ledUncorroborated?: number | null
  ledUnchecked?: number | null; ledAmbiguousQuery?: number | null
  best?: { topic: string; leadDays: number; refereeCorroborated?: number | null; queryAmbiguous?: number | null }[]
}

export interface LedgerRow {
  topic_key: string; topic_display: string
  detection_date?: string; detection_score?: number
  breakout_date?: string; breakout_multiple?: number
  lead_time_days?: number | null; verdict?: string
  validated_at?: string; provider?: string
  // Match-validity metadata (rows resolved before 2026-07-07 carry nulls = unchecked)
  pre_broken?: boolean
  sweep_query?: string | null
  query_ambiguous?: number | null
  referee_corroborated?: number | null
}

// Money Gradient ledger — validated by realized EOD price direction (FMP), NOT Google Trends.
export interface MarketLedgerSummary {
  status: string
  ground_truth?: string; distinct_from?: string
  move_threshold_pct?: number; timeout_days?: number
  resolved?: number; pending?: number; confirmed?: number; not_confirmed?: number; no_move?: number
  confirm_rate_pct?: number | null; median_lead_days?: number | null
  by_flow?: Record<string, { confirmed: number; resolved: number; confirm_rate_pct: number | null }>
  small_sample?: boolean; note?: string
}

export interface MarketLedgerRow {
  ticker?: string; coin?: string; name?: string; detection_date?: string; flow?: string
  detection_score?: number; money_movement?: number; price_at_detection?: number; price_at_move?: number
  price_change_pct?: number | null; move_date?: string
  lead_time_days?: number | null; verdict?: string; validated_at?: string
}

// ── Entity grouping (Board 2026-07-15, display-only): confirmed fragment keys
// fold under their canonical entity SERVER-side. Every score is that key's OWN
// measured score — constituents are never summed, blended, or maxed.
export interface EntityConstituent {
  topic_key: string; topic_display?: string
  overall_score?: number; detection_score?: number; confidence_score?: number
  nowtrendin_score?: number; signal_stage?: string
  total_mentions?: number; category?: string
}
export interface EntityGroup {
  constituents?: EntityConstituent[]
  grouped_keys?: string[]
  evidence_note?: string
  // detail-only:
  role?: 'canonical' | 'constituent'
  canonical_key?: string
  shared_evidence_sample?: string
}

export interface TopicRow {
  topic_key: string; topic_display: string; category?: string
  current_stage?: string; overall_score?: number
  detection_score?: number; confidence_score?: number
  nowtrendin_score?: number   // N — internal "Now Trending" demand metric
  total_mentions?: number; last_seen_at?: string; is_anomaly?: number
  entity_group?: EntityGroup
}

// ── Market Signal (the finance-native dual score — same data the mobile Market
// tab renders, via /risk/scores). The Market Gradient is distinct from attention:
// detection = analyst sentiment + smart-money positioning; tier vocab is
// ELEVATED / ACTIVE / BUILDING / ROUTINE / DORMANT (NOT BREAKOUT/STRONG). ──
export interface MarketComponent { score: number | null; feeds?: string; z?: number; not_applicable?: boolean }
export interface MarketGradient {
  detection?: number; confidence?: number; gap?: number
  tier?: string; gap_state?: string; interpretation?: string
  leverage_health?: number | null; calibrating?: boolean
  components?: Record<string, MarketComponent>
  // Display-only coverage caveat (positioning inputs absent → not a confirmed quiet market)
  data_coverage?: 'full' | 'partial' | 'insufficient'; absent_inputs?: number; total_inputs?: number
  // Coverage LANE — covered / halted_microcap / macro_theme. na_components = inputs
  // structurally inapplicable to this instrument (excluded from score + coverage).
  lane?: string; lane_label?: string; na_components?: string[]
  // Market Signal v2.0 (the Money Gradient) — present ONLY when MARKET_SIGNAL_V2 is on.
  // When present, Detection→Money Movement, Confidence→Market Confirmation, and flow
  // (the factual IN/OUT direction) + leverage facts surface. Absent → v1 labels (flag off).
  model_version?: string
  money_movement?: number; market_confirmation?: number
  flow?: 'inflow' | 'outflow' | 'neutral'
  // D8 (2026-07-20): true when EVERY money-movement input is absent/degenerate → money_movement
  // served null; render "Market-Confirmation-only", never a money read wearing a measured badge.
  money_data_absent?: boolean; composite_note?: string; unmeasured_in_composite?: number
  leverage_facts?: { company_leverage_health?: number | null; note?: string }
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

// ── Crypto Money Gradient (the crypto sibling of Market Signal) — Money Movement (D, crypto-
// exposure proxy Dark Matter) vs Market Confirmation (M, coin price/volume), per-coin flow.
// Same dual-ring shape as MarketGradient so it renders consistently. Flag-gated (CRYPTO_SIGNAL). ──
export interface CryptoComponent { score: number | null; feeds?: string; z?: number | null; baseline_relative?: boolean }
export interface CryptoCoin {
  coin: string; item_name: string; item_key?: string; section?: string; model_version?: string
  money_movement?: number; market_confirmation?: number
  detection?: number; confidence?: number; gap?: number
  tier?: string; detection_level?: string; confidence_level?: string
  gap_state?: string; interpretation?: string; calibrating?: boolean
  flow?: 'inflow' | 'outflow' | 'neutral' | 'no_data' | 'mixed' | 'divergent'
  money_data_absent?: boolean; composite_note?: string   // D8: null money read → market-confirmation only
  components?: Record<string, CryptoComponent>
  price?: { last_close?: number; change_7d_pct?: number | null; change_30d_pct?: number | null; trend?: string; as_of?: string } | null
  dark_matter?: { coverage?: string; flow?: string; intensity?: number; proxies_covered?: number } | null
  detection_fp?: string; confidence_fp?: string; disclaimer?: string
}
export interface CryptoFeed {
  available: boolean; held_out?: boolean; status?: string; note?: string
  model?: string; section?: string; coins: CryptoCoin[]; count?: number; disclaimer?: string
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
  // Money Gradient ledger (distinct ground truth: realized EOD price direction, FMP).
  marketAccuracy: () => get<MarketLedgerSummary>('/market/accuracy'),
  marketAccuracyDetail: () =>
    get<{ rows: MarketLedgerRow[]; count: number }>('/market/accuracy/detail?limit=500'),
  // Crypto accuracy ledger — validated by realized COIN price direction (FMP crypto + AV).
  cryptoAccuracy: () => get<MarketLedgerSummary>('/crypto/accuracy'),
  cryptoAccuracyDetail: () =>
    get<{ rows: MarketLedgerRow[]; count: number }>('/crypto/accuracy/detail?limit=500'),
  historyRecent: (window = '7d', limit = 80) =>
    get<{ window: string; count: number; results: HistoryRow[] }>(
      `/history/recent?window=${window}&limit=${limit}`),
  // The WHOLE History window, fetched 100 at a time (engine serves O(1) slices from
  // its prewarmed superset). onBatch fires after each page so the list paints
  // progressively instead of waiting on one ~2MB payload.
  historyAll: async (window = '7d', onBatch?: (rows: HistoryRow[], done: boolean) => void): Promise<HistoryRow[]> => {
    const all: HistoryRow[] = []; const PAGE = 100; let offset = 0;
    for (let i = 0; i < 100; i++) {
      const d = await get<{ total: number; results: HistoryRow[] }>(
        `/history/recent?window=${window}&limit=${PAGE}&offset=${offset}`);
      const batch = d.results || []; all.push(...batch); offset += PAGE;
      const done = batch.length < PAGE || all.length >= (d.total ?? all.length);
      onBatch?.(all.slice(), done);
      if (done) break;
    }
    return all;
  },
  historyAnalysis: (key: string, topic = '') =>
    get<{ available: boolean; direction?: string; short?: string; full?: string; citations?: string[]; reason?: string }>(
      `/history/${encodeURIComponent(key)}/analysis${topic ? `?topic=${encodeURIComponent(topic)}` : ''}`),
  // Crypto Money Gradient (flag-gated CRYPTO_SIGNAL; held-out research until live).
  crypto: () => get<CryptoFeed>('/crypto'),
  cryptoDetail: (coin: string) => get<CryptoCoin>(`/crypto/${encodeURIComponent(coin)}`),
  // Per-item Signal Analysis — POST the item the rail already has; engine attaches the matching
  // accuracy-ledger report and returns the held-out, reproducible narrative.
  analysis: (kind: 'trend' | 'market' | 'crypto' | 'ledger', item: any) =>
    post<SignalAnalysis>(`/analysis/${kind}`, { item }),
  risk: (limit = 200) => get<{ count: number; results: RiskRow[] }>(`/risk/scores?limit=${limit}`),
  // The WHOLE Market universe, fetched 100 at a time (engine serves O(1) slices from
  // its prewarmed superset). onBatch fires after each page so the table paints
  // progressively despite the rich per-instrument payloads.
  riskAll: async (onBatch?: (rows: RiskRow[], done: boolean) => void): Promise<RiskRow[]> => {
    const all: RiskRow[] = []; const PAGE = 100; let offset = 0;
    for (let i = 0; i < 100; i++) {
      const d = await get<{ total: number; results: RiskRow[] }>(
        `/risk/scores?limit=${PAGE}&offset=${offset}`);
      const batch = d.results || []; all.push(...batch); offset += PAGE;
      const done = batch.length < PAGE || all.length >= (d.total ?? all.length);
      onBatch?.(all.slice(), done);
      if (done) break;
    }
    return all;
  },
  ledgerDetail: (verdict = '') =>
    get<{ status: string; count: number; rows: LedgerRow[] }>(
      `/accuracy/ledger/detail?limit=500${verdict ? `&verdict=${verdict}` : ''}`),
  topics: (limit = 200, category = '') =>
    get<{ count: number; topics: TopicRow[] }>(
      `/topics?limit=${limit}${category ? `&category=${encodeURIComponent(category)}` : ''}`),
  // One page of the grid (engine serves O(1) slices). `total` says when it's complete.
  topicsPage: (limit = 100, offset = 0, category = '') =>
    get<{ count: number; total: number; topics: TopicRow[] }>(
      `/topics?limit=${limit}&offset=${offset}${category ? `&category=${encodeURIComponent(category)}` : ''}`),
  // The WHOLE grid, fetched 100 at a time (no cap, no giant payload). Optional
  // onBatch fires after each page so the UI can paint progressively.
  topicsAll: async (category = '', onBatch?: (rows: TopicRow[], done: boolean) => void): Promise<TopicRow[]> => {
    const all: TopicRow[] = []; const PAGE = 100; let offset = 0;
    for (let i = 0; i < 200; i++) {
      const d = await get<{ total: number; topics: TopicRow[] }>(
        `/topics?limit=${PAGE}&offset=${offset}${category ? `&category=${encodeURIComponent(category)}` : ''}`);
      const batch = d.topics || []; all.push(...batch); offset += PAGE;
      const done = batch.length < PAGE || all.length >= (d.total ?? all.length);
      onBatch?.(all.slice(), done);
      if (done) break;
    }
    return all;
  },
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
