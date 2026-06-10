import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ChevronLeft, Globe, Clock, Info, Activity, Play } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { GradientScoreRing } from '../../components/ui/GradientScoreRing';
import { useRisk } from '../../hooks/useSignals';

const CLASS_COLOR: Record<string, string> = {
  UNUSUAL: '#CF2A1B', ELEVATED: '#E85A1E', WATCH: '#2D7EEF', ROUTINE: '#9AA3B0', CALIBRATING: '#9AA3B0',
};

const MATURITY_COLOR: Record<string, string> = {
  ESTABLISHED: '#2D7EEF', MACRO: '#8B5CF6', EMERGING: '#D4A017',
};

const BASELINE_META: Record<string, { color: string; label: string }> = {
  SPIKE_VS_SELF:        { color: '#CF2A1B', label: 'Spike vs. own baseline' },
  ELEVATED_VS_SELF:     { color: '#E85A1E', label: 'Elevated vs. own baseline' },
  AT_BASELINE:          { color: '#00C896', label: 'At its own baseline' },
  BELOW_BASELINE:       { color: '#9AA3B0', label: 'Below its own baseline' },
  INSUFFICIENT_HISTORY: { color: '#9AA3B0', label: 'Building baseline' },
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
  ELEVATED: '#CF2A1B', ACTIVE: '#E85A1E', BUILDING: '#D4A017',
  ROUTINE: '#2D7EEF', DORMANT: '#9AA3B0',
};
const MARKET_TIERS = [
  { key: 'ELEVATED', range: '80–100', desc: 'Strongly elevated positioning' },
  { key: 'ACTIVE',   range: '60–79',  desc: 'Clearly above routine' },
  { key: 'BUILDING', range: '40–59',  desc: 'Building, not yet elevated' },
  { key: 'ROUTINE',  range: '25–39',  desc: 'In line with own baseline' },
  { key: 'DORMANT',  range: '0–24',   desc: 'Quiet vs baseline' },
];
// The six Market Gradient components, grouped by which score they drive.
const MARKET_COMPONENTS: { key: string; label: string; side: 'DET' | 'CONF' }[] = [
  { key: 'analyst_signal',       label: 'Analyst Signal',       side: 'DET' },
  { key: 'positioning_pressure', label: 'Positioning Pressure', side: 'DET' },
  { key: 'baseline_abnormality', label: 'Baseline Abnormality', side: 'DET' },
  { key: 'fundamentals',         label: 'Fundamentals',         side: 'CONF' },
  { key: 'price_action',         label: 'Price Action',         side: 'CONF' },
  { key: 'macro_context',        label: 'Macro Context',        side: 'CONF' },
];
const MKT_DET = '#2D7EEF';
const MKT_CONF = '#00C896';

