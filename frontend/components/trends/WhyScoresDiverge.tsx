import React from 'react';
import { View, Text } from 'react-native';
import { Signal, signedGap, signedLabel } from '../../lib/signals';

const DET = '#2A5B9E';   // Detection — earliness
const CONF = '#2E7D5B';  // Confidence — confirmation

// LIVE per-signal explanation of WHY Detection and Confidence diverge for THIS
// topic. Detection weights the early-edge components (Dark Matter, first-timers,
// niche concentration); Confidence weights cross-platform confirmation. The gap
// is the imbalance between them — so we show the signal's ACTUAL values on each
// side. (Previously this was a static hardcoded table identical for every signal.)
export function WhyScoresDiverge({ signal }: { signal: Signal }) {
  const sg = signedGap(signal);          // signed — what actually prints (K17)
  const ftPct = signal.firstTimerRatio != null ? Math.round(signal.firstTimerRatio * 100) : null;
  const platformCount = signal.platforms?.length ?? null;

  // Each row carries the signal's real value + which score it pushes toward.
  const rows: { label: string; value: string; favors: 'DET' | 'CONF'; note: string }[] = [];

  // This file had NO d_measured guard at all (Guardian + Challenger, board round 5), so
  // it rendered "UNDER-THE-RADAR (D) 0/100" on topics where D could not be read — a
  // structural zero presented as a measured one, on a panel whose whole job is to explain
  // WHY two scores diverge. §16a stage-2: a floor value must never wear a measured badge.
  // 4c TRI-STATE (web parity, all-pages audit 2026-09-14): dMeasured is tri-state —
  // true read · false blind (UNMEASURED — looked, could not read) · undefined/null
  // UNKNOWN (readability never recorded). Two different facts, never pooled, never
  // silently a number.
  const dReadable = signal.dMeasured === true;
  const dUnknown = signal.dMeasured === undefined;

  if (signal.darkMatter != null && dReadable)
    rows.push({ label: 'UNDER-THE-RADAR (D)', value: `${Math.round(signal.darkMatter)}/100`,
      favors: 'DET', note: 'hidden early activity → lifts Detection' });
  else if (signal.darkMatter != null && dUnknown)
    rows.push({ label: 'UNDER-THE-RADAR (D)', value: 'Unknown',
      favors: 'DET', note: 'scored before D readability was recorded — missing metadata, not a finding' });
  else if (signal.darkMatter != null)
    rows.push({ label: 'UNDER-THE-RADAR (D)', value: 'Unmeasured',
      favors: 'DET', note: 'D could not be read for this topic — absence of measurement, not a low reading' });
  if (ftPct != null && dReadable)
    rows.push({ label: 'FIRST-TIMER RATIO', value: `${ftPct}%`,
      favors: 'DET', note: 'new participants flooding in → lifts Detection' });
  else if (ftPct != null && dUnknown)
    rows.push({ label: 'FIRST-TIMER RATIO', value: 'Unknown',
      favors: 'DET', note: 'scored before D readability was recorded — missing metadata, not a finding' });
  else if (ftPct != null)
    rows.push({ label: 'FIRST-TIMER RATIO', value: 'Unmeasured',
      favors: 'DET', note: 'no author-bearing signals for this topic — D could not be read (not "read quiet")' });
  if (signal.engagementAsymmetry != null)
    rows.push({ label: 'ENGAGEMENT ASYMMETRY', value: signal.engagementAsymmetry ? 'Detected' : 'Normal',
      favors: 'DET', note: 'deep discussion vs surface votes → lifts Detection' });
  if (platformCount != null)
    rows.push({ label: 'PLATFORM SPREAD', value: `${platformCount} platform${platformCount === 1 ? '' : 's'}`,
      favors: 'CONF', note: 'broad cross-platform presence → lifts Confidence' });

  // Summary sentence keyed off the SIGNED gap (K17): a negative gap means
  // confirmation is ahead of the early edge — never describe it as "running
  // well ahead". The magnitude bands; the sign selects the direction sentence.
  const summary =
    sg >= 18
      ? `This signal's ${signedLabel(sg)}-pt gap means its early-edge components are running well ahead of cross-platform confirmation — detected early, not yet broadly confirmed.`
      : sg >= 8
      ? `A ${signedLabel(sg)}-pt gap: the early-edge signal is somewhat ahead of confirmation — building, but not fully aligned.`
      : sg <= -8
      ? `A ${signedLabel(sg)}-pt gap: broad confirmation is running ahead of the early-edge components — already widely confirmed, not an early read.`
      : `A ${signedLabel(sg)}-pt gap: early-edge and confirmation are closely aligned — the two scores agree on where this sits.`;

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
