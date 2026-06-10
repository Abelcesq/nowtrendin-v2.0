import React, { useState } from 'react';
import { View, Text } from 'react-native';
import { RefreshCw } from 'lucide-react-native';
import { useQueryClient } from '@tanstack/react-query';
import { Button } from '../ui/Button';
import { useAuthStore } from '../../store/auth.store';
import { TierID, canAccess } from '../../constants/tiers';
import { queryApi } from '../../lib/api';

// Enterprise-only "Pull Market Trends" — triggers a fresh risk/positioning
// collection run on the engine (FINRA shorts, OFR macro leverage, WhaleWisdom
// 13F, creator/broadcast coverage, Alpha Vantage news) and deducts 1 token.
// Mirrors PullTrendsButton in visual style + token mechanics for consistency.
//
// IMPLEMENTATION NOTE: the Django backend exposes /api/pull-market/ alongside
// /api/pull-trends/. If that endpoint doesn't exist yet on backend, this
// component degrades to the same /api/pull-trends/ call (which triggers both
// attention AND risk pipelines on the engine), so it remains functional —
// just less precisely scoped. Wire the dedicated endpoint when ready.
export function PullMarketButton() {
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
      // Prefer the dedicated Market endpoint when wired; fall back to
      // the general pullTrends action otherwise.
      const action = (queryApi as any).pullMarket ?? queryApi.pullTrends;
      const d: any = await action();
      if (user) updateUser({ ...user, tokensRemaining: d?.tokensRemaining ?? tokens });
      setMsg(d?.message ?? 'Market data collection started.');
      setTimeout(() => {
        qc.invalidateQueries({ queryKey: ['risk-scores'] });
        qc.invalidateQueries({ queryKey: ['macro-leverage'] });
      }, 4000);
    } catch (err: any) {
      setMsg(err?.data?.detail ?? 'Pull failed. Try again.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <View className="rounded-xl border p-4 mb-4" style={{ borderColor: '#CF2A1B66', backgroundColor: '#CF2A1B0D' }}>
      <View className="flex-row items-center gap-2 mb-1">
        <RefreshCw size={15} color="#CF2A1B" />
        <Text className="text-textPrimary text-sm font-bold">Pull Market Trends</Text>
        <Text className="text-textMuted text-xs ml-auto">{tokens} tokens left</Text>
      </View>
      <Text className="text-textMuted text-xs mb-3">
        Run a fresh collection across all market/positioning sources (FINRA shorts, OFR repo,
        WhaleWisdom 13F, creator + broadcast coverage) — uses 1 query token.
      </Text>
      <Button
        variant="enterprise"
        size="md"
        loading={busy}
        disabled={tokens <= 0}
        icon={<RefreshCw size={16} color="#FFFFFF" />}
        onPress={pull}
      >
        {tokens <= 0 ? 'No tokens remaining' : 'Pull Market Trends · 1 token'}
      </Button>
      {msg && <Text className="text-textMuted text-[11px] mt-2">{msg}</Text>}
    </View>
  );
}
