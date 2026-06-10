import React from 'react';
import { View, Text } from 'react-native';
import { GitMerge, TrendingUp, TrendingDown, Minus } from 'lucide-react-native';
import { useConvergence } from '../../hooks/useSignals';

// Signal Convergence — downstream directional validation surfaced on the
// signal-detail Now TrendIn card. Shows whether the Gradient Score's direction
// is backed by (1) raw volume and (2) niche concentration. Independent of the
// N demand metric, so it's a genuine cross-check, not a circular one.

const VERDICT_COLOR: Record<string, string> = {
  CONFIRMED: '#00C896',
  MIXED: '#D4A017',
  CONFLICTING: '#DC2626',
  INCONCLUSIVE: '#9AA3B0',
  STABLE: '#9AA3B0',
  UNKNOWN: '#9AA3B0',
};

function DirIcon({ dir }: { dir?: string }) {
  if (dir === 'RISING') return <TrendingUp size={14} color="#00C896" />;
  if (dir === 'FALLING') return <TrendingDown size={14} color="#DC2626" />;
  return <Minus size={14} color="#9AA3B0" />;
}

export function ConvergenceBadge({ topicKey }: { topicKey: string }) {
  const { convergence: c, isLoading } = useConvergence(topicKey);

  if (isLoading || !c) return null;

  if (c.status === 'warming_up') {
    return (
      <View className="rounded-xl px-3 py-2.5 mt-3 border border-border bg-bg">
        <View className="flex-row items-center gap-1.5 mb-0.5">
          <GitMerge size={13} color="#9AA3B0" />
          <Text className="text-textMuted text-[11px] font-bold tracking-wide uppercase">
            Signal Convergence
          </Text>
        </View>
        <Text className="text-textMuted text-[11px] leading-4">
          Warming up — needs {c.needed ?? 3} daily snapshots to validate direction
          ({c.snapshots ?? 0} so far). The reading appears once history accumulates.
        </Text>
      </View>
    );
  }

  if (c.status !== 'ok') return null;

  const col = VERDICT_COLOR[c.convergence ?? 'INCONCLUSIVE'] ?? '#9AA3B0';

  return (
    <View className="rounded-xl px-3 py-3 mt-3 border" style={{ borderColor: `${col}55`, backgroundColor: `${col}0C` }}>
      {/* Header: overall convergence verdict + direction */}
      <View className="flex-row items-center gap-2 mb-2">
        <GitMerge size={14} color={col} />
        <Text className="text-[11px] font-bold tracking-wide uppercase" style={{ color: col }}>
          Signal Convergence
        </Text>
        <View className="flex-row items-center gap-1 ml-auto">
          <DirIcon dir={c.direction} />
          <Text className="text-textSecondary text-[11px] font-semibold">{c.direction}</Text>
        </View>
      </View>

      <Text className="text-base font-black mb-1.5" style={{ color: col }}>
        {c.convergence}
      </Text>

      {/* Validation 1: vs the Gradient Score */}
      {!!c.vsGradient && (
        <View className="mb-2">
          <View className="flex-row items-center gap-1.5 mb-0.5">
            <Text className="text-textMuted text-[10px] font-bold uppercase tracking-wide">
              vs Gradient Score
            </Text>
            <Text className="text-[10px] font-bold" style={{ color: VERDICT_COLOR[c.vsGradient.validation] ?? '#9AA3B0' }}>
              {c.vsGradient.validation}
            </Text>
          </View>
          <Text className="text-textSecondary text-[12px] leading-4">{c.vsGradient.text}</Text>
        </View>
      )}

      {/* Validation 2: vs Niche analysis */}
      {!!c.vsNiche && (
        <View>
          <View className="flex-row items-center gap-1.5 mb-0.5">
            <Text className="text-textMuted text-[10px] font-bold uppercase tracking-wide">
              vs Niche Analysis
            </Text>
            <Text className="text-[10px] font-bold" style={{ color: VERDICT_COLOR[c.vsNiche.validation] ?? '#9AA3B0' }}>
              {c.vsNiche.validation}
            </Text>
          </View>
          <Text className="text-textSecondary text-[12px] leading-4">{c.vsNiche.text}</Text>
        </View>
      )}

      <Text className="text-textMuted text-[10px] leading-3 mt-2">
        Downstream validation — reads the score + raw data, never feeds it. Independent of N demand.
      </Text>
    </View>
  );
}
