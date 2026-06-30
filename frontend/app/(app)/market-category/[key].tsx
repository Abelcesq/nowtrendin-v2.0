import React, { useMemo, useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, ActivityIndicator, TextInput } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ChevronLeft, Search } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { RiskCard } from '../../../components/trends/RiskCard';
import { PullMarketButton } from '../../../components/trends/PullMarketButton';
import { LockedSignalsBanner } from '../../../components/trends/LockedSignalsBanner';
import { useAuthStore } from '../../../store/auth.store';
import { TierID, isDataAccessible } from '../../../constants/tiers';
import { dataWindowLabel } from '../../../lib/signals';
import { useRiskScores } from '../../../hooks/useSignals';
import { MARKET_CATEGORY_DEFS, getMarketCategory, leverageOf } from '../../../lib/marketCategories';

export default function MarketCategoryPage() {
  const router = useRouter();
  const { key } = useLocalSearchParams<{ key: string }>();
  const cat = getMarketCategory(key || 'all');

  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const { risks, isLoading } = useRiskScores();
  const [query, setQuery] = useState('');

  const accessible = risks.filter((r) => isDataAccessible(tier, Date.now() - r.firstSeenAt));
  const lockedCount = risks.length - accessible.length;

  const list = useMemo(() => {
    let l = accessible.filter(cat.filter);
    if (query) l = l.filter((r) => r.display.toLowerCase().includes(query.toLowerCase()));
    l = [...l].sort(cat.sort ?? ((a, b) => (b.marketGradient?.detection ?? b.detection ?? 0) - (a.marketGradient?.detection ?? a.detection ?? 0)));
    return l;
  }, [accessible, cat, query]);

  const isMS = cat.key === 'marketsignal';
  const isLeverage = cat.key === 'leverage';

  return (
    <Screen scroll>
      <View className="flex-row items-center pt-2 mb-3">
        <TouchableOpacity onPress={() => router.back()} className="flex-row items-center py-2 pr-3">
          <ChevronLeft size={20} color="#3C4663" />
          <Text className="text-textSecondary text-sm font-semibold">Back</Text>
        </TouchableOpacity>
        <View className="flex-1" />
        <Text className="text-textMuted text-[10px]">{dataWindowLabel(tier)}</Text>
      </View>

      {/* Hero */}
      <View className="bg-card rounded-2xl p-5 mb-4" style={{ borderColor: `${cat.color}44` }}>
        {isMS ? (
          <View className="flex-row items-baseline mb-1">
            <Text className="text-3xl font-black" style={{ color: cat.color }}>Market</Text>
            <Text className="text-3xl font-black" style={{ color: cat.altColor }}>Signal</Text>
          </View>
        ) : (
          <Text className="text-3xl font-black uppercase mb-1" style={{ color: cat.color }}>{cat.short}</Text>
        )}
        <Text className="text-textMuted text-[11px] font-bold uppercase tracking-wider mb-3">{cat.range}</Text>
        <View className="flex-row items-baseline gap-3">
          <Text className="text-5xl font-black" style={{ color: cat.color }}>{list.length}</Text>
          <Text className="text-textSecondary text-sm">{list.length === 1 ? 'item' : 'items'} in this view</Text>
        </View>
      </View>

      {/* Definition */}
      <View className="bg-card rounded-2xl p-5 mb-4">
        <Text className="text-textMuted text-[10px] font-bold tracking-widest uppercase mb-2">What is {cat.short}?</Text>
        <Text className="text-textPrimary text-sm leading-5 mb-4">{cat.definition}</Text>
        <Text className="text-textMuted text-[10px] font-bold tracking-widest uppercase mb-2">How an item reaches this view</Text>
        <Text className="text-textSecondary text-[13px] leading-5">{cat.howReached}</Text>
      </View>

      {/* Search within view */}
      <View className="flex-row items-center bg-card rounded-xl px-4 py-3 mb-3">
        <Search size={18} color="#9A9AA2" />
        <TextInput value={query} onChangeText={setQuery} placeholder={`Search within ${cat.short}`}
          placeholderTextColor="#9A9AA2" className="flex-1 ml-3 text-textPrimary text-base" style={{ color: '#16264A' }} />
      </View>

      <PullMarketButton />

      {isLoading ? (
        <ActivityIndicator size="large" color={cat.color} style={{ marginTop: 40 }} />
      ) : (
        <>
          {list.map((r) => (
            <View key={r.key}>
              {/* For Leverage Health, surface the score prominently on each card. */}
              {isLeverage && leverageOf(r) != null && (
                <View className="flex-row items-center justify-end -mb-1 mt-1 pr-1">
                  <Text className="text-[11px] font-bold" style={{ color: '#2E7D5B' }}>
                    Leverage Health {Math.round(leverageOf(r) as number)}/100
                  </Text>
                </View>
              )}
              <RiskCard risk={r} />
            </View>
          ))}
          {list.length === 0 && (
            <View className="bg-card rounded-2xl p-6 items-center mt-2">
              <Text className="text-textMuted text-center text-sm">No market items currently in this view.</Text>
              <Text className="text-textMuted text-center text-[11px] mt-1">Check back after the next collection cycle.</Text>
            </View>
          )}
          {lockedCount > 0 && (
            <View className="mt-1"><LockedSignalsBanner tier={tier} lockedCount={lockedCount} /></View>
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
