import React, { useMemo, useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ChevronLeft, Search } from 'lucide-react-native';
import { TextInput } from 'react-native';
import { Screen } from '../../../components/ui/Screen';
import { TrendCard } from '../../../components/trends/TrendCard';
import { PullTrendsButton } from '../../../components/trends/PullTrendsButton';
import { LockedSignalsBanner } from '../../../components/trends/LockedSignalsBanner';
import { useAuthStore } from '../../../store/auth.store';
import { TIERS, TierID } from '../../../constants/tiers';
import { dataWindowLabel } from '../../../lib/signals';
import { useTierFeed } from '../../../hooks/useSignals';
import { CATEGORY_DEFS, getCategory } from '../../../lib/signals';

export default function CategoryPage() {
  const router = useRouter();
  const { stage } = useLocalSearchParams<{ stage: string }>();
  const cat = getCategory(stage || 'all');

  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const { accessible, lockedCount, isLoading, isSample } = useTierFeed(tier);
  const [query, setQuery] = useState('');

  // Apply the category filter + the search query, then sort.
  const list = useMemo(() => {
    let l = accessible.filter(cat.filter);
    if (query) l = l.filter((s) => s.topic.toLowerCase().includes(query.toLowerCase()));
    // Default sort: by Detection Score descending. "Now TrendIn" view is
    // explicitly this — but every focused page benefits from earliness-first.
    l = [...l].sort((a, b) => b.detection - a.detection);
    return l;
  }, [accessible, cat, query]);

  const isNowTrendin = cat.key === 'nowtrendin';

  return (
    <Screen scroll>
      {/* Back row */}
      <View className="flex-row items-center pt-2 mb-3">
        <TouchableOpacity onPress={() => router.back()} className="flex-row items-center py-2 pr-3">
          <ChevronLeft size={20} color="#5B6472" />
          <Text className="text-textSecondary text-sm font-semibold">Back</Text>
        </TouchableOpacity>
        <View className="flex-1" />
        <Text className="text-textMuted text-[10px]">{dataWindowLabel(tier)}</Text>
      </View>

      {/* Category hero — title in brand colors (or category color) */}
      <View className="bg-surface rounded-2xl border border-border p-5 mb-4"
            style={{ borderColor: `${cat.color}44` }}>
        {isNowTrendin ? (
          // Two-color wordmark: "Now" orange + "TrendIn" maroon
          <View className="flex-row items-baseline mb-1">
            <Text className="text-3xl font-black" style={{ color: cat.color }}>Now</Text>
            <Text className="text-3xl font-black" style={{ color: cat.altColor }}>TrendIn</Text>
          </View>
        ) : (
          <Text className="text-3xl font-black uppercase mb-1" style={{ color: cat.color }}>
            {cat.short}
          </Text>
        )}
        <Text className="text-textMuted text-[11px] font-bold uppercase tracking-wider mb-3">
          {cat.range}
        </Text>
        <View className="flex-row items-baseline gap-3">
          <Text className="text-5xl font-black" style={{ color: cat.color }}>{list.length}</Text>
          <Text className="text-textSecondary text-sm">
            {list.length === 1 ? 'signal' : 'signals'} in this view
          </Text>
        </View>
      </View>

      {/* Definition + how-reached card */}
      <View className="bg-surface rounded-2xl border border-border p-5 mb-4">
        <Text className="text-textMuted text-[10px] font-bold tracking-widest uppercase mb-2">
          What is {cat.short}?
        </Text>
        <Text className="text-textPrimary text-sm leading-5 mb-4">{cat.definition}</Text>
        <Text className="text-textMuted text-[10px] font-bold tracking-widest uppercase mb-2">
          How a trend reaches this view
        </Text>
        <Text className="text-textSecondary text-[13px] leading-5">{cat.howReached}</Text>
      </View>

      {/* Signal Convergence explainer — only on the Now TrendIn page. Explains
          the downstream validation metric users will see on each signal's detail. */}
      {isNowTrendin && (
        <View className="bg-surface rounded-2xl border p-5 mb-4" style={{ borderColor: '#EE6A2A44' }}>
          <Text className="text-[10px] font-bold tracking-widest uppercase mb-2" style={{ color: '#B5341B' }}>
            Signal Convergence — how we validate direction
          </Text>
          <Text className="text-textPrimary text-sm leading-5 mb-3">
            Every signal here carries a Convergence check: a downstream test of whether the
            Gradient Score's direction is actually backed by the underlying data. It reads the
            score and the raw signals — it never feeds or alters the score — so it's an
            independent cross-check, not a circular one.
          </Text>
          <View className="rounded-xl p-3 mb-2 border" style={{ borderColor: '#00C89633', backgroundColor: '#00C8960A' }}>
            <Text className="text-[11px] font-bold mb-0.5" style={{ color: '#009970' }}>vs Gradient Score</Text>
            <Text className="text-textSecondary text-[12px] leading-4">
              Is the score's rise (or fall) confirmed by raw signal volume moving the same way?
              A rising score with falling volume is flagged CONFLICTING — a move the data doesn't support.
            </Text>
          </View>
          <View className="rounded-xl p-3 border" style={{ borderColor: '#2D7EEF33', backgroundColor: '#2D7EEF0A' }}>
            <Text className="text-[11px] font-bold mb-0.5" style={{ color: '#2D7EEF' }}>vs Niche Analysis</Text>
            <Text className="text-textSecondary text-[12px] leading-4">
              Is the direction consistent with where the topic sits in the diffusion curve? Rising while
              still niche-concentrated = genuine early spread; rising once already mainstream = a late move.
            </Text>
          </View>
          <Text className="text-textMuted text-[10px] leading-4 mt-2">
            Verdicts: CONFIRMED (data agrees) · MIXED (partial) · CONFLICTING (data disagrees). Open any
            signal to see its live Convergence reading.
          </Text>
        </View>
      )}

      {/* Search bar (lets you narrow within the focused view) */}
      <View className="flex-row items-center bg-surface rounded-xl px-4 py-3 border border-border mb-3">
        <Search size={18} color="#9AA3B0" />
        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder={`Search within ${cat.short}`}
          placeholderTextColor="#9AA3B0"
          className="flex-1 ml-3 text-textPrimary text-base"
          style={{ color: '#1A1A2E' }}
        />
      </View>

      {/* Enterprise: Pull Trends button (renders only on enterprise tier) */}
      <PullTrendsButton />

      {/* Trend list */}
      {isSample && (
        <View className="rounded-lg px-3 py-2 mb-3 border border-border bg-surface">
          <Text className="text-textMuted text-[11px]">Showing sample data — live engine unreachable.</Text>
        </View>
      )}
      {isLoading ? (
        <ActivityIndicator size="large" color={cat.color} style={{ marginTop: 40 }} />
      ) : (
        <>
          {list.map((s) => (
            <TrendCard key={s.id} signal={s} />
          ))}
          {list.length === 0 && (
            <View className="bg-surface rounded-2xl border border-border p-6 items-center mt-2">
              <Text className="text-textMuted text-center text-sm">
                No trends currently in this view.
              </Text>
              <Text className="text-textMuted text-center text-[11px] mt-1">
                Check back after the next collection cycle.
              </Text>
            </View>
          )}
          {lockedCount > 0 && (
            <View className="mt-1">
              <LockedSignalsBanner tier={tier} lockedCount={lockedCount} />
            </View>
          )}
        </>
      )}

      <Text className="text-textMuted text-[10px] text-center mt-6 mb-2 px-4 leading-4">
        Now TrendIn provides signal analysis for informational purposes only — not financial,
        investment, or legal advice. All decisions are your own.
      </Text>
    </Screen>
  );
}
