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

export function WhyScoresDiverge() {
  return (
    <View>
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3 mt-1">Why the scores diverge</Text>
      <View className="flex-row flex-wrap gap-2">
        {ROWS.map((r) => (
          <View key={r.label} className="flex-1 min-w-[46%] bg-surface rounded-xl border border-border p-3">
            <Text className="text-textMuted text-[9px] font-bold tracking-wider mb-1">{r.label}</Text>
            <View className="flex-row items-center">
              <Text style={{ color: DET }} className="text-sm font-bold">{r.det}</Text>
              <Text className="text-textMuted text-xs mx-1.5">/</Text>
              <Text style={{ color: CONF }} className="text-sm font-bold">{r.conf}</Text>
            </View>
          </View>
        ))}
      </View>
      <Text className="text-textMuted text-[10px] mt-2">Blue = Detection mode · Green = Confidence mode</Text>
    </View>
  );
}
