import { useState } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator, LayoutAnimation, Platform, UIManager } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { ChevronLeft, ChevronDown, Bell, ArrowRight } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { Disclaimer } from '../../../components/ui/Disclaimer';
import { Rise } from '../../../components/ui/Rise';
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
import { ageLabel, stageColor, stageLabel, scoreGap, actionFor, breakdownGroups, SCORE_ROLES, gapBandIndex, tierColourHex, maturityColourHex, titleCaseTopic } from '../../../lib/signals';

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

const MATURITY_EXPLAIN: Record<string, string> = {
  NEW: 'First cycles scored — the gradient is still stabilizing on this topic.',
  EMERGING: 'Gaining across cycles; calibration is still building confidence.',
  ESTABLISHED: 'A long-running topic with a permanent expert base. The gradient reflects its steady home, not a new surge — so scores are discounted to avoid over-reading an old, well-known topic as breaking news.',
  RESURGENT: 'A previously-established topic that is re-accelerating — worth a closer look.',
  MONITORING: 'Low-intensity background topic, below the emerging threshold.',
};

// Minimalist collapsible section — everything deep lives behind one of these,
// closed by default. Progressive disclosure: the screen stays calm until the
// reader chooses to go deeper. (Touch-only: tap to toggle, no hover.)
function Section({ title, hint, defaultOpen = false, children }: {
  title: string; hint?: string; defaultOpen?: boolean; children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const toggle = () => {
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
      <TouchableOpacity onPress={toggle} activeOpacity={0.7} className="flex-row items-center py-4">
        <View className="flex-1">
          <Text style={{ color: '#16264A', fontSize: 14, fontWeight: '800', letterSpacing: 0.4 }}>{title}</Text>
          {!!hint && <Text style={{ color: '#9A9AA2', fontSize: 12, marginTop: 3 }}>{hint}</Text>}
        </View>
        <ChevronDown size={18} color="#C7C7CE" style={{ transform: [{ rotate: open ? '180deg' : '0deg' }] }} />
      </TouchableOpacity>
      {open && <Rise duration={420} distance={10}><View className="pb-5">{children}</View></Rise>}
    </View>
  );
}

export default function SignalDetail() {
  const { id, from } = useLocalSearchParams<{ id: string; from?: string }>();
  const router = useRouter();
  const goBack = () => { if (from) router.replace(from as any); else router.back(); };
  const backLabel = from === '/profile/watchlists' ? 'Watchlists' : from === '/alerts' ? 'Alerts' : from === '/profile/favorites' ? 'Favorites' : 'Trends';
  const { signal, isLoading } = useSignal(String(id));

  if (isLoading) {
    return (
      <Screen>
        <TouchableOpacity onPress={goBack} className="mt-4 mb-8 self-start">
          <ChevronLeft size={24} color="#3C4663" />
        </TouchableOpacity>
        <ActivityIndicator size="large" color="#1B3066" style={{ marginTop: 40 }} />
      </Screen>
    );
  }

  if (!signal) {
    return (
      <Screen>
        <TouchableOpacity onPress={goBack} className="mt-4 mb-8 self-start">
          <ChevronLeft size={24} color="#3C4663" />
        </TouchableOpacity>
        <Text className="text-textMuted text-center mt-20">Signal not found.</Text>
      </Screen>
    );
  }

  const color = stageColor(signal.stage);
  const gap = scoreGap(signal);
  const action = actionFor(signal);
  const groups = breakdownGroups(signal);
  const agree = gapBandIndex(gap) === 0;
  const n = signal.nowTrending ?? 0;

  return (
    <Screen scroll>
      <TouchableOpacity onPress={goBack} className="mt-4 mb-5 self-start flex-row items-center gap-1" activeOpacity={0.6}>
        <ChevronLeft size={22} color="#3C4663" />
        <Text className="text-textSecondary text-sm font-semibold">{backLabel}</Text>
      </TouchableOpacity>

      {/* ── Header: the essentials only ── */}
      <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '800', letterSpacing: 2 }}>SIGNAL INTEL</Text>
      <Text style={{ color: '#16264A', fontSize: 28, fontWeight: '800', letterSpacing: -0.6, marginTop: 6, lineHeight: 35 }}>
        {titleCaseTopic(signal.topic)}
      </Text>
      <View className="flex-row items-center gap-2 mt-3">
        <View className="rounded-full px-2.5 py-1" style={{ backgroundColor: `${color}1A` }}>
          <Text style={{ color, fontSize: 12, fontWeight: '800', letterSpacing: 0.6 }}>{stageLabel(signal.stage)}</Text>
        </View>
        <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '500' }}>
          {signal.platforms?.[0] ?? 'Multi-Platform'} · {ageLabel(signal.createdAt)}
        </Text>
      </View>

      {/* Legal disclaimer — top of the panel (founder rule: top AND bottom) */}
      <Disclaimer className="mt-3 mb-0 px-0 text-left" />

      {/* ── Primary card: the two scores + gap + the one-line read ── */}
      <View className="bg-card rounded-3xl mt-5 px-5 pt-6 pb-5"
            style={{ shadowColor: '#0C1B3A', shadowOpacity: 0.06, shadowRadius: 14, shadowOffset: { width: 0, height: 8 }, elevation: 3 }}>
        <View className="flex-row justify-around items-start">
          <View className="items-center">
            <GradientScoreRing score={signal.detection} color={SCORE_ROLES.detection.color} size="lg" caption="/100" />
            <Text style={{ color: '#16264A', fontSize: 12, fontWeight: '800', marginTop: 8, letterSpacing: 0.5 }}>DETECTION</Text>
            <Text style={{ color: '#9A9AA2', fontSize: 12 }}>{SCORE_ROLES.detection.falsePositive}</Text>
          </View>
          <View className="items-center">
            <GradientScoreRing score={signal.confidence} color={SCORE_ROLES.confidence.color} size="lg" caption="/100" />
            <Text style={{ color: '#16264A', fontSize: 12, fontWeight: '800', marginTop: 8, letterSpacing: 0.5 }}>CONFIDENCE</Text>
            <Text style={{ color: '#9A9AA2', fontSize: 12 }}>{SCORE_ROLES.confidence.falsePositive}</Text>
          </View>
        </View>
        <View className="rounded-2xl px-4 py-3 mt-5" style={{ backgroundColor: agree ? '#2E7D5B0F' : '#B112260D' }}>
          <Text style={{ color: agree ? '#246B4A' : '#B11226', fontSize: 14, fontWeight: '800' }}>
            {gap}-point gap — {agree ? `scores aligned at ${stageLabel(signal.stage)}` : 'early stage, confirmation building'}
          </Text>
          <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 20, marginTop: 6, fontWeight: '500' }}>
            {action.title}{action.body ? ` ${action.body}` : ''}
          </Text>
        </View>
      </View>

      {/* ── Everything deeper: collapsed by default ── */}
      <View className="mt-5">
        <Section title={`Now TrendIn demand · N ${n}`} hint="On-platform query demand for this topic">
          <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 20, fontWeight: '500' }}>
            How often Now TrendIn users have asked the engine about this topic — real institutional
            curiosity no public source can see. The headline scores above stay demand-free.
          </Text>
          {n > 0 && signal.nowTrendingGradientDetection != null && signal.nowTrendingGradientConfidence != null && (
            <View className="flex-row gap-3 mt-4">
              <View className="flex-1 rounded-2xl p-3" style={{ borderColor: '#2A5B9E33', backgroundColor: '#2A5B9E0A' }}>
                <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '700', letterSpacing: 0.5 }}>DETECTION + N</Text>
                <Text style={{ color: '#2A5B9E', fontSize: 22, fontWeight: '800' }}>{Math.round(signal.nowTrendingGradientDetection)}</Text>
              </View>
              <View className="flex-1 rounded-2xl p-3" style={{ borderColor: '#2E7D5B33', backgroundColor: '#2E7D5B0A' }}>
                <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '700', letterSpacing: 0.5 }}>CONFIDENCE + N</Text>
                <Text style={{ color: '#2E7D5B', fontSize: 22, fontWeight: '800' }}>{Math.round(signal.nowTrendingGradientConfidence)}</Text>
              </View>
            </View>
          )}
          {n === 0 && (
            <Text style={{ color: '#9A9AA2', fontSize: 12, marginTop: 8, fontStyle: 'italic' }}>
              No on-platform demand has registered yet — N rises as users query about it.
            </Text>
          )}
          <View className="mt-3"><ConvergenceBadge topicKey={signal.id} /></View>
        </Section>

        <Section title="Why the two scores differ" hint="Detection leads speed, Confidence leads precision">
          {!!signal.gapMeaning && (
            <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 20, fontWeight: '500', marginBottom: 12 }}>{signal.gapMeaning}</Text>
          )}
          <DualScoreAnalysis signal={signal} />
          <View className="h-4" />
          <WhyScoresDiverge signal={signal} />
        </Section>

        {(!!signal.why || !!signal.whatToWatch) && (
          <Section title="What this means" hint="Why it matters and what to watch">
            {!!signal.why && (
              <>
                <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '700', letterSpacing: 1, marginBottom: 4 }}>WHY THIS MATTERS</Text>
                <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 22, marginBottom: 16 }}>{signal.why}</Text>
              </>
            )}
            {!!signal.whatToWatch && (
              <>
                <Text style={{ color: '#9A9AA2', fontSize: 12, fontWeight: '700', letterSpacing: 1, marginBottom: 4 }}>WHAT TO WATCH</Text>
                <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 22 }}>{signal.whatToWatch}</Text>
              </>
            )}
          </Section>
        )}

        <Section title="Score breakdown" hint="The components behind the score">
          {groups.map((g) => (
            <View key={g.title} className="mb-4">
              <Text style={{ color: '#16264A', fontSize: 12, fontWeight: '700', marginBottom: 8 }}>{g.title}</Text>
              {g.items.map((it) => (
                <View key={it.label} className="mb-2.5">
                  <View className="flex-row justify-between mb-1">
                    <Text style={{ color: '#3C4663', fontSize: 12, flex: 1, paddingRight: 8 }}>{it.label}</Text>
                    <Text style={{ color: '#16264A', fontSize: 12, fontWeight: '700' }}>
                      {it.value}{it.conf != null ? <Text style={{ color: '#9A9AA2' }}> / {it.conf}</Text> : null}
                    </Text>
                  </View>
                  <View style={{ height: 5, borderRadius: 980, backgroundColor: '#EDEDED', overflow: 'hidden' }}>
                    <View style={{ width: `${Math.max(0, Math.min(100, it.value))}%`, height: '100%', backgroundColor: color }} />
                  </View>
                </View>
              ))}
            </View>
          ))}
        </Section>

        <Section title="Research & variations" hint="Plain-English context for this trend">
          {!!signal.scoreExplanation && (
            <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 20, marginBottom: 12, fontWeight: '500' }}>{signal.scoreExplanation}</Text>
          )}
          <TopicVariationMap variations={signal.variations} />
          <TopicResearch topicKey={signal.id} topicName={signal.topic} />
          <View className="h-3" />
          <ResearchHistory topicKey={signal.id} />
        </Section>

        <Section title="Deeper signals" hint="Cross-platform & private-conversation indicators">
          <XSignalPanel topic={signal.topic} />
          <View className="h-4" />
          <DarkMatterPanel signal={signal} />
        </Section>

        {!!signal.maturityClass && (
          <Section title="Topic maturity" hint={signal.maturityBadge || signal.maturityClass}>
            <Text style={{ color: '#3C4663', fontSize: 14, lineHeight: 20, fontWeight: '500' }}>
              {signal.maturityReason || MATURITY_EXPLAIN[signal.maturityClass] || ''}
            </Text>
            <Text style={{ color: '#9A9AA2', fontSize: 12, marginTop: 8 }}>
              Lifecycle stage from the calibration engine · re-evaluated each scoring cycle
            </Text>
          </Section>
        )}

        <Section title="How scoring works" hint="The methodology behind the Gradient Score">
          <MethodologyExplainer />
        </Section>

        <Section title="Scoring history" hint="How this score has moved over time">
          <ScoringHistory signal={signal} />
        </Section>
      </View>

      {/* Primary action */}
      <TouchableOpacity
        onPress={() => router.push({ pathname: '/alerts', params: { topic: signal.topic, key: signal.id } })}
        activeOpacity={0.9}
        className="flex-row items-center justify-center mt-7 mb-2"
        style={{ backgroundColor: '#16264A', borderRadius: 980, paddingVertical: 16 }}
      >
        <Bell size={17} color="#FFFFFF" />
        <Text style={{ color: '#FFFFFF', fontSize: 14, fontWeight: '800', letterSpacing: 0.5, marginLeft: 8 }}>Set an alert for this topic</Text>
        <ArrowRight size={15} color="#F0758A" style={{ marginLeft: 8 }} />
      </TouchableOpacity>

      <Text style={{ color: '#9A9AA2', fontSize: 12, textAlign: 'center', marginTop: 6, lineHeight: 15 }}>
        Signal analysis only — not financial, investment, or legal advice. You decide any action.
      </Text>
      {/* Legal disclaimer — bottom of the panel */}
      <Disclaimer />
    </Screen>
  );
}
