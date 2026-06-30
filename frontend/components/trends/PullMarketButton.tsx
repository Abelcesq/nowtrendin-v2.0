import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { Sparkles } from 'lucide-react-native';
import { useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '../../store/auth.store';
import { TierID, canAccess } from '../../constants/tiers';
import { queryApi } from '../../lib/api';

// Enterprise-only "Pull Market Trends" — fresh risk/positioning collection run,
// deducts 1 token. Compact pill for the persistent action bar (mirrors
// PullTrendsButton). Falls back to pullTrends if the dedicated endpoint is absent.
export function PullMarketButton() {
  const qc = useQueryClient();
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  if (!canAccess(tier, 'canQueryNew')) return null; // Enterprise only

  const tokens = user?.tokensRemaining ?? 0;
  const disabled = busy || tokens <= 0;

  const pull = async () => {
    setMsg(null);
    setBusy(true);
    try {
      const action = (queryApi as any).pullMarket ?? queryApi.pullTrends;
      const d: any = await action();
      if (user) updateUser({ ...user, tokensRemaining: d?.tokensRemaining ?? tokens });
      setMsg(d?.message ?? 'Market collection started.');
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
    <View>
      {!!msg && (
        <Text style={{ color: '#16264A', fontSize: 11, fontWeight: '600', textAlign: 'center', marginBottom: 8 }}>{msg}</Text>
      )}
      <TouchableOpacity
        onPress={pull}
        disabled={disabled}
        activeOpacity={0.9}
        className="flex-row items-center justify-center"
        style={{
          backgroundColor: '#16264A', borderRadius: 980, paddingVertical: 15, paddingHorizontal: 22,
          shadowColor: '#0C1B3A', shadowOpacity: 0.32, shadowRadius: 18, shadowOffset: { width: 0, height: 10 },
          elevation: 9, opacity: tokens <= 0 ? 0.55 : 1,
        }}
      >
        {busy ? <ActivityIndicator color="#FFFFFF" size="small" /> : <Sparkles size={16} color="#F0758A" />}
        <Text style={{ color: '#FFFFFF', fontSize: 12.5, fontWeight: '800', letterSpacing: 1.2, marginLeft: 8 }}>
          {tokens <= 0 ? 'NO TOKENS LEFT' : 'PULL MARKET DATA'}
        </Text>
        {tokens > 0 && (
          <Text style={{ color: '#F0758A', fontSize: 11, fontWeight: '800', letterSpacing: 0.5, marginLeft: 8 }}>· 1 TOKEN</Text>
        )}
      </TouchableOpacity>
      <Text style={{ color: '#9A9AA2', fontSize: 9.5, fontWeight: '700', letterSpacing: 1, textAlign: 'center', marginTop: 7 }}>
        {tokens.toLocaleString()} TOKENS REMAINING
      </Text>
    </View>
  );
}
