import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { ChevronLeft } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { MembershipPlans } from '../../../components/membership/MembershipPlans';
import { useAuthStore } from '../../../store/auth.store';
import { setTier as apiSetTier } from '../../../lib/auth';
import { TierID } from '../../../constants/tiers';

export default function ProfileMembership() {
  const router = useRouter();
  const updateTier = useAuthStore((s) => s.updateTier);

  const apply = async (tier: TierID) => {
    // Persist first, then change local tier. Changing the tier rebuilds the
    // tab navigator (Business/Enterprise add the Search tab), which clears the
    // back stack — so navigate with replace() instead of back().
    await apiSetTier(tier);
    updateTier(tier);
    router.replace('/(app)');
  };

  return (
    <Screen scroll>
      <TouchableOpacity onPress={() => router.back()} className="mt-4 mb-2 self-start flex-row items-center gap-1">
        <ChevronLeft size={22} color="#3C4663" />
        <Text className="text-textSecondary text-sm">Profile</Text>
      </TouchableOpacity>
      <View className="pb-4">
        <Text className="text-textPrimary text-3xl font-bold mb-2">Membership</Text>
        <Text className="text-textMuted text-base">Change your plan anytime.</Text>
      </View>
      <MembershipPlans onChoose={apply} />
    </Screen>
  );
}
