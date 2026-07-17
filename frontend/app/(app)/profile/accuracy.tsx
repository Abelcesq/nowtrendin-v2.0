import { useMemo, useState } from 'react';
import { titleCaseTopic } from "../../../lib/signals";
import { View, Text, TouchableOpacity, ActivityIndicator, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronLeft, Target, TrendingUp, Clock } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { Disclaimer } from '../../../components/ui/Disclaimer';
import { SignalAnalysisPanel } from '../../../components/trends/SignalAnalysisPanel';
import { useAccuracy, useAccuracyDetail, useMarketAccuracy, useCryptoAccuracy } from '../../../hooks/useSignals';
import type { LedgerDetailRow, PriceLedgerDetailRow } from '../../../lib/gradientApi';

// ── Ledger modes (parity with the web terminal's LEDGER chips) ──────────────────
type Mode = 'attention' | 'money' | 'crypto';
const MODES: { key: Mode; label: string }[] = [
  { key: 'attention', label: 'ATTENTION · TRENDS' },
  { key: 'money', label: 'MONEY · MARKET' },
  { key: 'crypto', label: 'CRYPTO · COIN' },
];

// Verdict filter chips. PRE-BROKEN = the Google breakout happened >7d BEFORE our
// first sighting (server-computed flag) — never a race we could win. It stays
// COUNTED in the honest rate; the tracked-race rate reports only races run.
const A_FILTERS = [
  { key: '', label: 'ALL' },
  { key: 'LED', label: 'LED' },
  { key: 'SAME_DAY', label: 'SAME DAY' },
  { key: 'LAGGED_NEAR', label: 'LAGGED · NEAR' },
  { key: 'PRE_BROKEN', label: 'PRE-BROKEN' },
  { key: 'FALSE_POSITIVE', label: 'FALSE POSITIVE' },
];
const P_FILTERS = [
  { key: '', label: 'ALL' },
  { key: 'CONFIRMED', label: 'CONFIRMED' },
  { key: 'NOT_CONFIRMED', label: 'NOT CONFIRMED' },
  { key: 'NO_MOVE', label: 'NO MOVE' },
];

// Jewel-tone verdict colors (Aurora palette only).
const VERDICT_COLOR: Record<string, string> = {
  LED: '#2E7D5B', SAME_DAY: '#2A5B9E', LAGGED: '#A8456A', 'PRE-BROKEN': '#8A8F9C',
  FALSE_POSITIVE: '#B11226', LATE_REDETECTION: '#8A8F9C',
  CONFIRMED: '#2E7D5B', NOT_CONFIRMED: '#A8456A', NO_MOVE: '#8A8F9C',
};

const PAGE = 30;

