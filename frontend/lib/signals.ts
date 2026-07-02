// Signal model + tier filtering for Now TrendIn 2.0.
// Live data comes from the Gradient Score engine (see lib/gradientApi.ts);
// the MOCK feed below is the offline fallback. Tier gating uses isDataAccessible().
import { TierID, TIERS, isDataAccessible } from '../constants/tiers';

export type Stage =
  | 'VIRAL'
  | 'BREAKOUT'
  | 'STRONG'
  | 'EMERGING'
  | 'MARGINAL'
  | 'WATCHING'   // legacy alias of MARGINAL (kept for back-compat / server values)
  | 'WATCH'
  | 'MONITORING'
  | 'DECAY';

export interface BreakdownItem {
  label: string;
  value: number; // headline (detection) value for the bar
  conf?: number; // confidence value, when available
  desc?: string;
}
export interface BreakdownGroup {
  title: string;
  status?: string;
  note?: string;
  items: BreakdownItem[];
}

export interface WhatToDo {
  action: string;
  instruction?: string;
  detail?: string;
}

// One entry in the AI variation map (e.g. "AI"=20 vs "agentic coding"=97).
export interface TopicVariation {
  topicKey: string;
  display: string;
  tier?: string;
  tierLabel?: string;
  tierColour?: string;
  velocity?: string;
  typicalDetection: number;
  typicalConfidence: number;
  isQueried?: boolean;
  whyDifferent?: string;
}

// Map maturity class → design palette hex.
export function maturityColourHex(cls?: string): string {
  switch ((cls || '').toUpperCase()) {
    case 'RESURGENT': return '#A8456A';   // gold — established but re-accelerating
    case 'EMERGING': return '#2E7D5B';    // green
    case 'NEW': return '#2A5B9E';         // blue
    case 'ESTABLISHED': return '#8A8F9C'; // slate — permanent expert home
    case 'MONITORING': return '#9A9AA2';  // muted
    default: return '#3C4663';
  }
}

// Map AI taxonomy colour names → design palette hex.
export function tierColourHex(name?: string): string {
  switch ((name || '').toLowerCase()) {
    case 'green': return '#2E7D5B';
    case 'blue': return '#2A5B9E';
    case 'gray': case 'grey': return '#8A8F9C';
    case 'muted': return '#9A9AA2';
    default: return '#3C4663';
  }
}

export interface Signal {
  id: string;
  topic: string;
  category: string;
  score: number;
  detection: number;
  confidence: number;
  stage: Stage;               // displayed stage — Detection-based (see stageFromScore)
  engineStage?: Stage;        // engine's overall-based signal_stage, for reference
  createdAt: number; // epoch ms — latest score time (for "Xm ago" + sorting)
  firstSeenAt?: number; // epoch ms — earliest score time (for tier data-aging)
  // Rich fields (present for live engine data; optional for mock)
  overall?: number;
  gap?: number;
  gapMeaning?: string;
  whatToDo?: WhatToDo;
  why?: string;
  whatToWatch?: string;
  platforms?: string[];
  groups?: BreakdownGroup[];
  aiTierLabel?: string;
  totalMentions?: number;
  timesScored?: number;
  isAnomaly?: boolean;
  // N component — "Now Trending" internal app demand (0–100), from query frequency.
  nowTrending?: number;
  // "Now Trending Gradient Score" — separate, demand-inclusive what-if read: the
  // Detection/Confidence the engine would produce if N were folded in as an extra
  // factor. Computed server-side (weighting never exposed). Headline scores stay N-free.
  nowTrendingGradientDetection?: number;
  nowTrendingGradientConfidence?: number;
  // True when external evidence is thin and demand exceeds the external read —
  // surface a "limited external confirmation" note so demand can't quietly inflate.
  nowTrendingGradientDemandDriven?: boolean;
  // AI Topic Intelligence (present only for taxonomy-recognized AI topics)
  aiTier?: string;           // tier_1 | tier_2 | tier_3 | tier_4
  aiTierColour?: string;     // green | blue | gray | muted
  aiClassification?: string;
  aiVelocity?: string;       // ACCELERATING | STEADY | ...
  scoreExplanation?: string;
  variations?: TopicVariation[];
  // Dark Matter signatures (inferred private-conversation indicators)
  darkMatter?: number;          // D component 0–100
  firstTimerRatio?: number;     // 0–1 — share of first-time participants
  engagementAsymmetry?: boolean; // comments exceed normal upvote ratio
  // Maturity classification (calibration lifecycle)
  maturityClass?: string;       // NEW | EMERGING | ESTABLISHED | RESURGENT | MONITORING
  maturityBadge?: string;       // e.g. "🔵 New Signal"
  maturityReason?: string;
}

