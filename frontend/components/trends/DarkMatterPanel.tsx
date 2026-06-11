import { View, Text } from 'react-native';
import { Orbit } from 'lucide-react-native';
import { Signal } from '../../lib/signals';

/**
 * Dark Matter signatures — ported from the web dashboard's "Dark Matter" tab.
 * Infers unseen private conversations from anomalies in public data:
 * first-timer influx, engagement asymmetry, and clustering.
 */
function Indicator({
  label,
  value,
  active,
  desc,
}: {
  label: string;
  value: string;
  active: boolean;
  desc: string;
}) {
  const c = active ? '#7C3AED' : '#9AA3B0';
  return (
    <View
      className="rounded-xl px-3 py-3 mb-2 border flex-row gap-3"
      style={{ borderColor: active ? '#7C3AED55' : '#E4E7EC', backgroundColor: active ? '#7C3AED0D' : '#FFFFFF' }}
    >
      <View
        className="w-6 h-6 rounded-full items-center justify-center mt-0.5"
        style={{ backgroundColor: active ? '#7C3AED22' : '#F4F5F7', borderWidth: 1, borderColor: c }}
      >
        <Text style={{ color: c, fontSize: 11 }}>{active ? '●' : '○'}</Text>
      </View>
      <View className="flex-1">
        <View className="flex-row items-center gap-2 mb-0.5">
          <Text className="text-sm font-bold" style={{ color: active ? '#6D28D9' : '#5B6472' }}>{label}</Text>
          <Text className="text-[10px] font-bold px-1.5 rounded" style={{ color: c, backgroundColor: `${c}1A` }}>{value}</Text>
        </View>
        <Text className="text-textMuted text-[11px] leading-4">{desc}</Text>
      </View>
    </View>
  );
}

export function DarkMatterPanel({ signal }: { signal: Signal }) {
  const dm = signal.darkMatter;
  // Only render when we actually have dark-matter data.
  if (dm == null && signal.firstTimerRatio == null && signal.engagementAsymmetry == null) return null;

  const ftr = signal.firstTimerRatio ?? 0;
  const ftrPct = Math.round(ftr * 100);

  return (
    <View className="mb-5">
      <View className="flex-row items-center gap-2 mb-2">
        <Orbit size={16} color="#7C3AED" />
        <Text className="text-textSecondary text-xs uppercase tracking-wider">
          Dark Matter · {dm ?? 0}/100
        </Text>
      </View>
      <View className="rounded-xl px-4 py-3 mb-3 border" style={{ borderColor: '#7C3AED33', backgroundColor: '#7C3AED08' }}>
        <Text className="text-textSecondary text-xs leading-5">
          Like dark matter in cosmology, the earliest signals live in private channels we can't see —
          but their effects on public data are measurable. These indicators infer that unseen activity.
        </Text>
      </View>

      <Indicator
        label="First-Timer Ratio"
        value={`${ftrPct}%`}
        active={ftr >= 0.35}
        desc={
          ftr >= 0.35
            ? `${ftrPct}% of participants are new here — external traffic flowing in from a source we can't see. Threshold exceeded → dark-social signal inferred.`
            : `${ftrPct}% new participants — below the dark-social threshold; monitor for an increase.`
        }
      />
      <Indicator
        label="Engagement Asymmetry"
        value={signal.engagementAsymmetry ? 'DETECTED' : 'NORMAL'}
        active={!!signal.engagementAsymmetry}
        desc={
          signal.engagementAsymmetry
            ? 'Comments exceed normal upvote ratios — the community is actively discussing, not passively reacting. A sign they were already privately anticipating this.'
            : 'Normal engagement ratio. Asymmetry would indicate the community already knows more than the public post reveals.'
        }
      />

      <Text className="text-textMuted text-[10px] mt-1 leading-4">
        Dark Matter is probabilistic, not deterministic — it flags public behavior that has historically
        preceded trend emergence, not a confirmed private signal.
      </Text>
    </View>
  );
}