function fmtD(s?: string) {
  if (!s) return '—';
  const d = new Date(s);
  return isNaN(+d) ? s.slice(0, 10) : d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function Metric({ label, value, suffix }: { label: string; value: number | string; suffix?: string }) {
  return (
    <View className="flex-1 bg-card rounded-xl py-3 items-center">
      <Text className="text-2xl font-black text-textPrimary">
        {value}
        {suffix ? <Text className="text-sm text-textMuted">{suffix}</Text> : null}
      </Text>
      <Text className="text-textMuted text-[12px] font-bold tracking-wider mt-0.5">{label}</Text>
    </View>
  );
}

function Chip({ label, on, onPress }: { label: string; on: boolean; onPress: () => void }) {
  return (
    <TouchableOpacity onPress={onPress} activeOpacity={0.8} className="rounded-full"
      style={{ paddingVertical: 9, paddingHorizontal: 15, backgroundColor: on ? '#16264A' : '#F1F1F4' }}>
      <Text style={{ color: on ? '#FFFFFF' : '#3C4663', fontSize: 12, fontWeight: '700', letterSpacing: 0.4 }}>{label}</Text>
    </TouchableOpacity>
  );
}

function VerdictPill({ v }: { v: string }) {
  return (
    <View className="rounded-full" style={{ backgroundColor: (VERDICT_COLOR[v] || '#8A8F9C') + '1A', paddingVertical: 3, paddingHorizontal: 9 }}>
      <Text style={{ color: VERDICT_COLOR[v] || '#8A8F9C', fontSize: 12, fontWeight: '800', letterSpacing: 0.3 }}>{v.replace(/_/g, ' ')}</Text>
    </View>
  );
}

// Independent second-referee status on a WIN (honest: wins resolved before the
// metadata existed read "referee unchecked", never implied as verified).
function refereeLine(r: LedgerDetailRow) {
  if (r.refereeCorroborated === 1) return '✓ Wikipedia-corroborated';
  if (r.refereeCorroborated === 0) return '– Wikipedia: no arrival match';
  return '· referee unchecked';
}

export default function AccuracyLedger() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>('attention');
  const [filter, setFilter] = useState('');
  const [shown, setShown] = useState(PAGE);
  // Tap a row → the full Ledger Entry Analysis panel (/analysis/ledger).
  const [expanded, setExpanded] = useState<string | null>(null);

  const { report, isLoading } = useAccuracy();
  const { rows: aRows, isLoading: aLoading } = useAccuracyDetail();
  const money = useMarketAccuracy(mode === 'money');
  const crypto = useCryptoAccuracy(mode === 'crypto');

  const hasData = report?.status === 'ok';
  const priceMode = mode !== 'attention';
  const price = mode === 'crypto' ? crypto : money;

  const aView = useMemo(() => {
    let r = aRows;
    if (filter === 'PRE_BROKEN') r = r.filter((x) => x.preBroken);
    else if (filter === 'LAGGED_NEAR') r = r.filter((x) => x.verdict === 'LAGGED' && !x.preBroken);
    else if (filter) r = r.filter((x) => x.verdict === filter);
    return r;
  }, [aRows, filter]);

  const pView = useMemo(() => {
    let r = price.rows;
    if (filter) r = r.filter((x) => (x.verdict || '').toUpperCase() === filter);
    return r;
  }, [price.rows, filter]);

  const setModeAndReset = (m: Mode) => { setMode(m); setFilter(''); setShown(PAGE); };
  const filters = priceMode ? P_FILTERS : A_FILTERS;

  return (
    <Screen scroll>
      <Disclaimer />
      <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-2 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#3C4663" />
        <Text className="text-textSecondary text-sm">Profile</Text>
      </TouchableOpacity>
      <View className="flex-row items-center gap-2 mb-1">
        <Target size={22} color="#2E7D5B" />
        <Text className="text-textPrimary text-3xl font-bold">Accuracy Ledger</Text>
      </View>
      <Text className="text-textMuted text-sm mb-4 leading-5">
        {priceMode
          ? `A separate ledger: ${mode === 'crypto' ? 'crypto money-movement reads validated against realized coin price direction' : 'money-movement reads validated against realized end-of-day price direction'} — a retrospective measurement, not a forecast.`
          : 'Documented lead time — how many days Now TrendIn detected a topic before it broke out on Google Trends. The auditable proof that the Gradient Score leads Google Trends attention.'}
      </Text>

      {/* LEDGER mode chips (web parity) */}
      <Text className="text-textMuted text-[12px] font-bold tracking-widest uppercase mb-2.5">Ledger</Text>
      <View style={{ marginHorizontal: -20, marginBottom: 10 }}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8, paddingHorizontal: 20 }}>
          {MODES.map((m) => <Chip key={m.key} label={m.label} on={mode === m.key} onPress={() => setModeAndReset(m.key)} />)}
        </ScrollView>
      </View>

      {/* Verdict filter chips */}
      <View style={{ marginHorizontal: -20, marginBottom: 14 }}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 8, paddingHorizontal: 20 }}>
          {filters.map((f) => <Chip key={f.key || 'all'} label={f.label} on={filter === f.key} onPress={() => { setFilter(f.key); setShown(PAGE); }} />)}
        </ScrollView>
      </View>

      {priceMode ? (
        price.isLoading ? (
          <ActivityIndicator size="large" color="#2E7D5B" style={{ marginTop: 40 }} />
        ) : (
          <>
            <View className="flex-row gap-2 mb-3">
              <Metric label="CONFIRM RATE" value={price.report?.confirmRate != null ? price.report.confirmRate : '—'} suffix={price.report?.confirmRate != null ? '%' : undefined} />
              <Metric label="MEDIAN LEAD" value={price.report?.medianLead ?? '—'} suffix={price.report?.medianLead != null ? 'd' : undefined} />
              <Metric label="RESOLVED" value={price.report?.resolved ?? 0} />
            </View>
            <Text className="text-textMuted text-[12px] text-center mb-4">
              {Number(price.report?.pending ?? 0).toLocaleString()} in flight · confirmed {price.report?.confirmed ?? 0} · not confirmed {price.report?.notConfirmed ?? 0} · no move {price.report?.noMove ?? 0}
            </Text>
            {pView.length === 0 ? (
              <View className="bg-card rounded-2xl p-5 items-center">
                <Target size={40} color="#D8DCE3" />
                <Text className="text-textPrimary font-bold text-base mt-3 text-center">No resolved detections{filter ? ' for this filter' : ' yet'}</Text>
                <Text className="text-textMuted text-sm mt-2 text-center leading-5">
                  Detections resolve as the realized price confirms, or the window elapses.
                </Text>
              </View>
            ) : (
              <>
                {pView.slice(0, shown).map((r: PriceLedgerDetailRow, i) => (
                  <View key={r.key + i} className="bg-card rounded-xl p-3 mb-2">
                    <View className="flex-row items-center justify-between">
                      <Text className="text-textPrimary font-semibold flex-1 mr-2" numberOfLines={1}>{r.name}</Text>
                      <VerdictPill v={(r.verdict || '—').toUpperCase()} />
                    </View>
                    <View className="flex-row items-center justify-between mt-1.5">
                      <Text className="text-textMuted text-xs">
                        {fmtD(r.detectionDate)} · {r.flow === 'inflow' ? '▲ inflow' : r.flow === 'outflow' ? '▼ outflow' : '• neutral'}
                      </Text>
                      <Text className="text-textSecondary text-xs font-bold">
                        {r.priceChangePct != null ? `${r.priceChangePct > 0 ? '+' : ''}${r.priceChangePct}%` : '—'}{r.leadDays != null ? ` · ${r.leadDays}d` : ''}
                      </Text>
                    </View>
                  </View>
                ))}
                {pView.length > shown && (
                  <TouchableOpacity onPress={() => setShown((n) => n + PAGE)} className="bg-card rounded-xl py-3 items-center mb-2" activeOpacity={0.8}>
                    <Text className="text-textSecondary text-sm font-bold">Show more ({pView.length - shown} left)</Text>
                  </TouchableOpacity>
                )}
              </>
            )}
          </>
        )
      ) : isLoading ? (
        <ActivityIndicator size="large" color="#2E7D5B" style={{ marginTop: 40 }} />
      ) : hasData ? (
        <>
          <View className="flex-row gap-2 mb-2">
            <Metric label="HIT RATE" value={report!.hitRate ?? 0} suffix="%" />
            <Metric label="TRACKED-RACE" value={report!.trackedRaceHitRate != null ? report!.trackedRaceHitRate : '—'} suffix={report!.trackedRaceHitRate != null ? '%' : undefined} />
            <Metric label="MEDIAN LEAD" value={report!.medianLead ?? 0} suffix="d" />
          </View>
          <View className="flex-row gap-2 mb-2">
            <Metric label="RESOLVED" value={report!.total ?? 0} />
            <Metric label="LED" value={report!.led ?? 0} />
            <Metric label="MAX LEAD" value={report!.maxLead ?? 0} suffix="d" />
          </View>
          {/* Honest breakdown — near + pre-broken = lagged; nothing hidden. */}
          <Text className="text-textMuted text-[12px] text-center mb-1">
            {report!.led ?? 0} led · {report!.sameDay ?? 0} same-day · {report!.laggedNear ?? report!.lagged ?? 0} near-miss · {report!.preBroken ?? 0} pre-broken · {report!.falsePositives ?? 0} false positives
          </Text>
          <Text className="text-textMuted text-[12px] text-center mb-1">
            LED referee: {report!.ledCorroborated ?? 0} ✓ · {report!.ledUncorroborated ?? 0} – · {report!.ledUnchecked ?? 0} unchecked
          </Text>
          {report!.pending != null && (
            <Text className="text-textMuted text-[12px] text-center mb-3">
              {Number(report!.pending).toLocaleString()} pending detections still in flight — 365-day patience window
            </Text>
          )}
          <Text className="text-textMuted text-[12px] leading-4 mb-4">
            Pre-broken = the Google breakout happened more than 7 days before our first sighting — the topic
            entered tracking already post-breakout, so it was never a race. Pre-broken stays counted in the
            hit rate; Tracked-race reports only the races actually run.
          </Text>

          {aLoading ? (
            <ActivityIndicator size="small" color="#2E7D5B" style={{ marginVertical: 20 }} />
          ) : aView.length === 0 ? (
            <View className="bg-card rounded-2xl p-5 items-center mb-2">
              <Target size={40} color="#D8DCE3" />
              <Text className="text-textPrimary font-bold text-base mt-3 text-center">No entries for this filter</Text>
            </View>
          ) : (
            <>
              <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3">
                {filter ? `${aView.length} entries` : `All entries (${aView.length})`}
              </Text>
              {aView.slice(0, shown).map((r, i) => {
                const v = r.preBroken ? 'PRE-BROKEN' : (r.verdict || '—');
                const win = r.verdict === 'LED' || r.verdict === 'SAME_DAY';
                const rowId = r.topicKey + '|' + (r.detectionDate || i);
                const open = expanded === rowId;
                return (
                  <View key={rowId}>
                    <TouchableOpacity activeOpacity={0.85} onPress={() => setExpanded(open ? null : rowId)}
                      className="bg-card rounded-xl p-3 mb-2">
                      <View className="flex-row items-center justify-between">
                        <Text className="text-textPrimary font-semibold flex-1 mr-2" numberOfLines={1}>
                          {titleCaseTopic(r.topic)}
                          {r.queryAmbiguous === 1 ? <Text className="text-textMuted text-xs">  · broad term</Text> : null}
                        </Text>
                        <VerdictPill v={v} />
                      </View>
                      <View className="flex-row items-center justify-between mt-1.5">
                        <Text className="text-textMuted text-xs">
                          det {fmtD(r.detectionDate)} · breakout {fmtD(r.breakoutDate)}
                        </Text>
                        <Text className="text-textSecondary text-xs font-black">
                          {r.leadDays != null ? `${r.leadDays > 0 ? '+' : ''}${r.leadDays}d` : '—'}
                        </Text>
                      </View>
                      {win && <Text className="text-textMuted text-xs mt-1">{refereeLine(r)}</Text>}
                      {!open && <Text className="text-textMuted text-[12px] mt-1">Tap for the full entry analysis</Text>}
                    </TouchableOpacity>
                    {open && <SignalAnalysisPanel kind="ledger" item={r} />}
                  </View>
                );
              })}
              {aView.length > shown && (
                <TouchableOpacity onPress={() => setShown((n) => n + PAGE)} className="bg-card rounded-xl py-3 items-center mb-2" activeOpacity={0.8}>
                  <Text className="text-textSecondary text-sm font-bold">Show more ({aView.length - shown} left)</Text>
                </TouchableOpacity>
              )}
            </>
          )}

          {!!report!.best?.length && !filter && (
            <>
              <Text className="text-textSecondary text-xs uppercase tracking-wider mt-4 mb-3">Best lead times</Text>
              {report!.best!.map((b, i) => (
                <View key={i} className="flex-row items-center bg-card rounded-xl p-3 mb-2">
                  <TrendingUp size={15} color="#2E7D5B" />
                  <Text className="text-textPrimary font-semibold flex-1 ml-2">{titleCaseTopic(b.topic)}</Text>
                  <View className="flex-row items-center gap-1">
                    <Clock size={12} color="#3C4663" />
                    <Text className="text-textPrimary font-black">{b.leadDays}d</Text>
                  </View>
                  {b.multiple != null && <Text className="text-textMuted text-xs ml-3">{b.multiple}×</Text>}
                </View>
              ))}
            </>
          )}
        </>
      ) : (
        <View className="bg-card rounded-2xl p-5 items-center">
          <Target size={40} color="#D8DCE3" />
          <Text className="text-textPrimary font-bold text-base mt-3 text-center">No validated predictions yet</Text>
          <Text className="text-textMuted text-sm mt-2 text-center leading-5">
            The ledger fills in once a Google Trends provider (Apify) is connected and your detections are
            checked for breakout. Each entry records the days you led the Google Trends breakout — the proof asset for
            institutional clients.
          </Text>
        </View>
      )}

      <Disclaimer />
    </Screen>
  );
}
