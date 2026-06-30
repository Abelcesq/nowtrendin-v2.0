import React from 'react';
import { View, Text } from 'react-native';
import { Signal, scoreGap, GAP_BANDS, gapBandIndex, SCORE_ROLES } from '../../lib/signals';

function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <Text className="text-textMuted text-[10px] font-bold tracking-widest uppercase mb-2 mt-5">
      {children}
    </Text>
  );
}

// Mirrors the web prototype's "Dual Score Analysis" panel.
export function DualScoreAnalysis({ signal }: { signal: Signal }) {
  const gap = scoreGap(signal);
  const activeIdx = gapBandIndex(gap);
  const band = GAP_BANDS[activeIdx];

  return (
    <View>
      <Text className="text-textPrimary text-xl font-black mt-2">Dual Score Analysis</Text>
      <Text className="text-textSecondary text-sm leading-6 mt-1">
        The same measurements run once. Two threshold rule-sets produce two scores. The gap
        between them tells you how early this signal is.
      </Text>

      <View className="flex-row items-center gap-4 mt-3">
        <View className="flex-row items-center gap-1.5">
          <View className="w-3 h-3 rounded" style={{ backgroundColor: SCORE_ROLES.detection.color }} />
          <Text className="text-textSecondary text-xs font-semibold">Detection</Text>
        </View>
        <View className="flex-row items-center gap-1.5">
          <View className="w-3 h-3 rounded" style={{ backgroundColor: SCORE_ROLES.confidence.color }} />
          <Text className="text-textSecondary text-xs font-semibold">Confidence</Text>
        </View>
      </View>

      {/* Gap interpretation */}
      <SectionLabel>Gap interpretation</SectionLabel>
      <View className="bg-card rounded-2xl p-4">
        {GAP_BANDS.map((b, i) => (
          <View key={b.range} className="flex-row gap-3 mb-3" style={{ opacity: i === activeIdx ? 1 : 0.5 }}>
            <View className="w-1 rounded-full" style={{ backgroundColor: b.color }} />
            <View className="flex-1">
              <Text className="text-textPrimary text-sm font-bold">{b.range}</Text>
              <Text className="text-textMuted text-xs">{b.label}</Text>
            </View>
          </View>
        ))}
        <View
          className="rounded-xl px-3 py-2 mt-1"
          style={{ borderColor: `${band.color}66`, backgroundColor: `${band.color}12` }}
        >
          <Text className="text-xs font-bold" style={{ color: band.color }}>
            This signal: {gap}-point gap — {band.label.split(' — ')[0]}
          </Text>
        </View>
      </View>

      {/* Who uses which score */}
      <SectionLabel>Who uses which score</SectionLabel>
      <View
        className="rounded-2xl p-4 mb-3"
        style={{ borderColor: `${SCORE_ROLES.detection.color}55`, backgroundColor: `${SCORE_ROLES.detection.color}0D` }}
      >
        <Text style={{ color: SCORE_ROLES.detection.color }} className="text-sm font-bold">
          Detection score: {signal.detection}
        </Text>
        <Text className="text-textSecondary text-xs leading-5 mt-1">{SCORE_ROLES.detection.who}</Text>
      </View>
      <View
        className="rounded-2xl p-4"
        style={{ borderColor: `${SCORE_ROLES.confidence.color}55`, backgroundColor: `${SCORE_ROLES.confidence.color}0D` }}
      >
        <Text style={{ color: SCORE_ROLES.confidence.color }} className="text-sm font-bold">
          Confidence score: {signal.confidence}
        </Text>
        <Text className="text-textSecondary text-xs leading-5 mt-1">{SCORE_ROLES.confidence.who}</Text>
      </View>
    </View>
  );
}
