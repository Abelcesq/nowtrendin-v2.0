import React, { useState } from 'react';
import { View, Text, TextInput, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { useQueryClient } from '@tanstack/react-query';
import { GraduationCap, Sparkles, Lock } from 'lucide-react-native';
import { Button } from '../ui/Button';
import { useAuthStore } from '../../store/auth.store';
import { TierID, canAccess } from '../../constants/tiers';
import { queryApi } from '../../lib/api';
import { mapSignal, Signal } from '../../lib/gradientApi';

// GRADE tool — propose a Gradient Score for a topic that is NOT already in our
// trends data. Token-metered (1 token per grade). Enterprise only.
//
// Today this runs the engine's live query (collects real signals for the topic
// and scores it) → a genuine "proposed Gradient Score." The planned next layer
// adds an AI internet search that researches a brand-new term and returns the
// reasoning/evidence behind the proposed score.
export function GradeTool() {
  const router = useRouter();
  const qc = useQueryClient();
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const [topic, setTopic] = useState('');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  const canGrade = canAccess(tier, 'canQueryNew'); // Enterprise only
  const tokens = user?.tokensRemaining ?? 0;

  const grade = async () => {
    setMsg(null);
    setBusy(true);
    try {
      const d: any = await queryApi.run(topic.trim());
      if (d?.found && d?.result) {
        if (user) updateUser({ ...user, tokensRemaining: d.tokensRemaining ?? tokens });
        const mapped = mapSignal(d.result);
        qc.setQueryData<Signal[]>(['scores'], (old = []) => [mapped, ...old.filter((s) => s.id !== mapped.id)]);
        router.push(`/signal/${mapped.id}`);
      } else {
        setMsg(d?.detail ?? 'Not enough signal to grade this topic yet.');
      }
    } catch (err: any) {
      setMsg(err?.data?.detail ?? 'Grade failed. Try again.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <View>
      <View className="flex-row items-center gap-2 mb-1">
        <GraduationCap size={20} color="#D4A017" />
        <Text className="text-textPrimary text-xl font-black">Grade a Topic</Text>
      </View>
      <Text className="text-textMuted text-[12px] leading-4 mb-4">
        Propose a Gradient Score for a topic that isn&apos;t in our trends yet. We collect live signals across
        sources and return a proposed score with the reasoning behind it.
      </Text>

      {!canGrade ? (
        <View className="rounded-xl border p-5 items-center" style={{ borderColor: '#D4A01766', backgroundColor: '#D4A0170D' }}>
          <Lock size={22} color="#D4A017" />
          <Text className="text-textPrimary font-bold text-sm mt-2 text-center">Enterprise feature</Text>
          <Text className="text-textMuted text-xs mt-1 text-center">
            Grading new topics is available on the Enterprise plan (token-based).
          </Text>
        </View>
      ) : (
        <>
          <View className="flex-row items-center bg-surface rounded-xl px-4 py-3 border border-border mb-3">
            <Sparkles size={18} color="#D4A017" />
            <TextInput
              value={topic}
              onChangeText={setTopic}
              placeholder="Enter any word or topic to grade…"
              placeholderTextColor="#9AA3B0"
              className="flex-1 ml-3 text-base"
              style={{ color: '#1A1A2E' }}
            />
          </View>

          <View className="rounded-xl border p-4" style={{ borderColor: '#D4A01766', backgroundColor: '#D4A0170D' }}>
            <View className="flex-row items-center gap-2 mb-1">
              <Sparkles size={15} color="#D4A017" />
              <Text className="text-textPrimary text-sm font-bold">Proposed Gradient Score</Text>
              <Text className="text-textMuted text-xs ml-auto">{tokens} tokens left</Text>
            </View>
            <Text className="text-textMuted text-xs mb-3">
              Generates a live proposed score + research for a topic not in our data — uses 1 query token.
            </Text>
            <Button
              variant="enterprise"
              size="md"
              loading={busy}
              disabled={!topic.trim() || tokens <= 0}
              onPress={grade}
            >
              {tokens <= 0
                ? 'No tokens remaining'
                : topic.trim()
                  ? `Grade "${topic.trim()}" · 1 token`
                  : 'Type a topic to grade'}
            </Button>
            {msg && <Text className="text-error text-xs mt-2">{msg}</Text>}
            {busy && (
              <Text className="text-textMuted text-[11px] mt-2">
                Researching and scoring across sources… this can take ~30s.
              </Text>
            )}
          </View>

          <Text className="text-textMuted text-[10px] leading-4 mt-3">
            Coming soon: AI internet search that researches brand-new terms and shows the evidence behind each
            proposed score.
          </Text>
        </>
      )}
    </View>
  );
}
