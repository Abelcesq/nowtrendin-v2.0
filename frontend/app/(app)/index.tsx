import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { Bell, Zap, Briefcase, Building2, Search } from 'lucide-react-native';
import { Logo, Wordmark } from '../../components/ui/Logo';
import { Screen } from '../../components/ui/Screen';
import { TrendCard } from '../../components/trends/TrendCard';
import { RiskCard } from '../../components/trends/RiskCard';
import { RiskExplainer } from '../../components/trends/RiskExplainer';
import { ScoreLegend } from '../../components/trends/ScoreLegend';
import { LockedSignalsBanner } from '../../components/trends/LockedSignalsBanner';
import { PullTrendsButton } from '../../components/trends/PullTrendsButton';
import { GradeTool } from '../../components/trends/GradeTool';
import { useAuthStore } from '../../store/auth.store';
import { TIERS, TierID, isDataAccessible } from '../../constants/tiers';
import { dataWindowLabel, scoreGap } from '../../lib/signals';
import { useTierFeed, useRiskScores } from '../../hooks/useSignals';

const TIER_ICONS: Record<TierID, any> = { consumer: Zap, business: Briefcase, enterprise: Building2 };

const FILTERS = [
  { k: 'all', label: 'All Signals' },
  { k: 'breakout', label: 'Breakout ≥85' },
  { k: 'strong', label: 'Strong ≥70' },
  { k: 'emerging', label: 'Emerging' },
  { k: 'lowrisk', label: 'Low Risk' },
] as const;

const STATS = [
  { k: 'breakout', label: 'BREAKOUT', color: '#00C896' },
  { k: 'strong', label: 'STRONG', color: '#2D7EEF' },
  { k: 'emerging', label: 'EMERGING', color: '#D4A017' },
  { k: 'anomalies', label: 'ANOMALIES', color: '#8B5CF6' },
] as const;

