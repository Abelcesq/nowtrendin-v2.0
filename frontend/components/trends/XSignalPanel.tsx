import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { ChevronDown, ChevronUp } from 'lucide-react-native';
import { useXSignal } from '../../hooks/useSignals';

const ROLE_COLOR: Record<string, string> = {
  DETECTION: '#2E7D5B',
  'DETECTION+CONFIRMATION': '#2A5B9E',
  CONFIRMATION: '#A8456A',
  WEAK: '#9A9AA2',
};

const INTEGRITY_COLOR: Record<string, string> = {
  AUTHENTIC: '#2E7D5B',
  MIXED: '#A8456A',
  SUSPICIOUS: '#A8456A',
  MANUFACTURED: '#B11226',
  INSUFFICIENT_DATA: '#9A9AA2',
};

// Lazy X (Twitter) dual-role panel — fetches /signal-x/{topic} on expand.
export function XSignalPanel({ topic }: { topic: string }) {
  const [open, setOpen] = useState(false);
  const { x, isLoading } = useXSignal(topic, open);

  return (
    <View className="mb-1">
      <TouchableOpacity onPress={() => setOpen((o) => !o)} className="flex-row items-center justify-between mt-1" activeOpacity={0.8}>
        <Text className="text-textSecondary text-xs uppercase tracking-wider">X signal — expert vs. viral</Text>
        {open ? <ChevronUp size={16} color="#9A9AA2" /> : <ChevronDown size={16} color="#9A9AA2" />}
      </TouchableOpacity>

      {open && (
        <View className="bg-card rounded-2xl p-4 mt-2">
          {isLoading && <ActivityIndicator color="#2E7D5B" />}
          {!isLoading && !x?.available && (
            <Text className="text-textMuted text-sm leading-5">
              X signal not configured. Add an X_BEARER_TOKEN (Basic tier+) to surface the expert-vs-viral
              gradient for this topic.
            </Text>
          )}
          {!isLoading && x?.available && (
            <>
              <View className="flex-row items-center gap-2 mb-2">
                <View className="px-2.5 py-1 rounded-full" style={{ backgroundColor: `${ROLE_COLOR[x.role ?? 'WEAK'] ?? '#9A9AA2'}1A` }}>
                  <Text className="text-[12px] font-bold" style={{ color: ROLE_COLOR[x.role ?? 'WEAK'] ?? '#9A9AA2' }}>
                    {x.role}
                  </Text>
                </View>
                <Text className="text-textMuted text-xs">{x.stage}</Text>
              </View>
              <View className="flex-row gap-5 mb-2">
                <View>
                  <Text className="text-textMuted text-[12px] font-bold">INTRA-X GRADIENT</Text>
                  <Text className="text-textPrimary text-xl font-black">{Math.round(x.intraGradient ?? 0)}</Text>
                  <Text className="text-textMuted text-[12px]">expert concentration</Text>
                </View>
                <View>
                  <Text className="text-textMuted text-[12px] font-bold">VELOCITY</Text>
                  <Text className="text-textPrimary text-xl font-black">{Math.round(x.velocity ?? 0)}%</Text>
                  <Text className="text-textMuted text-[12px]">acceleration</Text>
                </View>
              </View>
              {!!x.interpretation && <Text className="text-textSecondary text-[14px] leading-5">{x.interpretation}</Text>}

              {/* Signal Integrity — genuine chatter vs bot/astroturf */}
              {x.integrity && (
                <View className="mt-3 pt-3 border-t border-border">
                  <View className="flex-row items-center justify-between mb-1.5">
                    <Text className="text-textMuted text-[12px] font-bold tracking-wider">SIGNAL INTEGRITY</Text>
                    <View className="flex-row items-center gap-1.5">
                      <View className="px-2 py-0.5 rounded-full" style={{ backgroundColor: `${INTEGRITY_COLOR[x.integrity.classification] ?? '#9A9AA2'}1A` }}>
                        <Text className="text-[12px] font-bold" style={{ color: INTEGRITY_COLOR[x.integrity.classification] ?? '#9A9AA2' }}>
                          {x.integrity.classification?.replace('_', ' ')}
                        </Text>
                      </View>
                      <Text className="text-textPrimary text-xs font-black">{Math.round(x.integrity.score)}<Text className="text-textMuted text-[12px]">/100</Text></Text>
                    </View>
                  </View>
                  <Text className="text-textSecondary text-[12px] leading-4">{x.integrity.summary}</Text>
                  {x.integrity.multiplier < 1 && (
                    <Text className="text-[12px] mt-1 font-semibold" style={{ color: INTEGRITY_COLOR[x.integrity.classification] ?? '#9A9AA2' }}>
                      Dark-matter contribution discounted {Math.round((1 - x.integrity.multiplier) * 100)}%.
                    </Text>
                  )}
                  {!!x.integrity.flags?.length && (
                    <View className="mt-2 gap-0.5">
                      {x.integrity.flags.slice(0, 4).map((f, i) => (
                        <Text key={i} className="text-textMuted text-[12px] leading-4">
                          <Text className="font-bold">[{f.source}]</Text> {f.flag}
                        </Text>
                      ))}
                    </View>
                  )}
                </View>
              )}
            </>
          )}
        </View>
      )}
    </View>
  );
}
