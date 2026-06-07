import React from 'react';
import { View, Text } from 'react-native';
import { STAGE_META } from '../../lib/signals';

// "What do these scores mean?" legend, matching the web prototype.
export function ScoreLegend() {
  return (
    <View className="bg-surface rounded-2xl border border-border p-4 mb-4">
      <Text className="text-textMuted text-[10px] font-bold tracking-widest uppercase mb-3">
        What do these scores mean?
      </Text>
      <View className="flex-row flex-wrap gap-2">
        {STAGE_META.map((s) => (
          <View
            key={s.key}
            className="flex-1 min-w-[46%] rounded-xl p-3 border"
            style={{ borderColor: `${s.color}55`, backgroundColor: `${s.color}12` }}
          >
            <Text style={{ color: s.color }} className="text-xs font-bold">
              {s.label}
            </Text>
            <Text className="text-textMuted text-[10px] mt-0.5">{s.range}</Text>
            <Text style={{ color: s.color }} className="text-[11px] font-semibold mt-1">
              {s.desc}
            </Text>
          </View>
        ))}
      </View>
    </View>
  );
}
