import { useState } from 'react';
import { View, Text, ActivityIndicator, TouchableOpacity, type LayoutChangeEvent, type GestureResponderEvent } from 'react-native';
import Svg, { Polyline, Line, Circle, G, Text as SvgText } from 'react-native-svg';
import { useRouter } from 'expo-router';
import { ChevronRight } from 'lucide-react-native';
import { Signal, stageColor, stageLabel, titleCaseTopic } from '../../lib/signals';
import { useScoreHistory } from '../../hooks/useSignals';
import type { ScoreHistoryRow } from '../../lib/gradientApi';

// Mobile History trajectory graph — same detail as the web ScoreChart. X = time
// (each scoring run), Y = score 0–100 with gridlines + labels, a dot at every REAL
// scoring event, Detection (blue) + Confidence (green) lines, and TAP-to-inspect:
// tapping the chart selects the nearest point and shows the driving factors
// (mentions, platforms, stage, and Δ vs the previous run). Clipped to the window.
const DET = '#2A5B9E', CONF = '#2E7D5B';

function fmtTime(ms: number) {
  const d = new Date(ms);
  const mo = d.toLocaleString('en-US', { month: 'short' });
  let h = d.getHours(); const ap = h >= 12 ? 'p' : 'a'; h = h % 12 || 12;
  return `${mo} ${d.getDate()}, ${h}:${d.getMinutes().toString().padStart(2, '0')}${ap}`;
}
function fmtAxis(ms: number) {
  const d = new Date(ms);
  let h = d.getHours(); const ap = h >= 12 ? 'p' : 'a'; h = h % 12 || 12;
  return `${d.getMonth() + 1}/${d.getDate()} ${h}${ap}`;
}

