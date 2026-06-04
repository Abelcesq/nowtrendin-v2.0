import { useState } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ChevronLeft, ChevronDown, ChevronUp, Bell } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { Button } from '../../components/ui/Button';
import { GradientScoreRing } from '../../components/ui/GradientScoreRing';
import { DualScoreAnalysis } from '../../components/trends/DualScoreAnalysis';
import { WhyScoresDiverge } from '../../components/trends/WhyScoresDiverge';
import { ScoringHistory } from '../../components/trends/ScoringHistory';
import { ResearchHistory } from '../../components/trends/ResearchHistory';
import { useSignal } from '../../hooks/useSignals';
import { ageLabel, stageColor, scoreGap, actionFor, breakdownGroups, SCORE_ROLES } from '../../lib/signals';

export default function SignalDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const { signal, isLoading } = useSignal(String(id));
  const [open, setOpen] = useState<string | null>('Signal Quality');

  if (isLoading) {
    return (
      <Screen>
        <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-8 self-start">
          <ChevronLeft size={24} color="#5B6472" />
        </TouchableOpacity>
        <ActivityIndicator size="large" color="#00C896" style={{ marginTop: 40 }} />
      </Screen>
    );
  }

  if (!signal) {
    return (
      <Screen>
        <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-8 self-start">
          <ChevronLeft size={24} color="#5B6472" />
        </TouchableOpacity>
        <Text className="text-textMuted text-center mt-20">Signal not found.</Text>
      </Screen>
    );
  }

  const color = stageColor(signal.stage);
  const gap = scoreGap(signal);
  const action = actionFor(signal);
  const groups = breakdownGroups(signal);
  const agree = gap <= 6;

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-4 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#5B6472" />
        <Text className="text-textSecondary text-sm">Signal Intel</Text>
      </TouchableOpacity>

      <Text className="text-textMuted text-[10px] font-bold tracking-widest uppercase">Now TrendIn · Signal Intel</Text>
      <Text className="text-textPrimary text-3xl font-bold mt-0.5">{signal.topic}</Text>
      <Text className="text-textMuted text-sm mb-4">
        {signal.totalMentions ?? 0} signals · {signal.platforms?.[0] ?? 'Multi-Platform'} · {ageLabel(signal.createdAt)}
      </Text>

      {/* Tagline */}
      <View className="rounded-xl px-4 py-3 mb-5 border border-border bg-surface">
        <Text className="text-textSecondary text-sm">
          Two scores, one engine. Earlier detection = lower certainty. You choose.
        </Text>
      </View>

      {/* Dual Gradient Score — Detection (blue) vs Confidence (green) */}
      <View className="bg-surface rounded-2xl p-5 border border-border mb-5" style={{ shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, elevation: 2 }}>
        <View className="flex-row justify-around items-start">
          <View className="items-center">
            <View className="px-2.5 py-1 rounded-full mb-2" style={{ backgroundColor: `${color}1A` }}>
              <Text style={{ color }} className="text-[9px] font-bold tracking-wide">{signal.stage}</Text>
            </View>
            <GradientScoreRing score={signal.detection} color={SCORE_ROLES.detection.color} size="lg" caption="/100" />
            <Text className="text-textPrimary text-xs font-bold mt-2">DETECTION</Text>
            <Text className="text-textMuted text-[10px]">{SCORE_ROLES.detection.falsePositive}</Text>
          </View>
          <View className="items-center">
            <View className="px-2.5 py-1 rounded-full mb-2" style={{ backgroundColor: `${color}1A` }}>
              <Text style={{ color }} className="text-[9px] font-bold tracking-wide">{signal.stage}</Text>
            </View>
            <GradientScoreRing score={signal.confidence} color={SCORE_ROLES.confidence.color} size="lg" caption="/100" />
            <Text className="text-textPrimary text-xs font-bold mt-2">CONFIDENCE</Text>
            <Text className="text-textMuted text-[10px]">{SCORE_ROLES.confidence.falsePositive}</Text>
          </View>
        </View>
        <View className="rounded-xl px-3 py-2 mt-4 border" style={{ borderColor: agree ? '#00C89655' : '#2D7EEF55', backgroundColor: agree ? '#00C8960F' : '#2D7EEF0F' }}>
          <Text className="text-sm font-bold" style={{ color: agree ? '#009970' : '#2D7EEF' }}>
            {gap}-point gap — {agree ? 'both models agree' : 'early stage, confirmation building'}
          </Text>
          {!!signal.gapMeaning && (
            <Text className="text-textMuted text-xs mt-1 leading-5">{signal.gapMeaning}</Text>
          )}
        </View>
      </View>

      {/* Dual Score Analysis (gap bands + who uses which score) */}
      <DualScoreAnalysis signal={signal} />
      <View className="h-5" />

      {/* Research history (lazy) */}
      <ResearchHistory topicKey={signal.id} />
      <View className="h-4" />

      {/* WHAT TO DO */}
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">What to do</Text>
      <View className="rounded-2xl p-5 mb-5 border" style={{ borderColor: color, backgroundColor: `${color}10` }}>
        <Text className="text-2xl font-black mb-1" style={{ color }}>
          {action.title}
        </Text>
        {!!action.body && <Text className="text-textSecondary text-base leading-6">{action.body}</Text>}
        {!!signal.whatToDo?.detail && signal.whatToDo.detail !== action.body && (
          <Text className="text-textMuted text-sm leading-5 mt-2">{signal.whatToDo.detail}</Text>
        )}
      </View>

      {/* WHY THIS MATTERS */}
      {!!signal.why && (
        <>
          <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Why this matters</Text>
          <Text className="text-textSecondary text-base leading-6 mb-5">{signal.why}</Text>
        </>
      )}

      {/* WHAT TO WATCH */}
      {!!signal.whatToWatch && (
        <>
          <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">What to watch</Text>
          <Text className="text-textSecondary text-base leading-6 mb-5">{signal.whatToWatch}</Text>
        </>
      )}

      {/* SCORE BREAKDOWN */}
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3">Score breakdown</Text>
      {groups.map((g) => {
        const isOpen = open === g.title;
        return (
          <View key={g.title} className="bg-surface rounded-xl border border-border mb-3 overflow-hidden">
            <TouchableOpacity
              onPress={() => setOpen(isOpen ? null : g.title)}
              className="flex-row items-center justify-between px-4 py-3.5"
              activeOpacity={0.8}
            >
              <View className="flex-row items-center gap-2">
                <Text className="text-textPrimary font-semibold">{g.title}</Text>
                {!!g.status && <Text className="text-textMuted text-[10px] font-bold">{g.status}</Text>}
              </View>
              {isOpen ? <ChevronUp size={18} color="#9AA3B0" /> : <ChevronDown size={18} color="#9AA3B0" />}
            </TouchableOpacity>
            {isOpen && (
              <View className="px-4 pb-4 gap-3">
                {g.items.map((it) => (
                  <View key={it.label}>
                    <View className="flex-row justify-between mb-1">
                      <Text className="text-textSecondary text-sm flex-1 pr-2">{it.label}</Text>
                      <Text className="text-textPrimary text-sm font-semibold">
                        {it.value}
                        {it.conf != null ? <Text className="text-textMuted"> / {it.conf}</Text> : null}
                      </Text>
                    </View>
                    <View className="h-1.5 rounded-full bg-border overflow-hidden">
                      <View style={{ width: `${Math.max(0, Math.min(100, it.value))}%`, backgroundColor: color }} className="h-full rounded-full" />
                    </View>
                    {!!it.desc && <Text className="text-textMuted text-[11px] mt-1">{it.desc}</Text>}
                  </View>
                ))}
              </View>
            )}
          </View>
        );
      })}

      {/* Why the scores diverge */}
      <View className="mt-5">
        <WhyScoresDiverge />
      </View>

      {/* Actual scoring history */}
      <View className="mt-5">
        <ScoringHistory signal={signal} />
      </View>

      <View className="mt-5 mb-2">
        <Button size="lg" icon={<Bell size={18} color="#FFFFFF" />} onPress={() => router.push('/alerts')}>
          Set Alert for this topic
        </Button>
      </View>
    </Screen>
  );
}
