import React, { useState } from 'react';
import { View, Text, TextInput } from 'react-native';
import { GraduationCap, Sparkles, Lock } from 'lucide-react-native';
import { Button } from '../ui/Button';
import { GradientScoreRing } from '../ui/GradientScoreRing';
import { useAuthStore } from '../../store/auth.store';
import { queryApi } from '../../lib/api';
import { GAP_BANDS, gapBandIndex } from '../../lib/signals';

const STAGE_COLOR: Record<string, string> = {
  BREAKOUT: '#00C896', STRONG: '#2D7EEF', EMERGING: '#D4A017', WATCHING: '#E85A1E', MONITORING: '#94A3B8',
};

interface Proposed {
  detection_score: number; confidence_score: number; heisenberg_gap: number;
  holistic_detection: number; holistic_confidence: number;
  gradient_strength: number; platform_diversity: number; inertia: number;
  dark_matter: number; persistence: number;
  stage: string; action: string; reasoning: string; research: string; citations: string[];
}

// GRADE — AI internet-search a topic NOT in our data → PROPOSED Gradient Score
// + research/citations. Perplexity researches the open web; Claude synthesizes
// the score in our framework. Token-metered (1 token). Enterprise only.
export function GradeTool() {
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);
  const [topic, setTopic] = useState('');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [result, setResult] = useState<Proposed | null>(null);

  const canGrade = !!user?.tier;            // any plan; metered by grade credits
  const tokens = user?.gradeTokens ?? 0;    // monthly AI-grade credits

  const grade = async () => {
    setMsg(null);
    setResult(null);
    setBusy(true);
    try {
      const d: any = await queryApi.grade(topic.trim());
      if (user) updateUser({ ...user, gradeTokens: d?.gradeTokens ?? tokens });
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
          <Text className="text-textPrimary font-bold text-sm mt-2 text-center">Choose a plan</Text>
          <Text className="text-textMuted text-xs mt-1 text-center">
            AI grading is included on every plan with a monthly credit allowance. Select a membership to start.
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
              <Text className="text-textMuted text-xs ml-auto">{tokens} grade credits left</Text>
            </View>
            <Text className="text-textMuted text-xs mb-3">
              Researches the open web and proposes a score with citations — uses 1 grade credit.
            </Text>
            <Button
              variant="enterprise"
              size="md"
              loading={busy}
              disabled={!topic.trim() || tokens <= 0}
              onPress={grade}
            >
              {tokens <= 0 ? 'No grade credits remaining this month' : topic.trim() ? `Grade "${topic.trim()}" · 1 credit` : 'Type a topic to grade'}
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

              {/* Gap interpretation — same bands as a regular signal */}
              {(() => {
                const gap = Math.abs(Math.round(result.heisenberg_gap ?? (result.detection_score - result.confidence_score)));
                const band = GAP_BANDS[gapBandIndex(gap)];
                return (
                  <View className="rounded-xl px-3 py-2 mb-3 border" style={{ borderColor: `${band.color}55`, backgroundColor: `${band.color}0F` }}>
                    <Text className="text-sm font-bold" style={{ color: band.color }}>{gap}-point gap — {band.label}</Text>
                  </View>
                );
              })()}

              {/* Claude's holistic read, shown alongside the engine-calibrated score */}
              <Text className="text-textMuted text-[11px] mb-3">
                Engine-calibrated above · AI holistic estimate: DET {Math.round(result.holistic_detection)} · CONF {Math.round(result.holistic_confidence)}
              </Text>

              {!!result.action && (
                <Text className="text-base font-black mb-1" style={{ color: STAGE_COLOR[result.stage] ?? '#1A1A2E' }}>{result.action}</Text>
              )}
              {!!result.reasoning && <Text className="text-textSecondary text-[13px] leading-5 mb-3">{result.reasoning}</Text>}

              {/* Signal Quality — component breakdown (same components as a signal) */}
              <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Signal quality</Text>
              <View className="gap-2 mb-3">
                <Bar label="Niche Concentration" value={result.gradient_strength} />
                <Bar label="Platform Diversity" value={result.platform_diversity} />
                <Bar label="Momentum" value={result.inertia} />
                <Bar label="Dark Matter" value={result.dark_matter} />
                <Bar label="Persistence" value={result.persistence} />
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
                      selectable
                      className="text-textMuted text-[11px] mb-1"
                      numberOfLines={1}
                    >
                      • {c}
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

function Bar({ label, value }: { label: string; value: number }) {
  const v = Math.max(0, Math.min(100, Math.round(value)));
  return (
    <View>
      <View className="flex-row justify-between mb-1">
        <Text className="text-textSecondary text-sm">{label}</Text>
        <Text className="text-textPrimary text-sm font-semibold">{v}</Text>
      </View>
      <View className="h-1.5 rounded-full bg-border overflow-hidden">
        <View style={{ width: `${v}%`, backgroundColor: '#D4A017' }} className="h-full rounded-full" />
      </View>
    </View>
  );
}
