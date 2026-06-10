// Signal model + tier filtering for Now TrendIn 2.0.
// Live data comes from the Gradient Score engine (see lib/gradientApi.ts);
// the MOCK feed below is the offline fallback. Tier gating uses isDataAccessible().
import { TierID, TIERS, isDataAccessible } from '../constants/tiers';

export type Stage =
  | 'VIRAL'
  | 'BREAKOUT'
  | 'STRONG'
  | 'EMERGING'
  | 'WATCHING'
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
    case 'RESURGENT': return '#D4A017';   // gold — established but re-accelerating
    case 'EMERGING': return '#00C896';    // green
    case 'NEW': return '#2D7EEF';         // blue
    case 'ESTABLISHED': return '#94A3B8'; // slate — permanent expert home
    case 'MONITORING': return '#9AA3B0';  // muted
    default: return '#5B6472';
  }
}

// Map AI taxonomy colour names → design palette hex.
export function tierColourHex(name?: string): string {
  switch ((name || '').toLowerCase()) {
    case 'green': return '#00C896';
    case 'blue': return '#2D7EEF';
    case 'gray': case 'grey': return '#94A3B8';
    case 'muted': return '#9AA3B0';
    default: return '#5B6472';
  }
}

export interface Signal {
  id: string;
  topic: string;
  category: string;
  score: number;
  detection: number;
  confidence: number;
  stage: Stage;
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
  { key: 'BREAKOUT', label: 'BREAKOUT', range: '85–100', desc: 'Strongest signal', color: '#00C896' },
  { key: 'STRONG', label: 'STRONG', range: '70–84', desc: 'High signal strength', color: '#2D7EEF' },
  { key: 'EMERGING', label: 'EMERGING', range: '55–69', desc: 'Building signal', color: '#D4A017' },
  { key: 'WATCHING', label: 'WATCHING', range: '35–54', desc: 'Early / unconfirmed', color: '#E85A1E' },
] as const;

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
  | 'emerging' | 'lowrisk' | 'anomalies';

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
    color: '#EE6A2A', altColor: '#B5341B',
    definition:
      'Every accessible trend, ranked by Detection Score from highest to lowest. ' +
      'Detection Score weights early-edge components (Gradient Strength 40%, Dark Matter 25%, ' +
      'Inertia 20%) — it is the metric Now TrendIn was built around: where attention is ' +
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
    color: '#5B6472',
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
    color: '#00C896',
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
    color: '#2D7EEF',
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
    label: 'Emerging',
    short: 'EMERGING',
    range: 'Detection Score 55–69',
    color: '#D4A017',
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
    key: 'lowrisk',
    label: 'Low Risk',
    short: 'LOW RISK',
    range: 'Detection vs Confidence gap ≤ 6 pts',
    color: '#10B981',
    definition:
      'Signals where Detection and Confidence Scores are tightly aligned (within 6 points). ' +
      'The engine sees both earliness AND confirmation — the most balanced, least uncertain band.',
    howReached:
      'Both Detection and Confidence land near the same value, meaning the early-edge ' +
      'components (G, D) and the confirmation components (I, M) are reading the same story. ' +
      'Convergent evidence on both sides of the Duality split.',
    showTile: true,
    filter: (s) => scoreGap(s) <= 6,
  },
  {
    key: 'anomalies',
    label: 'Anomalies',
    short: 'ANOMALIES',
    range: 'Detection vs Confidence gap ≥ 18 pts',
    color: '#8B5CF6',
    definition:
      'Signals where Detection Score is sharply diverging from Confidence Score by 18+ points. ' +
      'These are the engine\'s earliest, most uncertain leads — strong early-edge evidence (high G ' +
      'or D) running ahead of cross-platform confirmation. Sometimes the future arriving; ' +
      'sometimes noise.',
    howReached:
      'The absolute gap between Detection and Confidence reaches 18 points or more. Typically ' +
      'driven by a Dark Matter or Gradient Strength spike that has not yet been validated by ' +
      'Inertia or Medium Sequence.',
    showTile: true,
    filter: (s) => scoreGap(s) >= 18,
  },
];

export function getCategory(key: string) {
  return CATEGORY_DEFS.find((c) => c.key === key) ?? CATEGORY_DEFS[1]; // default to 'all'
}

// Short, descriptive signal-read per stage (analysis only — no action guidance).
const ACTION_LINE: Record<Stage, string> = {
  VIRAL: 'Viral-level signal across platforms.',
  BREAKOUT: 'Breakout in progress.',
  STRONG: 'Strong, sustained momentum.',
  EMERGING: 'Early momentum forming.',
  WATCHING: 'Building — not yet confirmed.',
  WATCH: 'Building — not yet confirmed.',
  MONITORING: 'Low-intensity background signal.',
  DECAY: 'Attention falling.',
};
export const actionLine = (s: Stage) => ACTION_LINE[s] ?? ACTION_LINE.MONITORING;

// Detection vs Confidence — fixed engine characteristics (the "Duality split").
export const SCORE_ROLES = {
  detection: {
    color: '#2D7EEF',
    falsePositive: '~22% false positive · Speed',
    who: 'Content creators, brand managers, trend-forward marketers. Speed creates value — accepts ~1 in 5 false alarms, based on the engine’s calibration model.',
  },
  confidence: {
    color: '#00C896',
    falsePositive: '<9% false positive · Precision',
    who: 'Institutional analysts, strategic planners, investors. Precision over speed — requires 4+ sustained evidence windows, based on the engine’s calibration model.',
  },
} as const;

// Gap interpretation bands — how early the signal is.
export const GAP_BANDS = [
  { max: 15, range: '0–15 pts', label: 'Both scores agree — aligned, not in conflict', color: '#00C896' },
  { max: 35, range: '16–35 pts', label: 'Early stage — confirmation building', color: '#D4A017' },
  { max: 60, range: '36–60 pts', label: 'Very early — detected, not confirmed', color: '#CF2A1B' },
  { max: Infinity, range: '60+ pts', label: 'Speculative — dark matter signal only', color: '#8B5CF6' },
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
  { id: '7', topic: 'vector databases',   category: 'Technology', score: 64, detection: 66, confidence: 60, stage: 'WATCHING',   createdAt: now - 13 * HOUR },
  { id: '8', topic: 'climate tech',       category: 'Business',   score: 57, detection: 59, confidence: 52, stage: 'WATCHING',   createdAt: now - 14 * HOUR },
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
  VIRAL: '#CF2A1B',
  BREAKOUT: '#00C896',
  STRONG: '#2D7EEF',
  EMERGING: '#D4A017',
  WATCHING: '#E85A1E',
  WATCH: '#E85A1E',
  MONITORING: '#9AA3B0',
  DECAY: '#94A3B8',
};
export const stageColor = (s: Stage) => STAGE_COLORS[s] ?? '#9AA3B0';

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
  WATCHING: { title: 'Building — unconfirmed.', body: 'The signal is building but has not yet been confirmed across cycles.' },
  WATCH: { title: 'Building — unconfirmed.', body: 'The signal is building but has not yet been confirmed across cycles.' },
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
