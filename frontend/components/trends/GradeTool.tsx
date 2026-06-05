import React, { useState } from 'react';
import { View, Text, TextInput, Linking } from 'react-native';
import { GraduationCap, Sparkles, Lock, ExternalLink } from 'lucide-react-native';
import { Button } from '../ui/Button';
import { GradientScoreRing } from '../ui/GradientScoreRing';
import { useAuthStore } from '../../store/auth.store';
import { TierID, canAccess } from '../../constants/tiers';
import { queryApi } from '../../lib/api';

const STAGE_COLOR: Record<string, string> = {
  BREAKOUT: '#00C896', STRONG: '#2D7EEF', EMERGING: '#D4A017', WATCHING: '#E85A1E', MONITORING: '#94A3B8',
};

interface Proposed {
  detection_score: number; confidence_score: number; gradient_strength: number;
  platform_diversity: number; inertia: number; stage: string; action: string;
  reasoning: string; research: string; citations: string[];
}

// GRADE — AI internet-search a topic NOT in our data → PROPOSED Gradient Score
// + research/citations. Perplexity researches the open web; Claude synthesizes
// the score in our framework. Token-metered (1 token). Enterprise only.
export function GradeTool() {
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const [topic, setTopic] = useState('');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [result, setResult] = useState<Proposed | null>(null);

  const canGrade = canAccess(tier, 'canQueryNew'); // Enterprise only
  const tokens = user?.tokensRemaining ?? 0;

  const grade = async () => {
    setMsg(null);
    setResult(null);
    setBusy(true);
    try {
      const d: any = await queryApi.grade(topic.trim());
      if (user) updateUser({ ...user, tokensRemaining: d?.tokensRemaining ?? tokens });
      if (d?.available && d?.proposed) {
        setResult(d as Proposed);
      } else {
        setMsg(d?.detail ?? d?.reason ?? 'AI grading is not available yet.');
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
        Propose a Gradient Score for a topic that isn&apos;t in our trends yet. AI researches the open web and
        returns a proposed score with the evidence behind it.
      </Text>

      {!canGrade ? (
        <View className="rounded-xl border p-5 items-center" style={{ borderColor: '#D4A01766', backgroundColor: '#D4A0170D' }}>
          <Lock size={22} color="#D4A017" />
          <Text className="text-textPrimary font-bold text-sm mt-2 text-center">Enterprise feature</Text>
          <Text className="text-textMuted text-xs mt-1 text-center">
            AI grading of new topics is available on the Enterprise plan (token-based).
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

          <View className="rounded-xl border p-4 mb-4" style={{ borderColor: '#D4A01766', backgroundColor: '#D4A0170D' }}>
            <View className="flex-row items-center gap-2 mb-1">
              <Sparkles size={15} color="#D4A017" />
              <Text className="text-textPrimary text-sm font-bold">AI Proposed Gradient Score</Text>
              <Text className="text-textMuted text-xs ml-auto">{tokens} tokens left</Text>
            </View>
            <Text className="text-textMuted text-xs mb-3">
              Researches the open web and proposes a score with citations — uses 1 query token.
            </Text>
            <Button
              variant="enterprise"
              size="md"
              loading={busy}
              disabled={!topic.trim() || tokens <= 0}
              onPress={grade}
            >
              {tokens <= 0 ? 'No tokens remaining' : topic.trim() ? `Grade "${topic.trim()}" · 1 token` : 'Type a topic to grade'}
            </Button>
            {msg && <Text className="text-error text-xs mt-2">{msg}</Text>}
            {busy && <Text className="text-textMuted text-[11px] mt-2">Researching the web and scoring… ~20–40s.</Text>}
          </View>

          {result && (
            <View className="bg-surface rounded-2xl border border-border p-5 mb-4">
              <View className="flex-row items-center justify-between mb-1">
                <Text className="text-textMuted text-[10px] font-bold tracking-widest uppercase">Proposed · AI estimate</Text>
                <View className="px-2.5 py-1 rounded-full" style={{ backgroundColor: `${STAGE_COLOR[result.stage] ?? '#94A3B8'}1A` }}>
                  <Text className="text-[10px] font-bold" style={{ color: STAGE_COLOR[result.stage] ?? '#94A3B8' }}>{result.stage}</Text>
                </View>
              </View>

              <View className="flex-row justify-around items-start mt-2 mb-3">
                <View className="items-center">
                  <GradientScoreRing score={Math.round(result.detection_score)} color="#2D7EEF" size="md" caption="/100" />
                  <Text className="text-textPrimary text-xs font-bold mt-2">DETECTION</Text>
                </View>
                <View className="items-center">
                  <GradientScoreRing score={Math.round(result.confidence_score)} color="#00C896" size="md" caption="/100" />
                  <Text className="text-textPrimary text-xs font-bold mt-2">CONFIDENCE</Text>
                </View>
              </View>

              {!!result.action && (
                <Text className="text-base font-black mb-1" style={{ color: STAGE_COLOR[result.stage] ?? '#1A1A2E' }}>{result.action}</Text>
              )}
              {!!result.reasoning && <Text className="text-textSecondary text-[13px] leading-5 mb-3">{result.reasoning}</Text>}

              <View className="flex-row flex-wrap gap-x-5 gap-y-1 mb-3">
                <Metric label="Niche concentration" value={result.gradient_strength} />
                <Metric label="Platform diversity" value={result.platform_diversity} />
                <Metric label="Momentum" value={result.inertia} />
              </View>

              {!!result.research && (
                <>
                  <Text className="text-textSecondary text-xs uppercase tracking-wider mb-1">Research</Text>
                  <Text className="text-textMuted text-[12px] leading-5 mb-3">{result.research}</Text>
                </>
              )}

              {Array.isArray(result.citations) && result.citations.length > 0 && (
                <>
                  <Text className="text-textSecondary text-xs uppercase tracking-wider mb-1">Sources</Text>
                  {result.citations.slice(0, 8).map((c, i) => (
                    <Text
                      key={i}
                      onPress={() => Linking.openURL(c)}
                      className="text-info text-[11px] mb-1"
                      numberOfLines={1}
                    >
                      <ExternalLink size={10} color="#2D7EEF" /> {c}
                    </Text>
                  ))}
                </>
              )}

              <Text className="text-textMuted text-[10px] leading-4 mt-3">
                Proposed score — an AI estimate from public web evidence, not a measured engine score.
              </Text>
            </View>
          )}
        </>
      )}
    </View>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <View>
      <Text className="text-textPrimary text-base font-black">{Math.round(value)}</Text>
      <Text className="text-textMuted text-[9px] font-bold uppercase tracking-wide">{label}</Text>
    </View>
  );
}
