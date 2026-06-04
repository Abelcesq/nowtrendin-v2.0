import { View, Text } from 'react-native';
import { useRouter } from 'expo-router';
import { Screen } from '../../components/ui/Screen';
import { MembershipPlans } from '../../components/membership/MembershipPlans';
import { useAuthStore } from '../../store/auth.store';
import { setTier as apiSetTier } from '../../lib/auth';
import { TierID } from '../../constants/tiers';

export default function Membership() {
  const router = useRouter();
  const updateTier = useAuthStore((s) => s.updateTier);

  const apply = async (tier: TierID) => {
    updateTier(tier);
    await apiSetTier(tier);
    router.replace('/(app)');
  };

  return (
    <Screen scroll>
      <View className="pt-10 pb-4">
        <Text className="text-textPrimary text-3xl font-bold mb-2">Choose your plan</Text>
        <Text className="text-textMuted text-base">Start measuring attention intelligence today.</Text>
      </View>
      <MembershipPlans onChoose={apply} />
    </Screen>
  );
}
