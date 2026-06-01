import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { Bell, Zap, Briefcase, Building2 } from 'lucide-react-native';
import { Logo, Wordmark } from '../../components/ui/Logo';
import { Screen } from '../../components/ui/Screen';
import { GradientScoreRing } from '../../components/ui/GradientScoreRing';
import { SignalCard } from '../../components/trends/SignalCard';
import { LockedSignalsBanner } from '../../components/trends/LockedSignalsBanner';
import { useAuthStore } from '../../store/auth.store';
import { TIERS, TierID } from '../../constants/tiers';
import { dataWindowLabel, stageColor } from '../../lib/signals';
import { useTierFeed } from '../../hooks/useSignals';

const TIER_ICONS: Record<TierID, any> = { consumer: Zap, business: Briefcase, enterprise: Building2 };

export default function Dashboard() {
  const router = useRouter();
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const cfg = TIERS[tier];
  const Icon = TIER_ICONS[tier];

  const { accessible, lockedCount, isLoading, isSample } = useTierFeed(tier);
  const hero = accessible[0];
  const recent = accessible.slice(1, 5);

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

      {isSample && (
        <View className="rounded-lg px-3 py-2 mb-4 border border-border bg-surface">
          <Text className="text-textMuted text-[11px]">Showing sample data — live engine unreachable.</Text>
        </View>
      )}

      {isLoading ? (
        <ActivityIndicator size="large" color="#00C896" style={{ marginTop: 60 }} />
      ) : (
      <>
      {hero && (
        <TouchableOpacity
          activeOpacity={0.9}
          onPress={() => router.push(`/signal/${hero.id}`)}
          className="bg-surface rounded-2xl p-5 border border-border mb-5 items-center"
          style={{ shadowColor: '#000', shadowOpacity: 0.06, shadowRadius: 8, shadowOffset: { width: 0, height: 3 }, elevation: 3 }}
        >
          {tier === 'enterprise' && (
            <View className="flex-row items-center gap-1.5 mb-3 self-start">
              <View className="w-2 h-2 rounded-full bg-primary" />
              <Text className="text-primary text-[10px] font-bold tracking-widest">LIVE</Text>
            </View>
          )}
          <Text className="text-textPrimary font-bold text-lg mb-3">{hero.topic}</Text>
          <GradientScoreRing score={hero.score} color={stageColor(hero.stage)} size="xl" label={hero.stage} />
          <View className="flex-row gap-6 mt-3">
            <Text className="text-textMuted text-xs">DET <Text className="text-textPrimary font-bold">{hero.detection}</Text></Text>
            <Text className="text-textMuted text-xs">CONF <Text className="text-textPrimary font-bold">{hero.confidence}</Text></Text>
          </View>
        </TouchableOpacity>
      )}

      <View className="flex-row items-center justify-between mb-3">
        <Text className="text-textSecondary text-xs uppercase tracking-wider">
          {tier === 'enterprise' ? 'Trending Now' : 'Recent Signals'}
        </Text>
        <Text className="text-textMuted text-[10px]">{dataWindowLabel(tier)}</Text>
      </View>

      {recent.map((s) => (
        <SignalCard key={s.id} signal={s} />
      ))}

      <View className="mt-2">
        <LockedSignalsBanner tier={tier} lockedCount={lockedCount} />
      </View>
      </>
      )}
    </Screen>
  );
}
