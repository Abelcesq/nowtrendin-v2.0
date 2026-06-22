// Mobile-app color scheme, mirrored for the web TREND and MARKET detail pages so
// the two surfaces read identically (authority: frontend/lib/signals.ts +
// risk/[key].tsx + tailwind.config.js / CLAUDE.md §3.1).

export const MC = {
  detection: '#2D7EEF',   // Detection — earliness (blue)
  confidence: '#00C896',  // Confidence — confirmation (green)
  orange: '#EE6A2A',      // brand "Now"
  maroon: '#B5341B',      // brand "TrendIn"
  gold: '#D4A017',
  red: '#CF2A1B',
  amber: '#E85A1E',
  purple: '#8B5CF6',
  slate: '#94A3B8',
  muted: '#9AA3B0',
  text: '#1A1A2E',
  textSec: '#5B6472',
}

// Signal stage → color (frontend STAGE_COLORS).
export const STAGE_COLOR: Record<string, string> = {
  VIRAL: '#CF2A1B', BREAKOUT: '#00C896', STRONG: '#2D7EEF', EMERGING: '#D4A017',
  MARGINAL: '#E85A1E', WATCHING: '#E85A1E', WATCH: '#E85A1E', MONITORING: '#9AA3B0', DECAY: '#94A3B8',
}
export const stageColor = (s?: string) => STAGE_COLOR[(s || '').toUpperCase()] ?? '#9AA3B0'

// Display rename: the "EMERGING" signal stage is shown to users as "INDICATING".
// Internal keys stay EMERGING (engine queries, colors, CSS classes) — display only.
export const stageLabel = (s?: string) =>
  (s || '').toUpperCase() === 'EMERGING' ? 'INDICATING' : (s || '')

// Topic maturity → color (frontend maturityColourHex).
export const MATURITY_COLOR: Record<string, string> = {
  RESURGENT: '#D4A017', EMERGING: '#00C896', NEW: '#2D7EEF',
  ESTABLISHED: '#94A3B8', MONITORING: '#9AA3B0',
}
export const maturityColor = (c?: string) => MATURITY_COLOR[(c || '').toUpperCase()] ?? '#5B6472'

// Market tier → color (risk/[key].tsx MARKET_TIER_COLOR).
export const MARKET_TIER_COLOR: Record<string, string> = {
  ELEVATED: '#CF2A1B', ACTIVE: '#E85A1E', BUILDING: '#D4A017',
  ROUTINE: '#2D7EEF', DORMANT: '#9AA3B0',
}
export const marketTierColor = (t?: string) => MARKET_TIER_COLOR[(t || '').toUpperCase()] ?? '#9AA3B0'

// Which score a market factor feeds → color.
export const FEEDS_COLOR: Record<string, string> = {
  detection: '#2D7EEF', confidence: '#00C896', both: '#8B5CF6',
}

// Detection–Confidence gap interpretation bands (frontend GAP_BANDS).
export const GAP_BANDS = [
  { max: 15, range: '0–15 pts', label: 'Both scores agree — aligned, not in conflict', color: '#00C896' },
  { max: 35, range: '16–35 pts', label: 'Early stage — confirmation building', color: '#D4A017' },
  { max: 60, range: '36–60 pts', label: 'Very early — detected, not confirmed', color: '#CF2A1B' },
  { max: Infinity, range: '60+ pts', label: 'Speculative — dark matter signal only', color: '#8B5CF6' },
]
export function gapBandIndex(gap: number): number {
  const i = GAP_BANDS.findIndex((b) => Math.abs(gap) <= b.max)
  return i < 0 ? GAP_BANDS.length - 1 : i
}

// Who uses which score (frontend SCORE_ROLES).
export const SCORE_ROLES = {
  detection: { color: '#2D7EEF', tag: 'Speed', who: 'Content creators, brand managers, trend-forward marketers. Optimized for speed — surfaces signals early, accepting more false alarms in exchange.' },
  confidence: { color: '#00C896', tag: 'Precision', who: 'Institutional analysts, investors, strategic planners. Optimized for precision — fewer false alarms, confirmed before it commits.' },
}

// Market intensity tiers — what the bands mean (risk/[key].tsx MARKET_TIERS).
export const MARKET_TIERS = [
  { key: 'ELEVATED', range: '80–100', desc: 'Strongly elevated positioning' },
  { key: 'ACTIVE', range: '60–79', desc: 'Clearly above routine' },
  { key: 'BUILDING', range: '40–59', desc: 'Building, not yet elevated' },
  { key: 'ROUTINE', range: '25–39', desc: 'In line with own baseline' },
  { key: 'DORMANT', range: '0–24', desc: 'Quiet vs baseline' },
]

// Diffusion pipeline stages (risk/[key].tsx PIPELINE).
export const RISK_PIPELINE = [
  { key: 'Dark Positioning', label: 'Dark Positioning', desc: 'Insider Form 4 / 13F — smart money', detect: true },
  { key: 'Expert Warning', label: 'Expert Warning', desc: '8-K material events, macro stress', detect: false },
  { key: 'Consumer Concern', label: 'Consumer Concern', desc: 'Financial communities', detect: false },
  { key: 'Media Coverage', label: 'Media Coverage', desc: 'News flow', detect: false },
  { key: 'Retail Amplify', label: 'Retail Amplify', desc: 'Finance YouTube / crowd', detect: false },
]

export const BASELINE_META: Record<string, { color: string; label: string }> = {
  SPIKE_VS_SELF: { color: '#CF2A1B', label: 'Spike vs. own baseline' },
  ELEVATED_VS_SELF: { color: '#E85A1E', label: 'Elevated vs. own baseline' },
  AT_BASELINE: { color: '#00C896', label: 'At its own baseline' },
  BELOW_BASELINE: { color: '#9AA3B0', label: 'Below its own baseline' },
  INSUFFICIENT_HISTORY: { color: '#9AA3B0', label: 'Building baseline' },
}
