import { titleCaseTopic } from "../../../lib/signals";
import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ChevronLeft, Globe, Clock, Info, Activity, Play } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { GradientScoreRing } from '../../../components/ui/GradientScoreRing';
import { useRisk } from '../../../hooks/useSignals';

const CLASS_COLOR: Record<string, string> = {
  UNUSUAL: '#B11226', ELEVATED: '#A8456A', WATCH: '#2A5B9E', ROUTINE: '#9A9AA2', CALIBRATING: '#9A9AA2',
};

const MATURITY_COLOR: Record<string, string> = {
  ESTABLISHED: '#2A5B9E', MACRO: '#6B4FA0', EMERGING: '#A8456A',
};

const BASELINE_META: Record<string, { color: string; label: string }> = {
  SPIKE_VS_SELF:        { color: '#B11226', label: 'Spike vs. own baseline' },
  ELEVATED_VS_SELF:     { color: '#A8456A', label: 'Elevated vs. own baseline' },
  AT_BASELINE:          { color: '#2E7D5B', label: 'At its own baseline' },
  BELOW_BASELINE:       { color: '#9A9AA2', label: 'Below its own baseline' },
  INSUFFICIENT_HISTORY: { color: '#9A9AA2', label: 'Building baseline' },
};

const PIPELINE = [
  { key: 'Dark Positioning', label: 'Dark Positioning', desc: 'Insider Form 4 / 13F — smart money', detect: true },
  { key: 'Expert Warning', label: 'Expert Warning', desc: '8-K material events, macro stress', detect: false },
  { key: 'Consumer Concern', label: 'Consumer Concern', desc: 'Financial communities', detect: false },
  { key: 'Media Coverage', label: 'Media Coverage', desc: 'News flow', detect: false },
  { key: 'Retail Amplify', label: 'Retail Amplify', desc: 'Finance YouTube / crowd', detect: false },
] as const;

const COMPONENT_LABELS: Record<string, string> = {
  gradient_strength: 'Niche Concentration',
  dark_matter: 'Dark matter (insider positioning)',
  inertia: 'Inertia (acceleration)',
  medium_sequence: 'Diffusion (cross-stage)',
  confidence_decay: 'Freshness',
};

// Market Gradient — neutral intensity tiers + colors (describe how unusual the
// positioning is, never what to do). Mirrors the Trends gradient's tier legend.
const MARKET_TIER_COLOR: Record<string, string> = {
  ELEVATED: '#B11226', ACTIVE: '#A8456A', MODERATE: '#A8456A', BUILDING: '#A8456A',
  ROUTINE: '#2A5B9E', DORMANT: '#9A9AA2',
};
const MARKET_TIERS = [
  { key: 'ELEVATED', range: '80–100', desc: 'Strongly elevated positioning' },
  { key: 'ACTIVE',   range: '60–79',  desc: 'Clearly above routine' },
  { key: 'BUILDING', range: '40–59',  desc: 'Building, not yet elevated' },
  { key: 'ROUTINE',  range: '25–39',  desc: 'In line with own baseline' },
  { key: 'DORMANT',  range: '0–24',   desc: 'Quiet vs baseline' },
];
// Component color by which score it feeds (detection=blue, confidence=green, both=purple).
const FEEDS_COLOR: Record<string, string> = { detection: '#2A5B9E', confidence: '#2E7D5B', both: '#6B4FA0' };
const MKT_DET = '#2A5B9E';
const MKT_CONF = '#2E7D5B';

