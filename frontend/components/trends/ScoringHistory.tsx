import React from 'react';
import { View, Text, ActivityIndicator } from 'react-native';
import { Signal, scoreGap, timeLabel, dayLabel } from '../../lib/signals';
import { useScoreHistory } from '../../hooks/useSignals';

// Per-collection-run scoring events for a topic (live from the engine).
export function ScoringHistory({ signal }: { signal: Signal }) {
  const { rows, isLoading } = useScoreHistory(signal.id);

  // Fall back to the current score until the engine has accumulated runs.
  const data =
    rows.length > 0
      ? rows
      : [{ scoredAt: signal.createdAt, detection: signal.detection, confidence: signal.confidence, overall: signal.overall ?? signal.score, gap: scoreGap(signal) }];

  return (
    <View>
      <View className="flex-row items-center justify-between mb-2 mt-1">
        <Text className="text-textSecondary text-xs uppercase tracking-wider">Actual scoring history</Text>
        <Text className="text-textMuted text-[10px]">live from engine</Text>
      </View>
      <View className="bg-surface rounded-2xl border border-border overflow-hidden">
        <View className="flex-row px-4 py-2 border-b border-border">
          <Text className="text-textMuted text-[9px] font-bold flex-1">SCORED AT</Text>
          <Text className="text-textMuted text-[9px] font-bold w-10 text-center">DET</Text>
          <Text className="text-textMuted text-[9px] font-bold w-10 text-center">CONF</Text>
          <Text className="text-textMuted text-[9px] font-bold w-10 text-center">GAP</Text>
        </View>
        {isLoading ? (
          <ActivityIndicator color="#00C896" style={{ marginVertical: 14 }} />
        ) : (
          data.map((r, i) => (
            <View key={i} className={`flex-row items-center px-4 py-2.5 ${i < data.length - 1 ? 'border-b border-border' : ''}`}>
              <Text className="text-textSecondary text-[11px] flex-1">
                {dayLabel(r.scoredAt)} · {timeLabel(r.scoredAt)}
              </Text>
              <Text style={{ color: '#2D7EEF' }} className="text-sm font-black w-10 text-center">{r.detection}</Text>
              <Text style={{ color: '#00C896' }} className="text-sm font-black w-10 text-center">{r.confidence}</Text>
              <Text className="text-textPrimary text-sm font-black w-10 text-center">{r.gap}</Text>
            </View>
          ))
        )}
      </View>
      <Text className="text-textMuted text-[10px] mt-1.5">
        Each row is a real scoring event from a collection run. Scores change as new signals are collected.
      </Text>
    </View>
  );
}
