import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { ChevronDown, ChevronUp } from 'lucide-react-native';
import { useResearch } from '../../hooks/useSignals';

// Lazy "how long has this been discussed?" panel — fetches /scores/{topic}/history on expand.
export function ResearchHistory({ topicKey }: { topicKey: string }) {
  const [open, setOpen] = useState(false);
  const { research, isLoading, isError } = useResearch(open ? topicKey : undefined);

  return (
    <View className="mb-1">
      <TouchableOpacity
        onPress={() => setOpen((o) => !o)}
        className="flex-row items-center justify-between mt-1"
        activeOpacity={0.8}
      >
        <Text className="text-textSecondary text-xs uppercase tracking-wider">
          Research history — how long has this been discussed?
        </Text>
        {open ? <ChevronUp size={16} color="#9A9AA2" /> : <ChevronDown size={16} color="#9A9AA2" />}
      </TouchableOpacity>

      {open && (
        <View className="bg-card rounded-2xl p-4 mt-2">
          {isLoading && <ActivityIndicator color="#2E7D5B" />}
          {isError && <Text className="text-textMuted text-sm">Research data unavailable.</Text>}
          {research && (
            <>
              {!!research.trajectoryLabel && (
                <View className="self-start px-3 py-1 rounded-full mb-2" style={{ backgroundColor: '#2A5B9E1A' }}>
                  <Text className="text-[11px] font-bold" style={{ color: '#2A5B9E' }}>{research.trajectoryLabel}</Text>
                </View>
              )}
              {!!research.summaryShort && (
                <Text className="text-textPrimary text-sm font-semibold mb-1">{research.summaryShort}</Text>
              )}
              {research.yearsDiscussed != null && (
                <Text className="text-textMuted text-xs mb-2">
                  ~{research.yearsDiscussed.toFixed(1)} years in discussion
                  {research.firstKnownDate ? ` · since ${research.firstKnownDate}` : ''}
                </Text>
              )}
              {!!research.gradientImplication && (
                <Text className="text-textSecondary text-[13px] leading-5 mt-1">{research.gradientImplication}</Text>
              )}
              {!!research.milestones?.length && (
                <View className="mt-3 gap-1.5">
                  {research.milestones.slice(0, 6).map((m, i) => (
                    <View key={i} className="flex-row gap-2">
                      <Text className="text-textMuted text-[11px] w-12">{String(m.year ?? '')}</Text>
                      <Text className="text-textSecondary text-[11px] flex-1">{m.label ?? ''}</Text>
                    </View>
                  ))}
                </View>
              )}
            </>
          )}
        </View>
      )}
    </View>
  );
}
