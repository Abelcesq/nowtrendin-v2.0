import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { Activity, Globe } from 'lucide-react-native';
import { RiskScore } from '../../lib/gradientApi';

// Positioning classification → colour.
const CLASS_COLOR: Record<string, string> = {
  UNUSUAL: '#CF2A1B',
  ELEVATED: '#E85A1E',
  WATCH: '#2D7EEF',
  ROUTINE: '#9AA3B0',
  CALIBRATING: '#9AA3B0',
};

// Diffusion stages (positioning shape: label -> {count, z}). Stage 1 is the
// early/high-value detection stage.
const STAGES = [
  { key: 'Dark Positioning', label: 'Insider' },
  { key: 'Expert Warning', label: 'Expert' },
  { key: 'Consumer Concern', label: 'Consumer' },
  { key: 'Media Coverage', label: 'Media' },
  { key: 'Retail Amplify', label: 'Retail' },
] as const;

export function RiskCard({ risk }: { risk: RiskScore }) {
  const router = useRouter();
  const cls = risk.classification ?? 'CALIBRATING';
  const color = CLASS_COLOR[cls] ?? '#9AA3B0';
  const score = risk.positioningScore ?? 0;
  const stages = risk.stages ?? {};
  const counts = STAGES.map((s) => stages[s.key]?.count ?? 0);
  const maxStage = Math.max(1, ...counts);

  return (
    <TouchableOpacity
      activeOpacity={0.9}
      onPress={() => router.push(`/risk/${risk.key}`)}
      className="bg-surface rounded-2xl p-4 mb-3 border border-border"
      style={{ shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 5, shadowOffset: { width: 0, height: 2 }, elevation: 2 }}
    >
      <View className="flex-row items-center justify-between">
        <View className="flex-row items-center gap-2 flex-1 pr-2">
          <Activity size={16} color={color} />
          <Text className="text-textPrimary font-bold text-base flex-1">{risk.display}</Text>
        </View>
        <View className="px-2.5 py-1 rounded-full" style={{ backgroundColor: `${color}1A` }}>
          <Text style={{ color }} className="text-[10px] font-bold tracking-wide">{cls}</Text>
        </View>
      </View>

      <View className="flex-row items-end gap-3 mt-2">
        <View>
          <Text className="text-textMuted text-[9px] font-bold">POSITIONING</Text>
          <Text style={{ color }} className="text-2xl font-black">{score}<Text className="text-textMuted text-sm font-bold">/100</Text></Text>
        </View>
        {risk.percentDelta != null && (
          <Text className="text-textMuted text-[11px] mb-1">
            {risk.percentDelta >= 0 ? '+' : ''}{Math.round(risk.percentDelta)}% vs baseline
          </Text>
        )}
        <Text className="text-textMuted text-[10px] ml-auto mb-1">{risk.totalSignals} signals</Text>
      </View>

      {/* Diffusion stages (insider → retail) */}
      <View className="flex-row gap-1.5 mt-3">
        {STAGES.map((s, i) => {
          const v = counts[i];
          const h = 4 + Math.round((v / maxStage) * 18);
          const on = v > 0;
          const isDetect = i === 0;
          return (
            <View key={s.key} className="flex-1 items-center">
              <View className="w-full justify-end" style={{ height: 22 }}>
                <View style={{ height: h, backgroundColor: on ? color : '#E4E7EC', borderRadius: 3 }} />
              </View>
              <Text className="text-textMuted text-[8px] mt-1">{s.label}</Text>
              <Text className="text-textSecondary text-[9px] font-bold">{v}</Text>
              {isDetect && (
                <View className="px-1 rounded mt-0.5" style={{ backgroundColor: color }}>
                  <Text style={{ fontSize: 6, color: '#FFFFFF', fontWeight: '700' }}>EARLY</Text>
                </View>
              )}
            </View>
          );
        })}
      </View>

      {!!(risk.narrative || risk.interpretation) && (
        <Text className="text-textSecondary text-[12px] leading-5 mt-3">{risk.narrative || risk.interpretation}</Text>
      )}

      {/* Source provenance — the audit trail (institutional trust) */}
      {risk.sources.length > 0 && (
        <View className="flex-row items-center gap-1 mt-3 pt-2 border-t border-border">
          <Globe size={10} color="#9AA3B0" />
          <Text className="text-textMuted text-[10px] flex-1" numberOfLines={1}>
            Sources: {risk.sources.join(' · ')}
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );
}
