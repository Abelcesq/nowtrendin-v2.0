import React from 'react';
import { View, Text } from 'react-native';
import { Signal, scoreGap, timeLabel, dayLabel } from '../../lib/signals';

// Latest scoring event for this topic, in the web prototype's table style.
// (One row from the current score; expands as the engine accumulates runs.)
export function ScoringHistory({ signal }: { signal: Signal }) {
  const gap = scoreGap(signal);
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
        <View className="flex-row items-center px-4 py-3">
          <Text className="text-textSecondary text-[11px] flex-1">
            {dayLabel(signal.createdAt)} · {timeLabel(signal.createdAt)}
          </Text>
          <Text style={{ color: '#2D7EEF' }} className="text-sm font-black w-10 text-center">{signal.detection}</Text>
          <Text style={{ color: '#00C896' }} className="text-sm font-black w-10 text-center">{signal.confidence}</Text>
          <Text className="text-textPrimary text-sm font-black w-10 text-center">{gap}</Text>
        </View>
      </View>
      <Text className="text-textMuted text-[10px] mt-1.5">
        Each row is a real scoring event from a collection run. Scores change as new signals are collected.
      </Text>
    </View>
  );
}
