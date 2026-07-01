import React from 'react';
import { View, Text } from 'react-native';
import { Signal, scoreGap } from '../../lib/signals';

const DET = '#2A5B9E';   // Detection — earliness
const CONF = '#2E7D5B';  // Confidence — confirmation

// LIVE per-signal explanation of WHY Detection and Confidence diverge for THIS
// topic. Detection weights the early-edge components (Dark Matter, first-timers,
// niche concentration); Confidence weights cross-platform confirmation. The gap
// is the imbalance between them — so we show the signal's ACTUAL values on each
// side. (Previously this was a static hardcoded table identical for every signal.)
export function WhyScoresDiverge({ signal }: { signal: Signal }) {
  const gap = scoreGap(signal);
  const ftPct = signal.firstTimerRatio != null ? Math.round(signal.firstTimerRatio * 100) : null;
  const platformCount = signal.platforms?.length ?? null;

  // Each row carries the signal's real value + which score it pushes toward.
  const rows: { label: string; value: string; favors: 'DET' | 'CONF'; note: string }[] = [];

  if (signal.darkMatter != null)
    rows.push({ label: 'DARK MATTER (D)', value: `${Math.round(signal.darkMatter)}/100`,
      favors: 'DET', note: 'hidden early activity → lifts Detection' });
  if (ftPct != null)
    rows.push({ label: 'FIRST-TIMER RATIO', value: `${ftPct}%`,
      favors: 'DET', note: 'new participants flooding in → lifts Detection' });
  if (signal.engagementAsymmetry != null)
    rows.push({ label: 'ENGAGEMENT ASYMMETRY', value: signal.engagementAsymmetry ? 'Detected' : 'Normal',
      favors: 'DET', note: 'deep discussion vs surface votes → lifts Detection' });
  if (platformCount != null)
    rows.push({ label: 'PLATFORM SPREAD', value: `${platformCount} platform${platformCount === 1 ? '' : 's'}`,
      favors: 'CONF', note: 'broad cross-platform presence → lifts Confidence' });

  // Summary sentence keyed off the actual gap.
  const summary =
    gap >= 18
      ? `This signal's ${gap}-pt gap means its early-edge components are running well ahead of cross-platform confirmation — detected early, not yet broadly confirmed.`
      : gap >= 8
      ? `A ${gap}-pt gap: the early-edge signal is somewhat ahead of confirmation — building, but not fully aligned.`
      : `A ${gap}-pt gap: early-edge and confirmation are closely aligned — the two scores agree on where this sits.`;

  return (
    <View>
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2 mt-1">Why the scores diverge</Text>
      <Text className="text-textSecondary text-[12px] leading-4 mb-3">{summary}</Text>
      {rows.length > 0 ? (
        <View className="flex-row flex-wrap gap-2">
          {rows.map((r) => {
            const col = r.favors === 'DET' ? DET : CONF;
            return (
              <View key={r.label} className="flex-1 min-w-[46%] bg-card rounded-xl p-3">
                <Text className="text-textMuted text-[12px] font-bold tracking-wider mb-1">{r.label}</Text>
                <View className="flex-row items-center gap-1.5">
                  <View style={{ width: 7, height: 7, borderRadius: 4, backgroundColor: col }} />
                  <Text style={{ color: col }} className="text-base font-black flex-1">{r.value}</Text>
                </View>
                <Text className="text-textMuted text-[12px] leading-3 mt-1">{r.note}</Text>
              </View>
            );
          })}
        </View>
      ) : (
        <Text className="text-textMuted text-[12px]">Component-level detail isn't available for this signal yet.</Text>
      )}
      <Text className="text-textMuted text-[12px] mt-2">
        <Text style={{ color: DET }}>Blue</Text> lifts Detection (earliness) · <Text style={{ color: CONF }}>Green</Text> lifts Confidence (confirmation)
      </Text>
    </View>
  );
}
