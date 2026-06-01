import { View, Text } from 'react-native';
import { Bell, Zap, Briefcase, Building2 } from 'lucide-react-native';
import { Logo, Wordmark } from '../../components/ui/Logo';
import { Screen } from '../../components/ui/Screen';
import { TierGate } from '../../components/trends/TierGate';
import { useAuthStore } from '../../store/auth.store';
import { TIERS, TierID } from '../../constants/tiers';

const TIER_ICONS: Record<TierID, any> = { consumer: Zap, business: Briefcase, enterprise: Building2 };

function SignalCard({ topic, score, stage, age }: { topic: string; score: number; stage: string; age: string }) {
  return (
    <View className="bg-surface rounded-xl p-4 mb-3 border border-border">
      <View className="flex-row items-center justify-between">
        <Text className="text-textPrimary font-semibold text-base">{topic}</Text>
        <Text className="text-primary font-black text-2xl">{score}</Text>
      </View>
      <View className="flex-row items-center justify-between mt-1">
        <Text className="text-primary text-xs font-bold">{stage} ↑</Text>
        <Text className="text-textMuted text-xs">{age}</Text>
      </View>
    </View>
  );
}

export default function Dashboard() {
  const user = useAuthStore((s) => s.user);
  const tier = (user?.tier ?? 'consumer') as TierID;
  const cfg = TIERS[tier];
  const Icon = TIER_ICONS[tier];

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
          <Text className="text-textMuted text-xs">
            {tier === 'enterprise' ? 'Live data' : tier === 'business' ? 'Data: 1h+' : 'Data: 12h+'}
          </Text>
        </View>
      </View>

      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3">Recent Signals</Text>
      <SignalCard topic="agentic coding" score={87} stage="BREAKOUT" age="14h ago" />
      <SignalCard topic="mcp servers" score={72} stage="STRONG" age="13h ago" />

      <Text className="text-textSecondary text-xs uppercase tracking-wider mb-3 mt-4">Live Signal</Text>
      <TierGate requiredTier="business" feature="canSearch" message="Live data requires the Business plan or higher">
        <SignalCard topic="quantum LLMs" score={94} stage="VIRAL" age="22m ago" />
      </TierGate>
    </Screen>
  );
}
