import { View, Text } from 'react-native';
import { Bell, Zap, Briefcase, Building2 } from 'lucide-react-native';
import { Logo, Wordmark } from '../../components/ui/Logo';
import { Screen } from '../../components/ui/Screen';
import { SignalCard } from '../../components/trends/SignalCard';
import { LockedSignalsBanner } from '../../components/trends/LockedSignalsBanner';
import { useAuthStore } from '../../store/auth.store';
import { TIERS, TierID } from '../../constants/tiers';
import { getSignals, dataWindowLabel } from '../../lib/signals';

const TIER_ICONS: Record<TierID, any> = { consumer: Zap, business: Briefcase, enterprise: Building2 };

export default function Dashboard() {
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const cfg = TIERS[tier];
  const Icon = TIER_ICONS[tier];

  const { accessible, lockedCount } = getSignals(tier);
  const recent = accessible.slice(0, 4);

  return (
    <Screen scroll>
      <View className="flex-row items-center justify-between pt-4 mb-1">
        <View className="flex-row items-center gap-2">
          <Logo size={34} />
          <View>
            <Wordmark size="text-xl" />
            <Text className="text-textMuted text-[10px] tracking-widest uppercase">Attention Intelligence</Text>
          </View>
        </View>
        <View className="w-9 h-9 rounded-full bg-surface items-center justify-center border border-border">
          <Bell size={18} color="#5B6472" />
        </View>
      </View>

      <View className="bg-surface rounded-2xl p-5 border border-border my-4">
        <Text className="text-textPrimary text-lg font-bold mb-3">
          Good day, {user?.name ?? 'there'} 👋
        </Text>
        <View className="flex-row items-center gap-2">
          <View className="flex-row items-center gap-1.5 px-3 py-1.5 rounded-full" style={{ backgroundColor: `${cfg.colour}20` }}>
            <Icon size={14} color={cfg.colour} />
            <Text style={{ color: cfg.colour }} className="text-xs font-bold uppercase">
              {cfg.name} Plan
            </Text>
          </View>
          <Text className="text-textMuted text-xs">{dataWindowLabel(tier)}</Text>
        </View>
      </View>

      <View className="flex-row items-center justify-between mb-3">
        <Text className="text-textSecondary text-xs uppercase tracking-wider">
          {tier === 'enterprise' ? 'Live Signals' : 'Recent Signals'}
        </Text>
        <Text className="text-textMuted text-[10px]">{dataWindowLabel(tier)}</Text>
      </View>

      {recent.map((s) => (
        <SignalCard key={s.id} signal={s} />
      ))}

      <View className="mt-2">
        <LockedSignalsBanner tier={tier} lockedCount={lockedCount} />
      </View>
    </Screen>
  );
}