// Legend shown on the home page ("what do these scores mean").
export const STAGE_META = [
  // Neutral, descriptive labels only — no prescriptive "what to do" guidance.
  // We surface the analysis; the user decides any action.
  { key: 'BREAKOUT', label: 'BREAKOUT', range: '85–100', desc: 'Strongest signal', color: '#2E7D5B' },
  { key: 'STRONG', label: 'STRONG', range: '70–84', desc: 'High signal strength', color: '#2A5B9E' },
  { key: 'EMERGING', label: 'INDICATING', range: '55–69', desc: 'Building signal', color: '#6B4FA0' },
  { key: 'MARGINAL', label: 'MARGINAL', range: '35–54', desc: 'Early / unconfirmed', color: '#A8456A' },
] as const;

// Single source of truth for the displayed stage band. Derived from the
// Detection score — the headline metric the product leads with and the basis
// the category tiles (CATEGORY_DEFS) and STAGE_META ranges already use. Keeping
// the badge on this same basis stops the stage label from contradicting the
// category a topic appears in (e.g. a Detection-74 topic sitting in the STRONG
// tile must not show an EMERGING badge sourced from a lower overall score).
export function stageFromScore(score: number): Stage {
  if (score >= 85) return 'BREAKOUT';
  if (score >= 70) return 'STRONG';
  if (score >= 55) return 'EMERGING';
  if (score >= 35) return 'MARGINAL';
  return 'MONITORING';
}

// CATEGORY_DEFS — the single source of truth for the homepage chip row, the
// stat-tile grid, and the focused category page. Each entry knows its label,
// brand colors, a long-form definition, and how a signal qualifies. Adding a
// category here automatically adds it to the chip row and the focused-page
// router (no other code change needed).
//
// ⚠️ The `filter` arrows below reference `scoreGap` BEFORE its definition
// further down in this file. This works ONLY because `scoreGap` is declared
// with the `function` keyword (hoisted to module scope). If you ever convert
// it to `const scoreGap = (s) => …`, these filters will throw ReferenceError
// at call time — move CATEGORY_DEFS below `scoreGap` if you make that switch.
export type CategoryKey =
  | 'nowtrendin' | 'all' | 'breakout' | 'strong'
  | 'emerging' | 'marginal' | 'anomalies';

