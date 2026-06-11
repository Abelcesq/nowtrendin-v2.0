import { useState } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ChevronLeft, ChevronDown, ChevronUp, Bell, Flame } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { Button } from '../../../components/ui/Button';
import { GradientScoreRing } from '../../../components/ui/GradientScoreRing';
import { DualScoreAnalysis } from '../../../components/trends/DualScoreAnalysis';
import { WhyScoresDiverge } from '../../../components/trends/WhyScoresDiverge';
import { ScoringHistory } from '../../../components/trends/ScoringHistory';
import { ResearchHistory } from '../../../components/trends/ResearchHistory';
import { TopicResearch } from '../../../components/trends/TopicResearch';
import { TopicVariationMap } from '../../../components/trends/TopicVariationMap';
import { DarkMatterPanel } from '../../../components/trends/DarkMatterPanel';
import { MethodologyExplainer } from '../../../components/trends/MethodologyExplainer';
import { XSignalPanel } from '../../../components/trends/XSignalPanel';
import { ConvergenceBadge } from '../../../components/trends/ConvergenceBadge';
import { useSignal } from '../../../hooks/useSignals';
import { ageLabel, stageColor, scoreGap, actionFor, breakdownGroups, SCORE_ROLES, gapBandIndex, tierColourHex, maturityColourHex } from '../../../lib/signals';

// Plain-English fallback for each maturity class (used when the engine's live
// maturity_reason is absent). Explains what the lifecycle stage means for the score.
const MATURITY_EXPLAIN: Record<string, string> = {
  NEW: 'First cycles scored — the gradient is still stabilizing on this topic.',
  EMERGING: 'Gaining across cycles; calibration is still building confidence.',
  ESTABLISHED: 'A long-running topic with a permanent expert base. The gradient reflects its steady home, not a new surge — so scores are discounted to avoid over-reading an old, well-known topic as breaking news.',
  RESURGENT: 'A previously-established topic that is re-accelerating — worth a closer look.',
  MONITORING: 'Low-intensity background topic, below the emerging threshold.',
};

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
  // Use the SAME 0–15 threshold as the Gap Interpretation table (gapBandIndex 0)
  // so the headline can't contradict the table on the same screen.
  const agree = gapBandIndex(gap) === 0;

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-4 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#5B6472" />
        <Text className="text-textSecondary text-sm">Signal Intel</Text>
      </TouchableOpacity>

      <Text className="text-textMuted text-[10px] font-bold tracking-widest uppercase">Now TrendIn · Signal Intel</Text>
      <Text className="text-textPrimary text-3xl font-bold mt-0.5">{signal.topic}</Text>

      {/* Topic maturity — LIVE calibration lifecycle (NEW / EMERGING /
          ESTABLISHED / RESURGENT / MONITORING). Updates each scoring cycle.
          Shows the engine's live maturity_reason so it's clear what the
          classification means for THIS topic, not a static label. */}
      {!!signal.maturityClass && (
        <View className="rounded-xl border border-border bg-surface p-3 mt-2">
          <View className="flex-row items-center gap-2">
            <View
              className="rounded-full px-2.5 py-1"
              style={{ backgroundColor: `${maturityColourHex(signal.maturityClass)}1A` }}
            >
              <Text className="text-[10px] font-bold" style={{ color: maturityColourHex(signal.maturityClass) }}>
                {signal.maturityBadge || signal.maturityClass}
              </Text>
            </View>
            <Text className="text-textMuted text-[10px] font-bold uppercase tracking-wider">
              Topic maturity
            </Text>
          </View>
          <Text className="text-textSecondary text-[12px] leading-4 mt-1.5">
            {signal.maturityReason || MATURITY_EXPLAIN[signal.maturityClass] || ''}
          </Text>
          <Text className="text-textMuted text-[10px] mt-1">
            Lifecycle stage from the calibration engine · re-evaluated each scoring cycle
          </Text>
        </View>
      )}

      {/* AI tier badge — only for taxonomy-recognized AI topics */}
      {!!signal.aiTierLabel && (
        <View
          className="self-start rounded-full px-2.5 py-1 mt-1.5"
          style={{ backgroundColor: `${tierColourHex(signal.aiTierColour)}1A` }}
        >
          <Text className="text-[10px] font-bold" style={{ color: tierColourHex(signal.aiTierColour) }}>
            {signal.aiTierLabel}{signal.aiVelocity ? ` · ${signal.aiVelocity}` : ''}
          </Text>
        </View>
      )}
      <Text className="text-textMuted text-sm mb-4">
        {signal.totalMentions ?? 0} signals · {signal.platforms?.[0] ?? 'Multi-Platform'} · {ageLabel(signal.createdAt)}
      </Text>

