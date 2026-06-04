import React from 'react';
import { View, Text } from 'react-native';

const DET = '#2D7EEF';
const CONF = '#00C896';

// The two threshold rule-sets, side by side. Blue = Detection, Green = Confidence.
const ROWS = [
  { label: 'INERTIA WINDOW', det: '1 window', conf: '2 windows' },
  { label: 'PLATFORM PATTERN', det: 'No match', conf: 'Partial match' },
  { label: 'FIRST-TIMER TRIGGER', det: '≥ 0%', conf: '≥ 10%' },
  { label: 'MAINSTREAM PENALTY', det: 'Gradual', conf: 'Strict' },
];

function ValueLine({ color, value }: { color: string; value: string }) {
  return (
    <View className="flex-row items-center gap-1.5">
      <View style={{ width: 7, height: 7, borderRadius: 4, backgroundColor: color }} />
      <Text style={{ color }} className="text-sm font-bold flex-1">{value}</Text>
    </View>
  );
}

export function WhyScoresDiverge() {
  return (
    <View>
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3 mt-1">Why the scores diverge</Text>
      <View className="flex-row flex-wrap gap-2">
        {ROWS.map((r) => (
          <View key={r.label} className="flex-1 min-w-[46%] bg-surface rounded-xl border border-border p-3">
            <Text className="text-textMuted text-[9px] font-bold tracking-wider mb-2">{r.label}</Text>
            <ValueLine color={DET} value={r.det} />
            <View className="h-1" />
            <ValueLine color={CONF} value={r.conf} />
          </View>
        ))}
      </View>
      <Text className="text-textMuted text-[10px] mt-2">Blue = Detection mode · Green = Confidence mode</Text>
    </View>
  );
}
