import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { ChevronDown, ChevronUp } from 'lucide-react-native';
import { useXSignal } from '../../hooks/useSignals';

const ROLE_COLOR: Record<string, string> = {
  DETECTION: '#00C896',
  'DETECTION+CONFIRMATION': '#2D7EEF',
  CONFIRMATION: '#E85A1E',
  WEAK: '#9AA3B0',
};

// Lazy X (Twitter) dual-role panel — fetches /signal-x/{topic} on expand.
export function XSignalPanel({ topic }: { topic: string }) {
  const [open, setOpen] = useState(false);
  const { x, isLoading } = useXSignal(topic, open);

  return (
    <View className="mb-1">
      <TouchableOpacity onPress={() => setOpen((o) => !o)} className="flex-row items-center justify-between mt-1" activeOpacity={0.8}>
        <Text className="text-textSecondary text-xs uppercase tracking-wider">X signal — expert vs. viral</Text>
        {open ? <ChevronUp size={16} color="#9AA3B0" /> : <ChevronDown size={16} color="#9AA3B0" />}
      </TouchableOpacity>

      {open && (
        <View className="bg-surface rounded-2xl border border-border p-4 mt-2">
          {isLoading && <ActivityIndicator color="#00C896" />}
          {!isLoading && !x?.available && (
            <Text className="text-textMuted text-sm leading-5">
              X signal not configured. Add an X_BEARER_TOKEN (Basic tier+) to surface the expert-vs-viral
              gradient for this topic.
            </Text>
          )}
          {!isLoading && x?.available && (
            <>
              <View className="flex-row items-center gap-2 mb-2">
                <View className="px-2.5 py-1 rounded-full" style={{ backgroundColor: `${ROLE_COLOR[x.role ?? 'WEAK'] ?? '#9AA3B0'}1A` }}>
                  <Text className="text-[10px] font-bold" style={{ color: ROLE_COLOR[x.role ?? 'WEAK'] ?? '#9AA3B0' }}>
                    {x.role}
                  </Text>
                </View>
                <Text className="text-textMuted text-xs">{x.stage}</Text>
              </View>
              <View className="flex-row gap-5 mb-2">
                <View>
                  <Text className="text-textMuted text-[9px] font-bold">INTRA-X GRADIENT</Text>
                  <Text className="text-textPrimary text-xl font-black">{Math.round(x.intraGradient ?? 0)}</Text>
                  <Text className="text-textMuted text-[9px]">expert concentration</Text>
                </View>
                <View>
                  <Text className="text-textMuted text-[9px] font-bold">VELOCITY</Text>
                  <Text className="text-textPrimary text-xl font-black">{Math.round(x.velocity ?? 0)}%</Text>
                  <Text className="text-textMuted text-[9px]">acceleration</Text>
                </View>
              </View>
              {!!x.interpretation && <Text className="text-textSecondary text-[13px] leading-5">{x.interpretation}</Text>}
            </>
          )}
        </View>
      )}
    </View>
  );
}
