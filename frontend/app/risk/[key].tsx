import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ChevronLeft, ShieldAlert, Globe, Clock, Info, Activity } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { GradientScoreRing } from '../../components/ui/GradientScoreRing';
import { useRisk } from '../../hooks/useSignals';

const STAGE_COLOR: Record<string, string> = {
  ACUTE: '#CF2A1B', ELEVATED: '#E85A1E', EMERGING: '#D4A017', WATCH: '#2D7EEF', BACKGROUND: '#9AA3B0',
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
  { key: 'dark', label: 'Dark Positioning', desc: 'Insider Form 4 / 13F — smart money', detect: true },
  { key: 'expert', label: 'Expert Warning', desc: '8-K material events, macro stress' },
  { key: 'consumer', label: 'Consumer Concern', desc: 'Financial communities' },
  { key: 'media', label: 'Media Coverage', desc: 'News flow' },
  { key: 'retail', label: 'Retail Amplify', desc: 'Finance YouTube / crowd' },
] as const;

const COMPONENT_LABELS: Record<string, string> = {
  gradient_strength: 'Gradient (niche vs mainstream)',
  dark_matter: 'Dark matter (insider positioning)',
  inertia: 'Inertia (acceleration)',
  medium_sequence: 'Diffusion (cross-stage)',
  confidence_decay: 'Freshness',
};

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
        <Text className="text-textMuted text-center mt-20">Risk not found.</Text>
      </Screen>
    );
  }

  const color = STAGE_COLOR[risk.stage] ?? '#9AA3B0';
  const matColor = MATURITY_COLOR[risk.maturity] ?? '#9AA3B0';
  const maxStage = Math.max(1, ...PIPELINE.map((s) => (risk.diffusion as any)[s.key] as number));

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-4 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#5B6472" />
        <Text className="text-textSecondary text-sm">Risk Intel</Text>
      </TouchableOpacity>

      <Text className="text-textMuted text-[10px] font-bold tracking-widest uppercase">Now TrendIn · Risk Gradient</Text>
      <View className="flex-row items-center gap-2 mt-0.5">
        <ShieldAlert size={22} color={color} />
        <Text className="text-textPrimary text-3xl font-bold flex-1">{risk.display}</Text>
      </View>
      <Text className="text-textMuted text-sm mb-4">{risk.totalSignals} signals · {risk.stage}</Text>

      {/* Dual score */}
      <View className="bg-surface rounded-2xl p-5 border border-border mb-5" style={{ shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, elevation: 2 }}>
        <View className="flex-row justify-around items-start">
          <View className="items-center">
            <View className="px-2.5 py-1 rounded-full mb-2" style={{ backgroundColor: `${color}1A` }}>
              <Text style={{ color }} className="text-[9px] font-bold">{risk.stage}</Text>
            </View>
            <GradientScoreRing score={risk.detection} color="#2D7EEF" size="lg" caption="/100" />
            <Text className="text-textPrimary text-xs font-bold mt-2">DETECTION</Text>
            <Text className="text-textMuted text-[10px]">earliness</Text>
          </View>
          <View className="items-center">
            <View className="px-2.5 py-1 rounded-full mb-2" style={{ backgroundColor: `${color}1A` }}>
              <Text style={{ color }} className="text-[9px] font-bold">{risk.stage}</Text>
            </View>
            <GradientScoreRing score={risk.confidence} color="#00C896" size="lg" caption="/100" />
            <Text className="text-textPrimary text-xs font-bold mt-2">CONFIDENCE</Text>
            <Text className="text-textMuted text-[10px]">precision</Text>
          </View>
        </View>
        {!!risk.action && (
          <View className="rounded-xl px-3 py-2 mt-4 border" style={{ borderColor: `${color}55`, backgroundColor: `${color}10` }}>
            <Text className="text-sm font-bold" style={{ color }}>{risk.action}</Text>
          </View>
        )}
      </View>

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
                  its baseline marks a genuinely emerging risk.
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
          const v = (risk.diffusion as any)[s.key] as number;
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
    </Screen>
  );
}
