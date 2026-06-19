import { View, Text, ActivityIndicator, TouchableOpacity } from 'react-native';
import Svg, { Polyline, Line } from 'react-native-svg';
import { useRouter } from 'expo-router';
import { ChevronRight } from 'lucide-react-native';
import { Signal, stageColor } from '../../lib/signals';
import { useScoreHistory } from '../../hooks/useSignals';

// Mobile History trajectory graph — mirrors the web History feature pane. Shows
// how a topic's Detection (blue) and Confidence (green) have scored over time.
// Tapping a History row reveals THIS, rather than jumping to the full signal page.
// The trajectory is clipped to the selected window (12h/24h/7d) so the chart
// truly reflects the chosen clip — not the full unwindowed history.
export function TrajectoryCard({ signal, windowMs, winLabel }: { signal: Signal; windowMs?: number; winLabel?: string }) {
  const router = useRouter();
  const { rows, isLoading } = useScoreHistory(signal.id);
  const col = stageColor(signal.stage);

  const cutoff = windowMs ? Date.now() - windowMs : 0;
  const pts = [...rows].filter((r) => r.scoredAt >= cutoff).sort((a, b) => a.scoredAt - b.scoredAt); // oldest → newest
  const W = 320, H = 120, pad = 8;
  const n = pts.length;
  const xs = (i: number) => (n <= 1 ? W / 2 : pad + (i * (W - 2 * pad)) / (n - 1));
  const ys = (v: number) => H - pad - (Math.max(0, Math.min(100, v)) / 100) * (H - 2 * pad);
  const poly = (k: 'detection' | 'confidence') => pts.map((r, i) => `${xs(i).toFixed(1)},${ys(r[k]).toFixed(1)}`).join(' ');

  return (
    <View className="bg-surface rounded-2xl border border-border p-4 mb-3" style={{ borderColor: `${col}55` }}>
      <View className="flex-row items-center justify-between mb-1">
        <Text className="text-textPrimary text-base font-bold flex-1 pr-2" numberOfLines={1}>{signal.topic}</Text>
        <View className="px-2 py-0.5 rounded-full" style={{ backgroundColor: `${col}1A` }}>
          <Text style={{ color: col }} className="text-[9px] font-bold tracking-wide">{signal.stage}</Text>
        </View>
      </View>
      <View className="flex-row gap-4 mb-2">
        <Text className="text-xs font-black" style={{ color: '#2D7EEF' }}>DET {signal.detection}</Text>
        <Text className="text-xs font-black" style={{ color: '#00C896' }}>CONF {signal.confidence}</Text>
      </View>

      {isLoading ? (
        <ActivityIndicator color="#00C896" style={{ marginVertical: 24 }} />
      ) : pts.length < 2 ? (
        <Text className="text-textMuted text-xs py-7 text-center">
          {pts.length === 1 ? `Only one scoring run in the last ${winLabel ?? 'window'} — not enough for a trajectory yet.`
            : `Not enough history yet for a trajectory — scores accumulate each collection cycle.`}
        </Text>
      ) : (
        <Svg width="100%" height={H} viewBox={`0 0 ${W} ${H}`}>
          <Line x1={0} y1={H - pad} x2={W} y2={H - pad} stroke="#E4E7EC" strokeWidth={1} />
          <Polyline points={poly('detection')} fill="none" stroke="#2D7EEF" strokeWidth={2.5} />
          <Polyline points={poly('confidence')} fill="none" stroke="#00C896" strokeWidth={2.5} />
        </Svg>
      )}

      <View className="flex-row items-center justify-between mt-1.5">
        <Text className="text-textMuted text-[10px]">
          <Text style={{ color: '#2D7EEF' }}>● Detection</Text> · <Text style={{ color: '#00C896' }}>● Confidence</Text>
          {winLabel ? ` · ${pts.length} run${pts.length === 1 ? '' : 's'} in ${winLabel}` : ' · oldest → newest'}
        </Text>
        <TouchableOpacity onPress={() => router.push(`/signal/${signal.id}`)} className="flex-row items-center">
          <Text className="text-primary text-xs font-semibold">Full signal</Text>
          <ChevronRight size={14} color="#00C896" />
        </TouchableOpacity>
      </View>
    </View>
  );
}
