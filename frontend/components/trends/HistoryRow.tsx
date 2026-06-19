import React from 'react';
import { View, Text, TouchableOpacity, Alert as RNAlert } from 'react-native';
import { useRouter } from 'expo-router';
import { Flame } from 'lucide-react-native';
import { Signal, stageColor, timeLabel } from '../../lib/signals';

function Metric({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <View className="items-center w-9">
      <Text className="text-textMuted text-[9px] font-bold">{label}</Text>
      <Text style={{ color }} className="text-base font-black">{value}</Text>
    </View>
  );
}

// Compact history list row, matching the web prototype.
export function HistoryRow({ signal }: { signal: Signal }) {
  const router = useRouter();
  const col = stageColor(signal.stage);
  const open = () => {
    RNAlert.alert('Open detail page?', `Go to the detail page for "${signal.topic}"?`, [
      { text: 'No', style: 'cancel' },
      { text: 'Yes', onPress: () => router.push(`/signal/${signal.id}`) },
    ]);
  };
  return (
    <TouchableOpacity
      activeOpacity={0.85}
      onPress={open}
      className="flex-row items-center bg-surface border-b border-border px-3 py-3"
    >
      <View className="w-1 self-stretch rounded-full mr-3" style={{ backgroundColor: col }} />
      <View className="flex-1 pr-2">
        <Text className="text-textPrimary text-base font-bold">{signal.topic}</Text>
        <View className="flex-row items-center gap-2 mt-1">
          <View className="px-2 py-0.5 rounded-full" style={{ backgroundColor: `${col}1A` }}>
            <Text style={{ color: col }} className="text-[9px] font-bold tracking-wide">{signal.stage}</Text>
          </View>
          {signal.isAnomaly && (
            <View className="flex-row items-center gap-1 px-2 py-0.5 rounded-full" style={{ backgroundColor: '#00C8961A' }}>
              <Flame size={9} color="#00C896" />
              <Text className="text-[9px] font-bold" style={{ color: '#009970' }}>ANOMALY</Text>
            </View>
          )}
          <Text className="text-textMuted text-[10px]">{timeLabel(signal.createdAt)}</Text>
        </View>
      </View>
      <View className="flex-row">
        <Metric label="OVR" value={signal.overall ?? signal.score} color="#1A1A2E" />
        <Metric label="DET" value={signal.detection} color="#2D7EEF" />
        <Metric label="CONF" value={signal.confidence} color="#00C896" />
      </View>
    </TouchableOpacity>
  );
}