export const CATEGORY_DEFS: Array<{
  key: CategoryKey;
  label: string;
  short: string;          // tile label (very short)
  range: string;          // score range / criterion string
  color: string;          // primary color
  altColor?: string;      // secondary color (used for NowTrendIn wordmark split)
  definition: string;     // 2-3 sentence explanation for the focused page
  howReached: string;     // how a trend lands here
  showTile: boolean;      // whether to render in the stat-tile grid
  filter: (s: Signal) => boolean; // membership predicate
}> = [
  {
    key: 'nowtrendin',
    label: 'Now TrendIn',
    short: 'NOW TRENDIN',
    range: 'Sorted by Detection Score 100 → 0',
    color: '#B11226', altColor: '#B11226',
    definition:
      'Every accessible trend, ranked by Detection Score from highest to lowest. ' +
      'Detection Score weights the early-edge components (Gradient Strength, Dark Matter, ' +
      'Inertia) — it is the metric Now TrendIn was built around: where attention is ' +
      'moving BEFORE it arrives at mainstream.',
    howReached:
      'No threshold — this view shows everything the engine has scored that is accessible ' +
      'to your tier, sorted by earliness. A high Detection Score here means the engine ' +
      'sees concentrated niche signal ahead of mainstream confirmation.',
    showTile: true,
    filter: () => true,
  },
  {
    key: 'all',
    label: 'All Signals',
    short: 'ALL',
    range: 'Every accessible signal',
    color: '#3C4663',
    definition: 'Every signal currently visible to your tier, in the default engine ordering.',
    howReached: 'No filter applied.',
    showTile: false,
    filter: () => true,
  },
  {
    key: 'breakout',
    label: 'Breakout ≥85',
    short: 'BREAKOUT',
    range: 'Detection Score 85–100',
    color: '#2E7D5B',
    definition:
      'Topics where Detection Score is at or above 85 — the strongest live signal band. ' +
      'These are trends already breaking out across multiple platforms with the engine ' +
      'showing high confidence in the diffusion.',
    howReached:
      'A topic reaches Breakout when its Detection Score (G·0.40 + D·0.25 + I·0.20 + M·0.10 + C·0.05) ' +
      'lands at 85 or higher. This typically requires sustained cross-platform mentions, strong ' +
      'first-timer ratio (Dark Matter), and accelerating engagement.',
    showTile: true,
    filter: (s) => s.score >= 85,
  },
  {
    key: 'strong',
    label: 'Strong ≥70',
    short: 'STRONG',
    range: 'Detection Score 70–84',
    color: '#2A5B9E',
    definition:
      'Topics with high signal strength but not yet at breakout intensity. The diffusion ' +
      'is established and momentum is steady — a candidate to watch for promotion to Breakout.',
    howReached:
      'Detection Score lands in the 70–84 band. Usually means broad platform coverage is in ' +
      'place, Inertia is positive, but one or more components (often Dark Matter or Gradient ' +
      'Strength) has not yet maxed out.',
    showTile: true,
    filter: (s) => s.score >= 70 && s.score < 85,
  },
  {
    key: 'emerging',
    label: 'Indicating',
    short: 'INDICATING',
    range: 'Detection Score 55–69',
    color: '#6B4FA0',
    definition:
      'Building signals — early momentum is forming but the engine has not yet confirmed ' +
      'sustained acceleration across multiple cycles. The earliest end of the actionable band.',
    howReached:
      'Detection Score 55–69. Typically Gradient Strength is high (niche concentration) but ' +
      'Inertia and Medium Sequence are still ramping. Many will fade; some will graduate to Strong.',
    showTile: true,
    filter: (s) => s.score >= 55 && s.score < 70,
  },
  {
    key: 'marginal',
    label: 'Marginal',
    short: 'MARGINAL',
    range: 'Detection Score 35–54',
    color: '#A8456A',
    definition:
      'Marginal signals — early and unconfirmed. Detection is in the 35–54 band: present and ' +
      'worth watching, but the engine has not yet seen sustained acceleration or broad confirmation.',
    howReached:
      'Detection Score lands in the 35–54 band. Usually some early-edge evidence is present but ' +
      'Inertia, breadth, and persistence are still thin — many of these fade before confirming.',
    showTile: true,
    filter: (s) => s.score >= 35 && s.score < 55,
  },
  {
    key: 'anomalies',
    label: 'Anomalies',
    short: 'ANOMALIES',
    range: 'Detection ahead of Confidence by 16+ pts',
    color: '#6B4FA0',
    definition:
      'Topics where the Detection Score is running well AHEAD of the Confidence Score (a 16+ ' +
      'point lead) — the engine sees strong early-edge evidence before broad confirmation has ' +
      'caught up. This is the "future arriving" shape: sometimes the real thing early, sometimes noise.',
    howReached:
      'Detection minus Confidence is 16 points or more (a SIGNED lead, not an absolute gap). ' +
      'This is orthogonal to strength — an anomaly can sit at any stage; what defines it is the ' +
      'early-edge lead, not the level. (Lagging topics where Confidence exceeds Detection are NOT anomalies.)',
    showTile: true,
    filter: (s) => (s.detection - s.confidence) >= 16,
  },
];

export function getCategory(key: string) {
  return CATEGORY_DEFS.find((c) => c.key === key) ?? CATEGORY_DEFS[1]; // default to 'all'
}

