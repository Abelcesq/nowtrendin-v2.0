import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { ShieldAlert, Globe } from 'lucide-react-native';
import { RiskScore } from '../../lib/gradientApi';

const STAGE_COLOR: Record<string, string> = {
  ACUTE: '#CF2A1B',
  ELEVATED: '#E85A1E',
  EMERGING: '#D4A017',
  WATCH: '#2D7EEF',
  BACKGROUND: '#9AA3B0',
};

// Stage 1 (Dark Positioning) is where the risk engine detects — the alpha.
const DETECT_STAGE = 'dark';
const STAGES = [
  { key: 'dark', label: 'Dark' },
  { key: 'expert', label: 'Expert' },
  { key: 'consumer', label: 'Consumer' },
  { key: 'media', label: 'Media' },
  { key: 'retail', label: 'Retail' },
] as const;

export function RiskCard({ risk }: { risk: RiskScore }) {
  const router = useRouter();
  const color = STAGE_COLOR[risk.stage] ?? '#9AA3B0';
  const maxStage = Math.max(1, ...STAGES.map((s) => (risk.diffusion as any)[s.key] as number));

  return (
    <TouchableOpacity
      activeOpacity={0.9}
      onPress={() => router.push(`/risk/${risk.key}`)}
      className="bg-surface rounded-2xl p-4 mb-3 border border-border"
      style={{ shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 5, shadowOffset: { width: 0, height: 2 }, elevation: 2 }}
    >
      <View className="flex-row items-center justify-between">
        <View className="flex-row items-center gap-2 flex-1 pr-2">
          <ShieldAlert size={16} color={color} />
          <Text className="text-textPrimary font-bold text-base flex-1">{risk.display}</Text>
        </View>
        <View className="px-2.5 py-1 rounded-full" style={{ backgroundColor: `${color}1A` }}>
          <Text style={{ color }} className="text-[10px] font-bold tracking-wide">{risk.stage}</Text>
        </View>
      </View>

      <View className="flex-row items-end gap-5 mt-2">
        <View>
          <Text className="text-textMuted text-[9px] font-bold">DETECTION</Text>
          <Text style={{ color: '#2D7EEF' }} className="text-2xl font-black">{risk.detection}</Text>
        </View>
        <View>
          <Text className="text-textMuted text-[9px] font-bold">CONFIDENCE</Text>
          <Text style={{ color: '#00C896' }} className="text-2xl font-black">{risk.confidence}</Text>
        </View>
        <Text className="text-textMuted text-[10px] ml-auto mb-1">{risk.totalSignals} signals</Text>
      </View>

      {/* Diffusion stages */}
      <View className="flex-row gap-1.5 mt-3">
        {STAGES.map((s) => {
          const v = (risk.diffusion as any)[s.key] as number;
          const h = 4 + Math.round((v / maxStage) * 18);
          const on = v > 0;
          const isDetect = s.key === DETECT_STAGE;
          return (
            <View key={s.key} className="flex-1 items-center">
              <View className="w-full justify-end" style={{ height: 22 }}>
                <View style={{ height: h, backgroundColor: on ? color : '#E4E7EC', borderRadius: 3 }} />
              </View>
              <Text className="text-textMuted text-[8px] mt-1">{s.label}</Text>
              <Text className="text-textSecondary text-[9px] font-bold">{v}</Text>
              {isDetect && (
                <View className="px-1 rounded mt-0.5" style={{ backgroundColor: color }}>
                  <Text style={{ fontSize: 6, color: '#FFFFFF', fontWeight: '700' }}>DETECT</Text>
                </View>
              )}
            </View>
          );
        })}
      </View>

      {!!risk.interpretation && (
        <Text className="text-textSecondary text-[12px] leading-5 mt-3">{risk.interpretation}</Text>
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
