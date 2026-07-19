import React from 'react';
import { View, Text, ActivityIndicator } from 'react-native';
import { Signal, scoreGap, timeLabel, dayLabel } from '../../lib/signals';
import { useScoreHistory } from '../../hooks/useSignals';

// Per-collection-run scoring events for a topic (live from the engine).
export function ScoringHistory({ signal }: { signal: Signal }) {
  const { rows, freshness, isLoading } = useScoreHistory(signal.id);

  // Fall back to the current score until the engine has accumulated runs.
  const data =
    rows.length > 0
      ? rows
      : [{ scoredAt: signal.createdAt, detection: signal.detection, confidence: signal.confidence, overall: signal.overall ?? signal.score, gap: scoreGap(signal) }];

  return (
    <View>
      <View className="flex-row items-center justify-between mb-2 mt-1">
        <Text className="text-textSecondary text-xs uppercase tracking-wider">Actual scoring history</Text>
        <Text className="text-textMuted text-[12px]">live from engine</Text>
      </View>
      <View className="bg-card rounded-2xl overflow-hidden">
        <View className="flex-row px-4 py-2 border-b border-border">
          <Text className="text-textMuted text-[12px] font-bold flex-1">SCORED AT</Text>
          <Text className="text-textMuted text-[12px] font-bold w-10 text-center">DET</Text>
          <Text className="text-textMuted text-[12px] font-bold w-10 text-center">CONF</Text>
          <Text className="text-textMuted text-[12px] font-bold w-10 text-center">GAP</Text>
        </View>
        {isLoading ? (
          <ActivityIndicator color="#2E7D5B" style={{ marginVertical: 14 }} />
        ) : (
          data.map((r, i) => (
            <View key={i} className={`flex-row items-center px-4 py-2.5 ${i < data.length - 1 ? 'border-b border-border' : ''}`}>
              <Text className="text-textSecondary text-[12px] flex-1">
                {dayLabel(r.scoredAt)} · {timeLabel(r.scoredAt)}
              </Text>
              <Text style={{ color: '#2A5B9E' }} className="text-sm font-black w-10 text-center">{r.detection}</Text>
              <Text style={{ color: '#2E7D5B' }} className="text-sm font-black w-10 text-center">{r.confidence}</Text>
              <Text className="text-textPrimary text-sm font-black w-10 text-center">{r.gap}</Text>
            </View>
          ))
        )}
      </View>
      <Text className="text-textMuted text-[12px] mt-1.5">
        Each row is a real scoring event from a collection run. Scores change as new signals are collected.
      </Text>
      {/* Input freshness — facts only (board item 5, 2026-07-18): explains post-burst
          reads (a surge whose inputs aged out) without reinterpreting the score. */}
      {freshness && freshness.newestSignalAgeH != null && (
        <View className="bg-card rounded-2xl px-4 py-3 mt-3">
          <Text className="text-textSecondary text-xs uppercase tracking-wider mb-1">Input freshness</Text>
          <Text className="text-textSecondary text-sm font-medium">
            Newest input {freshness.newestSignalAgeH < 1 ? 'under 1h' : `${Math.round(freshness.newestSignalAgeH)}h`} ago
            · {Number(freshness.signalsInWindow72h).toLocaleString()} signals in the 72h scoring window
          </Text>
          {freshness.newestSignalAgeH > 24 && (
            <Text className="text-textMuted text-[12px] mt-1">
              The newest contributing input is over {Math.floor(freshness.newestSignalAgeH)}h old — this topic is
              scored on its post-surge input state.
            </Text>
          )}
        </View>
      )}
    </View>
  );
}
