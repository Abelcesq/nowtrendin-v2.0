import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { CreditCard, Check, ChevronLeft } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { useAuthStore } from '../../../store/auth.store';
import { TIERS, TierID } from '../../../constants/tiers';

// Billing — UI shell (Stripe integration deferred). Shows the current plan +
// entitlements; "Manage billing" is wired when Stripe lands.
export default function Billing() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const cfg = TIERS[tier];

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="pt-4 mb-2 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#5B6472" /><Text className="text-textSecondary text-base">Back</Text>
      </TouchableOpacity>
      <Text className="text-textPrimary text-2xl font-bold mb-1">Billing</Text>
      <Text className="text-textMuted text-sm mb-4">Your plan and payment.</Text>

      <View className="bg-surface rounded-2xl p-5 border border-border mb-4">
        <View className="flex-row items-center gap-2 mb-2">
          <CreditCard size={18} color={cfg.colour} />
          <Text className="text-base font-bold" style={{ color: cfg.colour }}>{cfg.name} Plan</Text>
        </View>
        <Text className="text-textPrimary text-3xl font-black">${cfg.price}<Text className="text-textMuted text-sm font-normal">/mo</Text></Text>
        <View className="mt-3">
          {(cfg.features ?? []).slice(0, 5).map((f: string, i: number) => (
            <View key={i} className="flex-row items-center gap-2 py-1">
              <Check size={14} color="#00C896" />
              <Text className="text-textSecondary text-[13px]">{f}</Text>
            </View>
          ))}
        </View>
      </View>

      <TouchableOpacity className="bg-elevated rounded-xl border border-border py-3.5 items-center" disabled>
        <Text className="text-textMuted text-sm font-semibold">Manage billing — coming soon</Text>
      </TouchableOpacity>
      <Text className="text-textMuted text-xs text-center mt-3 px-4 leading-4">
        Payment management arrives with the upcoming billing release. Your plan and entitlements are
        shown above; contact support to change plans in the meantime.
      </Text>
    </Screen>
  );
}
