import { RiskScore } from './gradientApi';

// Single source of truth for the Market section's chip row, stat-tile grid, and
// focused category page — mirrors lib/signals.ts CATEGORY_DEFS for Trends so the
// two sections share an identical interaction model.

export type MarketCategoryKey =
  | 'marketsignal' | 'all' | 'elevated' | 'active'
  | 'building' | 'routine' | 'dormant' | 'leverage';

// Helpers reading the live Market Gradient off a RiskScore.
export const tierOf = (r: RiskScore) => r.marketGradient?.tier ?? r.stage ?? 'DORMANT';
const detOf = (r: RiskScore) => r.marketGradient?.detection ?? r.detection ?? 0;
export const leverageOf = (r: RiskScore): number | null =>
  r.marketGradient?.leverageHealth ?? null;
export const laneOf = (r: RiskScore) => r.marketGradient?.lane ?? '';
export const flowOf = (r: RiskScore) => r.marketGradient?.flow ?? null;

// ── The three Market filter axes — WEB PARITY (web MarketSignal.tsx is the model) ──
// LANE (coverage, Tier 1) · TIER (Market Gradient tier + the Watch/Leverage cuts) ·
// DIRECTION (factual net money-flow from filings — a fact, not advice).
// Defaults are 'all' on every axis, exactly like the web terminal.

export const MARKET_LANES: { key: string; label: string; lane?: string }[] = [
  { key: 'all', label: 'All lanes' },
  { key: 'covered', label: 'Covered', lane: 'covered' },
  { key: 'halted_microcap', label: 'Halted / micro-cap', lane: 'halted_microcap' },
  { key: 'macro_theme', label: 'Macro themes', lane: 'macro_theme' },
];

// 'Moderate' matches the BUILDING→MODERATE rename — the engine may serve either label.
export const MARKET_TIER_FILTERS: { key: string; label: string; test?: (r: RiskScore) => boolean }[] = [
  { key: 'all', label: 'All' },
  { key: 'elevated', label: 'Elevated', test: (r) => tierOf(r) === 'ELEVATED' },
  { key: 'active', label: 'Active', test: (r) => tierOf(r) === 'ACTIVE' },
  { key: 'moderate', label: 'Moderate', test: (r) => tierOf(r) === 'MODERATE' || tierOf(r) === 'BUILDING' },
  { key: 'routine', label: 'Routine', test: (r) => tierOf(r) === 'ROUTINE' },
  { key: 'dormant', label: 'Dormant', test: (r) => tierOf(r) === 'DORMANT' },
  { key: 'watch', label: 'Watch / Unusual', test: (r) => ['WATCH', 'ELEVATED', 'UNUSUAL'].includes((r.classification ?? '').toUpperCase()) },
  { key: 'leverage', label: 'Leverage ≥60', test: (r) => (leverageOf(r) ?? 0) >= 60 },
];

// Neutral covers anything without a clear in/out read (neutral, divergent, unknown).
export const MARKET_DIRECTION_FILTERS: { key: string; label: string; test: (r: RiskScore) => boolean }[] = [
  { key: 'all', label: 'All', test: () => true },
  { key: 'inflow', label: 'Inflow', test: (r) => flowOf(r) === 'inflow' },
  { key: 'outflow', label: 'Outflow', test: (r) => flowOf(r) === 'outflow' },
  { key: 'neutral', label: 'Neutral', test: (r) => flowOf(r) !== 'inflow' && flowOf(r) !== 'outflow' },
];

