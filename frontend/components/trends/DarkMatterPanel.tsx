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
  const c = active ? '#6B4FA0' : '#9A9AA2';
  return (
    <View
      className="rounded-xl px-3 py-3 mb-2 flex-row gap-3"
      style={{ borderColor: active ? '#6B4FA055' : '#ECECEC', backgroundColor: active ? '#6B4FA00D' : '#FFFFFF' }}
    >
      <View
        className="w-6 h-6 rounded-full items-center justify-center mt-0.5"
        style={{ backgroundColor: active ? '#6B4FA022' : '#FFFFFF', borderColor: c }}
      >
        <Text style={{ color: c, fontSize: 12 }}>{active ? '●' : '○'}</Text>
      </View>
      <View className="flex-1">
        <View className="flex-row items-center gap-2 mb-0.5">
          <Text className="text-sm font-bold" style={{ color: active ? '#6B4FA0' : '#3C4663' }}>{label}</Text>
          <Text className="text-[12px] font-bold px-1.5 rounded" style={{ color: c, backgroundColor: `${c}1A` }}>{value}</Text>
        </View>
        <Text className="text-textMuted text-[12px] leading-4">{desc}</Text>
      </View>
    </View>
  );
}

export function DarkMatterPanel({ signal }: { signal: Signal }) {
  const dm = signal.darkMatter;
  // Only render when we actually have dark-matter data.
  if (dm == null && signal.firstTimerRatio == null && signal.engagementAsymmetry == null) return null;

  // `?? 0` WAS THE DEFECT (Challenger, board 2026-08-20): on a topic we could not
  // measure, it rendered "First-Timer Ratio 0%" beside copy asserting the number means
  // something — a floor value wearing a measured badge (§16a stage 2) and a
  // non-contributing input rendered as a value (§17). Absence is now shown as absence.
  // `=== false` alone left the UNKNOWN case (pre-epoch rows, and INV-1 stale
  // serve_payloads older than 48h) rendering a ratio again. Treat unknown as
  // unmeasured when no ratio is present — never fall back to 0.
  const dUnmeasured = signal.dMeasured === false
    || (signal.dMeasured === undefined && signal.firstTimerRatio == null);
  const ftr = signal.firstTimerRatio ?? 0;
  const ftrPct = Math.round(ftr * 100);

  return (
    <View className="mb-5">
      <View className="flex-row items-center gap-2 mb-2">
        <Orbit size={16} color="#6B4FA0" />
        <Text className="text-textSecondary text-xs uppercase tracking-wider">
          Under-the-Radar Signals · {dm ?? 0}/100
        </Text>
      </View>
      <View className="rounded-xl px-4 py-3 mb-3" style={{ borderColor: '#6B4FA033', backgroundColor: '#6B4FA008' }}>
        <Text className="text-textSecondary text-xs leading-5">
          The earliest signals live in private channels we can't see — but their effects on public
          data are measurable. These indicators infer that unseen activity.
        </Text>
      </View>

      <Indicator
        label="First-Timer Ratio"
        value={dUnmeasured ? 'Unmeasured' : `${ftrPct}%`}
        active={!dUnmeasured && ftr >= 0.35}
        desc={
          ftr >= 0.35
            ? `${ftrPct}% of participants are new here — external traffic flowing in from a source we can't see. Threshold exceeded → private-channel activity inferred.`
            // The BADGE was fixed and the SENTENCE was not (Guardian, board 2026-08-20
            // late): on an unmeasured topic the panel read value "Unmeasured" with
            // "0% new participants — below the threshold" directly beneath it. The
            // sentence asserting the number means something is the defect, not the number.
            : dUnmeasured
            ? `No author-bearing signals reached us for this topic, so the first-timer ratio could not be read at all. This is absence of measurement — not evidence that nothing is happening.`
            : `${ftrPct}% new participants — below the private-channel threshold; monitor for an increase.`
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

      <Text className="text-textMuted text-[12px] mt-1 leading-4">
        Under-the-radar signals are probabilistic, not deterministic — they flag public behavior that
        has historically preceded trend emergence, not a confirmed private signal.
      </Text>
    </View>
  );
}
