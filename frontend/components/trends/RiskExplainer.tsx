import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { Activity } from 'lucide-react-native';

// Shown when the user first switches to the Market section. Frames the Market
// Signal honestly: a dual score (Detection vs Confidence) split by data type,
// measured vs each item's own baseline — measurement, not advice.
export function RiskExplainer({ onDismiss }: { onDismiss: () => void }) {
  return (
    <View className="rounded-2xl p-4 mb-4" style={{ backgroundColor: '#E85A1E12', borderWidth: 1, borderColor: '#E85A1E40' }}>
      <View className="flex-row items-center gap-2 mb-2">
        <Activity size={18} color="#E85A1E" />
        <Text className="font-bold text-base" style={{ color: '#E85A1E' }}>Market Signal</Text>
      </View>
      <Text className="text-textSecondary text-sm leading-5 mb-2">
        The Gradient-Score approach applied to markets, split by data type:
        <Text className="font-semibold"> Detection</Text> = what analysts are saying + how smart money is
        positioned (leading, soft); <Text className="font-semibold">Confidence</Text> = what fundamentals
        and price confirm (hard, realized). The gap shows how early the move is — informed actors moving
        before the hard data confirms.
      </Text>
      <Text className="text-textSecondary text-sm leading-5 mb-2">
        Every component is scored relative to the item's own baseline — from public SEC filings, Federal
        Reserve / OFR data, FINRA, and official APIs — so a high score means activity is unusual for that
        item, not that it is "risky."
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
