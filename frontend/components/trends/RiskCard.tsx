import React, { useState } from 'react';
import { View, Text, TouchableOpacity, LayoutAnimation, Platform, UIManager } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronDown, ArrowRight, Globe } from 'lucide-react-native';
import { Rise } from '../ui/Rise';
import { RiskScore } from '../../lib/gradientApi';
import { titleCaseTopic } from '../../lib/signals';

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

const CLASS_COLOR: Record<string, string> = {
  UNUSUAL: '#B11226',
  ELEVATED: '#A8456A',
  WATCH: '#2A5B9E',
  ROUTINE: '#9A9AA2',
  CALIBRATING: '#9A9AA2',
};

const STAGES = [
  { key: 'Dark Positioning', label: 'Insider' },
  { key: 'Expert Warning', label: 'Expert' },
  { key: 'Consumer Concern', label: 'Consumer' },
  { key: 'Media Coverage', label: 'Media' },
  { key: 'Retail Amplify', label: 'Retail' },
] as const;

// Calm, tap-to-expand market row — mirrors TrendCard. Collapsed: name,
// classification·signals, positioning score, chevron. Expanded: diffusion
// stages, narrative, financial sustainability, sources, and Full detail.
export function RiskCard({ risk }: { risk: RiskScore }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const cls = risk.classification ?? 'CALIBRATING';
  const color = CLASS_COLOR[cls] ?? '#9A9AA2';
  const score = risk.positioningScore ?? 0;
  const stages = risk.stages ?? {};
  const counts = STAGES.map((s) => stages[s.key]?.count ?? 0);
  const maxStage = Math.max(1, ...counts);

  const toggle = () => {
    LayoutAnimation.configureNext({
      duration: 440,
      create: { type: 'easeInEaseOut', property: 'opacity' },
      update: { type: 'easeInEaseOut' },
      delete: { type: 'easeInEaseOut', property: 'opacity' },
    });
    setOpen((o) => !o);
  };

  return (
    <View style={{ borderBottomWidth: 1, borderBottomColor: '#ECECEC' }}>
      <TouchableOpacity activeOpacity={0.7} onPress={toggle} className="py-4">
        <View className="flex-row items-center" style={{ gap: 14 }}>
          <View style={{ width: 8, height: 8, borderRadius: 4, backgroundColor: color }} />
          <View style={{ flex: 1 }}>
            <Text numberOfLines={1} style={{ color: '#16264A', fontSize: 16, fontWeight: '700', letterSpacing: -0.2 }}>{titleCaseTopic(risk.display)}</Text>
            <Text style={{ color: '#9A9AA2', fontSize: 9.5, fontWeight: '700', letterSpacing: 1, marginTop: 4 }}>
              <Text style={{ color }}>{cls}</Text> · {risk.totalSignals} SIGNALS{risk.percentDelta != null ? ` · ${risk.percentDelta >= 0 ? '+' : ''}${Math.round(risk.percentDelta)}%` : ''}
            </Text>
          </View>
          <View style={{ alignItems: 'flex-end' }}>
            <Text style={{ color: '#16264A', fontSize: 22, fontWeight: '800', letterSpacing: -0.6, lineHeight: 24 }}>{score}</Text>
            <Text style={{ color: '#9A9AA2', fontSize: 8, fontWeight: '700', letterSpacing: 1 }}>POS</Text>
          </View>
          <ChevronDown size={18} color="#C7C7CE" style={{ transform: [{ rotate: open ? '180deg' : '0deg' }] }} />
        </View>

        {open && (
          <Rise duration={420} distance={10} style={{ paddingTop: 16 }}>
            {/* Diffusion stages: insider → retail */}
            <View className="flex-row" style={{ gap: 6, marginBottom: 14 }}>
              {STAGES.map((s, i) => {
                const v = counts[i];
                const h = 4 + Math.round((v / maxStage) * 18);
                return (
                  <View key={s.key} className="flex-1 items-center">
                    <View className="w-full justify-end" style={{ height: 22 }}>
                      <View style={{ height: h, backgroundColor: v > 0 ? color : '#ECECEC', borderRadius: 3 }} />
                    </View>
                    <Text style={{ color: '#9A9AA2', fontSize: 8, marginTop: 4 }}>{s.label}</Text>
                    <Text style={{ color: '#3C4663', fontSize: 9, fontWeight: '700' }}>{v}</Text>
                  </View>
                );
              })}
            </View>

            {!!(risk.narrative || risk.interpretation) && (
              <Text style={{ color: '#3C4663', fontSize: 13, lineHeight: 20, fontWeight: '500', marginBottom: 12 }}>
                {risk.narrative || risk.interpretation}
              </Text>
            )}

            {!!risk.sustainability && (
              <View className="flex-row items-center gap-2 mb-3">
                <Text style={{ color: '#9A9AA2', fontSize: 11 }}>Financial sustainability</Text>
                <View className="px-2 py-0.5 rounded-full" style={{ backgroundColor: `${risk.sustainability.score >= 75 ? '#2E7D5B' : risk.sustainability.score >= 50 ? '#2A5B9E' : risk.sustainability.score >= 30 ? '#A8456A' : '#B11226'}1A` }}>
                  <Text style={{ fontSize: 11, fontWeight: '700', color: risk.sustainability.score >= 75 ? '#246B4A' : risk.sustainability.score >= 50 ? '#2A5B9E' : risk.sustainability.score >= 30 ? '#A8456A' : '#B11226' }}>
                    {risk.sustainability.score}/100 · {risk.sustainability.label}
                  </Text>
                </View>
              </View>
            )}

            {risk.sources.length > 0 && (
              <View className="flex-row items-center gap-1 mb-4">
                <Globe size={10} color="#9A9AA2" />
                <Text style={{ color: '#9A9AA2', fontSize: 10, flex: 1 }} numberOfLines={1}>Sources: {risk.sources.join(' · ')}</Text>
              </View>
            )}

            <TouchableOpacity onPress={() => router.push(`/risk/${risk.key}`)} activeOpacity={0.85}
              className="flex-row items-center self-start" style={{ backgroundColor: '#16264A', borderRadius: 980, paddingVertical: 11, paddingHorizontal: 22 }}>
              <Text style={{ color: '#FFFFFF', fontSize: 11, fontWeight: '800', letterSpacing: 1 }}>FULL DETAIL</Text>
              <ArrowRight size={13} color="#F0758A" style={{ marginLeft: 6 }} />
            </TouchableOpacity>
          </Rise>
        )}
      </TouchableOpacity>
    </View>
  );
}
