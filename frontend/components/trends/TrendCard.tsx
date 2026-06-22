import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronRight, Sparkles, Flame } from 'lucide-react-native';
import { Signal, ageLabel, stageColor, stageLabel, scoreGap, gapInsight, STAGE_META, contentCategoryMeta } from '../../lib/signals';
import { useExplainer } from '../../hooks/useSignals';

const DET_COLOR = '#2D7EEF';
const CONF_COLOR = '#00C896';

function barColor(v: number) {
  if (v >= 70) return '#00C896';
  if (v >= 40) return '#2D7EEF';
  return '#C7CDD6';
}

// Web-prototype-style trend card: source header, dual score, component bars,
// gap pill, and a coloured gap-insight footer.
export function TrendCard({ signal }: { signal: Signal }) {
  const router = useRouter();
  const stageCol = stageColor(signal.stage);
  const gap = scoreGap(signal);
  const insight = gapInsight(gap);
  const { explainer } = useExplainer(signal.id, signal.topic);
  const platform = signal.platforms?.[0] ?? 'Multi-Platform';
  const multi = (signal.platforms?.length ?? 0) > 1;
  const isNew = (signal.timesScored ?? 0) <= 1;
  // Short stage definition surfaced on the card (e.g. "Building signal" for
  // EMERGING). Pulled from STAGE_META so it stays in sync with the homepage
  // legend + the focused category page.
  const stageDef = STAGE_META.find((m) => m.key === signal.stage)?.desc ?? '';
  const cat = contentCategoryMeta(signal.category);
  // Now Trending score (N component) — always show; default to 0 when absent
  // so users see the metric exists and can read its detail on tap.
  const nowTrending = signal.nowTrending ?? 0;

  const bars = (signal.groups?.flatMap((g) => g.items.map((i) => i.value)) ?? [
    signal.detection,
    signal.confidence,
    signal.score,
  ]).slice(0, 6);

  return (
    <TouchableOpacity
      activeOpacity={0.9}
      onPress={() => router.push(`/signal/${signal.id}`)}
      className="bg-surface rounded-2xl border border-border p-4 mb-3"
      style={{ shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, elevation: 2 }}
    >
      {/* header row */}
      <View className="flex-row items-start justify-between">
        <Text className="text-textMuted text-[11px]">
          {platform} · {signal.totalMentions ?? 0} signals · {ageLabel(signal.createdAt)}
        </Text>
        <View className="flex-row items-center gap-1.5">
          {/* Content-category badge (WHAT) — sits beside the stage badge (HOW) */}
          <View className="px-2.5 py-1 rounded-full" style={{ backgroundColor: `${cat.color}1A` }}>
            <Text style={{ color: cat.color }} className="text-[10px] font-bold tracking-wide">
              {cat.label}
            </Text>
          </View>
          <View className="px-2.5 py-1 rounded-full" style={{ backgroundColor: `${stageCol}1A` }}>
            <Text style={{ color: stageCol }} className="text-[10px] font-bold tracking-wide">
              {stageLabel(signal.stage)}
            </Text>
          </View>
        </View>
      </View>

      {/* title + scores */}
      <View className="flex-row items-start justify-between mt-1">
        <View className="flex-1 pr-3">
          <Text className="text-textPrimary text-2xl font-bold">{signal.topic}</Text>
          <View className="flex-row items-center gap-1.5 mt-0.5">
            <Text className="text-textMuted text-xs">{multi ? 'Multi-Platform' : platform}</Text>
            {!!stageDef && (
              <>
                <Text className="text-textMuted text-xs">·</Text>
                <Text style={{ color: stageCol }} className="text-xs font-semibold">{stageDef}</Text>
              </>
            )}
          </View>
        </View>
        <View className="flex-row gap-3">
          <View className="items-center">
            <Text className="text-textMuted text-[9px] font-bold">DET</Text>
            <Text style={{ color: DET_COLOR }} className="text-xl font-black">{signal.detection}</Text>
          </View>
          <View className="items-center">
            <Text className="text-textMuted text-[9px] font-bold">CONF</Text>
            <Text style={{ color: CONF_COLOR }} className="text-xl font-black">{signal.confidence}</Text>
          </View>
        </View>
      </View>

      {/* component bars + Now Trending pill + gap pill row */}
      <View className="flex-row items-center justify-between mt-3 gap-1.5">
        <View className="flex-row items-center gap-1.5 flex-1 mr-1">
          {bars.map((v, i) => (
            <View key={i} className="flex-1 h-1.5 rounded-full bg-border overflow-hidden">
              <View style={{ width: `${Math.max(6, Math.min(100, v))}%`, backgroundColor: barColor(v) }} className="h-full rounded-full" />
            </View>
          ))}
        </View>
        {/* Now TrendIn (N) — brand-colored pill, parallel to the gap pill.
            Surfaces the headline metric on every card for visual consistency
            with the chip + tile rows on the homepage. */}
        <View className="flex-row items-center px-2 py-1 rounded-full"
              style={{ backgroundColor: '#EE6A2A1A' }}>
          <Flame size={10} color="#EE6A2A" />
          <Text className="text-[10px] font-bold ml-0.5" style={{ color: '#B5341B' }}>
            N {nowTrending}
          </Text>
        </View>
        <View
          className="px-2.5 py-1 rounded-full"
          style={{ backgroundColor: insight.agree ? '#00C8961A' : '#D4A0171A' }}
        >
          <Text style={{ color: insight.agree ? '#009970' : '#9A7B16' }} className="text-[10px] font-bold">
            {gap}pt gap
          </Text>
        </View>
      </View>

      {isNew && (
        <View className="flex-row items-center gap-1 mt-2">
          <View className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: DET_COLOR }} />
          <Text className="text-textMuted text-[10px]">New</Text>
        </View>
      )}

      {/* gap insight footer */}
      <View
        className="rounded-xl px-3 py-2 mt-3 border"
        style={{
          borderColor: insight.agree ? '#00C89655' : '#D4A01755',
          backgroundColor: insight.agree ? '#00C8960F' : '#D4A0170F',
        }}
      >
        <Text className="text-[11px]" style={{ color: insight.agree ? '#009970' : '#9A7B16' }}>
          {gap}-point gap: {insight.text}
        </Text>
      </View>

      {/* AI explainer (when available) + ALWAYS-visible MORE INFO button.
          The button now renders regardless of whether the AI explainer has
          generated yet — matches the per-item pattern used in the Market tab. */}
      <View className="mt-3">
        {!!explainer?.short && (
          <Text className="text-textSecondary text-[13px] leading-5 mb-2" numberOfLines={3}>
            {explainer.short}
          </Text>
        )}
        <View className="flex-row items-center self-start px-3 py-1.5 rounded-full" style={{ backgroundColor: '#2D7EEF' }}>
          <Sparkles size={12} color="#FFFFFF" />
          <Text className="text-white text-[11px] font-bold ml-1 mr-0.5">MORE INFO</Text>
          <ChevronRight size={13} color="#FFFFFF" />
        </View>
      </View>
    </TouchableOpacity>
  );
}
