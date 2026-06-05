import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { ShieldAlert } from 'lucide-react-native';

// Shown when the user first switches to Risk mode. Carries the legitimacy +
// proprietary-results message (the same T&C clause accepted at signup).
export function RiskExplainer({ onDismiss }: { onDismiss: () => void }) {
  return (
    <View className="rounded-2xl p-4 mb-4" style={{ backgroundColor: '#E85A1E12', borderWidth: 1, borderColor: '#E85A1E40' }}>
      <View className="flex-row items-center gap-2 mb-2">
        <ShieldAlert size={18} color="#E85A1E" />
        <Text className="font-bold text-base" style={{ color: '#E85A1E' }}>Other Items</Text>
      </View>
      <Text className="text-textSecondary text-sm leading-5 mb-2">
        Scores emerging financial items before they're priced in. A high score means smart money
        is positioning early — detected from public SEC filings, Federal Reserve data, and official APIs.
        Every signal shows its sources for full transparency.
      </Text>
      <Text className="text-textMuted text-[11px] leading-4 mb-3">
        All data is public, government-published, or accessed via official APIs. Results are proprietary to
        Now TrendIn under your Terms of Service.
      </Text>
      <TouchableOpacity onPress={onDismiss} className="self-start">
        <Text className="text-sm font-semibold" style={{ color: '#E85A1E' }}>Got it</Text>
      </TouchableOpacity>
    </View>
  );
}
