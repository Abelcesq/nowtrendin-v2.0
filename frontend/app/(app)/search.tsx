import { useState } from 'react';
import { View, Text, TextInput, ActivityIndicator } from 'react-native';
import { Search as SearchIcon, Zap } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { TrendCard } from '../../components/trends/TrendCard';
import { useTierFeed } from '../../hooks/useSignals';
import { useAuthStore } from '../../store/auth.store';
import { TIERS, TierID, canAccess } from '../../constants/tiers';

export default function Search() {
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const { accessible, isLoading } = useTierFeed(tier);
  const [query, setQuery] = useState('');

  const q = query.trim().toLowerCase();
  const results = q
    ? accessible.filter((s) => s.topic.toLowerCase().includes(q) || s.category.toLowerCase().includes(q))
    : accessible;

  return (
    <Screen scroll>
      <Text className="text-textPrimary text-2xl font-bold pt-4 mb-4">Search Signals</Text>

      <View className="flex-row items-center bg-surface rounded-xl px-4 py-3 border border-border mb-3">
        <SearchIcon size={18} color="#9AA3B0" />
        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder="Search topics..."
          placeholderTextColor="#9AA3B0"
          autoFocus
          className="flex-1 ml-3 text-base"
          style={{ color: '#1A1A2E' }}
        />
      </View>

      {/* Enterprise direct-query affordance */}
      {canAccess(tier, 'canQueryNew') && (
        <View className="rounded-xl border p-3 mb-4 flex-row items-center gap-2" style={{ borderColor: '#D4A01755', backgroundColor: '#D4A0170D' }}>
          <Zap size={14} color="#D4A017" />
          <Text className="text-textSecondary text-xs flex-1">
            Enterprise: direct topic queries (tokenised) coming soon — {user?.tokensRemaining ?? 0} tokens available.
          </Text>
        </View>
      )}

      <Text className="text-textMuted text-[11px] mb-2">
        {q ? `${results.length} result${results.length === 1 ? '' : 's'}` : `${accessible.length} signals in your ${TIERS[tier].name} window`}
      </Text>

      {isLoading ? (
        <ActivityIndicator size="large" color="#00C896" style={{ marginTop: 40 }} />
      ) : results.length === 0 ? (
        <View className="items-center mt-16">
          <SearchIcon size={44} color="#C7CDD6" />
          <Text className="text-textMuted text-sm mt-4">No topics match "{query}".</Text>
        </View>
      ) : (
        results.map((s) => <TrendCard key={s.id} signal={s} />)
      )}
    </Screen>
  );
}
