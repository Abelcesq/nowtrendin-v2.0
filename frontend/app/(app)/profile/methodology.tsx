import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronLeft } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { Disclaimer } from '../../../components/ui/Disclaimer';

function Block({ title, color, children }: { title: string; color: string; children: React.ReactNode }) {
  return (
    <View className="bg-surface rounded-2xl p-4 border border-border mb-3">
      <Text className="text-sm font-bold mb-1.5" style={{ color }}>{title}</Text>
      <Text className="text-textSecondary text-[13px] leading-5">{children}</Text>
    </View>
  );
}

export default function Methodology() {
  const router = useRouter();
  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="pt-4 mb-2 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#5B6472" /><Text className="text-textSecondary text-base">Back</Text>
      </TouchableOpacity>
      <Text className="text-textPrimary text-2xl font-bold mb-1">Methodology</Text>
      <Text className="text-textMuted text-sm mb-4">How the Gradient Score is measured.</Text>

      <Block title="Two scores from one engine" color="#1A1A2E">
        The same measurements run once; two threshold rule-sets produce two scores.
        <Text style={{ color: '#2D7EEF', fontWeight: '600' }}> Detection</Text> weights early-edge
        components (niche concentration, dark matter, acceleration) — speed.
        <Text style={{ color: '#00C896', fontWeight: '600' }}> Confidence</Text> weights cross-platform
        confirmation — precision. The gap between them tells you how early a signal is.
      </Block>

      <Block title="Detection — speed" color="#2D7EEF">
        Surfaces a signal early, before broad confirmation arrives. Higher detection = the engine sees
        attention moving ahead of the mainstream. Optimized for earliness, accepting more false alarms.
      </Block>

      <Block title="Confidence — precision" color="#00C896">
        Confirms a signal across many independent sources. Higher confidence = broadly corroborated.
        Optimized for fewer false alarms — confirmed before it commits.
      </Block>

      <Block title="The gap — how early you are" color="#E85A1E">
        Detection minus Confidence. A wide positive gap means the signal is detected but not yet
        confirmed (earliest, highest potential lead time). A small gap means both agree — a
        high-conviction read.
      </Block>

      <Block title="The N (Now Trending) signal" color="#EE6A2A">
        N is the on-platform demand signal — how often Now TrendIn users ask the engine about a topic.
        It is shown separately and <Text style={{ fontWeight: '600' }}>never feeds the Gradient Score</Text>,
        so the Detection/Confidence read stays an objective measurement of the external world.
      </Block>

      <Block title="Maturity calibration" color="#94A3B8">
        Long-running, already-mainstream topics are discounted so a permanent expert base isn't
        misread as a new surge. New and emerging topics are calibrated as their baseline accumulates.
      </Block>

      <Disclaimer />
    </Screen>
  );
}
