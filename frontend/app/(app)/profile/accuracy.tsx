import { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronLeft, Target, TrendingUp, Clock } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { Disclaimer } from '../../../components/ui/Disclaimer';
import { useAccuracy } from '../../../hooks/useSignals';
import { fetchMarketAccuracy, type MarketAccuracyReport } from '../../../lib/gradientApi';

function Metric({ label, value, suffix }: { label: string; value: number | string; suffix?: string }) {
  return (
    <View className="flex-1 bg-surface rounded-xl border border-border py-3 items-center">
      <Text className="text-2xl font-black text-textPrimary">
        {value}
        {suffix ? <Text className="text-sm text-textMuted">{suffix}</Text> : null}
      </Text>
      <Text className="text-textMuted text-[9px] font-bold tracking-wider mt-0.5">{label}</Text>
    </View>
  );
}

export default function AccuracyLedger() {
  const router = useRouter();
  const { report, isLoading } = useAccuracy();
  const hasData = report?.status === 'ok';

  // Money Gradient ledger (distinct: realized EOD price direction, not Google Trends).
  const [tab, setTab] = useState<'attention' | 'money'>('attention');
  const [mrep, setMrep] = useState<MarketAccuracyReport | null>(null);
  const [mLoading, setMLoading] = useState(false);
  useEffect(() => {
    if (tab !== 'money' || mrep) return;
    let alive = true;
    setMLoading(true);
    fetchMarketAccuracy()
      .then((r) => { if (alive) setMrep(r); })
      .catch(() => { if (alive) setMrep({ status: 'error' }); })
      .finally(() => { if (alive) setMLoading(false); });
    return () => { alive = false; };
  }, [tab, mrep]);
  const money = tab === 'money';

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-2 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#5B6472" />
        <Text className="text-textSecondary text-sm">Profile</Text>
      </TouchableOpacity>
      <View className="flex-row items-center gap-2 mb-1">
        <Target size={22} color="#00C896" />
        <Text className="text-textPrimary text-3xl font-bold">Accuracy Ledger</Text>
      </View>
      <Text className="text-textMuted text-sm mb-3 leading-5">
        {money
          ? `Where money moved: did our detected flow (inflow→up / outflow→down) match the realized EOD price direction, past ±${mrep?.moveThresholdPct ?? 5}%? A retrospective measurement — not a forecast or advice.`
          : 'Documented lead time — how many days Now TrendIn detected a topic before it broke out on Google Trends. The auditable proof that the Gradient Score leads the market.'}
      </Text>

      {/* Two ledgers, two ground truths */}
      <View className="flex-row gap-2 mb-5">
        <TouchableOpacity onPress={() => setTab('attention')} className="flex-1 rounded-xl py-2 items-center border" style={{ backgroundColor: !money ? '#00C89614' : '#FFFFFF', borderColor: !money ? '#00C896' : '#E4E7EC' }}>
          <Text className="text-[11px] font-bold" style={{ color: !money ? '#009970' : '#5B6472' }}>Attention · Trends</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => setTab('money')} className="flex-1 rounded-xl py-2 items-center border" style={{ backgroundColor: money ? '#2D7EEF14' : '#FFFFFF', borderColor: money ? '#2D7EEF' : '#E4E7EC' }}>
          <Text className="text-[11px] font-bold" style={{ color: money ? '#2D7EEF' : '#5B6472' }}>Money · Market</Text>
        </TouchableOpacity>
      </View>

      {money ? (
        mLoading ? (
          <ActivityIndicator size="large" color="#2D7EEF" style={{ marginTop: 40 }} />
        ) : (mrep?.resolved ?? 0) > 0 ? (
          <>
            <View className="flex-row gap-2 mb-3">
              <Metric label="CONFIRM RATE" value={mrep!.confirmRate ?? 0} suffix="%" />
              <Metric label="MEDIAN LEAD" value={mrep!.medianLead ?? 0} suffix="d" />
              <Metric label="RESOLVED" value={mrep!.resolved ?? 0} />
            </View>
            <View className="flex-row gap-2 mb-3">
              <Metric label="CONFIRMED" value={mrep!.confirmed ?? 0} />
              <Metric label="NOT CONF." value={mrep!.notConfirmed ?? 0} />
              <Metric label="NO MOVE" value={mrep!.noMove ?? 0} />
            </View>
            <Text className="text-textMuted text-[11px] leading-4 mb-6">
              Inflow confirm {mrep!.inflowConfirm ?? '—'}% · outflow confirm {mrep!.outflowConfirm ?? '—'}%. Ground truth =
              realized EOD close direction (FMP) — distinct from the Attention ledger's Google Trends breakout.
            </Text>
          </>
        ) : (
          <View className="bg-surface rounded-2xl border border-border p-5 items-center">
            <Target size={40} color="#C7CDD6" />
            <Text className="text-textPrimary font-bold text-base mt-3 text-center">No resolved money-movement detections yet</Text>
            <Text className="text-textMuted text-sm mt-2 text-center leading-5">
              The Money ledger fills in as detected money flows are checked against the realized EOD price
              direction (or the {mrep?.timeoutDays ?? 60}-day window elapses). Populates once the Money Gradient is live.
            </Text>
          </View>
        )
      ) : isLoading ? (
        <ActivityIndicator size="large" color="#00C896" style={{ marginTop: 40 }} />
      ) : hasData ? (
        <>
          <View className="flex-row gap-2 mb-3">
            <Metric label="HIT RATE" value={report!.hitRate ?? 0} suffix="%" />
            <Metric label="AVG LEAD" value={report!.avgLead ?? 0} suffix="d" />
            <Metric label="MAX LEAD" value={report!.maxLead ?? 0} suffix="d" />
          </View>
          <View className="flex-row gap-2 mb-6">
            <Metric label="PREDICTIONS" value={report!.total ?? 0} />
            <Metric label="LED" value={report!.led ?? 0} />
            <Metric label="MEDIAN LEAD" value={report!.medianLead ?? 0} suffix="d" />
          </View>

          {!!report!.best?.length && (
            <>
              <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3">Best lead times</Text>
              {report!.best!.map((b, i) => (
                <View key={i} className="flex-row items-center bg-surface rounded-xl border border-border p-3 mb-2">
                  <TrendingUp size={15} color="#00C896" />
                  <Text className="text-textPrimary font-semibold flex-1 ml-2">{b.topic}</Text>
                  <View className="flex-row items-center gap-1">
                    <Clock size={12} color="#5B6472" />
                    <Text className="text-textPrimary font-black">{b.leadDays}d</Text>
                  </View>
                  <Text className="text-textMuted text-xs ml-3">{b.multiple}×</Text>
                </View>
              ))}
            </>
          )}
        </>
      ) : (
        <View className="bg-surface rounded-2xl border border-border p-5 items-center">
          <Target size={40} color="#C7CDD6" />
          <Text className="text-textPrimary font-bold text-base mt-3 text-center">No validated predictions yet</Text>
          <Text className="text-textMuted text-sm mt-2 text-center leading-5">
            The ledger fills in once a Google Trends provider (Apify) is connected and your detections are
            checked for breakout. Each entry records the days you led the market — the proof asset for
            institutional clients.
          </Text>
        </View>
      )}

      <Disclaimer />
    </Screen>
  );
}