// ── CONTENT CATEGORIES (the WHAT axis — Now TrendIn 1.0 taxonomy) ──────────
// Orthogonal to the signal-STAGE axis above. Mirrors the engine's
// topic_categories.py keys so the chip row, card badge, and ?category= API
// filter all agree. Each entry: engine key + display label + accent color.
export const CONTENT_CATEGORIES: Array<{ key: string; label: string; color: string }> = [
  { key: 'technology',     label: 'Technology',     color: '#2A5B9E' },
  { key: 'business',       label: 'Business',       color: '#2A5B9E' },
  { key: 'economy',        label: 'Economy',        color: '#A8456A' },
  { key: 'sports',         label: 'Sports',         color: '#2E7D5B' },
  { key: 'entertainment',  label: 'Entertainment',  color: '#A8456A' },
  { key: 'politics',       label: 'Politics',       color: '#6B4FA0' },
  { key: 'current_events', label: 'Current Events', color: '#A8456A' },
  { key: 'health',         label: 'Health',         color: '#2E7D5B' },
  { key: 'fashion',        label: 'Fashion',        color: '#A8456A' },
  { key: 'education',      label: 'Education',       color: '#6B4FA0' },
  { key: 'religion',       label: 'Religion',        color: '#B11226' },
  { key: 'general',        label: 'General',         color: '#3C4663' },
];

const CONTENT_CATEGORY_INDEX: Record<string, { key: string; label: string; color: string }> =
  Object.fromEntries(CONTENT_CATEGORIES.map((c) => [c.key, c]));

// Look up display metadata for a content-category key (case/spacing tolerant).
export function contentCategoryMeta(key?: string) {
  if (!key) return { key: 'general', label: 'General', color: '#9A9AA2' };
  const norm = key.toLowerCase().trim().replace(/\s+/g, '_');
  return CONTENT_CATEGORY_INDEX[norm] ?? { key: norm, label: key, color: '#9A9AA2' };
}

// Short, descriptive signal-read per stage (analysis only — no action guidance).
const ACTION_LINE: Record<Stage, string> = {
  VIRAL: 'Viral-level signal across platforms.',
  BREAKOUT: 'Breakout in progress.',
  STRONG: 'Strong, sustained momentum.',
  EMERGING: 'Early momentum forming.',
  MARGINAL: 'Marginal — early, not yet confirmed.',
  WATCHING: 'Marginal — early, not yet confirmed.',
  WATCH: 'Marginal — early, not yet confirmed.',
  MONITORING: 'Low-intensity background signal.',
  DECAY: 'Attention falling.',
};
export const actionLine = (s: Stage) => ACTION_LINE[s] ?? ACTION_LINE.MONITORING;

// Detection vs Confidence — fixed engine characteristics (the "Duality split").
export const SCORE_ROLES = {
  detection: {
    color: '#2A5B9E',
    falsePositive: 'Speed',
    who: 'Content creators, brand managers, trend-forward marketers. Optimized for speed — surfaces signals early, accepting more false alarms in exchange.',
  },
  confidence: {
    color: '#2E7D5B',
    falsePositive: 'Precision',
    who: 'Institutional analysts, strategic planners, investors. Optimized for precision over speed — requires sustained, repeated confirmation.',
  },
} as const;

// Gap interpretation bands — how early the signal is.
export const GAP_BANDS = [
  { max: 15, range: '0–15 pts', label: 'Both scores agree — aligned, not in conflict', color: '#2E7D5B' },
  { max: 35, range: '16–35 pts', label: 'Early stage — confirmation building', color: '#A8456A' },
  { max: 60, range: '36–60 pts', label: 'Very early — detected, not confirmed', color: '#B11226' },
  { max: Infinity, range: '60+ pts', label: 'Speculative — dark matter signal only', color: '#6B4FA0' },
] as const;

export function gapBandIndex(gap: number): number {
  const i = GAP_BANDS.findIndex((b) => gap <= b.max);
  return i < 0 ? GAP_BANDS.length - 1 : i;
}

// One-line gap meaning + tone for the card footer. Uses the SAME 0–15 threshold
// as GAP_BANDS so the headline can never contradict the interpretation table.
// "Agree" means the two scores are aligned (not in conflict) — NOT that the
// signal is strong; a low-but-aligned signal is agreement that it's early.
export function gapInsight(gap: number): { text: string; agree: boolean } {
  return gap <= 15
    ? { text: 'Scores aligned — agreement on where this sits, not that it’s strong', agree: true }
    : { text: 'Confirmation building — 24–72h to alignment', agree: false };
}

const MIN = 60 * 1000;
const HOUR = 60 * MIN;
const now = Date.now();

