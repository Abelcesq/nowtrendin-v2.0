import { useState } from 'react';
import { View, Text, TextInput, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { useQueryClient } from '@tanstack/react-query';
import { Search as SearchIcon, Zap } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { Button } from '../../components/ui/Button';
import { TrendCard } from '../../components/trends/TrendCard';
import { useTierFeed } from '../../hooks/useSignals';
import { useAuthStore } from '../../store/auth.store';
import { TIERS, TierID, canAccess } from '../../constants/tiers';
import { queryApi } from '../../lib/api';
import { mapSignal } from '../../lib/gradientApi';
import { Signal } from '../../lib/signals';

export default function Search() {
  const router = useRouter();
  const qc = useQueryClient();
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const { accessible, isLoading } = useTierFeed(tier);
  const [query, setQuery] = useState('');
  const [querying, setQuerying] = useState(false);
  const [queryMsg, setQueryMsg] = useState<string | null>(null);

  const canQuery = canAccess(tier, 'canQueryNew'); // enterprise only
  const tokens = user?.tokensRemaining ?? 0;

  const q = query.trim().toLowerCase();
  const results = q
    ? accessible.filter((s) => s.topic.toLowerCase().includes(q) || s.category.toLowerCase().includes(q))
    : accessible;

  const runDirectQuery = async () => {
    setQueryMsg(null);
    setQuerying(true);
    try {
      const d: any = await queryApi.run(query.trim());
      if (d?.found && d?.result) {
        // Reflect the new token balance + inject the scored topic into the feed cache.
        if (user) updateUser({ ...user, tokensRemaining: d.tokensRemaining ?? tokens });
        const mapped = mapSignal(d.result);
        qc.setQueryData<Signal[]>(['scores'], (old = []) => [mapped, ...old.filter((s) => s.id !== mapped.id)]);
        router.push(`/signal/${mapped.id}`);
      } else {
        setQueryMsg(d?.detail ?? 'Not enough signal to score this topic yet.');
      }
    } catch (err: any) {
      setQueryMsg(err?.data?.detail ?? 'Query failed. Try again.');
    } finally {
      setQuerying(false);
    }
  };

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

      {/* Enterprise direct query */}
      {canQuery && (
        <View className="rounded-xl border p-4 mb-4" style={{ borderColor: '#D4A01766', backgroundColor: '#D4A0170D' }}>
          <View className="flex-row items-center gap-2 mb-1">
            <Zap size={15} color="#D4A017" />
            <Text className="text-textPrimary text-sm font-bold">Score any topic</Text>
            <Text className="text-textMuted text-xs ml-auto">{tokens} tokens left</Text>
          </View>
          <Text className="text-textMuted text-xs mb-3">
            Not in the list? Run a live Gradient Score for any term — uses 1 query token.
          </Text>
          <Button
            variant="enterprise"
            size="md"
            loading={querying}
            disabled={!query.trim() || tokens <= 0}
            onPress={runDirectQuery}
          >
            {query.trim() ? `Score "${query.trim()}" · 1 token` : 'Type a topic to score'}
          </Button>
          {queryMsg && <Text className="text-error text-xs mt-2">{queryMsg}</Text>}
          {querying && <Text className="text-textMuted text-[11px] mt-2">Collecting signals across platforms… this can take ~30s.</Text>}
        </View>
      )}

      <Text className="text-textMuted text-[11px] mb-2">
        {q ? `${results.length} result${results.length === 1 ? '' : 's'}` : `${accessible.length} signals in your ${TIERS[tier].name} window`}
      </Text>

      {isLoading ? (
        <ActivityIndicator size="large" color="#00C896" style={{ marginTop: 40 }} />
      ) : results.length === 0 ? (
        <View className="items-center mt-12">
          <SearchIcon size={44} color="#C7CDD6" />
          <Text className="text-textMuted text-sm mt-4 text-center">
            No topics match "{query}".{canQuery ? '\nUse "Score any topic" above to query it live.' : ''}
          </Text>
        </View>
      ) : (
        results.map((s) => <TrendCard key={s.id} signal={s} />)
      )}
    </Screen>
  );
}
