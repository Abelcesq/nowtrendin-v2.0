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
  urgency?: string;
  instruction?: string;
  detail?: string;
}

export interface Signal {
  id: string;
  topic: string;
  category: string;
  score: number;
  detection: number;
  confidence: number;
  stage: Stage;
  createdAt: number; // epoch ms
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
export function filterFeed(list: Signal[], tier: TierID): SignalFeed {
  const t = Date.now();
  const accessible = list
    .filter((s) => isDataAccessible(tier, t - s.createdAt))
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

// Fallback "what to do" (used only when live whatToDo is absent).
const ACTIONS: Record<Stage, { title: string; body: string }> = {
  VIRAL: { title: 'Act now.', body: 'Tier 1 viral topic across platforms. The window is open — move before it goes fully mainstream.' },
  BREAKOUT: { title: 'Move fast.', body: 'Breakout in progress with strong multi-platform momentum. High-conviction entry.' },
  STRONG: { title: 'Lean in.', body: 'Established strength and steady momentum. Solid entry with manageable risk.' },
  EMERGING: { title: 'Position early.', body: 'Early momentum forming. Get ahead of confirmation while attention is still cheap.' },
  WATCHING: { title: 'Keep on radar.', body: 'Signal is building but not yet confirmed. Set an alert and wait for acceleration.' },
  WATCH: { title: 'Keep on radar.', body: 'Signal is building but not yet confirmed. Set an alert and wait for acceleration.' },
  MONITORING: { title: 'Note it.', body: 'Low-intensity background signal. Worth tracking, not yet actionable.' },
  DECAY: { title: 'Stand down.', body: 'Attention is falling. The window has likely closed.' },
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
  return `${TIERS[tier].name === 'Consumer' ? '12h' : '1h'}+ data`;
}