// Offline fallback dataset (used if the live engine is unreachable).
export const MOCK_SIGNALS: Signal[] = [
  { id: '1', topic: 'quantum LLMs',       category: 'Technology', score: 94, detection: 96, confidence: 91, stage: 'VIRAL',      createdAt: now - 22 * MIN },
  { id: '2', topic: 'agentic coding',     category: 'Technology', score: 87, detection: 88, confidence: 84, stage: 'BREAKOUT',   createdAt: now - 48 * MIN },
  { id: '3', topic: 'stablecoin bill',    category: 'Business',   score: 81, detection: 83, confidence: 78, stage: 'STRONG',     createdAt: now - 1.5 * HOUR },
  { id: '4', topic: 'mcp servers',        category: 'Technology', score: 72, detection: 74, confidence: 69, stage: 'STRONG',     createdAt: now - 3 * HOUR },
  { id: '5', topic: 'rag pipelines',      category: 'Technology', score: 66, detection: 68, confidence: 61, stage: 'EMERGING',   createdAt: now - 6 * HOUR },
  { id: '6', topic: 'creator economy',    category: 'Business',   score: 59, detection: 62, confidence: 55, stage: 'EMERGING',   createdAt: now - 11 * HOUR },
  { id: '7', topic: 'vector databases',   category: 'Technology', score: 64, detection: 66, confidence: 60, stage: 'MARGINAL',   createdAt: now - 13 * HOUR },
  { id: '8', topic: 'climate tech',       category: 'Business',   score: 57, detection: 59, confidence: 52, stage: 'MARGINAL',   createdAt: now - 14 * HOUR },
  { id: '9', topic: 'longevity drugs',    category: 'Health',     score: 53, detection: 55, confidence: 48, stage: 'MONITORING', createdAt: now - 26 * HOUR },
  { id: '10', topic: 'spatial computing', category: 'Technology', score: 49, detection: 51, confidence: 44, stage: 'MONITORING', createdAt: now - 38 * HOUR },
];

export interface SignalFeed {
  accessible: Signal[];
  lockedCount: number;
  total: number;
}

// Tier-gated feed from a signal list (live or mock), newest first.
// Gating uses the topic's first-seen age (a new score ages into lower tiers);
// display/sort still use the latest score time.
export function filterFeed(list: Signal[], tier: TierID): SignalFeed {
  const t = Date.now();
  const accessible = list
    .filter((s) => isDataAccessible(tier, t - (s.firstSeenAt ?? s.createdAt)))
    .sort((a, b) => b.createdAt - a.createdAt);
  return { accessible, lockedCount: list.length - accessible.length, total: list.length };
}

// Mock-only convenience (kept for fallback / tests).
export function getSignals(tier: TierID): SignalFeed {
  return filterFeed(MOCK_SIGNALS, tier);
}

export function findSignal(list: Signal[], id: string): Signal | undefined {
  return list.find((s) => s.id === id);
}

export function ageLabel(createdAt: number): string {
  const ms = Date.now() - createdAt;
  if (ms < HOUR) return `${Math.max(1, Math.round(ms / MIN))}m ago`;
  if (ms < 24 * HOUR) return `${Math.round(ms / HOUR)}h ago`;
  return `${Math.round(ms / (24 * HOUR))}d ago`;
}

export function timeLabel(createdAt: number): string {
  const d = new Date(createdAt);
  let h = d.getHours();
  const m = d.getMinutes();
  const ap = h >= 12 ? 'PM' : 'AM';
  h = h % 12 || 12;
  return `${h}:${m.toString().padStart(2, '0')} ${ap}`;
}

const MONTHS = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];
export function dayLabel(createdAt: number): string {
  const d = new Date(createdAt);
  return `${MONTHS[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`;
}

const STAGE_COLORS: Record<Stage, string> = {
  VIRAL: '#B11226',
  BREAKOUT: '#2E7D5B',
  STRONG: '#2A5B9E',
  EMERGING: '#6B4FA0',
  MARGINAL: '#A8456A',
  WATCHING: '#A8456A',
  WATCH: '#A8456A',
  MONITORING: '#8A8F9C',
  DECAY: '#8A8F9C',
};
export const stageColor = (s: Stage) => STAGE_COLORS[s] ?? '#9A9AA2';

