import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronLeft, Target, TrendingUp, Clock } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { Disclaimer } from '../../../components/ui/Disclaimer';
import { useAccuracy } from '../../../hooks/useSignals';

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
      <Text className="text-textMuted text-sm mb-6 leading-5">
        Documented lead time — how many days Now TrendIn detected a topic before it broke out on Google Trends.
        The auditable proof that the Gradient Score leads the market.
      </Text>

      {isLoading ? (
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