export default function RiskDetail() {
  const { key, from } = useLocalSearchParams<{ key: string; from?: string }>();
  const router = useRouter();
  const goBack = () => { if (from) router.replace(from as any); else router.back(); };
  const backLabel = from === '/profile/watchlists' ? 'Watchlists' : from === '/alerts' ? 'Alerts' : from === '/profile/favorites' ? 'Favorites' : 'Market Signal';
  const { risk, isLoading } = useRisk(String(key));

  if (isLoading) {
    return (
      <Screen>
        <TouchableOpacity onPress={goBack} className="mt-4 mb-8 self-start">
          <ChevronLeft size={24} color="#3C4663" />
        </TouchableOpacity>
        <ActivityIndicator size="large" color="#A8456A" style={{ marginTop: 40 }} />
      </Screen>
    );
  }
  if (!risk) {
    return (
      <Screen>
        <TouchableOpacity onPress={goBack} className="mt-4 mb-8 self-start">
          <ChevronLeft size={24} color="#3C4663" />
        </TouchableOpacity>
        <Text className="text-textMuted text-center mt-20">Not found.</Text>
      </Screen>
    );
  }

  const cls = risk.classification ?? 'CALIBRATING';
  const color = CLASS_COLOR[cls] ?? '#9A9AA2';
  const matColor = MATURITY_COLOR[risk.maturity] ?? '#9A9AA2';
  const maxStage = Math.max(1, ...PIPELINE.map((s) => risk.stages?.[s.key]?.count ?? 0));

  return (
    <Screen scroll>
      {(() => {
        const mg = risk.marketGradient;
        const tier = mg?.tier ?? 'DORMANT';
        const tierCol = MARKET_TIER_COLOR[tier] ?? '#9A9AA2';
        const gap = mg ? Math.round(Math.abs(mg.gap)) : 0;
        const v2 = !!(mg && (mg.modelVersion || mg.flow));
        const flowMeta = mg?.flow === 'inflow' ? { t: '▲ inflow', c: '#2E7D5B' }
          : mg?.flow === 'outflow' ? { t: '▼ outflow', c: '#B11226' }
          : mg?.flow === 'neutral' ? { t: '• neutral', c: '#9A9AA2' } : null;
        return (
          <>
            <TouchableOpacity onPress={goBack} className="mt-4 mb-4 self-start flex-row items-center gap-1">
              <ChevronLeft size={22} color="#3C4663" />
              <Text className="text-textSecondary text-sm">{backLabel}</Text>
            </TouchableOpacity>

            <Text className="text-textMuted text-[12px] font-bold tracking-widest uppercase">Now TrendIn · Market Signal</Text>
            <View className="flex-row items-center gap-2 mt-0.5">
              <Activity size={22} color={tierCol} />
              <Text className="text-textPrimary text-3xl font-bold flex-1">{titleCaseTopic(risk.display)}</Text>
            </View>
            <Text className="text-textMuted text-sm mb-4">{risk.totalSignals} signals · {tier}</Text>

            {/* Market Gradient — dual score (Detection vs Confidence), mirrors Trends */}
            {mg ? (
              <View className="bg-card rounded-2xl p-5 mb-2" style={{ shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, elevation: 2 }}>
                {/* Company / item name above the tier badge + scores */}
                <Text className="text-textPrimary text-lg font-black text-center mb-1">{titleCaseTopic(risk.display)}</Text>
                <View className="self-center flex-row items-center gap-1.5 mb-3">
                  <View className="px-2.5 py-1 rounded-full" style={{ backgroundColor: `${tierCol}1A` }}>
                    <Text style={{ color: tierCol }} className="text-[12px] font-bold tracking-wide">{tier}</Text>
                  </View>
                  {v2 && flowMeta && (
                    <View className="px-2.5 py-1 rounded-full" style={{ backgroundColor: `${flowMeta.c}1A` }}>
                      <Text style={{ color: flowMeta.c }} className="text-[12px] font-bold tracking-wide">{flowMeta.t}</Text>
                    </View>
                  )}
                </View>
                <View className="flex-row justify-around items-start">
                  <View className="items-center">
                    <GradientScoreRing score={Math.round(mg.detection)} color={MKT_DET} size="lg" caption="/100" />
                    <Text className="text-textPrimary text-xs font-bold mt-2">{v2 ? 'MONEY MOVEMENT' : 'DETECTION'}</Text>
                    <Text className="text-textMuted text-[12px]">{v2 ? 'informed money · D' : 'analysts + positioning'}</Text>
                  </View>
                  <View className="items-center">
                    <GradientScoreRing score={Math.round(mg.confidence)} color={MKT_CONF} size="lg" caption="/100" />
                    <Text className="text-textPrimary text-xs font-bold mt-2">{v2 ? 'MARKET CONFIRMATION' : 'CONFIDENCE'}</Text>
                    <Text className="text-textMuted text-[12px]">{v2 ? 'broad market · M' : 'fundamentals + price'}</Text>
                  </View>
                </View>
                <View className="rounded-xl px-3 py-2 mt-4" style={{ borderColor: `${tierCol}55`, backgroundColor: `${tierCol}10` }}>
                  <Text className="text-sm font-bold" style={{ color: tierCol }}>
                    {mg.calibrating ? 'CALIBRATING' : (mg.gapState || `${gap}-pt gap`)}
                    {!mg.calibrating && ` · ${gap}-pt gap`}
                  </Text>
                  {!!mg.interpretation && (
                    <Text className="text-textSecondary text-[14px] leading-5 mt-1">{mg.interpretation}</Text>
                  )}
                </View>
              </View>
            ) : (
              // Fallback: items without a market gradient yet show baseline only.
              <View className="bg-card rounded-2xl p-5 mb-2 items-center">
                <GradientScoreRing score={risk.positioningScore ?? 0} color={tierCol} size="lg" caption="/100" />
                <Text className="text-textPrimary text-xs font-bold mt-2">POSITIONING</Text>
                <Text className="text-textMuted text-[12px]">{risk.percentDelta != null ? `${risk.percentDelta >= 0 ? '+' : ''}${Math.round(risk.percentDelta)}% vs baseline` : 'baseline building'}</Text>
              </View>
            )}
            <Text className="text-textMuted text-[12px] mb-4">
              The Market Gradient splits signals by type: Detection = what analysts say + how smart money is
              positioned (leading); Confidence = what fundamentals and price confirm (hard data). The gap shows
              how early the move is. Measurement only — not financial advice.
            </Text>

            {/* Component breakdown — the seven market factors, colored by which
                score they feed. ✓ = baseline-relative (scored vs this item's own
                history); otherwise still calibrating on absolute scale. */}
            {mg && Object.keys(mg.components).length > 0 && (
              <View className="bg-card rounded-2xl p-4 mb-3">
                <Text className="text-textMuted text-[12px] font-bold tracking-widest uppercase mb-3">Market factors</Text>
                {Object.entries(mg.components).map(([label, c]) => {
                  const na = c.notApplicable || c.score == null;
                  const col = na ? '#9A9AA2' : (FEEDS_COLOR[c.feeds] ?? '#9A9AA2');
                  const pct = na ? 0 : Math.max(4, Math.min(100, c.score ?? 0));
                  return (
                    <View key={label} className="mb-2.5" style={na ? { opacity: 0.5 } : undefined}>
                      <View className="flex-row justify-between mb-1">
                        <View className="flex-row items-center gap-1.5 flex-1 pr-2">
                          <View style={{ width: 7, height: 7, borderRadius: 4, backgroundColor: col }} />
                          <Text className="text-textSecondary text-[12px] flex-1" numberOfLines={1}>{label}</Text>
                          {!na && c.baselineRelative && <Text className="text-[12px]" style={{ color: '#2E7D5B' }}>✓ base</Text>}
                        </View>
                        <Text className="text-textPrimary text-[12px] font-bold">{na ? 'n/a' : Math.round(c.score ?? 0)}</Text>
                      </View>
                      <View className="h-1.5 rounded-full bg-border overflow-hidden">
                        <View style={{ width: `${pct}%`, backgroundColor: col }} className="h-full rounded-full" />
                      </View>
                    </View>
                  );
                })}
                <Text className="text-textMuted text-[12px] mt-1">
                  <Text style={{ color: '#2A5B9E' }}>Blue</Text> = leading (Detection) · <Text style={{ color: '#2E7D5B' }}>Green</Text> = confirming · <Text style={{ color: '#6B4FA0' }}>Purple</Text> = both. ✓ base = scored vs this item's own history.
                </Text>
              </View>
            )}

            {/* Tier legend — what the intensity bands mean (mirrors Trends legend) */}
            <View className="bg-card rounded-2xl p-4 mb-5">
              <Text className="text-textMuted text-[12px] font-bold tracking-widest uppercase mb-3">What the tiers mean</Text>
              <View className="flex-row flex-wrap gap-2">
                {MARKET_TIERS.map((t) => {
                  const tc = MARKET_TIER_COLOR[t.key];
                  return (
                    <View key={t.key} className="flex-1 min-w-[46%] rounded-xl p-3" style={{ borderColor: `${tc}55`, backgroundColor: `${tc}12` }}>
                      <Text style={{ color: tc }} className="text-xs font-bold">{t.key}</Text>
                      <Text className="text-textMuted text-[12px] mt-0.5">{t.range}</Text>
                      <Text style={{ color: tc }} className="text-[12px] font-semibold mt-1">{t.desc}</Text>
                    </View>
                  );
                })}
              </View>
            </View>
          </>
        );
      })()}

      {/* Financial Sustainability — factual balance-sheet health (companies only) */}
      {!!risk.sustainability && (() => {
        const s = risk.sustainability!;
        const tone = (v: number) => v >= 75 ? '#2E7D5B' : v >= 50 ? '#2A5B9E' : v >= 30 ? '#A8456A' : '#B11226';
        const sc = tone(s.score);
        const hasAdj = s.sectorAdjustedScore != null && s.sectorAdjustedScore !== s.score;
        const adj = s.sectorAdjustedScore ?? s.score;
        const adjC = tone(adj);
        const Bar = ({ label, val }: { label: string; val: number | null }) => (
          <View className="mb-2">
            <View className="flex-row justify-between mb-1">
              <Text className="text-textSecondary text-[12px]">{label}</Text>
              <Text className="text-textPrimary text-[12px] font-bold">{val == null ? 'n/a' : Math.round(val)}</Text>
            </View>
            <View className="h-1.5 rounded-full bg-border overflow-hidden">
              <View style={{ width: `${Math.max(0, Math.min(100, val ?? 0))}%`, backgroundColor: sc }} className="h-full rounded-full" />
            </View>
          </View>
        );
        return (
          <>
            <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Financial sustainability</Text>
            <View className="bg-card rounded-2xl p-4 mb-2" style={{ borderColor: `${sc}55` }}>
              {/* Dual score: raw (vs all companies) + sector-adjusted */}
              <View className="flex-row gap-3 mb-3">
                <View className="flex-1 rounded-xl p-3" style={{ backgroundColor: `${sc}12` }}>
                  <Text className="text-textMuted text-[12px] font-bold">SCORE</Text>
                  <Text className="text-2xl font-black" style={{ color: sc }}>{s.score}<Text className="text-textMuted text-sm font-bold">/100</Text></Text>
                  <Text className="text-[12px] font-semibold" style={{ color: sc }}>{s.label}</Text>
                  <Text className="text-textMuted text-[12px] mt-0.5">vs all companies</Text>
                </View>
                <View className="flex-1 rounded-xl p-3" style={{ backgroundColor: `${adjC}12` }}>
                  <Text className="text-textMuted text-[12px] font-bold">SECTOR-ADJUSTED</Text>
                  <Text className="text-2xl font-black" style={{ color: adjC }}>{adj}<Text className="text-textMuted text-sm font-bold">/100</Text></Text>
                  <Text className="text-[12px] font-semibold" style={{ color: adjC }}>{s.sectorAdjustedLabel || s.label}</Text>
                  <Text className="text-textMuted text-[12px] mt-0.5">vs {s.sector || 'sector'} peers</Text>
                </View>
              </View>
              {!!s.sectorExplanation && (
                <Text className="text-textSecondary text-[12px] leading-4 mb-3">{s.sectorExplanation}</Text>
              )}
              <Bar label="Profitability (margin · ROE)" val={s.profitability} />
              <Bar label="Cash & liquidity" val={s.liquidity} />
              <Bar label={hasAdj ? 'Leverage health (raw)' : 'Leverage health (lower debt = higher)'} val={s.leverageHealth} />
              {hasAdj && <Bar label={`Leverage health (vs ${s.sector || 'sector'})`} val={s.leverageHealthSector ?? null} />}
              <View className="flex-row flex-wrap gap-x-4 gap-y-1 mt-2 pt-2 border-t border-border">
                {s.netProfitMargin != null && <Text className="text-textMuted text-[12px]">Net margin {s.netProfitMargin}%</Text>}
                {s.roe != null && <Text className="text-textMuted text-[12px]">ROE {s.roe}%</Text>}
                {s.currentRatio != null && <Text className="text-textMuted text-[12px]">Current ratio {s.currentRatio}</Text>}
                {s.debtToEquity != null && <Text className="text-textMuted text-[12px]">Debt/equity {s.debtToEquity}</Text>}
              </View>
            </View>
            <Text className="text-textMuted text-[12px] mb-5">
              From {s.ticker}'s reported financials. Descriptive data only — not a buy/sell recommendation or financial advice.
            </Text>
          </>
        );
      })()}

      {/* Retail Coverage — attributed data points, not advice. No external
          links (titles/URLs are shown as plain copyable text).
          §17: show ONLY sources that contribute for this topic — omit no-data sources entirely. */}
      {(() => {
        const hasNews = !!risk.alphaVantage && (risk.alphaVantage.articleCount ?? 0) > 0;
        const coveredCreators = (risk.creatorCoverage?.creators ?? []).filter((c) => c.covered);
        const hasBroadcast = !!risk.broadcastCoverage && risk.broadcastCoverage.channels.length > 0;
        const note = risk.alphaVantage?.note || risk.creatorCoverage?.note || risk.meetKevin?.note;
        if (!hasNews && coveredCreators.length === 0 && !hasBroadcast) return null;
        return (
        <>
          <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Retail Coverage</Text>
          <View className="bg-card rounded-2xl p-4 mb-2">
            {/* Alpha Vantage — news volume + tone */}
            {hasNews && (
              <View className="mb-3">
                <Text className="text-textPrimary text-sm font-bold mb-1">
                  {risk.alphaVantage!.articleCount} recent news article{risk.alphaVantage!.articleCount === 1 ? '' : 's'}
                  {risk.alphaVantage!.sentimentLabel ? ` · ${risk.alphaVantage!.sentimentLabel}` : ''}
                </Text>
                {(risk.alphaVantage!.recent ?? []).slice(0, 3).map((a, i) => (
                  <View key={i} className="mb-1">
                    <Text className="text-textSecondary text-[12px] leading-4" numberOfLines={2}>▸ {a.title}</Text>
                    <Text className="text-textMuted text-[12px]">{a.source} · {(a.published || '').slice(0, 8)}</Text>
                  </View>
                ))}
              </View>
            )}
            {/* Creator coverage — only creators that actually covered this topic */}
            {coveredCreators.map((cr, ci) => (
              <View key={cr.handle} className={(ci > 0 || hasNews) ? 'pt-3 border-t border-border' : ''}>
                <View className="flex-row items-center gap-2 mb-1">
                  <Play size={16} color="#B11226" />
                  <Text className="text-textPrimary text-sm font-bold flex-1">
                    {cr.name}: {cr.count} recent video{cr.count === 1 ? '' : 's'} on this name
                  </Text>
                </View>
                {(cr.recent ?? []).map((v, i) => (
                  <View key={i} className="mb-1.5">
                    <Text className="text-textSecondary text-[14px] leading-5" numberOfLines={2}>▸ {v.title}</Text>
                    <Text className="text-textMuted text-[12px]">{(v.published || '').slice(0, 10)}</Text>
                  </View>
                ))}
                <Text className="text-textMuted text-[12px] mt-1">Source: {cr.name} (youtube.com/@{cr.handle})</Text>
              </View>
            ))}
          </View>
          {/* Broadcast / institutional media coverage */}
          {hasBroadcast && (
            <View className={(coveredCreators.length > 0 || hasNews) ? 'pt-3 border-t border-border mt-1' : ''}>
              <Text className="text-textSecondary text-xs font-semibold uppercase tracking-wider mb-2">
                Broadcast Media ({risk.broadcastCoverage!.channels.length}/{risk.broadcastCoverage!.totalChannels} channels)
              </Text>
              {risk.broadcastCoverage!.channels.map((ch, ci) => (
                <View key={ch.handle} className={ci > 0 ? 'pt-2 border-t border-border mt-1' : ''}>
                  <View className="flex-row items-center gap-2 mb-0.5">
                    <Play size={14} color="#3C4663" />
                    <Text className="text-textPrimary text-[14px] font-semibold flex-1">
                      {ch.name}{ch.region ? ` · ${ch.region}` : ''}: {ch.count} recent video{ch.count === 1 ? '' : 's'}
                    </Text>
                  </View>
                  {(ch.recent ?? []).slice(0, 2).map((v, i) => (
                    <View key={i} className="mb-1">
                      <Text className="text-textSecondary text-[12px] leading-4" numberOfLines={2}>▸ {v.title}</Text>
                      <Text className="text-textMuted text-[12px]">{(v.published || '').slice(0, 10)}</Text>
                    </View>
                  ))}
                </View>
              ))}
            </View>
          )}
          {!!note && (
            <Text className="text-textMuted text-[12px] mb-5">{note}</Text>
          )}
        </>
        );
      })()}

      {/* Leverage — FINRA short interest (company) + OFR macro funding context */}
      {(!!risk.shortInterest || !!risk.macroLeverage || !!risk.institutionalHoldings) && (
        <>
          <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Leverage &amp; funding</Text>
          <View className="bg-card rounded-2xl p-4 mb-5">
            {!!risk.shortInterest && (
              <View className="mb-2">
                <Text className="text-textPrimary text-sm font-bold mb-1">{risk.shortInterest.label}</Text>
                <View className="flex-row flex-wrap gap-x-4 gap-y-1">
                  {risk.shortInterest.shortPosition != null && (
                    <Text className="text-textSecondary text-[12px]">Short interest {(risk.shortInterest.shortPosition / 1e6).toFixed(1)}M sh</Text>
                  )}
                  {risk.shortInterest.changePct != null && (
                    <Text className="text-textSecondary text-[12px]">{risk.shortInterest.changePct >= 0 ? '+' : ''}{risk.shortInterest.changePct}% vs prior</Text>
                  )}
                  {risk.shortInterest.daysToCover != null && (
                    <Text className="text-textSecondary text-[12px]">{risk.shortInterest.daysToCover} days to cover</Text>
                  )}
                </View>
                <Text className="text-textMuted text-[12px] mt-1">FINRA short interest{risk.shortInterest.settlementDate ? ` · ${risk.shortInterest.settlementDate}` : ''}</Text>
              </View>
            )}
            {!!risk.macroLeverage && (
              <View className={risk.shortInterest ? 'pt-2 border-t border-border' : ''}>
                <Text className="text-textSecondary text-[12px]">
                  Market funding: <Text className="font-semibold text-textPrimary">{risk.macroLeverage.leverageLabel}</Text>
                  {risk.macroLeverage.stressLabel ? ` · ${risk.macroLeverage.stressLabel}` : ''}
                </Text>
                <Text className="text-textMuted text-[12px] mt-1">OFR Short-Term Funding Monitor (repo){risk.macroLeverage.asOf ? ` · ${risk.macroLeverage.asOf}` : ''}</Text>
              </View>
            )}
            {!!risk.institutionalHoldings && (
              <View className={(risk.shortInterest || risk.macroLeverage) ? 'pt-2 border-t border-border mt-2' : ''}>
                <Text className="text-textPrimary text-sm font-bold mb-1">{risk.institutionalHoldings.label || 'Institutional positioning'}</Text>
                <View className="flex-row flex-wrap gap-x-4 gap-y-1">
                  {risk.institutionalHoldings.holdersCount != null && (
                    <Text className="text-textSecondary text-[12px]">{risk.institutionalHoldings.holdersCount} institutional holders</Text>
                  )}
                  {risk.institutionalHoldings.sharesChangePct != null && (
                    <Text className="text-textSecondary text-[12px]">{risk.institutionalHoldings.sharesChangePct >= 0 ? '+' : ''}{risk.institutionalHoldings.sharesChangePct}% avg position change</Text>
                  )}
                </View>
                {!!risk.institutionalHoldings.topHolders?.length && (
                  <Text className="text-textMuted text-[12px] mt-1" numberOfLines={2}>
                    Top: {risk.institutionalHoldings.topHolders.slice(0, 4).map((h) => h.name).join(', ')}
                  </Text>
                )}
                <Text className="text-textMuted text-[12px] mt-1">WhaleWisdom 13F institutional holdings</Text>
              </View>
            )}
            <Text className="text-textMuted text-[12px] mt-2">Descriptive leverage indicators — not investment advice.</Text>
          </View>
        </>
      )}

      {/* Market tenure / maturity — the analysis the user asked for */}
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Market tenure</Text>
      <View className="bg-card rounded-2xl p-4 mb-5" style={{ borderColor: `${matColor}55` }}>
        <View className="flex-row items-center gap-2 mb-2">
          <Clock size={14} color={matColor} />
          <Text className="text-sm font-bold" style={{ color: matColor }}>{risk.maturity || 'UNCLASSIFIED'}</Text>
        </View>
        <Text className="text-textSecondary text-[14px] leading-5">{risk.maturityNote}</Text>
      </View>

      {/* Abnormal-vs-own-baseline — emerging vs. always-present */}
      {!!risk.baselineStatus && (() => {
        const bm = BASELINE_META[risk.baselineStatus!] ?? BASELINE_META.INSUFFICIENT_HISTORY;
        const insufficient = risk.baselineStatus === 'INSUFFICIENT_HISTORY';
        const abn = risk.abnormality ?? 0;
        const abnLabel = abn > 0 ? `+${abn}%` : `${abn}%`;
        return (
          <>
            <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Vs. its own baseline</Text>
            <View className="bg-card rounded-2xl p-4 mb-5" style={{ borderColor: `${bm.color}55` }}>
              <View className="flex-row items-center justify-between mb-2">
                <View className="flex-row items-center gap-2">
                  <Activity size={14} color={bm.color} />
                  <Text className="text-sm font-bold" style={{ color: bm.color }}>{bm.label}</Text>
                </View>
                {!insufficient && (
                  <Text className="text-lg font-black" style={{ color: bm.color }}>{abnLabel}</Text>
                )}
              </View>
              {!insufficient && (
                <Text className="text-textMuted text-[12px] mb-2">
                  Now {risk.totalSignals} signals vs. a {risk.baselineSignals}-signal baseline over{' '}
                  {risk.baselineCycles} prior cycles.
                </Text>
              )}
              <Text className="text-textSecondary text-[14px] leading-5">{risk.baselineNote}</Text>
              <View className="flex-row items-start gap-2 mt-3 pt-3 border-t border-border">
                <Info size={13} color="#9A9AA2" />
                <Text className="text-textMuted text-[12px] leading-4 flex-1">
                  Established names carry routine insider / 8-K activity every cycle, so absolute counts always
                  look elevated. This compares the topic against ITS OWN history — only an abnormal rise above
                  its baseline marks genuinely unusual positioning.
                </Text>
              </View>
            </View>
          </>
        );
      })()}

      {/* Why this matters */}
      {!!risk.interpretation && (
        <>
          <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">What this means</Text>
          <Text className="text-textSecondary text-base leading-6 mb-5">{risk.interpretation}</Text>
        </>
      )}

      {/* Diffusion pipeline */}
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3">Diffusion pipeline</Text>
      <View className="bg-card rounded-2xl p-4 mb-5">
        {PIPELINE.map((s) => {
          const v = risk.stages?.[s.key]?.count ?? 0;
          const pct = Math.round((v / maxStage) * 100);
          return (
            <View key={s.key} className="mb-3">
              <View className="flex-row items-center justify-between mb-1">
                <View className="flex-row items-center gap-2 flex-1 pr-2">
                  <Text className="text-textPrimary text-sm font-semibold">{s.label}</Text>
                  {s.detect && (
                    <View className="px-1.5 rounded" style={{ backgroundColor: color }}>
                      <Text style={{ fontSize: 12, color: '#FFF', fontWeight: '700' }}>DETECT</Text>
                    </View>
                  )}
                </View>
                <Text className="text-textPrimary text-sm font-bold">{v}</Text>
              </View>
              <View className="h-1.5 rounded-full bg-border overflow-hidden">
                <View style={{ width: `${pct}%`, backgroundColor: v > 0 ? color : '#ECECEC' }} className="h-full rounded-full" />
              </View>
              <Text className="text-textMuted text-[12px] mt-1">{s.desc}</Text>
            </View>
          );
        })}
      </View>

      {/* Components */}
      {Object.keys(risk.components).length > 0 && (
        <>
          <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3">Score components</Text>
          <View className="bg-card rounded-2xl p-4 mb-5 gap-3">
            {Object.entries(risk.components).map(([k, val]) => (
              <View key={k}>
                <View className="flex-row justify-between mb-1">
                  <Text className="text-textSecondary text-sm flex-1 pr-2">{COMPONENT_LABELS[k] ?? k}</Text>
                  <Text className="text-textPrimary text-sm font-semibold">{Math.round(Number(val))}</Text>
                </View>
                <View className="h-1.5 rounded-full bg-border overflow-hidden">
                  <View style={{ width: `${Math.max(0, Math.min(100, Number(val)))}%`, backgroundColor: color }} className="h-full rounded-full" />
                </View>
              </View>
            ))}
          </View>
        </>
      )}

      {/* Source provenance */}
      {risk.sources.length > 0 && (
        <View className="flex-row items-center gap-2 mb-8 bg-card rounded-xl px-4 py-3">
          <Globe size={13} color="#3C4663" />
          <Text className="text-textSecondary text-xs flex-1">
            Sources: {risk.sources.join(' · ')} — all public filings, government data, or official APIs. Results proprietary to Now TrendIn.
          </Text>
        </View>
      )}

      <Text className="text-textMuted text-[12px] text-center mb-8 px-2 leading-4">
        Positioning analysis for informational purposes only — not financial, investment, or legal advice,
        and not a risk rating of any company. All decisions are your own.
      </Text>
    </Screen>
  );
}
