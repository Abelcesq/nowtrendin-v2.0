// Client for the live Gradient Score engine (separate FastAPI service).
// Maps the engine's /scores response into our Signal model.
import { Signal, Stage, BreakdownGroup } from './signals';

export const GRADIENT_API =
  process.env.EXPO_PUBLIC_GRADIENT_API || 'https://nowtrendin-e62dcb9ecb69.herokuapp.com';

function normalizeStage(raw: string | undefined): Stage {
  const s = (raw || '').toUpperCase();
  if (s === 'WATCH') return 'WATCHING';
  if (['VIRAL', 'BREAKOUT', 'STRONG', 'EMERGING', 'WATCHING', 'MONITORING', 'DECAY'].includes(s)) {
    return s as Stage;
  }
  return 'MONITORING';
}

// Friendlier display names for specific engine component keys. "Gradient
// Strength" is really the niche-vs-mainstream concentration ratio — labeling it
// "Niche Concentration" stops it being confused with the headline Gradient Score
// (Detection/Confidence are the composites; this is one input to them).
const LABEL_OVERRIDES: Record<string, string> = {
  gradient_strength: 'Niche Concentration',
  nowtrendin_demand: 'Now Trending (internal demand)',
};

function prettify(key: string): string {
  const k = (key || '').toLowerCase();
  if (LABEL_OVERRIDES[k]) return LABEL_OVERRIDES[k];
  return key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

function mapGroups(cg: any, nVal?: number): BreakdownGroup[] | undefined {
  if (!cg || typeof cg !== 'object') return undefined;
  const groups: BreakdownGroup[] = [];
  for (const groupKey of Object.keys(cg)) {
    const g = cg[groupKey];
    if (!g) continue;
    const items = Object.keys(g.components || {}).map((compKey) => {
      const c = g.components[compKey];
      // The "now trending" N component (internal app demand) is computed and
      // served on every row as `nowtrendin_score`, but the engine's
      // component_groups structure still carries it as a hardcoded 0/pending
      // placeholder. Splice the real value in so it surfaces in the breakdown.
      if (compKey === 'nowtrendin_demand' && nVal != null && nVal > 0) {
        const v = Math.round(Number(nVal));
        return { label: prettify(compKey), value: v, conf: v, desc: c?.desc || undefined };
      }
      return {
        label: prettify(compKey),
        value: Math.round(Number(c?.det ?? 0)),
        conf: c?.conf != null ? Math.round(Number(c.conf)) : undefined,
        desc: c?.desc || undefined,
      };
    });
    groups.push({ title: g.label || prettify(groupKey), status: g.status, note: g.note, items });
  }
  return groups.length ? groups : undefined;
}

export function mapSignal(r: any): Signal {
  const det = Math.round(Number(r.detection_score ?? 0));
  const conf = Math.round(Number(r.confidence_score ?? 0));
  return {
    id: String(r.topic_key),
    topic: r.topic_display || r.topic_key,
    category: r.ai_tier_label || 'Signal',
    score: det,
    detection: det,
    confidence: conf,
    stage: normalizeStage(r.signal_stage),
    createdAt: Date.parse(r.scored_at) || Date.now(),
    // Earliest time this topic was scored — used for tier data-aging gating
    // (the latest scored_at is always recent because topics are re-scored each cycle).
    firstSeenAt: Date.parse(r.first_scored_at) || Date.parse(r.scored_at) || Date.now(),
    overall: r.overall_score != null ? Math.round(Number(r.overall_score)) : undefined,
    // Gap is the difference of the displayed (rounded) scores so it always
    // reconciles with DET/CONF. (The engine's stored heisenberg_gap can be
    // stale relative to floored/calibrated scores.)
    gap: Math.abs(det - conf),
    gapMeaning: r.gap_meaning || r.gap_label || undefined,
    whatToDo: r.what_to_do_action
      ? {
          action: r.what_to_do_action,
          instruction: r.what_to_do_instruction || undefined,
          detail: r.what_to_do_detail || undefined,
        }
      : undefined,
    why: r.why_this_matters || undefined,
    whatToWatch: r.what_to_watch || undefined,
    platforms: Array.isArray(r.platforms_active) ? r.platforms_active : [],
    groups: mapGroups(r.component_groups, r.nowtrendin_score != null ? Number(r.nowtrendin_score) : undefined),
    nowTrending: r.nowtrendin_score != null ? Math.round(Number(r.nowtrendin_score)) : undefined,
    maturityClass: r.calibration?.maturity_class ?? r.maturity_class ?? undefined,
    maturityBadge: r.calibration?.maturity_badge ?? undefined,
    maturityReason: r.calibration?.maturity_reason ?? r.maturity_reason ?? undefined,
    darkMatter: r.dark_matter_score != null ? Math.round(Number(r.dark_matter_score)) : undefined,
    firstTimerRatio: r.first_timer_ratio != null ? Number(r.first_timer_ratio) : undefined,
    engagementAsymmetry: r.engagement_asymmetry != null
      ? Boolean(Number(r.engagement_asymmetry))
      : (typeof r.engagement_asymmetry === 'boolean' ? r.engagement_asymmetry : undefined),
    aiTierLabel: r.ai_tier_label || undefined,
    aiTier: r.ai_tier || undefined,
    aiTierColour: r.ai_tier_colour || undefined,
    aiClassification: r.ai_classification || undefined,
    aiVelocity: r.ai_velocity_signal || undefined,
    scoreExplanation: typeof r.score_explanation === 'string' ? r.score_explanation : undefined,
    variations: Array.isArray(r.variations)
      ? r.variations.map((v: any) => ({
          topicKey: String(v.topic_key ?? ''),
          display: v.display ?? v.topic_key ?? '',
          tier: v.tier ?? undefined,
          tierLabel: v.tier_label ?? undefined,
          tierColour: v.tier_colour ?? undefined,
          velocity: v.velocity ?? undefined,
          typicalDetection: Math.round(Number(v.typical_detection ?? 0)),
          typicalConfidence: Math.round(Number(v.typical_confidence ?? 0)),
          isQueried: Boolean(v.is_queried),
          whyDifferent: v.why_different || undefined,
        }))
      : undefined,
    totalMentions: r.total_mentions != null ? Number(r.total_mentions) : undefined,
    timesScored: r.times_scored != null ? Number(r.times_scored) : undefined,
    isAnomaly: Boolean(r.is_anomaly ?? r.is_gravitational_anomaly),
  };
}

// Fetch all scored topics from the live engine.
export async function fetchScores(): Promise<Signal[]> {
  const res = await fetch(`${GRADIENT_API}/scores`, { headers: { Accept: 'application/json' } });
  if (!res.ok) throw new Error(`Gradient API ${res.status}`);
  const data = await res.json();
  const results = Array.isArray(data?.results) ? data.results : [];
  return results.map(mapSignal);
}

export interface ScoreHistoryRow {
  scoredAt: number;
  detection: number;
  confidence: number;
  overall: number;
  gap: number;
}

// Per-collection-run scoring events for a topic (newest first).
export async function fetchScoreHistory(topicKey: string): Promise<ScoreHistoryRow[]> {
  const res = await fetch(`${GRADIENT_API}/scores/${encodeURIComponent(topicKey)}/score-history`, {
    headers: { Accept: 'application/json' },
  });
  if (!res.ok) throw new Error(`Gradient API ${res.status}`);
  const d = await res.json();
  const rows = Array.isArray(d?.rows) ? d.rows : [];
  return rows.map((r: any) => ({
    scoredAt: Date.parse(r.scored_at) || Date.now(),
    detection: Math.round(Number(r.detection ?? 0)),
    confidence: Math.round(Number(r.confidence ?? 0)),
    overall: Math.round(Number(r.overall ?? 0)),
    gap: Math.round(Number(r.gap ?? 0)),
  }));
}

export interface RiskScore {
  key: string;
  display: string;
  detection: number;
  confidence: number;
  stage: string;
  action: string;
  interpretation: string;
  diffusion: { dark: number; expert: number; consumer: number; media: number; retail: number };
  totalSignals: number;
  sources: string[];
  firstSeenAt: number;
  maturity: string;
  maturityNote: string;
  components: Record<string, number>;
  baselineSignals?: number;
  baselineCycles?: number;
  abnormality?: number;     // % above (or below) the topic's own baseline
  baselineStatus?: string;  // INSUFFICIENT_HISTORY | BELOW_BASELINE | AT_BASELINE | ELEVATED_VS_SELF | SPIKE_VS_SELF
  baselineNote?: string;
  // ── Market Gradient (data-type Duality — the primary Market score) ──
  marketGradient?: {
    detection: number;             // leading/soft: analyst + positioning + baseline
    confidence: number;            // lagging/hard: fundamentals + price + macro
    tier: string;                  // ELEVATED | ACTIVE | BUILDING | ROUTINE | DORMANT
    gap: number;                   // detection − confidence
    components: {
      analyst_signal?: number | null;
      positioning_pressure?: number | null;
      baseline_abnormality?: number | null;
      fundamentals?: number | null;
      price_action?: number | null;
      macro_context?: number | null;
    };
    confidenceBasis?: string;
    interpretation?: string;
  };
  // ── Positioning engine (baseline-relative; now a component of the above) ──
  positioningScore?: number;       // 0–100 anomaly vs the item's own baseline
  classification?: string;         // CALIBRATING | ROUTINE | WATCH | ELEVATED | UNUSUAL
  headline?: string;
  narrative?: string;
  earlySignal?: boolean;
  percentDelta?: number | null;    // % vs baseline
  positioningCycles?: number;      // baseline cycles accumulated
  definition?: string;
  // diffusion (positioning shape): stage label -> { count, z }
  stages?: Record<string, { count: number; z: number | null }>;
  // Financial Sustainability (factual fundamentals; companies only)
  sustainability?: {
    score: number;
    label: string;
    sector?: string;
    sectorAdjustedScore?: number | null;
    sectorAdjustedLabel?: string;
    sectorExplanation?: string;
    profitability: number | null;
    liquidity: number | null;
    leverageHealth: number | null;
    leverageHealthSector?: number | null;
    ticker?: string;
    netProfitMargin?: number | null;
    roe?: number | null;
    currentRatio?: number | null;
    debtToEquity?: number | null;
    definition?: string;
  };
  // Meet Kevin retail-attention coverage (attributed data point; not advice)
  meetKevin?: {
    covered: boolean;
    count: number;
    latestTitle?: string;
    latestPublished?: string;
    latestUrl?: string;
    recent?: { title: string; published: string; url: string }[];
    channelUrl: string;
    note: string;
  };
  // FINRA short interest — leverage/distress indicator (companies only)
  shortInterest?: {
    shortPosition?: number | null;
    changePct?: number | null;
    daysToCover?: number | null;
    settlementDate?: string;
    label?: string;
    note?: string;
  };
  // OFR macro leverage / funding-stress context (shared)
  macroLeverage?: MacroLeverage;
  // WhaleWisdom 13F — institutional smart-money positioning (companies only)
  institutionalHoldings?: {
    holdersCount?: number | null;
    sharesHeld?: number | null;
    sharesChangePct?: number | null;
    sentiment?: string;
    label?: string;
    topHolders?: { name: string; shares?: number | null; changePct?: number | null }[];
  };
  // Retail finance creator coverage (Meet Kevin, Andrei Jikh, Graham Stephan, etc.)
  creatorCoverage?: {
    note: string;
    creators: { name: string; handle: string; covered: boolean; count: number;
                recent?: { title: string; published: string }[] }[];
  };
  // Broadcast / institutional media coverage (CNBC, Bloomberg, Reuters, BBC, etc.)
  broadcastCoverage?: {
    note: string;
    totalChannels: number;
    channels: { name: string; handle: string; region: string; covered: boolean;
                count: number; recent?: { title: string; published: string }[] }[];
  };
  // Alpha Vantage news/retail coverage (article volume + tone; attributed)
  alphaVantage?: {
    covered: boolean;
    articleCount: number;
    avgSentiment?: number | null;
    sentimentLabel?: string;
    recent?: { title: string; source: string; published: string }[];
    note: string;
  };
}

// OFR Short-Term Funding Monitor — systemic leverage + funding-stress overlay.
export interface MacroLeverage {
  asOf?: string;
  leverageLabel?: string;
  leverageScore?: number | null;
  repoVolumeUsd?: number | null;
  repoVolumeChangePct?: number | null;
  stressLabel?: string;
  repoSpreadBps?: number | null;
  source?: string;
  note?: string;
}

function mapMacro(m: any): MacroLeverage {
  return {
    asOf: m.as_of || undefined,
    leverageLabel: m.leverage?.label,
    leverageScore: m.leverage?.score ?? null,
    repoVolumeUsd: m.leverage?.repo_volume_usd ?? null,
    repoVolumeChangePct: m.leverage?.repo_volume_change_pct ?? null,
    stressLabel: m.funding_stress?.label,
    repoSpreadBps: m.funding_stress?.repo_rate_spread_bps ?? null,
    source: m.source,
    note: m.note,
  };
}

export async function fetchMacroLeverage(): Promise<MacroLeverage | null> {
  try {
    const res = await fetch(`${GRADIENT_API}/macro/leverage`, { headers: { Accept: 'application/json' } });
    if (!res.ok) return null;
    const d = await res.json();
    return d?.available ? mapMacro(d) : null;
  } catch {
    return null;
  }
}

// Risk Gradient Scores — emerging financial risks scored by diffusion stage.
export async function fetchRiskScores(): Promise<RiskScore[]> {
  const res = await fetch(`${GRADIENT_API}/risk/scores`, { headers: { Accept: 'application/json' } });
  if (!res.ok) throw new Error(`Risk API ${res.status}`);
  const d = await res.json();
  return (Array.isArray(d?.results) ? d.results : []).map((r: any) => ({
    key: String(r.risk_topic),
    display: r.risk_display || r.risk_topic,
    detection: Math.round(Number(r.detection_score ?? 0)),
    confidence: Math.round(Number(r.confidence_score ?? 0)),
    stage: r.risk_stage || 'BACKGROUND',
    action: r.risk_action || '',
    interpretation: r.interpretation || '',
    diffusion: {
      dark: r.diffusion?.stage_1_dark_positioning ?? 0,
      expert: r.diffusion?.stage_2_expert_warning ?? 0,
      consumer: r.diffusion?.stage_3_consumer_concern ?? 0,
      media: r.diffusion?.stage_4_media_coverage ?? 0,
      retail: r.diffusion?.stage_5_retail_amplify ?? 0,
    },
    totalSignals: r.total_signals ?? 0,
    sources: String(r.source_provenance || '')
      .split('·')
      .map((s: string) => s.trim())
      .filter(Boolean),
    firstSeenAt: Date.parse(r.first_scored_at) || Date.parse(r.scored_at) || Date.now(),
    maturity: r.maturity || '',
    maturityNote: r.maturity_note || '',
    components: r.components && typeof r.components === 'object' ? r.components : {},
    baselineSignals: r.baseline_signals != null ? Number(r.baseline_signals) : undefined,
    baselineCycles: r.baseline_cycles != null ? Number(r.baseline_cycles) : undefined,
    abnormality: r.abnormality != null ? Number(r.abnormality) : undefined,
    baselineStatus: r.baseline_status || undefined,
    baselineNote: r.baseline_note || undefined,
    // Market Gradient (data-type Duality) — primary Market score.
    marketGradient: r.market_gradient ? {
      detection: Number(r.market_gradient.detection ?? 0),
      confidence: Number(r.market_gradient.confidence ?? 0),
      tier: r.market_gradient.tier || 'DORMANT',
      gap: Number(r.market_gradient.gap ?? 0),
      components: r.market_gradient.components || {},
      confidenceBasis: r.market_gradient.confidence_basis || undefined,
      interpretation: r.market_gradient.interpretation || undefined,
    } : undefined,
    // Positioning (baseline-relative) fields — now a component of the above.
    positioningScore: r.positioning_score != null ? Math.round(Number(r.positioning_score)) : undefined,
    classification: r.classification || undefined,
    headline: r.headline || undefined,
    narrative: r.narrative || undefined,
    earlySignal: Boolean(r.early_signal),
    percentDelta: r.percent_delta != null ? Number(r.percent_delta) : null,
    positioningCycles: r.baseline_cycles != null ? Number(r.baseline_cycles) : undefined,
    definition: r.definition || undefined,
    stages: r.diffusion && typeof r.diffusion === 'object' && !Array.isArray(r.diffusion)
      ? r.diffusion : undefined,
    sustainability: r.sustainability ? {
      score: Math.round(Number(r.sustainability.score ?? 0)),
      label: r.sustainability.label || '',
      sector: r.sustainability.sector || undefined,
      sectorAdjustedScore: r.sustainability.sector_adjusted_score != null
        ? Math.round(Number(r.sustainability.sector_adjusted_score)) : null,
      sectorAdjustedLabel: r.sustainability.sector_adjusted_label || undefined,
      sectorExplanation: r.sustainability.sector_explanation || undefined,
      profitability: r.sustainability.profitability ?? null,
      liquidity: r.sustainability.liquidity ?? null,
      leverageHealth: r.sustainability.leverage_health ?? null,
      leverageHealthSector: r.sustainability.leverage_health_sector ?? null,
      ticker: r.sustainability.ticker || undefined,
      netProfitMargin: r.sustainability.metrics?.net_profit_margin_pct ?? null,
      roe: r.sustainability.metrics?.roe_pct ?? null,
      currentRatio: r.sustainability.metrics?.current_ratio ?? null,
      debtToEquity: r.sustainability.metrics?.debt_to_equity ?? null,
      definition: r.sustainability.definition || undefined,
    } : undefined,
    meetKevin: r.meet_kevin ? {
      covered: Boolean(r.meet_kevin.covered),
      count: Number(r.meet_kevin.count ?? 0),
      latestTitle: r.meet_kevin.latest_title || undefined,
      latestPublished: r.meet_kevin.latest_published || undefined,
      latestUrl: r.meet_kevin.latest_url || undefined,
      recent: Array.isArray(r.meet_kevin.recent) ? r.meet_kevin.recent : undefined,
      channelUrl: r.meet_kevin.channel_url || 'https://www.youtube.com/@MeetKevin',
      note: r.meet_kevin.note || '',
    } : undefined,
    creatorCoverage: r.creator_coverage ? {
      note: r.creator_coverage.note || '',
      creators: Array.isArray(r.creator_coverage.creators) ? r.creator_coverage.creators : [],
    } : undefined,
    shortInterest: r.short_interest && r.short_interest.available ? {
      shortPosition: r.short_interest.short_position ?? null,
      changePct: r.short_interest.change_pct ?? null,
      daysToCover: r.short_interest.days_to_cover ?? null,
      settlementDate: r.short_interest.settlement_date || undefined,
      label: r.short_interest.label || undefined,
      note: r.short_interest.note || undefined,
    } : undefined,
    macroLeverage: r.macro_leverage ? mapMacro(r.macro_leverage) : undefined,
    broadcastCoverage: r.broadcast_coverage ? {
      note: r.broadcast_coverage.note || '',
      totalChannels: r.broadcast_coverage.total_channels ?? 0,
      channels: Array.isArray(r.broadcast_coverage.channels)
        ? r.broadcast_coverage.channels.map((c: any) => ({
            name: c.name, handle: c.handle, region: c.region || '',
            covered: !!c.covered, count: c.count ?? 0,
            recent: Array.isArray(c.recent) ? c.recent : [],
          }))
        : [],
    } : undefined,
    institutionalHoldings: r.institutional_holdings && r.institutional_holdings.available ? {
      holdersCount: r.institutional_holdings.holders_count ?? null,
      sharesHeld: r.institutional_holdings.shares_held ?? null,
      sharesChangePct: r.institutional_holdings.shares_change_pct ?? null,
      sentiment: r.institutional_holdings.sentiment || undefined,
      label: r.institutional_holdings.label || undefined,
      topHolders: Array.isArray(r.institutional_holdings.top_holders)
        ? r.institutional_holdings.top_holders.map((h: any) => ({
            name: h.name, shares: h.shares ?? null, changePct: h.change_pct ?? null }))
        : undefined,
    } : undefined,
    alphaVantage: r.alpha_vantage ? {
      covered: Boolean(r.alpha_vantage.covered),
      articleCount: Number(r.alpha_vantage.article_count ?? 0),
      avgSentiment: r.alpha_vantage.avg_sentiment ?? null,
      sentimentLabel: r.alpha_vantage.sentiment_label || undefined,
      recent: Array.isArray(r.alpha_vantage.recent) ? r.alpha_vantage.recent : undefined,
      note: r.alpha_vantage.note || '',
    } : undefined,
  }));
}

export interface AccuracyReport {
  status: string;
  total?: number;
  led?: number;
  lagged?: number;
  hitRate?: number;
  avgLead?: number;
  medianLead?: number;
  maxLead?: number;
  best?: { topic: string; leadDays: number; multiple: number }[];
}

// The Accuracy Ledger — documented lead time vs Google Trends breakout.
export async function fetchAccuracy(): Promise<AccuracyReport> {
  const res = await fetch(`${GRADIENT_API}/accuracy/ledger`, { headers: { Accept: 'application/json' } });
  if (!res.ok) throw new Error(`Accuracy ${res.status}`);
  const d = await res.json();
  return {
    status: d.status,
    total: d.total_predictions,
    led: d.led_count,
    lagged: d.lagged_count,
    hitRate: d.hit_rate_pct,
    avgLead: d.avg_lead_time_days,
    medianLead: d.median_lead_time_days,
    maxLead: d.max_lead_time_days,
    best: (d.best_predictions || []).map((b: any) => ({ topic: b.topic, leadDays: b.lead_days, multiple: b.multiple })),
  };
}

export interface TopicExplainer {
  available: boolean;
  short?: string;
  full?: string;
}

// Evergreen plain-English explainer for a topic (cached server-side; ~free).
// Shown on trend cards (short) and the signal-detail Research section (full).
export async function fetchExplainer(topicKey: string, topicName?: string): Promise<TopicExplainer> {
  const q = topicName ? `?topic=${encodeURIComponent(topicName)}` : '';
  const res = await fetch(`${GRADIENT_API}/explainer/${encodeURIComponent(topicKey)}${q}`, { headers: { Accept: 'application/json' } });
  if (!res.ok) return { available: false };
  const d = await res.json();
  if (!d?.available) return { available: false };
  const clean = (s?: string) => (s || '').replace(/\[\d+\]/g, '').replace(/\s+\./g, '.').trim();
  return { available: true, short: clean(d.short), full: clean(d.full) };
}

export interface SignalIntegrity {
  score: number;
  classification: string; // AUTHENTIC | MIXED | SUSPICIOUS | MANUFACTURED | INSUFFICIENT_DATA
  multiplier: number;
  summary: string;
  components?: { network?: number; temporal?: number; account?: number; engagement?: number; incentiveRisk?: number };
  flags?: { source: string; flag: string }[];
}

export interface XSignal {
  available: boolean;
  role?: string;
  stage?: string;
  interpretation?: string;
  intraGradient?: number;
  velocity?: number;
  xContribution?: number;
  integrity?: SignalIntegrity;
}

// Live X (Twitter) dual-role analysis for a topic (gated on X_BEARER_TOKEN).
export async function fetchXSignal(topic: string): Promise<XSignal> {
  const res = await fetch(`${GRADIENT_API}/signal-x/${encodeURIComponent(topic)}`, { headers: { Accept: 'application/json' } });
  if (!res.ok) return { available: false };
  const d = await res.json();
  if (!d?.available) return { available: false };
  const diff = d.diffusion || {};
  const si = d.signal_integrity;
  return {
    available: true,
    role: d.x_role || diff.role,
    stage: d.x_stage || diff.stage,
    interpretation: diff.interpretation,
    intraGradient: diff.intra_gradient,
    velocity: diff.velocity,
    xContribution: diff.x_contribution,
    integrity: si ? {
      score: si.score,
      classification: si.classification,
      multiplier: si.multiplier,
      summary: si.summary,
      components: si.component_scores ? {
        network: si.component_scores.network,
        temporal: si.component_scores.temporal,
        account: si.component_scores.account,
        engagement: si.component_scores.engagement,
        incentiveRisk: si.component_scores.incentive_risk,
      } : undefined,
      flags: Array.isArray(si.flags) ? si.flags.map((f: any) => ({ source: f.source, flag: f.flag })) : [],
    } : undefined,
  };
}

export interface ResearchHistory {
  trajectoryLabel?: string;
  summaryShort?: string;
  summaryLong?: string;
  yearsDiscussed?: number;
  firstKnownDate?: string;
  gradientImplication?: string;
  milestones?: { year?: string | number; label?: string }[];
}

// Signal Convergence — downstream directional validation. Reads the Gradient
// Score's recent trajectory + raw volume + niche concentration and reports
// whether the score's direction is CONFIRMED / MIXED / CONFLICTING by the data.
// Independent of the N demand metric (non-circular). Never feeds the score.
export interface Convergence {
  status: 'ok' | 'warming_up' | 'unavailable' | 'error';
  direction?: 'RISING' | 'FALLING' | 'HOLDING';
  convergence?: 'CONFIRMED' | 'MIXED' | 'CONFLICTING' | 'INCONCLUSIVE';
  snapshots?: number;
  needed?: number;
  note?: string;
  vsGradient?: { validation: string; text: string; scoreSlope?: number; volumeChangePct?: number };
  vsNiche?: { validation: string; text: string; nicheG?: number | null };
}

export async function fetchConvergence(topicKey: string): Promise<Convergence> {
  const res = await fetch(`${GRADIENT_API}/convergence/${encodeURIComponent(topicKey)}`, {
    headers: { Accept: 'application/json' },
  });
  if (!res.ok) throw new Error(`Gradient API ${res.status}`);
  const d = await res.json();
  return {
    status: d.status,
    direction: d.direction,
    convergence: d.convergence,
    snapshots: d.snapshots,
    needed: d.needed,
    note: d.note,
    vsGradient: d.vs_gradient ? {
      validation: d.vs_gradient.validation,
      text: d.vs_gradient.text,
      scoreSlope: d.vs_gradient.score_slope,
      volumeChangePct: d.vs_gradient.volume_change_pct,
    } : undefined,
    vsNiche: d.vs_niche ? {
      validation: d.vs_niche.validation,
      text: d.vs_niche.text,
      nicheG: d.vs_niche.niche_g,
    } : undefined,
  };
}

// Research history for a topic ("how long has this been discussed").
export async function fetchResearch(topicKey: string): Promise<ResearchHistory> {
  const res = await fetch(`${GRADIENT_API}/scores/${encodeURIComponent(topicKey)}/history`, {
    headers: { Accept: 'application/json' },
  });
  if (!res.ok) throw new Error(`Gradient API ${res.status}`);
  const d = await res.json();
  return {
    trajectoryLabel: d.trajectory_label || undefined,
    summaryShort: d.summary_short || undefined,
    summaryLong: d.summary_long || undefined,
    yearsDiscussed: d.years_discussed != null ? Number(d.years_discussed) : undefined,
    firstKnownDate: d.first_known_date || undefined,
    gradientImplication: d.gradient_implication || undefined,
    milestones: Array.isArray(d.milestones) ? d.milestones : [],
  };
}
