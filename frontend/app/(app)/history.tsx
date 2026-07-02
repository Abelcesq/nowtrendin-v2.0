import { useState, useCallback } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useFocusEffect } from 'expo-router';
import { Search, ArrowUp, ArrowDown, RotateCcw, X } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { Disclaimer } from '../../components/ui/Disclaimer';
import { HistoryRow } from '../../components/trends/HistoryRow';
import { TrajectoryCard } from '../../components/trends/TrajectoryCard';
import { LockedSignalsBanner } from '../../components/trends/LockedSignalsBanner';
import { useAuthStore } from '../../store/auth.store';
import { TierID } from '../../constants/tiers';
import { dayLabel, Signal } from '../../lib/signals';
import { useTierFeed } from '../../hooks/useSignals';

const HOUR = 60 * 60 * 1000;
const DAY = 24 * HOUR;
const ALL_WINDOWS = [
  { k: '12h', label: '12h', ms: 12 * HOUR },
  { k: '24h', label: '24h', ms: 24 * HOUR },
  { k: '7d', label: '7d', ms: 7 * DAY },
] as const;

export default function History() {
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const { accessible, lockedCount, isLoading, refetch } = useTierFeed(tier);

  // Consumer data freshness is ≥24h (constants/tiers) — they never see 12h-fresh
  // data, so the 12h window is hidden for that tier.
  const WINDOWS = tier === 'consumer' ? ALL_WINDOWS.filter((w) => w.k !== '12h') : ALL_WINDOWS;

  const [win, setWin] = useState<string>('7d');
  const [query, setQuery] = useState('');
  const [desc, setDesc] = useState(true);
  const [selected, setSelected] = useState<Signal | null>(null);

  // Clear the search filter whenever the user navigates to this tab.
  useFocusEffect(useCallback(() => { setQuery(''); }, []));

  const windowMs = WINDOWS.find((w) => w.k === win)?.ms ?? 7 * DAY;
  const winLabel = WINDOWS.find((w) => w.k === win)?.label ?? '7d';
  const now = Date.now();

  const filtered = accessible
    .filter((s) => now - s.createdAt <= windowMs)
    .filter((s) => !query || s.topic.toLowerCase().includes(query.toLowerCase()))
    .sort((a, b) => (desc ? b.createdAt - a.createdAt : a.createdAt - b.createdAt));

  // Group by day (preserving sort order).
  const groups: { day: string; items: typeof filtered }[] = [];
  for (const s of filtered) {
    const day = dayLabel(s.createdAt);
    const last = groups[groups.length - 1];
    if (last && last.day === day) last.items.push(s);
    else groups.push({ day, items: [s] });
  }

  return (
    <Screen scroll padded={false}>
      <View className="px-5 pt-4">
        <Text className="text-textPrimary text-2xl font-bold mb-4">History</Text>

        {/* Window toggle + sort + refresh */}
        <View className="flex-row items-center justify-between mb-3">
          <View className="flex-row items-center gap-2">
            <Text className="text-textMuted text-[12px] font-bold tracking-wider">WINDOW</Text>
            <View className="flex-row gap-1.5">
              {WINDOWS.map((w) => {
                const active = win === w.k;
                return (
                  <TouchableOpacity
                    key={w.k}
                    onPress={() => setWin(w.k)}
                    className="px-3 py-1.5 rounded-lg"
                    style={{ backgroundColor: active ? '#2E7D5B1A' : '#FFFFFF', borderColor: active ? '#2E7D5B' : '#ECECEC' }}
                  >
                    <Text className="text-xs font-bold" style={{ color: active ? '#246B4A' : '#3C4663' }}>{w.label}</Text>
                  </TouchableOpacity>
                );
              })}
            </View>
            <View className="flex-row gap-1 ml-1">
              <TouchableOpacity onPress={() => setDesc(false)} className="w-8 h-8 rounded-lg items-center justify-center" style={{ borderColor: !desc ? '#2E7D5B' : '#ECECEC' }}>
                <ArrowUp size={14} color={!desc ? '#2E7D5B' : '#9A9AA2'} />
              </TouchableOpacity>
              <TouchableOpacity onPress={() => setDesc(true)} className="w-8 h-8 rounded-lg items-center justify-center" style={{ borderColor: desc ? '#2E7D5B' : '#ECECEC' }}>
                <ArrowDown size={14} color={desc ? '#2E7D5B' : '#9A9AA2'} />
              </TouchableOpacity>
            </View>
          </View>
          <TouchableOpacity onPress={() => refetch()} className="w-8 h-8 rounded-lg items-center justify-center">
            <RotateCcw size={14} color="#3C4663" />
          </TouchableOpacity>
        </View>

        {/* Search */}
        <View className="flex-row items-center bg-card rounded-xl px-4 py-3 mb-3">
          <Search size={18} color="#9A9AA2" />
          <TextInput
            value={query}
            onChangeText={setQuery}
            placeholder="Search history..."
            placeholderTextColor="#9A9AA2"
            className="flex-1 ml-3 text-textPrimary text-base"
            style={{ color: '#16264A' }}
          />
          {query ? <TouchableOpacity onPress={() => setQuery('')} className="ml-2"><X size={16} color="#9A9AA2" /></TouchableOpacity> : null}
        </View>

        <Text className="text-textSecondary text-[12px] mb-2">
          <Text className="font-bold text-textPrimary">{filtered.length}</Text> topics scored in the last {winLabel}
        </Text>

        {/* Selected topic's score trajectory (tap a row below to view its graph). */}
        {selected && (
          <View className="mt-1">
            <View className="flex-row items-center justify-between mb-1">
              <Text className="text-textMuted text-[12px] font-bold tracking-wider">SCORE TRAJECTORY</Text>
              <TouchableOpacity onPress={() => setSelected(null)}><Text className="text-textMuted text-[12px]">Hide</Text></TouchableOpacity>
            </View>
            <TrajectoryCard signal={selected} windowMs={windowMs} winLabel={winLabel} />
          </View>
        )}
      </View>

      {isLoading ? (
        <ActivityIndicator size="large" color="#2E7D5B" style={{ marginTop: 40 }} />
      ) : (
        <>
          {groups.map((g) => (
            <View key={g.day}>
              <View className="bg-bg px-5 py-2">
                <Text className="text-textMuted text-[12px] font-bold tracking-wider">
                  {g.day} · {g.items.length} topics
                </Text>
              </View>
              {g.items.map((s) => (
                <HistoryRow key={s.id} signal={s} onPress={setSelected} selected={selected?.id === s.id} />
              ))}
            </View>
          ))}

          {filtered.length === 0 && (
            <Text className="text-textMuted text-center mt-10">No history in this window.</Text>
          )}

          <View className="px-5 mt-3">
            <LockedSignalsBanner tier={tier} lockedCount={lockedCount} />
          </View>
        </>
      )}

      <Disclaimer />
    </Screen>
  );
}