export const MARKET_CATEGORY_DEFS: Array<{
  key: MarketCategoryKey;
  label: string;
  short: string;
  range: string;
  color: string;
  altColor?: string;
  definition: string;
  howReached: string;
  showTile: boolean;
  sort?: (a: RiskScore, b: RiskScore) => number;
  filter: (r: RiskScore) => boolean;
}> = [
  {
    key: 'marketsignal',
    label: 'Market Signal',
    short: 'MARKET SIGNAL',
    range: 'Sorted by Detection 100 → 0',
    color: '#B11226', altColor: '#B11226',
    definition:
      'Every market item, ranked by Market Detection (the leading signal — what ' +
      'analysts are saying + how smart money is positioned). The market analogue of ' +
      'the Now TrendIn view: where informed actors are moving before the hard data confirms.',
    howReached:
      'No threshold — shows everything scored, sorted by Detection. A high value means ' +
      'leading indicators (analyst sentiment, insider/13F/short positioning) are elevated.',
    showTile: false,
    sort: (a, b) => detOf(b) - detOf(a),
    filter: () => true,
  },
  {
    key: 'all', label: 'All Market', short: 'ALL', range: 'Every market item',
    color: '#3C4663',
    definition: 'Every market item visible to your tier, in the default ordering.',
    howReached: 'No filter applied.',
    showTile: false, filter: () => true,
  },
  {
    key: 'elevated', label: 'Elevated', short: 'ELEVATED', range: 'Score 80–100',
    color: '#B11226',
    definition: 'Positioning is strongly elevated across leading and confirming signals — the most unusual activity vs the item\'s own baseline.',
    howReached: 'The average of Market Detection and Confidence lands at 80+.',
    showTile: true, filter: (r) => tierOf(r) === 'ELEVATED',
  },
  {
    key: 'active', label: 'Active', short: 'ACTIVE', range: 'Score 60–79',
    color: '#A8456A',
    definition: 'Active positioning — signals are clearly above this item\'s routine level, though not strongly elevated.',
    howReached: 'The average of Detection and Confidence lands in 60–79.',
    showTile: true, filter: (r) => tierOf(r) === 'ACTIVE',
  },
  {
    key: 'building', label: 'Building', short: 'BUILDING', range: 'Score 40–59',
    color: '#A8456A',
    definition: 'Positioning is building but not yet broadly elevated — worth watching for promotion.',
    howReached: 'The average of Detection and Confidence lands in 40–59.',
    showTile: true, filter: (r) => tierOf(r) === 'BUILDING',
  },
  {
    key: 'routine', label: 'Routine', short: 'ROUTINE', range: 'Score 25–39',
    color: '#2A5B9E',
    definition: 'Activity is in line with this item\'s own normal level — nothing unusual right now.',
    howReached: 'The average of Detection and Confidence lands in 25–39.',
    showTile: true, filter: (r) => tierOf(r) === 'ROUTINE',
  },
  {
    key: 'dormant', label: 'Dormant', short: 'DORMANT', range: 'Score 0–24',
    color: '#9A9AA2',
    definition: 'Quiet — little positioning activity relative to this item\'s baseline.',
    howReached: 'The average of Detection and Confidence lands below 25.',
    showTile: true, filter: (r) => tierOf(r) === 'DORMANT',
  },
  {
    key: 'leverage',
    label: 'Leverage Health',
    short: 'LEVERAGE HEALTH',
    range: '1–100 · high number = lower debt',
    color: '#2E7D5B',
    definition:
      'A balance-sheet health read for companies — HIGH means LOWER debt / a healthier ' +
      'balance sheet, LOW means more leverage. Derived from factual financial data (not advice). ' +
      'Use it to see which names carry the least debt.',
    howReached:
      'Computed from each company\'s balance-sheet sustainability (debt, profitability, coverage). ' +
      'Only companies with financial data have a Leverage Health score; macro themes do not.',
    showTile: true,
    sort: (a, b) => (leverageOf(b) ?? -1) - (leverageOf(a) ?? -1),
    filter: (r) => leverageOf(r) != null,
  },
];

export function getMarketCategory(key: string) {
  return MARKET_CATEGORY_DEFS.find((c) => c.key === key) ?? MARKET_CATEGORY_DEFS[1];
}

export const MARKET_TIER_COLOR: Record<string, string> = {
  ELEVATED: '#B11226', ACTIVE: '#A8456A', MODERATE: '#A8456A', BUILDING: '#A8456A',
  ROUTINE: '#2A5B9E', DORMANT: '#9A9AA2',
};
