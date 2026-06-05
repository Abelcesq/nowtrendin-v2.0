import { useState } from 'react';
import { View, Text, TextInput, ActivityIndicator } from 'react-native';
import { Search as SearchIcon } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { TrendCard } from '../../components/trends/TrendCard';
import { useTierFeed } from '../../hooks/useSignals';
import { useAuthStore } from '../../store/auth.store';
import { TIERS, TierID } from '../../constants/tiers';

// Search Current Trends — a FREE, local filter over the trends already in your
// tier's data window. No tokens are spent here. Grading a brand-new topic (which
// generates new data and costs a token) lives in the Grade tab.
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
      <Text className="text-textPrimary text-2xl font-bold pt-4 mb-1">Search Current Trends</Text>
      <Text className="text-textMuted text-xs mb-4">
        Find a topic already scored in your data window — free, no tokens used.
      </Text>

      <View className="flex-row items-center bg-surface rounded-xl px-4 py-3 border border-border mb-4">
        <SearchIcon size={18} color="#9AA3B0" />
        <TextInput
          value={query}
          onChangeText={setQuery}
          placeholder="Search Current Trends"
          placeholderTextColor="#9AA3B0"
          autoFocus
          className="flex-1 ml-3 text-base"
          style={{ color: '#1A1A2E' }}
        />
      </View>

      <Text className="text-textMuted text-[11px] mb-2">
        {q ? `${results.length} result${results.length === 1 ? '' : 's'}` : `${accessible.length} signals in your ${TIERS[tier].name} window`}
      </Text>

      {isLoading ? (
        <ActivityIndicator size="large" color="#00C896" style={{ marginTop: 40 }} />
      ) : results.length === 0 ? (
        <View className="items-center mt-12">
          <SearchIcon size={44} color="#C7CDD6" />
          <Text className="text-textMuted text-sm mt-4 text-center">
            No current trends match "{query}".{'\n'}To grade a brand-new topic, use the Grade tab.
          </Text>
        </View>
      ) : (
        results.map((s) => <TrendCard key={s.id} signal={s} />)
      )}
    </Screen>
  );
}
