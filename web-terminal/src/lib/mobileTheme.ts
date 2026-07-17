// Mobile-app color scheme, mirrored for the web TREND and MARKET detail pages so
// the two surfaces read identically (authority: frontend/lib/signals.ts +
// risk/[key].tsx + tailwind.config.js / CLAUDE.md §3.1).

export const MC = {
  detection: '#2A5B9E',   // Detection — earliness (blue)
  confidence: '#2E7D5B',  // Confidence — confirmation (green)
  orange: '#B11226',      // brand "Now"
  maroon: '#7A0D1A',      // brand "TrendIn"
  gold: '#C9A24B',
  red: '#B11226',
  amber: '#A8456A',
  purple: '#6B4FA0',
  slate: '#8A8F9C',
  muted: '#9A9AA2',
  text: '#16264A',
  textSec: '#3C4663',
}

// Signal stage → color (frontend STAGE_COLORS).
export const STAGE_COLOR: Record<string, string> = {
  VIRAL: '#B11226', BREAKOUT: '#2E7D5B', STRONG: '#2A5B9E', EMERGING: '#C9A24B',
  MARGINAL: '#A8456A', WATCHING: '#A8456A', WATCH: '#A8456A', MONITORING: '#9A9AA2', DECAY: '#8A8F9C',
}
export const stageColor = (s?: string) => STAGE_COLOR[(s || '').toUpperCase()] ?? '#9A9AA2'

// Display rename: the "EMERGING" signal stage is shown to users as "INDICATING".
// Internal keys stay EMERGING (engine queries, colors, CSS classes) — display only.
export const stageLabel = (s?: string) =>
  (s || '').toUpperCase() === 'EMERGING' ? 'INDICATING' : (s || '')

// Topic maturity → color (frontend maturityColourHex).
export const MATURITY_COLOR: Record<string, string> = {
  RESURGENT: '#C9A24B', EMERGING: '#2E7D5B', NEW: '#2A5B9E',
  ESTABLISHED: '#8A8F9C', MONITORING: '#9A9AA2',
}
export const maturityColor = (c?: string) => MATURITY_COLOR[(c || '').toUpperCase()] ?? '#3C4663'

// Market tier → color (risk/[key].tsx MARKET_TIER_COLOR).
export const MARKET_TIER_COLOR: Record<string, string> = {
  ELEVATED: '#B11226', ACTIVE: '#A8456A', MODERATE: '#C9A24B', BUILDING: '#C9A24B',
  ROUTINE: '#2A5B9E', DORMANT: '#9A9AA2',
}
export const marketTierColor = (t?: string) => MARKET_TIER_COLOR[(t || '').toUpperCase()] ?? '#9A9AA2'

// Which score a market factor feeds → color.
export const FEEDS_COLOR: Record<string, string> = {
  detection: '#2A5B9E', confidence: '#2E7D5B', both: '#6B4FA0',
}

// Detection–Confidence gap interpretation bands (frontend GAP_BANDS).
export const GAP_BANDS = [
  { max: 15, range: '0–15 pts', label: 'Both scores agree — aligned, not in conflict', color: '#2E7D5B' },
  { max: 35, range: '16–35 pts', label: 'Early stage — confirmation building', color: '#C9A24B' },
  { max: 60, range: '36–60 pts', label: 'Very early — detected, not confirmed', color: '#B11226' },
  { max: Infinity, range: '60+ pts', label: 'Speculative — dark matter signal only', color: '#6B4FA0' },
]
export function gapBandIndex(gap: number): number {
  const i = GAP_BANDS.findIndex((b) => Math.abs(gap) <= b.max)
  return i < 0 ? GAP_BANDS.length - 1 : i
}

// Who uses which score (frontend SCORE_ROLES).
export const SCORE_ROLES = {
  detection: { color: '#2A5B9E', tag: 'Speed', who: 'Content creators, brand managers, trend-forward marketers. Optimized for speed — surfaces signals early, accepting more false alarms in exchange.' },
  confidence: { color: '#2E7D5B', tag: 'Precision', who: 'Institutional analysts, investors, strategic planners. Optimized for precision — fewer false alarms, confirmed before it commits.' },
}

// Market intensity tiers — what the bands mean (risk/[key].tsx MARKET_TIERS).
export const MARKET_TIERS = [
  { key: 'ELEVATED', range: '80–100', desc: 'Strongly elevated positioning' },
  { key: 'ACTIVE', range: '60–79', desc: 'Clearly above routine' },
  { key: 'MODERATE', range: '40–59', desc: 'Moderate, not yet elevated' },
  { key: 'ROUTINE', range: '25–39', desc: 'In line with own baseline' },
  { key: 'DORMANT', range: '0–24', desc: 'Quiet vs baseline' },
]

// Diffusion pipeline stages (risk/[key].tsx PIPELINE).
export const RISK_PIPELINE = [
  { key: 'Dark Positioning', label: 'Insider Tracking', desc: 'Insider Form 4 / 13F — smart money', detect: true },
  { key: 'Expert Warning', label: 'Expert Warning', desc: '8-K material events, macro stress', detect: false },
  { key: 'Consumer Concern', label: 'Consumer Concern', desc: 'Financial communities', detect: false },
  { key: 'Media Coverage', label: 'Media Coverage', desc: 'News flow', detect: false },
  { key: 'Retail Amplify', label: 'Retail Amplify', desc: 'Finance YouTube / crowd', detect: false },
]

export const BASELINE_META: Record<string, { color: string; label: string }> = {
  SPIKE_VS_SELF: { color: '#B11226', label: 'Spike vs. own baseline' },
  ELEVATED_VS_SELF: { color: '#A8456A', label: 'Elevated vs. own baseline' },
  AT_BASELINE: { color: '#2E7D5B', label: 'At its own baseline' },
  BELOW_BASELINE: { color: '#9A9AA2', label: 'Below its own baseline' },
  INSUFFICIENT_HISTORY: { color: '#9A9AA2', label: 'Building baseline' },
}


// ── Aurora Title Case (DESIGN_SYSTEM.md §2): trend/topic names render Title
// Case; words already ALL-CAPS or with interior capitals are preserved
// ("quantum LLMs" -> "Quantum LLMs", "AI" -> "AI"). Display-only.
export function titleCaseTopic(topic: string): string {
  return (topic || '')
    .split(' ')
    .map((w) => (/[A-Z]/.test(w) ? w : w.charAt(0).toUpperCase() + w.slice(1)))
    .join(' ')
}
