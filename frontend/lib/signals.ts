// Phase 2 signal data + tier-based age filtering.
// Currently a local mock dataset. The filtering mirrors the planned Django param
// (?min_age=43200 consumer / 3600 business / none enterprise) so swapping getSignals()
// for a real fetch to lib/api.ts later requires no screen changes.
import { TierID, TIERS, TIER_ORDER, isDataAccessible } from '../constants/tiers';

export type Stage = 'VIRAL' | 'BREAKOUT' | 'STRONG' | 'EMERGING' | 'WATCHING' | 'MONITORING';

export interface Signal {
  id: string;
  topic: string;
  category: string;
  score: number;
  detection: number;
  confidence: number;
  stage: Stage;
  createdAt: number; // epoch ms
}

const MIN = 60 * 1000;
const HOUR = 60 * MIN;
const now = Date.now();

// Spread across ages so each tier sees a different slice:
// Enterprise: all · Business: age >= 1h · Consumer: age >= 12h
const RAW: Signal[] = [
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
  accessible: Signal[]; // visible to this tier, newest first
  lockedCount: number;  // how many newer signals are gated
  total: number;
}

// Tier-gated feed. Replace the RAW source with `await signalsApi.list({ min_age })` later.
export function getSignals(tier: TierID): SignalFeed {
  const t = Date.now();
  const accessible = RAW.filter((s) => isDataAccessible(tier, t - s.createdAt)).sort(
    (a, b) => b.createdAt - a.createdAt
  );
  return { accessible, lockedCount: RAW.length - accessible.length, total: RAW.length };
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
  MONITORING: '#9AA3B0',
};
export const stageColor = (s: Stage) => STAGE_COLORS[s];

// Tier whose data window the user should upgrade to next (for locked prompts).
export function nextTier(tier: TierID): TierID | null {
  if (tier === 'consumer') return 'business';
  if (tier === 'business') return 'enterprise';
  return null;
}

export function dataWindowLabel(tier: TierID): string {
  if (tier === 'enterprise') return 'Live + full history';
  return `${TIERS[tier].name === 'Consumer' ? '12h' : '1h'}+ data`;
}

export { TIER_ORDER };
