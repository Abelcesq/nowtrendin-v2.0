import { View, Text, ActivityIndicator } from 'react-native';
import { Clock } from 'lucide-react-native';
import { Screen } from '../../components/ui/Screen';
import { SignalCard } from '../../components/trends/SignalCard';
import { LockedSignalsBanner } from '../../components/trends/LockedSignalsBanner';
import { useAuthStore } from '../../store/auth.store';
import { TierID } from '../../constants/tiers';
import { dataWindowLabel } from '../../lib/signals';
import { useTierFeed } from '../../hooks/useSignals';

const DAY = 24 * 60 * 60 * 1000;

export default function History() {
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const { accessible, lockedCount, isLoading } = useTierFeed(tier);

  const t = Date.now();
  const today = accessible.filter((s) => t - s.createdAt < DAY);
  const earlier = accessible.filter((s) => t - s.createdAt >= DAY);

  return (
    <Screen scroll>
      <View className="flex-row items-center justify-between pt-4 mb-4">
        <Text className="text-textPrimary text-2xl font-bold">History</Text>
        <View className="flex-row items-center gap-1.5 px-3 py-1.5 rounded-full bg-surface border border-border">
          <Clock size={12} color="#5B6472" />
          <Text className="text-textSecondary text-xs font-bold">{dataWindowLabel(tier)}</Text>
        </View>
      </View>

      {isLoading && <ActivityIndicator size="large" color="#00C896" style={{ marginTop: 60 }} />}

      {!isLoading && accessible.length === 0 && lockedCount === 0 && (
        <Text className="text-textMuted text-center mt-16">No signals yet.</Text>
      )}

      {today.length > 0 && (
        <>
          <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3">Today</Text>
          {today.map((s) => (
            <SignalCard key={s.id} signal={s} />
          ))}
        </>
      )}

      {earlier.length > 0 && (
        <>
          <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3 mt-3">Earlier</Text>
          {earlier.map((s) => (
            <SignalCard key={s.id} signal={s} />
          ))}
        </>
      )}

      <View className="mt-2">
        <LockedSignalsBanner tier={tier} lockedCount={lockedCount} />
      </View>
    </Screen>
  );
}