{/* (N — Now TrendIn — section moved below, just above Dual Score Analysis) */}

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
            {gap}-point gap — {agree ? `scores aligned at ${signal.stage}` : 'early stage, confirmation building'}
          </Text>
          {!!signal.gapMeaning && (
            <Text className="text-textMuted text-xs mt-1 leading-5">{signal.gapMeaning}</Text>
          )}
        </View>
      </View>

      {/* AI score explanation — why this taxonomy topic scores where it does */}
      {!!signal.scoreExplanation && (
        <View className="rounded-xl px-4 py-3 mb-5 border border-border bg-surface">
          <Text className="text-textSecondary text-sm leading-5">{signal.scoreExplanation}</Text>
        </View>
      )}

      {/* AI Variation Map — "AI" umbrella vs specific variations like "agentic coding" */}
      <TopicVariationMap variations={signal.variations} />

      {/* Research — AI plain-English explanation of what this trend means */}
      <TopicResearch topicKey={signal.id} topicName={signal.topic} />

      {/* Now TrendIn (N component) — internal on-platform query demand.
          Positioned just above the Dual Score Analysis so the reader sees
          our headline metric before reading about Detection/Confidence gap
          mechanics. Always rendered — when N=0 we explain why (no demand yet). */}
      <View className="rounded-2xl p-4 mb-5 border"
            style={{ borderColor: '#EE6A2A55', backgroundColor: '#EE6A2A0C' }}>
        <View className="flex-row items-center gap-2 mb-2">
          <Flame size={16} color="#EE6A2A" />
          <View className="flex-row items-baseline">
            <Text className="text-base font-black" style={{ color: '#EE6A2A' }}>Now</Text>
            <Text className="text-base font-black" style={{ color: '#B5341B' }}>TrendIn</Text>
            <Text className="text-textSecondary text-sm font-semibold ml-2">
              · N component
            </Text>
          </View>
          <View className="flex-1" />
          <Text className="text-2xl font-black" style={{ color: '#EE6A2A' }}>
            {signal.nowTrending ?? 0}
          </Text>
        </View>
        <Text className="text-textSecondary text-[12px] leading-4 mb-2">
          The on-platform demand signal — how often Now TrendIn users have been asking the
          engine about this topic. Captures real institutional curiosity that no public
          source can see.
        </Text>
        {/* The "Now Trending Gradient Score" — a separate, demand-inclusive read
            unique to the trend signal section. The headline Detection/Confidence
            stay N-free (external-world only); this shows where the score would land
            if internal demand (N) were folded in as an extra factor. The weighting
            is computed server-side and never exposed (internal trade secret). */}
        {signal.nowTrending != null && signal.nowTrending > 0 &&
         signal.nowTrendingGradientDetection != null &&
         signal.nowTrendingGradientConfidence != null && (
          <View className="mt-3 pt-3 border-t" style={{ borderColor: '#EE6A2A33' }}>
            <View className="flex-row items-center justify-between mb-1">
              <Text className="text-[10px] font-bold tracking-widest uppercase" style={{ color: '#EE6A2A' }}>
                Now Trending Gradient Score
              </Text>
              <View className="px-2 py-0.5 rounded-full" style={{ backgroundColor: '#EE6A2A1A' }}>
                <Text className="text-[9px] font-bold" style={{ color: '#EE6A2A' }}>SEPARATE · DEMAND-INCLUSIVE</Text>
              </View>
            </View>
            <Text className="text-textMuted text-[11px] leading-4 mb-2">
              A separate, what-if read: where the score would land if on-platform demand (N)
              were folded in. The headline Detection/Confidence above stay N-free (external
              world only) — this demand-inclusive view is shown only here, never sold as the
              Gradient Score.
            </Text>
            <View className="flex-row gap-3">
              <View className="flex-1 rounded-xl border p-2.5" style={{ borderColor: '#2D7EEF33', backgroundColor: '#2D7EEF0A' }}>
                <Text className="text-textMuted text-[9px] font-bold tracking-wider">DETECTION + N</Text>
                <Text className="text-xl font-black" style={{ color: '#2D7EEF' }}>{Math.round(signal.nowTrendingGradientDetection)}</Text>
              </View>
              <View className="flex-1 rounded-xl border p-2.5" style={{ borderColor: '#00C89633', backgroundColor: '#00C8960A' }}>
                <Text className="text-textMuted text-[9px] font-bold tracking-wider">CONFIDENCE + N</Text>
                <Text className="text-xl font-black" style={{ color: '#00C896' }}>{Math.round(signal.nowTrendingGradientConfidence)}</Text>
              </View>
            </View>
            {signal.nowTrendingGradientDemandDriven && (
              <Text className="text-[10px] leading-4 mt-2" style={{ color: '#B5341B' }}>
                ⚠ Substantially driven by internal demand — external confirmation is limited
                for this topic. N's weight is reduced here so demand alone can't lift the score.
              </Text>
            )}
          </View>
        )}

        {(!signal.nowTrending || signal.nowTrending === 0) && (
          <View className="mt-2 pt-2 border-t" style={{ borderColor: '#EE6A2A33' }}>
            <Text className="text-textMuted text-[11px] italic">
              No on-platform demand has registered for this topic yet — N will rise as
              users query about it.
            </Text>
          </View>
        )}

        {/* Signal Convergence — downstream directional validation of the score's
            direction against raw volume + niche concentration. Lazy-loaded;
            independent of N (non-circular). */}
        <ConvergenceBadge topicKey={signal.id} />
      </View>

      {/* Dual Score Analysis (gap bands + who uses which score) */}
      <DualScoreAnalysis signal={signal} />
      <View className="h-5" />

      {/* Research history (lazy) */}
      <ResearchHistory topicKey={signal.id} />
      <View className="h-4" />

      {/* X dual-role signal (lazy) */}
      <XSignalPanel topic={signal.topic} />
      <View className="h-4" />

      {/* Dark Matter signatures — inferred private-conversation indicators */}
      <DarkMatterPanel signal={signal} />

      {/* WHAT THIS MEANS (signal read — analysis only, not advice) */}
      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-2">Signal read</Text>
      <View className="rounded-2xl p-5 mb-2 border" style={{ borderColor: color, backgroundColor: `${color}10` }}>
        <Text className="text-2xl font-black mb-1" style={{ color }}>
          {action.title}
        </Text>
        {!!action.body && <Text className="text-textSecondary text-base leading-6">{action.body}</Text>}
        {!!signal.whatToDo?.detail && signal.whatToDo.detail !== action.body && (
          <Text className="text-textMuted text-sm leading-5 mt-2">{signal.whatToDo.detail}</Text>
        )}
      </View>
      <Text className="text-textMuted text-[10px] mb-5">
        Signal analysis only — not financial, investment, or legal advice. You decide any action.
      </Text>

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
        <WhyScoresDiverge signal={signal} />
      </View>

      {/* How the Gradient Score works (methodology — the 3 laws + Duality) */}
      <View className="mt-5">
        <MethodologyExplainer />
      </View>

      {/* Actual scoring history */}
      <View className="mt-5">
        <ScoringHistory signal={signal} />
      </View>

      <View className="mt-5 mb-2">
        <Button size="lg" icon={<Bell size={18} color="#FFFFFF" />} onPress={() => router.push({ pathname: '/alerts', params: { topic: signal.topic, key: signal.id } })}>
          Set Alert for this topic
        </Button>
      </View>
    </Screen>
  );
}
