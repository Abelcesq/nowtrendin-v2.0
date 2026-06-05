import React, { useState } from 'react';
import { View, Text } from 'react-native';
import { RefreshCw } from 'lucide-react-native';
import { useQueryClient } from '@tanstack/react-query';
import { Button } from '../ui/Button';
import { useAuthStore } from '../../store/auth.store';
import { TierID, canAccess } from '../../constants/tiers';
import { queryApi } from '../../lib/api';

// Enterprise-only "Pull Trends" — triggers a fresh collect+score run on the
// engine and deducts 1 token (same per-search token model as a direct query).
// Shared across iOS / Android / Web via React Native Web — identical behaviour.
export function PullTrendsButton() {
  const qc = useQueryClient();
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  if (!canAccess(tier, 'canQueryNew')) return null; // Enterprise only

  const tokens = user?.tokensRemaining ?? 0;

  const pull = async () => {
    setMsg(null);
    setBusy(true);
    try {
      const d: any = await queryApi.pullTrends();
      if (user) updateUser({ ...user, tokensRemaining: d?.tokensRemaining ?? tokens });
      setMsg(d?.message ?? 'Trend collection started.');
      // Give the engine a moment, then refresh the feeds.
      setTimeout(() => {
        qc.invalidateQueries({ queryKey: ['scores'] });
        qc.invalidateQueries({ queryKey: ['risk-scores'] });
      }, 4000);
    } catch (err: any) {
      setMsg(err?.data?.detail ?? 'Pull failed. Try again.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <View className="rounded-xl border p-4 mb-4" style={{ borderColor: '#D4A01766', backgroundColor: '#D4A0170D' }}>
      <View className="flex-row items-center gap-2 mb-1">
        <RefreshCw size={15} color="#D4A017" />
        <Text className="text-textPrimary text-sm font-bold">Pull Trends</Text>
        <Text className="text-textMuted text-xs ml-auto">{tokens} tokens left</Text>
      </View>
      <Text className="text-textMuted text-xs mb-3">
        Run a fresh collection across all sources for the latest Gradient Scores — uses 1 query token.
      </Text>
      <Button
        variant="enterprise"
        size="md"
        loading={busy}
        disabled={tokens <= 0}
        icon={<RefreshCw size={16} color="#FFFFFF" />}
        onPress={pull}
      >
        {tokens <= 0 ? 'No tokens remaining' : 'Pull Trends · 1 token'}
      </Button>
      {msg && <Text className="text-textMuted text-[11px] mt-2">{msg}</Text>}
    </View>
  );
}
