import { RiskScore } from './gradientApi';

// Single source of truth for the Market section's chip row, stat-tile grid, and
// focused category page — mirrors lib/signals.ts CATEGORY_DEFS for Trends so the
// two sections share an identical interaction model.

export type MarketCategoryKey =
  | 'marketsignal' | 'all' | 'elevated' | 'active'
  | 'building' | 'routine' | 'dormant' | 'leverage';

// Helpers reading the live Market Gradient off a RiskScore.
const tierOf = (r: RiskScore) => r.marketGradient?.tier ?? r.stage ?? 'DORMANT';
const detOf = (r: RiskScore) => r.marketGradient?.detection ?? r.detection ?? 0;
export const leverageOf = (r: RiskScore): number | null =>
  r.marketGradient?.leverageHealth ?? null;
export const laneOf = (r: RiskScore): string => r.marketGradient?.lane ?? '';

// Coverage-LANE axis (Tier 1) — EXACT parity with the web terminal's LANE_FILTERS so all
// three platforms share the same lane chips. Covered = institutional positioning available;
// halted_microcap = ticker but limited coverage; macro_theme = no ticker (positioning N/A).
export const MARKET_LANES: Array<{ key: string; label: string; lane?: string }> = [
  { key: 'all', label: 'All lanes' },
  { key: 'covered', label: 'Covered', lane: 'covered' },
  { key: 'halted_microcap', label: 'Halted / micro-cap', lane: 'halted_microcap' },
  { key: 'macro_theme', label: 'Macro themes', lane: 'macro_theme' },
];
export const LANE_SHORT: Record<string, string> = {
  covered: 'covered', halted_microcap: 'halt · micro-cap', macro_theme: 'macro theme',
};

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
    color: '#EE6A2A', altColor: '#B5341B',
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
    color: '#5B6472',
    definition: 'Every market item visible to your tier, in the default ordering.',
    howReached: 'No filter applied.',
    showTile: false, filter: () => true,
  },
  {
    key: 'elevated', label: 'Elevated', short: 'ELEVATED', range: 'Score 80–100',
    color: '#CF2A1B',
    definition: 'Positioning is strongly elevated across leading and confirming signals — the most unusual activity vs the item\'s own baseline.',
    howReached: 'The average of Market Detection and Confidence lands at 80+.',
    showTile: true, filter: (r) => tierOf(r) === 'ELEVATED',
  },
  {
    key: 'active', label: 'Active', short: 'ACTIVE', range: 'Score 60–79',
    color: '#E85A1E',
    definition: 'Active positioning — signals are clearly above this item\'s routine level, though not strongly elevated.',
    howReached: 'The average of Detection and Confidence lands in 60–79.',
    showTile: true, filter: (r) => tierOf(r) === 'ACTIVE',
  },
  {
    key: 'building', label: 'Building', short: 'BUILDING', range: 'Score 40–59',
    color: '#D4A017',
    definition: 'Positioning is building but not yet broadly elevated — worth watching for promotion.',
    howReached: 'The average of Detection and Confidence lands in 40–59.',
    showTile: true, filter: (r) => tierOf(r) === 'BUILDING',
  },
  {
    key: 'routine', label: 'Routine', short: 'ROUTINE', range: 'Score 25–39',
    color: '#2D7EEF',
    definition: 'Activity is in line with this item\'s own normal level — nothing unusual right now.',
    howReached: 'The average of Detection and Confidence lands in 25–39.',
    showTile: true, filter: (r) => tierOf(r) === 'ROUTINE',
  },
  {
    key: 'dormant', label: 'Dormant', short: 'DORMANT', range: 'Score 0–24',
    color: '#9AA3B0',
    definition: 'Quiet — little positioning activity relative to this item\'s baseline.',
    howReached: 'The average of Detection and Confidence lands below 25.',
    showTile: true, filter: (r) => tierOf(r) === 'DORMANT',
  },
  {
    key: 'leverage',
    label: 'Leverage Health',
    short: 'LEVERAGE HEALTH',
    range: '1–100 · high number = lower debt',
    color: '#10B981',
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
  ELEVATED: '#CF2A1B', ACTIVE: '#E85A1E', BUILDING: '#D4A017',
  ROUTINE: '#2D7EEF', DORMANT: '#9AA3B0',
};