export default function Dashboard() {
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const cfg = TIERS[tier];
  const Icon = TIER_ICONS[tier];

  const { accessible, lockedCount, isLoading, isSample } = useTierFeed(tier);
  const { risks, isLoading: riskLoading } = useRiskScores();
  const [mode, setMode] = useState<'attention' | 'risk' | 'grade'>('attention');
  const [riskExplainerDismissed, setRiskExplainerDismissed] = useState(false);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<string>('all');

  // Risk obeys the same data-aging waterfall as Attention.
  const accessibleRisks = risks.filter((r) => isDataAccessible(tier, Date.now() - r.firstSeenAt));
  const lockedRiskCount = risks.length - accessibleRisks.length;

  const firstName = (user?.name ?? 'there').split(' ')[0];
  const hour = new Date().getHours();
  const greeting =
    hour >= 1 && hour < 11 ? 'Good morning'      // 1:00am – 10:59am
      : hour >= 11 && hour < 15 ? 'Good day'      // 11:00am – 2:59pm
      : hour >= 15 && hour < 18 ? 'Good afternoon' // 3:00pm – 5:59pm
      : hour >= 18 && hour < 21 ? 'Good evening'   // 6:00pm – 8:59pm
      : 'Good night';                              // 9:00pm – 12:59am

  const counts = {
    breakout: accessible.filter((s) => s.stage === 'BREAKOUT' || s.score >= 85).length,
    strong: accessible.filter((s) => s.stage === 'STRONG').length,
    emerging: accessible.filter((s) => s.stage === 'EMERGING').length,
    anomalies: accessible.filter((s) => s.isAnomaly).length,
  } as Record<string, number>;

  const filtered = accessible.filter((s) => {
    if (query && !s.topic.toLowerCase().includes(query.toLowerCase())) return false;
    if (filter === 'breakout') return s.score >= 85;
    if (filter === 'strong') return s.score >= 70;
    if (filter === 'emerging') return s.score >= 55 && s.score < 70;
    if (filter === 'lowrisk') return scoreGap(s) <= 6;
    return true;
  });

  return (
    <Screen scroll>
      {/* Brand header */}
      <View className="flex-row items-center justify-between pt-4 mb-1">
        <View className="flex-row items-center gap-2">
          <Logo size={34} />
          <View>
            <Wordmark size="text-xl" />
            <Text className="text-textMuted text-[10px] tracking-widest uppercase">Attention Intelligence</Text>
          </View>
        </View>
        <View className="w-9 h-9 rounded-full bg-surface items-center justify-center border border-border">
          <Bell size={18} color="#5B6472" />
        </View>
      </View>

      {/* Greeting */}
      <View className="bg-surface rounded-2xl p-5 border border-border my-4">
        <Text className="text-textPrimary text-2xl font-bold">{greeting}, {firstName}!</Text>
        <Text className="text-textSecondary text-sm mt-1 mb-3">Let me show you what's trending.</Text>
        <View className="flex-row items-center gap-2">
          <View className="flex-row items-center gap-1.5 px-3 py-1.5 rounded-full" style={{ backgroundColor: `${cfg.colour}20` }}>
            <Icon size={14} color={cfg.colour} />
            <Text style={{ color: cfg.colour }} className="text-xs font-bold uppercase">{cfg.name} Plan</Text>
          </View>
          <Text className="text-textMuted text-xs">{dataWindowLabel(tier)}</Text>
        </View>
      </View>

      {/* Trends | Other | Grade toggle */}
      <View className="flex-row bg-surface rounded-xl border border-border p-1 mb-4">
        {([
          { k: 'attention', label: 'Trends', color: '#00C896' },
          { k: 'risk', label: 'Other', color: '#CF2A1B' },
          { k: 'grade', label: 'Grade', color: '#D4A017' },
        ] as const).map((t) => {
          const on = mode === t.k;
          return (
            <TouchableOpacity
              key={t.k}
              onPress={() => setMode(t.k)}
              className="flex-1 rounded-lg py-2 items-center"
              style={{ backgroundColor: on ? t.color : 'transparent' }}
            >
              <Text className="text-xs font-bold" style={{ color: on ? '#FFFFFF' : '#5B6472' }}>
                {t.label}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {mode === 'attention' && (
        <>
      {/* Search bar */}
      <View className="flex-row items-center bg-surface rounded-xl px-4 py-3 border border-border mb-3">
        <Search size={18} color="#9AA3B0" />
        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder="Search Current Trends"
          placeholderTextColor="#9AA3B0"
          className="flex-1 ml-3 text-textPrimary text-base"
          style={{ color: '#1A1A2E' }}
        />
      </View>

      {/* Enterprise: token-metered Pull Trends (renders only for enterprise tier) */}
      <PullTrendsButton />

      {/* Filter chips — fixed-height row so the pills can't stretch */}
      <View style={{ height: 40 }} className="mb-4">
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8, alignItems: 'center' }}>
          {FILTERS.map((f) => {
            const active = filter === f.k;
            return (
              <TouchableOpacity
                key={f.k}
                onPress={() => setFilter(f.k)}
                className="px-4 rounded-full items-center justify-center"
                style={{
                  height: 34,
                  borderWidth: 1,
                  backgroundColor: active ? '#00C896' : '#FFFFFF',
                  borderColor: active ? '#00C896' : '#E4E7EC',
                }}
              >
                <Text className="text-xs font-semibold" style={{ color: active ? '#FFFFFF' : '#5B6472' }}>
                  {f.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      </View>

      {/* Trends header */}
      <View className="flex-row items-center mb-3">
        <View className="flex-row items-center gap-2">
          <View className="w-1 h-5 rounded-full bg-brandMaroon" />
          <Text className="text-textPrimary text-xl font-black">Trends</Text>
          <View className="px-2 py-0.5 rounded-full bg-surface border border-border">
            <Text className="text-textMuted text-[11px] font-bold">{filtered.length}</Text>
          </View>
        </View>
        {/* The token-metered "Pull Trends" action lives in <PullTrendsButton /> above —
            the yellow CTA that clearly states it costs 1 token. A second unlabeled
            refetch button here was redundant and confusing, so it was removed. */}
      </View>

      {/* Stat row */}
      <View className="flex-row gap-2 mb-4">
        {STATS.map((st) => (
          <View key={st.k} className="flex-1 bg-surface rounded-xl border border-border py-3 items-center">
            <Text className="text-2xl font-black" style={{ color: st.color }}>{counts[st.k] ?? 0}</Text>
            <Text className="text-textMuted text-[9px] font-bold tracking-wider mt-0.5">{st.label}</Text>
          </View>
        ))}
      </View>

      {/* Legend */}
      <ScoreLegend />

      {isSample && (
        <View className="rounded-lg px-3 py-2 mb-4 border border-border bg-surface">
          <Text className="text-textMuted text-[11px]">Showing sample data — live engine unreachable.</Text>
        </View>
      )}

      {/* Trend list */}
      {isLoading ? (
        <ActivityIndicator size="large" color="#00C896" style={{ marginTop: 40 }} />
      ) : (
        <>
          {filtered.map((s) => (
            <TrendCard key={s.id} signal={s} />
          ))}
          {filtered.length === 0 && (
            <Text className="text-textMuted text-center mt-8 mb-4">No trends match your search.</Text>
          )}
          <View className="mt-1">
            <LockedSignalsBanner tier={tier} lockedCount={lockedCount} />
          </View>
        </>
      )}
        </>
      )}

      {mode === 'grade' && <GradeTool />}

      {mode === 'risk' && (
        <>
          {!riskExplainerDismissed && <RiskExplainer onDismiss={() => setRiskExplainerDismissed(true)} />}

          <View className="flex-row items-center gap-2 mb-2">
            <View className="w-1 h-5 rounded-full" style={{ backgroundColor: '#E85A1E' }} />
            <Text className="text-textPrimary text-xl font-black">Positioning</Text>
            <View className="px-2 py-0.5 rounded-full bg-surface border border-border">
              <Text className="text-textMuted text-[11px] font-bold">{accessibleRisks.length}</Text>
            </View>
            <Text className="text-textMuted text-[10px] ml-auto">{dataWindowLabel(tier)}</Text>
          </View>
          <Text className="text-textMuted text-[11px] mb-3">
            Items where insider/institutional positioning is unusually active vs their own baseline. Analysis only — not advice or a risk rating.
          </Text>
          {riskLoading ? (
            <ActivityIndicator size="large" color="#E85A1E" style={{ marginTop: 40 }} />
          ) : accessibleRisks.length === 0 ? (
            <Text className="text-textMuted text-center mt-8">
              {lockedRiskCount > 0 ? 'Newer risk signals are still aging into your tier.' : 'No risk signals yet.'}
            </Text>
          ) : (
            accessibleRisks.map((r) => <RiskCard key={r.key} risk={r} />)
          )}
          {lockedRiskCount > 0 && accessibleRisks.length > 0 && (
            <View className="mt-1">
              <LockedSignalsBanner tier={tier} lockedCount={lockedRiskCount} />
            </View>
          )}
        </>
      )}

      {/* Global disclaimer — we provide analysis, not advice. */}
      <Text className="text-textMuted text-[10px] text-center mt-6 mb-2 px-4 leading-4">
        Now TrendIn provides signal analysis for informational purposes only — not financial,
        investment, or legal advice. All decisions are your own.
      </Text>
    </Screen>
  );
}
