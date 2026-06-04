import { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { Bell, Zap, Briefcase, Building2, Search, RotateCcw } from 'lucide-react-native';
import { Logo, Wordmark } from '../../components/ui/Logo';
import { Screen } from '../../components/ui/Screen';
import { TrendCard } from '../../components/trends/TrendCard';
import { ScoreLegend } from '../../components/trends/ScoreLegend';
import { LockedSignalsBanner } from '../../components/trends/LockedSignalsBanner';
import { useAuthStore } from '../../store/auth.store';
import { TIERS, TierID } from '../../constants/tiers';
import { dataWindowLabel, scoreGap } from '../../lib/signals';
import { useTierFeed } from '../../hooks/useSignals';

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

  const { accessible, lockedCount, isLoading, isSample, refetch } = useTierFeed(tier);
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<string>('all');

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

      {/* Search bar */}
      <View className="flex-row items-center bg-surface rounded-xl px-4 py-3 border border-border mb-3">
        <Search size={18} color="#9AA3B0" />
        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder="Search trends..."
          placeholderTextColor="#9AA3B0"
          className="flex-1 ml-3 text-textPrimary text-base"
          style={{ color: '#1A1A2E' }}
        />
      </View>

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
      <View className="flex-row items-center justify-between mb-3">
        <View className="flex-row items-center gap-2">
          <View className="w-1 h-5 rounded-full bg-brandMaroon" />
          <Text className="text-textPrimary text-xl font-black">Trends</Text>
          <View className="px-2 py-0.5 rounded-full bg-surface border border-border">
            <Text className="text-textMuted text-[11px] font-bold">{filtered.length}</Text>
          </View>
        </View>
        {tier !== 'consumer' && (
          <TouchableOpacity
            onPress={() => refetch()}
            className="flex-row items-center gap-1.5 px-3 py-1.5 rounded-full border"
            style={{ borderColor: '#E8551C' }}
          >
            <RotateCcw size={13} color="#E8551C" />
            <Text className="text-xs font-bold" style={{ color: '#E8551C' }}>Pull Trends</Text>
          </TouchableOpacity>
        )}
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
    </Screen>
  );
}
