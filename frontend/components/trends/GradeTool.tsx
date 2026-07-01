import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, TextInput, TouchableOpacity, ActivityIndicator, ScrollView } from 'react-native';
import { GraduationCap, Sparkles, Lock, Clock, Globe, Search, Plus } from 'lucide-react-native';
import { Button } from '../ui/Button';
import { GradientScoreRing } from '../ui/GradientScoreRing';
import { useAuthStore } from '../../store/auth.store';
import { queryApi } from '../../lib/api';
import { GAP_BANDS, gapBandIndex, titleCaseTopic } from '../../lib/signals';

const STAGE_COLOR: Record<string, string> = {
  BREAKOUT: '#2E7D5B', STRONG: '#2A5B9E', EMERGING: '#A8456A', MARGINAL: '#A8456A', WATCHING: '#A8456A', MONITORING: '#8A8F9C',
};

interface Proposed {
  detection_score: number; confidence_score: number; heisenberg_gap: number;
  holistic_detection: number; holistic_confidence: number;
  gradient_strength: number; platform_diversity: number; inertia: number;
  dark_matter: number; persistence: number;
  stage: string; action: string; reasoning: string; research: string; citations: string[];
  market_signal?: {
    ticker?: string; display?: string;
    market_gradient?: {
      detection: number; confidence: number; tier: string; gap: number;
      gap_state?: string; calibrating?: boolean; leverage_health?: number | null;
      interpretation?: string;
    };
  };
}

const MARKET_TIER_COLOR: Record<string, string> = {
  ELEVATED: '#B11226', ACTIVE: '#A8456A', BUILDING: '#A8456A', ROUTINE: '#2A5B9E', DORMANT: '#9A9AA2',
};
interface GradeRow {
  id: number; topic: string; detection: number; confidence: number;
  stage: string; createdAt: string; result?: any;
}

type Tab = 'new' | 'history' | 'graded';