export function TrajectoryCard({ signal, windowMs, winLabel }: { signal: Signal; windowMs?: number; winLabel?: string }) {
  const router = useRouter();
  const { rows, isLoading } = useScoreHistory(signal.id);
  const col = stageColor(signal.stage);
  const [w, setW] = useState(0);
  const [sel, setSel] = useState<number | null>(null);

  const cutoff = windowMs ? Date.now() - windowMs : 0;
  const pts: ScoreHistoryRow[] = [...rows].filter((r) => r.scoredAt >= cutoff).sort((a, b) => a.scoredAt - b.scoredAt);

  const H = 154, mL = 24, mR = 10, mT = 10, mB = 22;
  const plotW = Math.max(1, w - mL - mR), plotH = H - mT - mB;
  const n = pts.length;
  const x = (i: number) => mL + (n <= 1 ? plotW / 2 : (i * plotW) / (n - 1));
  const y = (v: number) => mT + plotH - (Math.max(0, Math.min(100, v)) / 100) * plotH;
  const poly = (k: 'detection' | 'confidence') => pts.map((p, i) => `${x(i).toFixed(1)},${y(p[k]).toFixed(1)}`).join(' ');
  const yticks = [0, 25, 50, 75, 100];
  const xtickIdx = n <= 5 ? pts.map((_, i) => i) : [0, Math.round((n - 1) * 0.33), Math.round((n - 1) * 0.66), n - 1];

  const onTouch = (e: GestureResponderEvent) => {
    if (n === 0 || w === 0) return;
    const px = e.nativeEvent.locationX;
    let best = 0, bd = Infinity;
    for (let i = 0; i < n; i++) { const d = Math.abs(x(i) - px); if (d < bd) { bd = d; best = i; } }
    setSel(best);
  };

  const sp = sel != null ? pts[sel] : null;
  const prev = sel != null && sel > 0 ? pts[sel - 1] : null;
  const delta = (cur: number, p?: number) => (p == null ? '' : ` (${cur - p >= 0 ? '+' : ''}${cur - p})`);

  return (
    <View className="bg-card rounded-2xl p-4 mb-3" style={{ borderColor: `${col}55` }}>
      <View className="flex-row items-center justify-between mb-1">
        <Text className="text-textPrimary text-base font-bold flex-1 pr-2" numberOfLines={1}>{titleCaseTopic(signal.topic)}</Text>
        <View className="px-2 py-0.5 rounded-full" style={{ backgroundColor: `${col}1A` }}>
          <Text style={{ color: col }} className="text-[12px] font-bold tracking-wide">{stageLabel(signal.stage)}</Text>
        </View>
      </View>
      <View className="flex-row gap-4 mb-2">
        <Text className="text-xs font-black" style={{ color: DET }}>DET {signal.detection}</Text>
        <Text className="text-xs font-black" style={{ color: CONF }}>CONF {signal.confidence}</Text>
      </View>

      {isLoading ? (
        <ActivityIndicator color="#2E7D5B" style={{ marginVertical: 30 }} />
      ) : pts.length < 2 ? (
        <Text className="text-textMuted text-xs py-8 text-center">
          {pts.length === 1
            ? `Only one scoring run in the last ${winLabel ?? 'window'} — a trajectory appears after the next cycle.`
            : 'Not enough history yet for a trajectory.'}
        </Text>
      ) : (
        <>
          <View
            onLayout={(e: LayoutChangeEvent) => setW(e.nativeEvent.layout.width)}
            onStartShouldSetResponder={() => true}
            onMoveShouldSetResponder={() => true}
            onStartShouldSetResponderCapture={() => true}
            onMoveShouldSetResponderCapture={() => true}
            onResponderTerminationRequest={() => false}
            onResponderGrant={onTouch}
            onResponderMove={onTouch}
            hitSlop={{ top: 8, bottom: 8, left: 4, right: 4 }}
          >
            {w > 0 && (
              <Svg width={w} height={H}>
                {yticks.map((t) => (
                  <G key={t}>
                    <Line x1={mL} y1={y(t)} x2={w - mR} y2={y(t)} stroke="#ECECEC" strokeWidth={1} />
                    <SvgText x={mL - 4} y={y(t) + 3} fontSize="8" fill="#9A9AA2" textAnchor="end">{String(t)}</SvgText>
                  </G>
                ))}
                {xtickIdx.map((i) => (
                  <SvgText key={i} x={x(i)} y={H - 6} fontSize="8" fill="#9A9AA2" textAnchor="middle">{fmtAxis(pts[i].scoredAt)}</SvgText>
                ))}
                <Polyline points={poly('confidence')} fill="none" stroke={CONF} strokeWidth={2.25} />
                <Polyline points={poly('detection')} fill="none" stroke={DET} strokeWidth={2.25} />
                {pts.map((p, i) => (
                  <G key={i}>
                    <Circle cx={x(i)} cy={y(p.confidence)} r={sel === i ? 4 : 2.4} fill={CONF} />
                    <Circle cx={x(i)} cy={y(p.detection)} r={sel === i ? 4 : 2.4} fill={DET} />
                  </G>
                ))}
                {sel != null && <Line x1={x(sel)} y1={mT} x2={x(sel)} y2={mT + plotH} stroke="#9A9AA2" strokeWidth={1} strokeDasharray="3,3" />}
              </Svg>
            )}
          </View>

          {sp ? (
            <View className="bg-bg rounded-lg p-2.5 mt-2">
              <Text className="text-textPrimary text-[12px] font-bold mb-1">{fmtTime(sp.scoredAt)}{sp.stage ? ` · ${stageLabel(sp.stage)}` : ''}</Text>
              <View className="flex-row flex-wrap" style={{ columnGap: 14, rowGap: 2 }}>
                <Text className="text-[12px]" style={{ color: DET }}>Det {sp.detection}<Text className="text-textMuted">{delta(sp.detection, prev?.detection)}</Text></Text>
                <Text className="text-[12px]" style={{ color: CONF }}>Conf {sp.confidence}<Text className="text-textMuted">{delta(sp.confidence, prev?.confidence)}</Text></Text>
                <Text className="text-[12px] text-textSecondary">Gap {sp.gap}</Text>
                {sp.mentions != null && <Text className="text-[12px] text-textSecondary">{sp.mentions.toLocaleString()} mentions<Text className="text-textMuted">{delta(sp.mentions, prev?.mentions)}</Text></Text>}
                {sp.platforms != null && <Text className="text-[12px] text-textSecondary">{sp.platforms} platform{sp.platforms === 1 ? '' : 's'}</Text>}
                {sp.darkMatter ? <Text className="text-[12px] text-textMuted">dark-matter {sp.darkMatter}</Text> : null}
              </View>
            </View>
          ) : (
            <Text className="text-textMuted text-[12px] mt-1.5">Tap the chart to see the factors at each point.</Text>
          )}
        </>
      )}

      <View className="flex-row items-center justify-between mt-2">
        <Text className="text-textMuted text-[12px]">
          <Text style={{ color: DET }}>● Detection</Text> · <Text style={{ color: CONF }}>● Confidence</Text>
          {winLabel ? ` · ${pts.length} run${pts.length === 1 ? '' : 's'} in ${winLabel}` : ''}
        </Text>
        <TouchableOpacity onPress={() => router.push(`/signal/${signal.id}`)} className="flex-row items-center">
          <Text className="text-primary text-xs font-semibold">Full signal</Text>
          <ChevronRight size={14} color="#2E7D5B" />
        </TouchableOpacity>
      </View>
    </View>
  );
}
