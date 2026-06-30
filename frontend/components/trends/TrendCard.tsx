import React, { useState } from 'react';
import { View, Text, TouchableOpacity, LayoutAnimation, Platform, UIManager } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronDown, ArrowRight } from 'lucide-react-native';
import { Rise } from '../ui/Rise';
import { Signal, ageLabel, stageColor, stageLabel, scoreGap, gapInsight, contentCategoryMeta, titleCaseTopic } from '../../lib/signals';

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

// Component-bar fill color by strength (sapphire → faded → track).
function barColor(v: number) {
  if (v >= 70) return '#2A5B9E';
  if (v >= 40) return '#7C93C8';
  return '#D8DCE3';
}

const metaLabel = { color: '#9A9AA2', fontSize: 9, fontWeight: '700', letterSpacing: 1 } as const;
const metaNum = { color: '#16264A', fontSize: 26, fontWeight: '800', letterSpacing: -0.6 } as const;

// Calm, tap-to-expand trend row (Aurora journey). Collapsed: rank, title,
// platform·stage·age, score, chevron. Expanded (quick-look): detection /
// confidence / gap, the component bars, the gap insight, category·stage, and a
// MORE INFO button that opens the full Trend Detail screen. Nothing is removed —
// the deeper analysis (AI explainer, history, etc.) lives one tap further in.
export function TrendCard({ signal, rank }: { signal: Signal; rank?: number }) {
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const stageCol = stageColor(signal.stage);
  const gap = scoreGap(signal);
  const insight = gapInsight(gap);
  const platform = signal.platforms?.[0] ?? 'Multi-Platform';
  const cat = contentCategoryMeta(signal.category);
  const bars = (signal.groups?.flatMap((g) => g.items.map((i) => i.value)) ?? [
    signal.detection,
    signal.confidence,
    signal.score,
  ]).slice(0, 6);

  const toggle = () => {
    // Soft, relaxed expand — slower easeInEaseOut, no spring/bounce (Apple feel).
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
          {rank != null && (
            <Text style={{ color: stageCol, fontSize: 30, fontWeight: '800', letterSpacing: -1.5, width: 38 }}>
              {String(rank).padStart(2, '0')}
            </Text>
          )}
          <View style={{ flex: 1 }}>
            <Text numberOfLines={1} style={{ color: '#16264A', fontSize: 17, fontWeight: '700', letterSpacing: -0.3 }}>
              {titleCaseTopic(signal.topic)}
            </Text>
            <Text style={{ color: '#9A9AA2', fontSize: 9.5, fontWeight: '700', letterSpacing: 1, marginTop: 4 }}>
              {platform.toUpperCase()} · <Text style={{ color: stageCol }}>{stageLabel(signal.stage)}</Text> · {ageLabel(signal.createdAt).toUpperCase()}
            </Text>
          </View>
          <View style={{ alignItems: 'flex-end' }}>
            <Text style={{ color: '#16264A', fontSize: 22, fontWeight: '800', letterSpacing: -0.6, lineHeight: 24 }}>{signal.score}</Text>
            <Text style={{ color: '#9A9AA2', fontSize: 8, fontWeight: '700', letterSpacing: 1 }}>SCORE</Text>
          </View>
          <ChevronDown size={18} color="#C7C7CE" style={{ transform: [{ rotate: open ? '180deg' : '0deg' }] }} />
        </View>

        {open && (
          <Rise duration={420} distance={10} style={{ paddingLeft: rank != null ? 52 : 0, paddingTop: 16 }}>
            <View className="flex-row" style={{ gap: 24, marginBottom: 16 }}>
              <View>
                <Text style={metaLabel}>DETECTION</Text>
                <Text style={metaNum}>{signal.detection}</Text>
              </View>
              <View>
                <Text style={metaLabel}>CONFIDENCE</Text>
                <Text style={metaNum}>{signal.confidence}</Text>
              </View>
              <View style={{ marginLeft: 'auto', alignItems: 'flex-end' }}>
                <Text style={metaLabel}>GAP</Text>
                <Text style={[metaNum, { color: '#B11226' }]}>{gap}</Text>
              </View>
            </View>

            <View className="flex-row" style={{ gap: 5, marginBottom: 16 }}>
              {bars.map((v, i) => (
                <View key={i} style={{ flex: 1, height: 5, borderRadius: 980, backgroundColor: '#EDEDED', overflow: 'hidden' }}>
                  <View style={{ width: `${Math.max(6, Math.min(100, v))}%`, height: '100%', backgroundColor: barColor(v) }} />
                </View>
              ))}
            </View>

            <Text style={{ color: '#3C4663', fontSize: 13.5, lineHeight: 21, fontWeight: '500', marginBottom: 10 }}>
              {gap}-point gap: {insight.text}
            </Text>
            <Text style={{ color: '#9A9AA2', fontSize: 12, lineHeight: 19, fontWeight: '500', marginBottom: 16 }}>
              Category: {cat.label} · Stage: {stageLabel(signal.stage)}
            </Text>

            <TouchableOpacity
              onPress={() => router.push(`/signal/${signal.id}`)}
              activeOpacity={0.85}
              className="flex-row items-center self-start"
              style={{ backgroundColor: '#16264A', borderRadius: 980, paddingVertical: 11, paddingHorizontal: 22 }}
            >
              <Text style={{ color: '#FFFFFF', fontSize: 11, fontWeight: '800', letterSpacing: 1 }}>MORE INFO</Text>
              <ArrowRight size={13} color="#F0758A" style={{ marginLeft: 6 }} />
            </TouchableOpacity>
          </Rise>
        )}
      </TouchableOpacity>
    </View>
  );
}