export default function RiskDetail() {
  const { key } = useLocalSearchParams<{ key: string }>();
  const router = useRouter();
  const { risk, isLoading } = useRisk(String(key));

  if (isLoading) {
    return (
      <Screen>
        <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-8 self-start">
          <ChevronLeft size={24} color="#5B6472" />
        </TouchableOpacity>
        <ActivityIndicator size="large" color="#E85A1E" style={{ marginTop: 40 }} />
      </Screen>
    );
  }
  if (!risk) {
    return (
      <Screen>
        <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-8 self-start">
          <ChevronLeft size={24} color="#5B6472" />
        </TouchableOpacity>
        <Text className="text-textMuted text-center mt-20">Not found.</Text>
      </Screen>
    );
  }

  const cls = risk.classification ?? 'CALIBRATING';
  const color = CLASS_COLOR[cls] ?? '#9AA3B0';
  const matColor = MATURITY_COLOR[risk.maturity] ?? '#9AA3B0';
  const maxStage = Math.max(1, ...PIPELINE.map((s) => risk.stages?.[s.key]?.count ?? 0));

  return (
    <Screen scroll>
      {(() => {
        const mg = risk.marketGradient;
        const tier = mg?.tier ?? 'DORMANT';
        const tierCol = MARKET_TIER_COLOR[tier] ?? '#9AA3B0';
        const gap = mg ? Math.round(Math.abs(mg.gap)) : 0;
        return (
          <>
            <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-4 self-start flex-row items-center gap-1">
              <ChevronLeft size={22} color="#5B6472" />
              <Text className="text-textSecondary text-sm">Market Signal</Text>
            </TouchableOpacity>

            <Text className="text-textMuted text-[10px] font-bold tracking-widest uppercase">Now TrendIn · Market Signal</Text>
            <View className="flex-row items-center gap-2 mt-0.5">
              <Activity size={22} color={tierCol} />
              <Text className="text-textPrimary text-3xl font-bold flex-1">{risk.display}</Text>
            </View>
            <Text className="text-textMuted text-sm mb-4">{risk.totalSignals} signals · {tier}</Text>

            {/* Market Gradient — dual score (Detection vs Confidence), mirrors Trends */}
            {mg ? (
              <View className="bg-surface rounded-2xl p-5 border border-border mb-2" style={{ shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, elevation: 2 }}>
                <View className="self-center px-2.5 py-1 rounded-full mb-3" style={{ backgroundColor: `${tierCol}1A` }}>
                  <Text style={{ color: tierCol }} className="text-[9px] font-bold tracking-wide">{tier}</Text>
                </View>
                <View className="flex-row justify-around items-start">
                  <View className="items-center">
                    <GradientScoreRing score={Math.round(mg.detection)} color={MKT_DET} size="lg" caption="/100" />
                    <Text className="text-textPrimary text-xs font-bold mt-2">DETECTION</Text>
                    <Text className="text-textMuted text-[10px]">analysts + positioning</Text>
                  </View>
                  <View className="items-center">
                    <GradientScoreRing score={Math.round(mg.confidence)} color={MKT_CONF} size="lg" caption="/100" />
                    <Text className="text-textPrimary text-xs font-bold mt-2">CONFIDENCE</Text>
                    <Text className="text-textMuted text-[10px]">fundamentals + price</Text>
                  </View>
                </View>
                <View className="rounded-xl px-3 py-2 mt-4 border" style={{ borderColor: `${tierCol}55`, backgroundColor: `${tierCol}10` }}>
                  <Text className="text-sm font-bold" style={{ color: tierCol }}>
                    {gap}-pt gap{mg.gap >= 0 ? ' — leading signals ahead of confirmation' : ' — confirmed in hard data'}
                  </Text>
                  {!!mg.interpretation && (
                    <Text className="text-textSecondary text-[13px] leading-5 mt-1">{mg.interpretation}</Text>
                  )}
                </View>
              </View>
            ) : (
              // Fallback: items without a market gradient yet show baseline only.
              <View className="bg-surface rounded-2xl p-5 border border-border mb-2 items-center">
                <GradientScoreRing score={risk.positioningScore ?? 0} color={tierCol} size="lg" caption="/100" />
                <Text className="text-textPrimary text-xs font-bold mt-2">POSITIONING</Text>
                <Text className="text-textMuted text-[10px]">{risk.percentDelta != null ? `${risk.percentDelta >= 0 ? '+' : ''}${Math.round(risk.percentDelta)}% vs baseline` : 'baseline building'}</Text>
              </View>
            )}
            <Text className="text-textMuted text-[10px] mb-4">
              The Market Gradient splits signals by type: Detection = what analysts say + how smart money is
              positioned (leading); Confidence = what fundamentals and price confirm (hard data). The gap shows
              how early the move is. Measurement only — not financial advice.
            </Text>

            {/* Component breakdown — the six market factors, by side */}
            {mg && (
              <View className="bg-surface rounded-2xl border border-border p-4 mb-3">
                <Text className="text-textMuted text-[10px] font-bold tracking-widest uppercase mb-3">Market factors</Text>
                {MARKET_COMPONENTS.map((c) => {
                  const raw = (mg.components as any)?.[c.key];
                  const col = c.side === 'DET' ? MKT_DET : MKT_CONF;
                  const present = raw != null;
                  return (
                    <View key={c.key} className="mb-2.5">
                      <View className="flex-row justify-between mb-1">
                        <View className="flex-row items-center gap-1.5">
                          <View style={{ width: 7, height: 7, borderRadius: 4, backgroundColor: present ? col : '#E4E7EC' }} />
                          <Text className="text-textSecondary text-[12px]">{c.label}</Text>
                        </View>
                        <Text className="text-textPrimary text-[12px] font-bold">{present ? Math.round(raw) : 'n/a'}</Text>
                      </View>
                      <View className="h-1.5 rounded-full bg-border overflow-hidden">
                        <View style={{ width: `${present ? Math.max(4, Math.min(100, raw)) : 0}%`, backgroundColor: col }} className="h-full rounded-full" />
                      </View>
                    </View>
                  );
                })}
                <Text className="text-textMuted text-[10px] mt-1">
                  <Text style={{ color: MKT_DET }}>Blue</Text> = leading (Detection) · <Text style={{ color: MKT_CONF }}>Green</Text> = confirming (Confidence). "n/a" = no ticker-level data for this item.
                </Text>
              </View>
            )}

            {/* Tier legend — what the intensity bands mean (mirrors Trends legend) */}
            <View className="bg-surface rounded-2xl border border-border p-4 mb-5">
              <Text className="text-textMuted text-[10px] font-bold tracking-widest uppercase mb-3">What the tiers mean</Text>
              <View className="flex-row flex-wrap gap-2">
                {MARKET_TIERS.map((t) => {
                  const tc = MARKET_TIER_COLOR[t.key];
                  return (
                    <View key={t.key} className="flex-1 min-w-[46%] rounded-xl p-3 border" style={{ borderColor: `${tc}55`, backgroundColor: `${tc}12` }}>
                      <Text style={{ color: tc }} className="text-xs font-bold">{t.key}</Text>
                      <Text className="text-textMuted text-[10px] mt-0.5">{t.range}</Text>
                      <Text style={{ color: tc }} className="text-[11px] font-semibold mt-1">{t.desc}</Text>
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
        const tone = (v: number) => v >= 75 ? '#00C896' : v >= 50 ? '#2D7EEF' : v >= 30 ? '#D4A017' : '#CF2A1B';
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
            <View className="bg-surface rounded-2xl border p-4 mb-2" style={{ borderColor: `${sc}55` }}>
              {/* Dual score: raw (vs all companies) + sector-adjusted */}
              <View className="flex-row gap-3 mb-3">
                <View className="flex-1 rounded-xl p-3" style={{ backgroundColor: `${sc}12` }}>
                  <Text className="text-textMuted text-[10px] font-bold">SCORE</Text>
                  <Text className="text-2xl font-black" style={{ color: sc }}>{s.score}<Text className="text-textMuted text-sm font-bold">/100</Text></Text>
                  <Text className="text-[11px] font-semibold" style={{ color: sc }}>{s.label}</Text>
                  <Text className="text-textMuted text-[9px] mt-0.5">vs all companies</Text>
                </View>
                <View className="flex-1 rounded-xl p-3" style={{ backgroundColor: `${adjC}12` }}>
                  <Text className="text-textMuted text-[10px] font-bold">SECTOR-ADJUSTED</Text>
                  <Text className="text-2xl font-black" style={{ color: adjC }}>{adj}<Text className="text-textMuted text-sm font-bold">/100</Text></Text>
                  <Text className="text-[11px] font-semibold" style={{ color: adjC }}>{s.sectorAdjustedLabel || s.label}</Text>
                  <Text className="text-textMuted text-[9px] mt-0.5">vs {s.sector || 'sector'} peers</Text>
                </View>
              </View>
              {!!s.sectorExplanation && (
                <Text className="text-textSecondary text-[11px] leading-4 mb-3">{s.sectorExplanation}</Text>
              )}
              <Bar label="Profitability (margin · ROE)" val={s.profitability} />
              <Bar label="Cash & liquidity" val={s.liquidity} />
              <Bar label={hasAdj ? 'Leverage health (raw)' : 'Leverage health (lower debt = higher)'} val={s.leverageHealth} />
              {hasAdj && <Bar label={`Leverage health (vs ${s.sector || 'sector'})`} val={s.leverageHealthSector ?? null} />}
              <View className="flex-row flex-wrap gap-x-4 gap-y-1 mt-2 pt-2 border-t border-border">
                {s.netProfitMargin != null && <Text className="text-textMuted text-[11px]">Net margin {s.netProfitMargin}%</Text>}
                {s.roe != null && <Text className="text-textMuted text-[11px]">ROE {s.roe}%</Text>}
                {s.currentRatio != null && <Text className="text-textMuted text-[11px]">Current ratio {s.currentRatio}</Text>}
                {s.debtToEquity != null && <Text className="text-textMuted text-[11px]">Debt/equity {s.debtToEquity}</Text>}
              </View>
            </View>
            <Text className="text-textMuted text-[10px] mb-5">
              From {s.ticker}'s reported financials. Descriptive data only — not a buy/sell recommendation or financial advice.
            </Text>
          </>
        );
      })()}

      {/* Retail Coverage — attributed data points, not advice. No external
          links (titles/URLs are shown as plain copyable text). */}
      {(!!risk.creatorCoverage || !!risk.alphaVantage || !!risk.broadcastCoverage) && (
        <>
          <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Retail Coverage</Text>
          <View className="bg-surface rounded-2xl border border-border p-4 mb-2">
            {/* Alpha Vantage — news volume + tone */}
            {!!risk.alphaVantage && (
              <View className="mb-3">
                <Text className="text-textPrimary text-sm font-bold mb-1">
                  {risk.alphaVantage.articleCount} recent news article{risk.alphaVantage.articleCount === 1 ? '' : 's'}
                  {risk.alphaVantage.sentimentLabel ? ` · ${risk.alphaVantage.sentimentLabel}` : ''}
                </Text>
                {(risk.alphaVantage.recent ?? []).slice(0, 3).map((a, i) => (
                  <View key={i} className="mb-1">
                    <Text className="text-textSecondary text-[12px] leading-4" numberOfLines={2}>▸ {a.title}</Text>
                    <Text className="text-textMuted text-[10px]">{a.source} · {(a.published || '').slice(0, 8)}</Text>
                  </View>
                ))}
              </View>
            )}
            {/* Creator coverage (Meet Kevin + Andrei Jikh) — attributed, no links */}
            {(risk.creatorCoverage?.creators ?? []).map((cr, ci) => (
              <View key={cr.handle} className={(ci > 0 || risk.alphaVantage) ? 'pt-3 border-t border-border' : ''}>
                <View className="flex-row items-center gap-2 mb-1">
                  <Play size={16} color="#CF2A1B" />
                  <Text className="text-textPrimary text-sm font-bold flex-1">
                    {cr.name}: {cr.covered
                      ? `${cr.count} recent video${cr.count === 1 ? '' : 's'} on this name`
                      : 'not in recent uploads'}
                  </Text>
                </View>
                {cr.covered && (cr.recent ?? []).map((v, i) => (
                  <View key={i} className="mb-1.5">
                    <Text className="text-textSecondary text-[13px] leading-5" numberOfLines={2}>▸ {v.title}</Text>
                    <Text className="text-textMuted text-[10px]">{(v.published || '').slice(0, 10)}</Text>
                  </View>
                ))}
                <Text className="text-textMuted text-[10px] mt-1">Source: {cr.name} (youtube.com/@{cr.handle})</Text>
              </View>
            ))}
          </View>
          {/* Broadcast / institutional media coverage */}
          {!!risk.broadcastCoverage && risk.broadcastCoverage.channels.length > 0 && (
            <View className={(risk.creatorCoverage || risk.alphaVantage) ? 'pt-3 border-t border-border mt-1' : ''}>
              <Text className="text-textSecondary text-xs font-semibold uppercase tracking-wider mb-2">
                Broadcast Media ({risk.broadcastCoverage.channels.length}/{risk.broadcastCoverage.totalChannels} channels)
              </Text>
              {risk.broadcastCoverage.channels.map((ch, ci) => (
                <View key={ch.handle} className={ci > 0 ? 'pt-2 border-t border-border mt-1' : ''}>
                  <View className="flex-row items-center gap-2 mb-0.5">
                    <Play size={14} color="#5B6472" />
                    <Text className="text-textPrimary text-[13px] font-semibold flex-1">
                      {ch.name}{ch.region ? ` · ${ch.region}` : ''}: {ch.count} recent video{ch.count === 1 ? '' : 's'}
                    </Text>
                  </View>
                  {(ch.recent ?? []).slice(0, 2).map((v, i) => (
                    <View key={i} className="mb-1">
                      <Text className="text-textSecondary text-[12px] leading-4" numberOfLines={2}>▸ {v.title}</Text>
                      <Text className="text-textMuted text-[10px]">{(v.published || '').slice(0, 10)}</Text>
                    </View>
                  ))}
                </View>
              ))}
            </View>
          )}
          {!!risk.broadcastCoverage && risk.broadcastCoverage.channels.length === 0 && (
            <View className={(risk.creatorCoverage || risk.alphaVantage) ? 'pt-3 border-t border-border mt-1' : ''}>
              <Text className="text-textMuted text-[12px]">No recent broadcast media coverage across {risk.broadcastCoverage.totalChannels} monitored channels.</Text>
            </View>
          )}
          <Text className="text-textMuted text-[10px] mb-5">
            {risk.alphaVantage?.note || risk.creatorCoverage?.note || risk.meetKevin?.note}
          </Text>
        </>
      )}

      {/* Leverage — FINRA short interest (company) + OFR macro funding context */}
      {(!!risk.shortInterest || !!risk.macroLeverage || !!risk.institutionalHoldings) && (
        <>
          <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Leverage &amp; funding</Text>
          <View className="bg-surface rounded-2xl border border-border p-4 mb-5">
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
                <Text className="text-textMuted text-[10px] mt-1">FINRA short interest{risk.shortInterest.settlementDate ? ` · ${risk.shortInterest.settlementDate}` : ''}</Text>
              </View>
            )}
            {!!risk.macroLeverage && (
              <View className={risk.shortInterest ? 'pt-2 border-t border-border' : ''}>
                <Text className="text-textSecondary text-[12px]">
                  Market funding: <Text className="font-semibold text-textPrimary">{risk.macroLeverage.leverageLabel}</Text>
                  {risk.macroLeverage.stressLabel ? ` · ${risk.macroLeverage.stressLabel}` : ''}
                </Text>
                <Text className="text-textMuted text-[10px] mt-1">OFR Short-Term Funding Monitor (repo){risk.macroLeverage.asOf ? ` · ${risk.macroLeverage.asOf}` : ''}</Text>
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
                  <Text className="text-textMuted text-[11px] mt-1" numberOfLines={2}>
                    Top: {risk.institutionalHoldings.topHolders.slice(0, 4).map((h) => h.name).join(', ')}
                  </Text>
                )}
                <Text className="text-textMuted text-[10px] mt-1">WhaleWisdom 13F institutional holdings</Text>
              </View>
            )}
            <Text className="text-textMuted text-[10px] mt-2">Descriptive leverage indicators — not investment advice.</Text>
          </View>
        </>
      )}

      {/* Market tenure / maturity — the analysis the user asked for */}
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Market tenure</Text>
      <View className="bg-surface rounded-2xl border p-4 mb-5" style={{ borderColor: `${matColor}55` }}>
        <View className="flex-row items-center gap-2 mb-2">
          <Clock size={14} color={matColor} />
          <Text className="text-sm font-bold" style={{ color: matColor }}>{risk.maturity || 'UNCLASSIFIED'}</Text>
        </View>
        <Text className="text-textSecondary text-[13px] leading-5">{risk.maturityNote}</Text>
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
            <View className="bg-surface rounded-2xl border p-4 mb-5" style={{ borderColor: `${bm.color}55` }}>
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
                <Text className="text-textMuted text-[11px] mb-2">
                  Now {risk.totalSignals} signals vs. a {risk.baselineSignals}-signal baseline over{' '}
                  {risk.baselineCycles} prior cycles.
                </Text>
              )}
              <Text className="text-textSecondary text-[13px] leading-5">{risk.baselineNote}</Text>
              <View className="flex-row items-start gap-2 mt-3 pt-3 border-t border-border">
                <Info size={13} color="#9AA3B0" />
                <Text className="text-textMuted text-[11px] leading-4 flex-1">
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
      <View className="bg-surface rounded-2xl border border-border p-4 mb-5">
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
                      <Text style={{ fontSize: 8, color: '#FFF', fontWeight: '700' }}>DETECT</Text>
                    </View>
                  )}
                </View>
                <Text className="text-textPrimary text-sm font-bold">{v}</Text>
              </View>
              <View className="h-1.5 rounded-full bg-border overflow-hidden">
                <View style={{ width: `${pct}%`, backgroundColor: v > 0 ? color : '#E4E7EC' }} className="h-full rounded-full" />
              </View>
              <Text className="text-textMuted text-[10px] mt-1">{s.desc}</Text>
            </View>
          );
        })}
      </View>

      {/* Components */}
      {Object.keys(risk.components).length > 0 && (
        <>
          <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3">Score components</Text>
          <View className="bg-surface rounded-2xl border border-border p-4 mb-5 gap-3">
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
        <View className="flex-row items-center gap-2 mb-8 bg-surface rounded-xl border border-border px-4 py-3">
          <Globe size={13} color="#5B6472" />
          <Text className="text-textSecondary text-xs flex-1">
            Sources: {risk.sources.join(' · ')} — all public filings, government data, or official APIs. Results proprietary to Now TrendIn.
          </Text>
        </View>
      )}

      <Text className="text-textMuted text-[10px] text-center mb-8 px-2 leading-4">
        Positioning analysis for informational purposes only — not financial, investment, or legal advice,
        and not a risk rating of any company. All decisions are your own.
      </Text>
    </Screen>
  );
}
