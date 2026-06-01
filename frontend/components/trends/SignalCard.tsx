import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { ArrowUpRight } from 'lucide-react-native';
import { useRouter } from 'expo-router';
import { Signal, ageLabel, stageColor } from '../../lib/signals';

export function SignalCard({ signal, onPress }: { signal: Signal; onPress?: () => void }) {
  const router = useRouter();
  const color = stageColor(signal.stage);
  const handlePress = onPress ?? (() => router.push(`/signal/${signal.id}`));
  return (
    <TouchableOpacity
      activeOpacity={0.85}
      onPress={handlePress}
      className="bg-surface rounded-xl p-4 mb-3 border border-border"
      style={{ shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 5, shadowOffset: { width: 0, height: 2 }, elevation: 2 }}
    >
      <View className="flex-row items-center justify-between">
        <View className="flex-1 pr-3">
          <Text className="text-textPrimary font-semibold text-base">{signal.topic}</Text>
          <Text className="text-textMuted text-xs mt-0.5">{signal.category}</Text>
        </View>
        <Text className="font-black text-3xl" style={{ color }}>
          {signal.score}
        </Text>
      </View>
      <View className="flex-row items-center justify-between mt-2">
        <View className="flex-row items-center gap-1">
          <ArrowUpRight size={13} color={color} />
          <Text className="text-xs font-bold" style={{ color }}>
            {signal.stage}
          </Text>
        </View>
        <Text className="text-textMuted text-xs">{ageLabel(signal.createdAt)}</Text>
      </View>
    </TouchableOpacity>
  );
}
