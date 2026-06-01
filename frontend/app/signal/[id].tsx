import { useState } from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ChevronLeft, ChevronDown, ChevronUp, Bell } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { Button } from '../../components/ui/Button';
import { GradientScoreRing } from '../../components/ui/GradientScoreRing';
import {
  getSignalById,
  ageLabel,
  stageColor,
  scoreGap,
  actionFor,
  breakdownGroups,
} from '../../lib/signals';

export default function SignalDetail() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const signal = getSignalById(String(id));
  const [open, setOpen] = useState<string | null>('Signal Quality');

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

      <Text className="text-textPrimary text-3xl font-bold">{signal.topic}</Text>
      <Text className="text-textMuted text-sm mb-5">
        {signal.category} · {ageLabel(signal.createdAt)}
      </Text>

      {/* Dual Gradient Score */}
      <View className="bg-surface rounded-2xl p-5 border border-border mb-5" style={{ shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, elevation: 2 }}>
        <View className="flex-row justify-around items-center">
          <GradientScoreRing score={signal.detection} color={color} size="lg" label="DETECTION" caption="/100" />
          <GradientScoreRing score={signal.confidence} color="#2D7EEF" size="lg" label="CONFIDENCE" caption="/100" />
        </View>
        <Text className="text-textSecondary text-sm text-center mt-4">
          {gap}-point gap — {agree ? 'both models agree' : 'very early, models diverging'}
        </Text>
      </View>

      {/* WHAT TO DO */}
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">What to do</Text>
      <View className="rounded-2xl p-5 mb-5 border" style={{ borderColor: color, backgroundColor: `${color}10` }}>
        <Text className="text-2xl font-black mb-1" style={{ color }}>
          {action.title}
        </Text>
        <Text className="text-textSecondary text-base leading-6">{action.body}</Text>
      </View>

      {/* WHY THIS MATTERS */}
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Why this matters</Text>
      <Text className="text-textSecondary text-base leading-6 mb-5">
        "{signal.topic}" is registering a <Text className="font-semibold" style={{ color }}>{signal.stage.toLowerCase()}</Text> signal
        with a Gradient Score of {signal.score}. Detection ({signal.detection}) leads confidence ({signal.confidence}),
        indicating attention is moving {agree ? 'with conviction' : 'ahead of consensus'} in {signal.category.toLowerCase()}.
      </Text>

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
              <Text className="text-textPrimary font-semibold">{g.title}</Text>
              {isOpen ? <ChevronUp size={18} color="#9AA3B0" /> : <ChevronDown size={18} color="#9AA3B0" />}
            </TouchableOpacity>
            {isOpen && (
              <View className="px-4 pb-4 gap-3">
                {g.items.map((it) => (
                  <View key={it.label}>
                    <View className="flex-row justify-between mb-1">
                      <Text className="text-textSecondary text-sm">{it.label}</Text>
                      <Text className="text-textPrimary text-sm font-semibold">{it.value}</Text>
                    </View>
                    <View className="h-1.5 rounded-full bg-border overflow-hidden">
                      <View style={{ width: `${it.value}%`, backgroundColor: color }} className="h-full rounded-full" />
                    </View>
                  </View>
                ))}
              </View>
            )}
          </View>
        );
      })}

      <View className="mt-3 mb-2">
        <Button size="lg" icon={<Bell size={18} color="#FFFFFF" />} onPress={() => router.push('/alerts')}>
          Set Alert for this topic
        </Button>
      </View>
    </Screen>
  );
}
