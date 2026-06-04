import { View, Text, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { User, Bell, CreditCard, Shield, FileText, LogOut, ChevronRight, Zap, Briefcase, Building2 } from 'lucide-react-native';
import { Screen } from '../../../components/ui/Screen';
import { useAuthStore } from '../../../store/auth.store';
import { TIERS, TierID } from '../../../constants/tiers';

const TIER_ICONS: Record<TierID, any> = { consumer: Zap, business: Briefcase, enterprise: Building2 };

function Row({ icon, label, onPress }: { icon: React.ReactNode; label: string; onPress?: () => void }) {
  return (
    <TouchableOpacity onPress={onPress} className="flex-row items-center justify-between py-3.5">
      <View className="flex-row items-center gap-3">
        {icon}
        <Text className="text-textPrimary text-base">{label}</Text>
      </View>
      <ChevronRight size={18} color="#475569" />
    </TouchableOpacity>
  );
}

export default function Profile() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const clearAuth = useAuthStore((s) => s.clearAuth);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const cfg = TIERS[tier];
  const Icon = TIER_ICONS[tier];

  const signOut = () => {
    clearAuth();
    router.replace('/login');
  };

  return (
    <Screen scroll>
      <Text className="text-textPrimary text-2xl font-bold pt-4 mb-4">Profile</Text>

      <View className="bg-surface rounded-2xl p-5 border border-border mb-6">
        <View className="w-14 h-14 rounded-full bg-elevated items-center justify-center mb-3">
          <User size={26} color="#94A3B8" />
        </View>
        <Text className="text-textPrimary text-lg font-bold">{user?.name ?? 'Member'}</Text>
        <Text className="text-textMuted text-sm mb-3">{user?.email ?? ''}</Text>
        <View className="flex-row items-center gap-1.5 self-start px-3 py-1.5 rounded-full" style={{ backgroundColor: `${cfg.colour}20` }}>
          <Icon size={14} color={cfg.colour} />
          <Text style={{ color: cfg.colour }} className="text-xs font-bold uppercase">{cfg.name}</Text>
        </View>
      </View>

      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-1">Account</Text>
      <Row icon={<User size={18} color="#94A3B8" />} label="Edit Profile" onPress={() => router.push('/profile/edit')} />
      <Row icon={<Bell size={18} color="#94A3B8" />} label="Notifications" />
      <Row icon={<CreditCard size={18} color="#94A3B8" />} label="Billing" />
      <Row icon={<Shield size={18} color="#94A3B8" />} label="Membership" onPress={() => router.push('/profile/membership')} />

      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-1 mt-5">Legal</Text>
      <Row icon={<FileText size={18} color="#94A3B8" />} label="Terms & Conditions" />

      <TouchableOpacity onPress={signOut} className="flex-row items-center gap-3 py-4 mt-4">
        <LogOut size={18} color="#DC2626" />
        <Text className="text-error text-base font-semibold">Sign Out</Text>
      </TouchableOpacity>
    </Screen>
  );
}