function timeAgo(iso: string): string {
  const d = new Date(iso).getTime();
  const mins = Math.floor((Date.now() - d) / 60000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  const h = Math.floor(mins / 60);
  if (h < 24) return `${h}h ago`;
  const days = Math.floor(h / 24);
  if (days < 30) return `${days}d ago`;
  return new Date(iso).toLocaleDateString();
}

// GRADE — three tabs: New Grade (token-metered AI score), History (this member's
// past grades, 12 months, free), Graded (all members' graded topics, free).
export function GradeTool() {
  const user = useAuthStore((s) => s.user);
  const updateUser = useAuthStore((s) => s.updateUser);
  const [tab, setTab] = useState<Tab>('new');
  const [topic, setTopic] = useState('');
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [result, setResult] = useState<Proposed | null>(null);

  const canGrade = !!user?.tier;
  const tokens = user?.gradeTokens ?? 0;

  const grade = async () => {
    setMsg(null); setResult(null); setBusy(true);
    try {
      const d: any = await queryApi.grade(topic.trim());
      if (user) updateUser({ ...user, gradeTokens: d?.gradeTokens ?? tokens });
      if (d?.available && d?.proposed) setResult(d as Proposed);
      else setMsg(d?.detail ?? d?.reason ?? 'AI grading is not available yet.');
    } catch (err: any) {
      setMsg(err?.data?.detail ?? 'Grade failed. Try again.');
    } finally { setBusy(false); }
  };

  return (
    <View>
      <View className="flex-row items-center gap-2 mb-1">
        <GraduationCap size={20} color="#A8456A" />
        <Text className="text-textPrimary text-xl font-black">Grade a Topic</Text>
      </View>
      <Text className="text-textMuted text-[12px] leading-4 mb-3">
        Propose a Gradient Score for a topic that isn&apos;t in our trends yet. AI researches the open web and
        returns a proposed score with the evidence behind it.
      </Text>

      {/* Three tab icons — New Grade | History | Graded */}
      <View className="flex-row gap-2 mb-4">
        <TabBtn icon={<Plus size={15} color={tab === 'new' ? '#FFFFFF' : '#3C4663'} />} label="New Grade" active={tab === 'new'} onPress={() => setTab('new')} />
        <TabBtn icon={<Clock size={15} color={tab === 'history' ? '#FFFFFF' : '#3C4663'} />} label="History" active={tab === 'history'} onPress={() => setTab('history')} />
        <TabBtn icon={<Globe size={15} color={tab === 'graded' ? '#FFFFFF' : '#3C4663'} />} label="Graded" active={tab === 'graded'} onPress={() => setTab('graded')} />
      </View>

      {tab === 'new' && (
        !canGrade ? (
          <View className="rounded-xl p-5 items-center" style={{ borderColor: '#A8456A66', backgroundColor: '#A8456A0D' }}>
            <Lock size={22} color="#A8456A" />
            <Text className="text-textPrimary font-bold text-sm mt-2 text-center">Choose a plan</Text>
            <Text className="text-textMuted text-xs mt-1 text-center">AI grading is included on every plan with a monthly credit allowance.</Text>
          </View>
        ) : (
          <>
            <View className="flex-row items-center bg-card rounded-xl px-4 py-3 mb-3">
              <Sparkles size={18} color="#A8456A" />
              <TextInput value={topic} onChangeText={setTopic} placeholder="Enter any word or topic to grade…"
                placeholderTextColor="#9A9AA2" className="flex-1 ml-3 text-base" style={{ color: '#16264A' }} />
            </View>
            <Text className="text-textMuted text-[12px] leading-4 mb-3">Researches the open web and proposes a score with citations — uses 1 grade token.</Text>
            <TouchableOpacity onPress={grade} disabled={!topic.trim() || tokens <= 0 || busy} activeOpacity={0.9}
              className="flex-row items-center justify-center"
              style={{ backgroundColor: '#16264A', borderRadius: 980, paddingVertical: 15, opacity: (!topic.trim() || tokens <= 0) ? 0.5 : 1 }}>
              {busy ? <ActivityIndicator color="#FFFFFF" size="small" /> : <Sparkles size={16} color="#F0758A" />}
              <Text style={{ color: '#FFFFFF', fontSize: 12, fontWeight: '800', letterSpacing: 1, marginLeft: 8 }}>
                {tokens <= 0 ? 'NO GRADE TOKENS LEFT' : 'GRADE THIS TOPIC'}
              </Text>
              {tokens > 0 && <Text style={{ color: '#F0758A', fontSize: 12, fontWeight: '800', marginLeft: 8 }}>· 1 TOKEN</Text>}
            </TouchableOpacity>
            <Text className="text-textMuted text-[12px] font-bold tracking-wide text-center mt-2 uppercase">{tokens} grade tokens left</Text>
            {msg && <Text className="text-error text-xs mt-2 text-center">{msg}</Text>}
            {busy && <Text className="text-textMuted text-[12px] mt-2 text-center">Researching the web and scoring… ~20–40s.</Text>}
            <View className="mb-4" />
            {result && <ProposedCard result={result} />}
          </>
        )
      )}

      {tab === 'history' && <GradeList kind="history" />}
      {tab === 'graded' && <GradeList kind="graded" />}
    </View>
  );
}

function TabBtn({ icon, label, active, onPress }: { icon: React.ReactNode; label: string; active: boolean; onPress: () => void }) {
  return (
    <TouchableOpacity onPress={onPress} className="flex-1 flex-row items-center justify-center gap-1.5 rounded-xl py-2.5"
      style={{ backgroundColor: active ? '#A8456A' : '#FFFFFF', borderColor: active ? '#A8456A' : '#ECECEC' }}>
      {icon}
      <Text className="text-[12px] font-bold" style={{ color: active ? '#FFFFFF' : '#3C4663' }}>{label}</Text>
    </TouchableOpacity>
  );
}

// History (this member's grades) + Graded (all members') share one list component.
function GradeList({ kind }: { kind: 'history' | 'graded' }) {
  const [q, setQ] = useState('');
  const [rows, setRows] = useState<GradeRow[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async (query: string) => {
    setLoading(true);
    try {
      const d: any = kind === 'history' ? await queryApi.gradeHistory(query) : await queryApi.gradedAll(query);
      setRows(Array.isArray(d?.grades) ? d.grades : []);
    } catch { setRows([]); }
    finally { setLoading(false); }
  }, [kind]);

  useEffect(() => { load(''); }, [load]);
  // Debounced search.
  useEffect(() => {
    const t = setTimeout(() => load(q.trim()), 350);
    return () => clearTimeout(t);
  }, [q, load]);

  return (
    <View>
      <View className="flex-row items-center bg-card rounded-xl px-4 py-2.5 mb-3">
        <Search size={16} color="#9A9AA2" />
        <TextInput value={q} onChangeText={setQ}
          placeholder={kind === 'history' ? 'Search your graded topics…' : 'Search all graded topics…'}
          placeholderTextColor="#9A9AA2" className="flex-1 ml-2.5 text-sm" style={{ color: '#16264A' }} />
      </View>
      <Text className="text-textMuted text-[12px] mb-3">
        {kind === 'history'
          ? 'Your AI grades from the last 12 months. No token charge to view.'
          : 'Topics graded by Now TrendIn members across all plans. No token charge to view.'}
      </Text>

      {loading ? (
        <ActivityIndicator size="small" color="#A8456A" style={{ marginTop: 24 }} />
      ) : rows.length === 0 ? (
        <View className="bg-card rounded-2xl p-6 items-center">
          <Text className="text-textMuted text-sm text-center">
            {q ? 'No graded topics match your search.' : (kind === 'history' ? 'You haven’t graded any topics yet.' : 'No topics have been graded yet.')}
          </Text>
        </View>
      ) : (
        rows.map((g) => {
          const col = STAGE_COLOR[g.stage] ?? '#8A8F9C';
          return (
            <View key={g.id} className="bg-card rounded-xl p-3 mb-2">
              <View className="flex-row items-center justify-between">
                <Text className="text-textPrimary text-sm font-bold flex-1 pr-2" numberOfLines={1}>{titleCaseTopic(g.topic)}</Text>
                {!!g.stage && (
                  <View className="px-2 py-0.5 rounded-full" style={{ backgroundColor: `${col}1A` }}>
                    <Text className="text-[12px] font-bold" style={{ color: col }}>{g.stage}</Text>
                  </View>
                )}
              </View>
              <View className="flex-row items-center gap-3 mt-1">
                <Text className="text-[12px]" style={{ color: '#2A5B9E' }}>DET {Math.round(g.detection)}</Text>
                <Text className="text-[12px]" style={{ color: '#2E7D5B' }}>CONF {Math.round(g.confidence)}</Text>
                <Text className="text-textMuted text-[12px] ml-auto">{timeAgo(g.createdAt)}</Text>
              </View>
            </View>
          );
        })
      )}
    </View>
  );
}

function ProposedCard({ result }: { result: Proposed }) {
  const gap = Math.abs(Math.round(result.heisenberg_gap ?? (result.detection_score - result.confidence_score)));
  const band = GAP_BANDS[gapBandIndex(gap)];
  const ms = result.market_signal?.market_gradient;
  // Grade Agent: measured (already in our data pool) vs AI-proposed; live N score.
  const measured = (result as any).source === 'measured';
  const nScore = (result as any).n_score != null ? Math.round((result as any).n_score) : null;
  return (
    <>
    {/* MARKET read for companies — identical to the Market section, pulled from
        the full financial stack. Shown FIRST so a company's market read leads. */}
    {ms && (() => {
      const tc = MARKET_TIER_COLOR[ms.tier] ?? '#9A9AA2';
      return (
        <View className="bg-card rounded-2xl p-5 mb-4" style={{ borderColor: `${tc}44` }}>
          <View className="flex-row items-center justify-between mb-2">
            <Text className="text-[12px] font-bold tracking-widest uppercase" style={{ color: '#A8456A' }}>Market Signal · measured</Text>
            <View className="px-2.5 py-1 rounded-full" style={{ backgroundColor: `${tc}1A` }}>
              <Text className="text-[12px] font-bold" style={{ color: tc }}>{ms.calibrating ? 'CALIBRATING' : ms.tier}</Text>
            </View>
          </View>
          <View className="flex-row justify-around items-start mb-2">
            <View className="items-center">
              <GradientScoreRing score={Math.round(ms.detection)} color="#2A5B9E" size="md" caption="/100" />
              <Text className="text-textPrimary text-xs font-bold mt-2">DETECTION</Text>
              <Text className="text-textMuted text-[12px]">analysts + positioning</Text>
            </View>
            <View className="items-center">
              <GradientScoreRing score={Math.round(ms.confidence)} color="#2E7D5B" size="md" caption="/100" />
              <Text className="text-textPrimary text-xs font-bold mt-2">CONFIDENCE</Text>
              <Text className="text-textMuted text-[12px]">fundamentals + price</Text>
            </View>
          </View>
          {ms.leverage_health != null && (
            <Text className="text-[12px] font-bold text-center mb-1" style={{ color: '#2E7D5B' }}>Leverage Health {Math.round(ms.leverage_health)}/100 (high = lower debt)</Text>
          )}
          {!!ms.interpretation && <Text className="text-textSecondary text-[12px] leading-4">{ms.interpretation}</Text>}
          <Text className="text-textMuted text-[12px] mt-2">This is the measured MARKET read — the same as the Market section. The AI estimate below is the separate ATTENTION read.</Text>
        </View>
      );
    })()}

    <View className="bg-card rounded-2xl p-5 mb-4">
      <View className="flex-row items-center justify-between mb-1">
        <Text className="text-textMuted text-[12px] font-bold tracking-widest uppercase">
          {measured ? 'Gradient Score · measured' : (ms ? 'Attention estimate · AI' : 'Proposed · AI estimate')}
        </Text>
        <View className="flex-row items-center gap-1.5">
          <View className="px-2 py-0.5 rounded-full" style={{ backgroundColor: `${measured ? '#2E7D5B' : '#A8456A'}1A` }}>
            <Text className="text-[12px] font-bold" style={{ color: measured ? '#2E7D5B' : '#A8456A' }}>{measured ? 'IN DATA POOL' : 'AI ESTIMATE'}</Text>
          </View>
          <View className="px-2.5 py-1 rounded-full" style={{ backgroundColor: `${STAGE_COLOR[result.stage] ?? '#8A8F9C'}1A` }}>
            <Text className="text-[12px] font-bold" style={{ color: STAGE_COLOR[result.stage] ?? '#8A8F9C' }}>{result.stage}</Text>
          </View>
        </View>
      </View>
      {!!(result as any).note && <Text className="text-textMuted text-[12px] leading-4 mb-2">{(result as any).note}</Text>}
      <View className="flex-row justify-around items-start mt-2 mb-3">
        <View className="items-center">
          <GradientScoreRing score={Math.round(result.detection_score)} color="#2A5B9E" size="md" caption="/100" />
          <Text className="text-textPrimary text-xs font-bold mt-2">DETECTION</Text>
        </View>
        <View className="items-center">
          <GradientScoreRing score={Math.round(result.confidence_score)} color="#2E7D5B" size="md" caption="/100" />
          <Text className="text-textPrimary text-xs font-bold mt-2">CONFIDENCE</Text>
        </View>
      </View>
      <View className="rounded-xl px-3 py-2 mb-3" style={{ borderColor: `${band.color}55`, backgroundColor: `${band.color}0F` }}>
        <Text className="text-sm font-bold" style={{ color: band.color }}>{gap}-point gap — {band.label}</Text>
      </View>
      {!!result.action && <Text className="text-base font-black mb-1" style={{ color: STAGE_COLOR[result.stage] ?? '#16264A' }}>{result.action}</Text>}
      {!!result.reasoning && <Text className="text-textSecondary text-[14px] leading-5 mb-3">{result.reasoning}</Text>}
      {!!(result as any).mainstream_vs_niche && (() => {
        const mv = (result as any).mainstream_vs_niche;
        const col = mv.label === 'mainstream' ? '#2E7D5B' : mv.label === 'emerging' ? '#A8456A' : mv.label === 'fading' ? '#8A8F9C' : '#2A5B9E';
        return (
          <View className="mb-3">
            <View className="flex-row items-center justify-between">
              <Text className="text-textSecondary text-xs uppercase tracking-wider">Mainstream vs Niche</Text>
              <Text className="text-sm font-black capitalize" style={{ color: col }}>{mv.label}</Text>
            </View>
            {!!mv.note && <Text className="text-textMuted text-[12px] leading-4 mt-1">{mv.note}</Text>}
            <Text className="text-textMuted text-[12px] mt-1">Determined from: {mv.source}</Text>
          </View>
        );
      })()}
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
            <Text key={i} selectable className="text-textMuted text-[12px] mb-1" numberOfLines={1}>• {c}</Text>
          ))}
        </>
      )}
      {/* N (on-platform demand) explanation — kept consistent with the trend
          signal section. N is a separate, measured signal; the Gradient Score
          itself stays demand-free (no internal-demand feedback loop). */}
      <View className="mt-3 pt-3 border-t border-border">
        <View className="flex-row items-center justify-between mb-1">
          <Text className="text-[12px] font-bold tracking-widest uppercase" style={{ color: '#B11226' }}>N Score · Now Trending</Text>
          <Text className="text-base font-black" style={{ color: '#B11226' }}>{nScore != null && nScore > 0 ? nScore : '—'}</Text>
        </View>
        <Text className="text-textMuted text-[12px] leading-4">
          On-platform demand (N) — how often Now TrendIn users ask about a topic — is a
          separate signal, never folded into the Gradient (no demand feedback loop).
          {measured ? ' Measured live from the engine.' : ' Registers once demand accrues; this grade query logs it.'}
        </Text>
      </View>
      <Text className="text-textMuted text-[12px] leading-4 mt-3">Proposed score — an AI estimate from public web evidence, not a measured engine score.</Text>
    </View>
    </>
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
        <View style={{ width: `${v}%`, backgroundColor: '#A8456A' }} className="h-full rounded-full" />
      </View>
    </View>
  );
}
