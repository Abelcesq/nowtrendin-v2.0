import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Activity } from 'lucide-react-native';

// Shown when the user first switches to the Positioning ("Other") section.
// Frames it honestly: unusual positioning vs. an item's own baseline — not risk.
export function RiskExplainer({ onDismiss }: { onDismiss: () => void }) {
  return (
    <View className="rounded-2xl p-4 mb-4" style={{ backgroundColor: '#E85A1E12', borderWidth: 1, borderColor: '#E85A1E40' }}>
      <View className="flex-row items-center gap-2 mb-2">
        <Activity size={18} color="#E85A1E" />
        <Text className="font-bold text-base" style={{ color: '#E85A1E' }}>Positioning</Text>
      </View>
      <Text className="text-textSecondary text-sm leading-5 mb-2">
        Flags where insider and institutional positioning is unusually active relative to an item's own
        baseline — detected from public SEC filings, Federal Reserve data, and official APIs. A high score
        means activity is abnormal versus that item's normal level, not that the item is "risky."
      </Text>
      <Text className="text-textMuted text-[11px] leading-4 mb-3">
        Analysis only — not financial, investment, or legal advice, and not a risk rating. All data is public,
        government-published, or accessed via official APIs; results are proprietary to Now TrendIn under your Terms of Service.
      </Text>
      <TouchableOpacity onPress={onDismiss} className="self-start">
        <Text className="text-sm font-semibold" style={{ color: '#E85A1E' }}>Got it</Text>
      </TouchableOpacity>
    </View>
  );
}
