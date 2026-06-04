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

function prettify(key: string): string {
  return key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

function mapGroups(cg: any): BreakdownGroup[] | undefined {
  if (!cg || typeof cg !== 'object') return undefined;
  const groups: BreakdownGroup[] = [];
  for (const groupKey of Object.keys(cg)) {
    const g = cg[groupKey];
    if (!g) continue;
    const items = Object.keys(g.components || {}).map((compKey) => {
      const c = g.components[compKey];
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
          urgency: r.what_to_do_urgency || undefined,
          instruction: r.what_to_do_instruction || undefined,
          detail: r.what_to_do_detail || undefined,
        }
      : undefined,
    why: r.why_this_matters || undefined,
    whatToWatch: r.what_to_watch || undefined,
    platforms: Array.isArray(r.platforms_active) ? r.platforms_active : [],
    groups: mapGroups(r.component_groups),
    aiTierLabel: r.ai_tier_label || undefined,
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
  }));
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