// Display rename: the EMERGING signal stage is shown to users as INDICATING.
// Internal keys/values stay EMERGING (type, colors, scoring) — display only.
export const stageLabel = (s?: string) =>
  (s || '').toUpperCase() === 'EMERGING' ? 'INDICATING' : (s || '');

// Title-case a trend topic for display (design rule: trend titles are Title Case).
// Capitalizes the first letter of each word but PRESERVES words that already carry
// an interior capital or are all-caps — so acronyms/brands stay intact
// ("quantum LLMs" → "Quantum LLMs", "AI" → "AI", "stablecoin bill" → "Stablecoin Bill").
export function titleCaseTopic(s?: string): string {
  if (!s) return '';
  return s
    .split(/(\s+)/)
    .map((w) => {
      if (!w.trim()) return w; // keep whitespace runs
      if (w === w.toUpperCase() || /[A-Z]/.test(w.slice(1))) {
        return w.charAt(0).toUpperCase() + w.slice(1);
      }
      return w.charAt(0).toUpperCase() + w.slice(1).toLowerCase();
    })
    .join('');
}

export function scoreGap(s: Signal): number {
  return s.gap ?? Math.abs(s.detection - s.confidence);
}

// Descriptive "signal read" per stage — analysis only, no action guidance.
// (Used only when live engine text is absent.)
const ACTIONS: Record<Stage, { title: string; body: string }> = {
  VIRAL: { title: 'Viral-level signal.', body: 'Tier-1 viral topic across multiple platforms, still concentrated in expert communities ahead of mainstream awareness.' },
  BREAKOUT: { title: 'Breakout in progress.', body: 'Strong multi-platform momentum with both scores in the breakout band.' },
  STRONG: { title: 'Strong signal.', body: 'Established strength and steady momentum across platforms.' },
  EMERGING: { title: 'Early momentum.', body: 'Momentum is forming but not yet confirmed across multiple cycles.' },
  MARGINAL: { title: 'Marginal — unconfirmed.', body: 'An early signal in the marginal band — present but not yet confirmed across cycles.' },
  WATCHING: { title: 'Marginal — unconfirmed.', body: 'An early signal in the marginal band — present but not yet confirmed across cycles.' },
  WATCH: { title: 'Marginal — unconfirmed.', body: 'An early signal in the marginal band — present but not yet confirmed across cycles.' },
  MONITORING: { title: 'Background signal.', body: 'Low-intensity background activity, below the emerging threshold.' },
  DECAY: { title: 'Attention falling.', body: 'Attention for this topic is declining from its peak.' },
};
export function actionFor(s: Signal) {
  if (s.whatToDo?.action) {
    return { title: s.whatToDo.action, body: s.whatToDo.instruction || s.whatToDo.detail || '' };
  }
  return ACTIONS[s.stage] ?? ACTIONS.MONITORING;
}

// Fallback synthetic breakdown (used only when live groups are absent).
export function breakdownGroups(s: Signal): BreakdownGroup[] {
  if (s.groups && s.groups.length) return s.groups;
  const clamp = (n: number) => Math.max(0, Math.min(100, Math.round(n)));
  return [
    { title: 'Signal Quality', items: [
      { label: 'Detection', value: s.detection },
      { label: 'Confidence', value: s.confidence },
      { label: 'Source spread', value: clamp((s.detection + s.confidence) / 2 - 4) },
    ] },
    { title: 'Signal Momentum', items: [
      { label: 'Velocity', value: clamp(s.score + 6) },
      { label: 'Acceleration', value: clamp(s.score - 8) },
      { label: 'Volume', value: clamp(s.detection - 3) },
    ] },
    { title: 'Signal Context', items: [
      { label: 'Cross-platform', value: clamp(s.confidence + 5) },
      { label: 'Novelty', value: clamp(100 - s.score + 20) },
      { label: 'Saturation', value: clamp(s.score - 15) },
    ] },
  ];
}

export function nextTier(tier: TierID): TierID | null {
  if (tier === 'consumer') return 'business';
  if (tier === 'business') return 'enterprise';
  return null;
}

export function dataWindowLabel(tier: TierID): string {
  if (tier === 'enterprise') return 'Live + full history';
  if (tier === 'business') return '30m+ data';
  return '1h+ data';
}
